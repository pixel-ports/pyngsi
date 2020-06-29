#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.parse

from datetime import datetime
from geojson import Point
from typing import Any
from collections.abc import Sequence, Callable


class NgsiException(Exception):
    pass


def escape(value: str) -> str:
    return urllib.parse.quote(value)


def unescape(value: str) -> str:
    return urllib.parse.unquote(value)


class DataModel(dict):

    def __init__(self, id: str, type: str, serializer: Callable = str):
        self.serializer = serializer
        self["id"] = id
        self["type"] = type

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
            # t = "DateTime" if isdate else "STRING_URL_ENCODED" if urlencode else "Text"
            v = escape(value) if urlencode else value
        elif isinstance(value, bool):
            t, v = "Boolean", value
        elif isinstance(value, int):
            t, v = "Integer", value
        elif isinstance(value, float):
            t, v = "Float", value
        elif isinstance(value, datetime):
            t, v = "DateTime", value.strftime("%Y-%m-%dT%H:%M:%S")
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
        else:
            raise NgsiException(
                f"Cannot map {type(value)} to NGSI type. {name=} {value=}")
        #self[name] = v if t == "Array" else {"value": v, "type": t}
        self[name] = {"value": v, "type": t}
        if metadata:
            self[name]["metadata"] = metadata

    def add_relationship(self, rel_name: str, ref_type: str, ref_id: str):
        if not rel_name.startswith("ref"):
            raise NgsiException(
                f"Bad relationship name : {rel_name}. Relationship attributes must use prefix 'ref'")
        t, v = "Relationship", f"urn:ngsi-ld:{ref_type}:{ref_id}"
        self[rel_name] = {"value": v, "type": t}

    def json(self):
        """Returns the datamodel in json format"""
        return json.dumps(self, default=self.serializer, ensure_ascii=False)

    def pprint(self):
        """Returns the datamodel pretty-json-formatted"""
        print(json.dumps(self, default=self.serializer, indent=2))
