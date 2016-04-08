# -*- coding: utf-8 -*-
#
# Copyright 2015 Ternaris, Munich, Germany
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division

import os
from marv import bb, db
from marv.bb import job_logger as logger
from bagbunker import bb_bag


__version__ = '0.0.3'


@bb.job_model()
class Metadata(object):
    sensor_name = db.Column(db.String(42), nullable=False)
    company = db.Column(db.String(126), nullable=False)
    location = db.Column(db.String(126), nullable=False)


@bb.job()
@bb_bag.messages(topics=())
def job(fileset, messages):
    if not fileset.bag:
        return
    path = fileset.dirpath.split(os.sep)
    sensor_name = path[3] if len(path) > 3 else 'unknown'
    company = path[4] if len(path) > 4 else 'unknown'
    location = path[5] if len(path) > 5 else 'unknown'
    logger.info('sensor_name=%s, company=%s, location=%s', sensor_name, company, location)
    yield Metadata(sensor_name=sensor_name, company=company, location=location)


@bb.filter()
@bb.filter_input('sensor', operators=['substring'])
def filter_sensor(query, ListingEntry, sensor):
    return query.filter(ListingEntry.sensor.contains(sensor.val))

@bb.filter()
@bb.filter_input('company', operators=['substring'])
def filter_company(query, ListingEntry, company):
    return query.filter(ListingEntry.company.contains(company.val))

@bb.filter()
@bb.filter_input('location', operators=['substring'])
def filter_location(query, ListingEntry, location):
    return query.filter(ListingEntry.location.contains(location.val))


@bb.listing()
@bb.listing_column('sensor')
@bb.listing_column('company')
@bb.listing_column('location')
def listing(fileset):
    jobrun = fileset.get_latest_jobrun('deepfield::metadata')
    if jobrun is None:
        return {}

    meta = Metadata.query.filter(Metadata.jobrun == jobrun).first()
    if meta is None:
        return {}
    return {
        'sensor': meta.sensor_name,
        'company': meta.company,
        'location': meta.location,
    }
