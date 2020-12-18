#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.parse

from datetime import datetime, timedelta
from geojson import Point
from typing import Any
from collections.abc import Sequence, Callable

ONE_WEEK = 7*86400


class NgsiException(Exception):
    pass


def escape(value: str) -> str:
    return urllib.parse.quote(value)


def unescape(value: str) -> str:
    return urllib.parse.unquote(value)


class DataModel(dict):

    transient_timeout = None

    def __init__(self, id: str, type: str, serializer: Callable = str):
        self.serializer = serializer
        self["id"] = id
        self["type"] = type
        if self.transient_timeout:
            self.add_transient(self.transient_timeout)

    @classmethod
    def set_transient(cls, timeout: int = ONE_WEEK):
        cls.transient_timeout = timeout

    @classmethod
    def unset_transient(cls):
        cls.transient_timeout = None

    def add(self, name: str, value: Any,
            isdate: bool = False, isurl: bool = False, urlencode=False, metadata: dict = {}):
        if isinstance(value, str):
            if isdate:
                t = "DateTime"
            elif isurl:
                t = "URL"
            elif urlencode:
                t = "STRING_URL_ENCODED"
            else:
                t = "Text"
            v = escape(value) if urlencode else value
        elif isinstance(value, bool):
            t, v = "Boolean", value
        elif isinstance(value, int):
            t, v = "Integer", value
        elif isinstance(value, float):
            t, v = "Float", value
        elif isinstance(value, datetime):
            # the value datetime MUST be UTC
            t, v = "DateTime", value.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(value, Point):
            t, v = "geo:json", value
        elif isinstance(value, tuple) and len(value) == 2:
            lat, lon = value
            try:
                location = Point((lon, lat))
            except Exception as e:
                raise NgsiException(f"Cannot create geojson field : {e}")
            t, v = "geo:json", location
        elif isinstance(value, Sequence):
            t, v = "Array", value
        elif isinstance(value, dict):
            t, v = "Property", value
        else:
            raise NgsiException(
                f"Cannot map {type(value)} to NGSI type. {name=} {value=}")
        self[name] = {"value": v, "type": t}
        if metadata:
            self[name]["metadata"] = metadata

    def add_date(self, *args, **kwargs):
        self.add(isdate=True, *args, **kwargs)

    def add_now(self, *args, **kwargs):
        self.add(value=datetime.utcnow(), *args, **kwargs)

    def add_url(self, *args, **kwargs):
        self.add(isurl=True, *args, **kwargs)

    def add_relationship(self, rel_name: str, ref_type: str, ref_id: str):
        if not rel_name.startswith("ref"):
            raise NgsiException(
                f"Bad relationship name : {rel_name}. Relationship attributes must use prefix 'ref'")
        t, v = "Relationship", f"urn:ngsi-ld:{ref_type}:{ref_id}"
        self[rel_name] = {"value": v, "type": t}

    def add_address(self, value: dict):
        t, v = "PostalAddress", value
        self["address"] = {"value": v, "type": t}

    def add_transient(self, timeout: int = ONE_WEEK, expire: datetime = None):
        if not expire:
            expire = datetime.utcnow() + timedelta(seconds=timeout)
        self.add("dateExpires", expire)

    def json(self):
        """Returns the datamodel in json format"""
        return json.dumps(self, default=self.serializer, ensure_ascii=False)

    def pprint(self):
        """Returns the datamodel pretty-json-formatted"""
        print(json.dumps(self, default=self.serializer, indent=2))
