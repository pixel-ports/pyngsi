#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from datetime import datetime
from geojson import Point

from pyngsi.ngsi import DataModel, NgsiException, unescape


def test_create():
    m = DataModel("id", "type")
    assert m["id"] == "id"
    assert m["type"] == "type"


def test_add_field_str():
    m = DataModel("id", "type")
    m.add("projectName", "Pixel")
    assert m.json(
    ) == r'{"id": "id", "type": "type", "projectName": {"value": "Pixel", "type": "Text"}}'


def test_add_field_str_escaped():
    m = DataModel("id", "type")
    m.add("forbiddenCharacters", r"""BEGIN<>"'=;()END""", urlencode=True)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "forbiddenCharacters": {"value": "BEGIN%3C%3E%22%27%3D%3B%28%29END", "type": "STRING_URL_ENCODED"}}'
    assert unescape(m["forbiddenCharacters"]["value"]
                    ) == r"""BEGIN<>"'=;()END"""


def test_add_field_int():
    m = DataModel("id", "type")
    m.add("temperature", 37)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "temperature": {"value": 37, "type": "Integer"}}'


def test_add_field_float():
    m = DataModel("id", "type")
    m.add("temperature", 37.2)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "temperature": {"value": 37.2, "type": "Float"}}'


def test_add_field_bool():
    m = DataModel("id", "type")
    m.add("loading", True)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "loading": {"value": true, "type": "Boolean"}}'


def test_add_field_date_from_str_old_way():
    m = DataModel("id", "type")
    m.add("dateObserved", "2018-01-01T15:00:00", isdate=True)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "dateObserved": {"value": "2018-01-01T15:00:00", "type": "DateTime"}}'


def test_add_field_date_from_str():
    m = DataModel("id", "type")
    m.add_date("dateObserved", "2018-01-01T15:00:00")
    assert m.json(
    ) == r'{"id": "id", "type": "type", "dateObserved": {"value": "2018-01-01T15:00:00", "type": "DateTime"}}'


def test_add_field_url_from_str_old_way():
    m = DataModel("id", "type")
    m.add("dataProvider", "https://www.fiware.org", isurl=True)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "dataProvider": {"value": "https://www.fiware.org", "type": "URL"}}'


def test_add_field_url_from_str():
    m = DataModel("id", "type")
    m.add_url("dataProvider", "https://www.fiware.org")
    assert m.json(
    ) == r'{"id": "id", "type": "type", "dataProvider": {"value": "https://www.fiware.org", "type": "URL"}}'


def test_add_field_date_from_datetime():
    m = DataModel("id", "type")
    d = datetime(2019, 6, 1, 18, 30, 0)
    m.add("dateObserved", d)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "dateObserved": {"value": "2019-06-01T18:30:00Z", "type": "DateTime"}}'


def test_add_location_from_tuple():
    m = DataModel("id", "type")
    m.add("location", (44.8333, -0.5667))
    assert m.json(
    ) == r'{"id": "id", "type": "type", "location": {"value": {"type": "Point", "coordinates": [-0.5667, 44.8333]}, "type": "geo:json"}}'


def test_add_location_from_geojson():
    m = DataModel("id", "type")
    location = Point((-0.5667, 44.8333))
    m.add("location", location)
    assert m.json(
    ) == r'{"id": "id", "type": "type", "location": {"value": {"type": "Point", "coordinates": [-0.5667, 44.8333]}, "type": "geo:json"}}'


def test_add_location_invalid():
    m = DataModel("id", "type")
    with pytest.raises(NgsiException, match=r".*JSON compliant.*"):
        m.add("location", ('A', -0.5667))


def test_cannot_map_ngsi_type():
    m = DataModel("id", "type")
    with pytest.raises(NgsiException, match=r".*Cannot map.*"):
        m.add("unknown", None)


def test_add_field_sequence():
    m = DataModel("id", "type")
    d1 = {}
    d1["major"] = "standard"
    d1["minor"] = "surface"
    d1["dateObserved"] = datetime(2019, 6, 1, 18, 30, 0)
    seq = [{"major": "standard", "minor": "surface", "elapsed": 3600},
           {"major": "standard", "minor": "tropopause", "elapsed": 1800},
           d1]
    m.add("collection", seq)
    assert m.json() == r'{"id": "id", "type": "type", ' \
        r'"collection": {"value": [{"major": "standard", "minor": "surface", "elapsed": 3600}, ' \
        r'{"major": "standard", "minor": "tropopause", "elapsed": 1800}, ' \
        r'{"major": "standard", "minor": "surface", "dateObserved": "2019-06-01 18:30:00"}], ' \
        r'"type": "Array"}}'


# https://fiware-datamodels.readthedocs.io/en/latest/Environment/AirQualityObserved/doc/spec/index.html#representing-air-pollutants
def test_metadata():
    m = DataModel("AirQualityObserved", "AirQualityObserved")
    unitsGP = {"unitCode": {"value": "GP"}}
    unitsGQ = {"unitCode": {"value": "GQ"}}
    m.add("CO", 500, metadata=unitsGP)
    m.add("NO", 45, metadata=unitsGQ)
    assert m.json() == r'{"id": "AirQualityObserved", "type": "AirQualityObserved", ' \
        r'"CO": {"value": 500, "type": "Integer", "metadata": {"unitCode": {"value": "GP"}}}, ' \
        r'"NO": {"value": 45, "type": "Integer", "metadata": {"unitCode": {"value": "GQ"}}}}'


def test_add_relationship():
    # https://github.com/Fiware/tutorials.Entity-Relationships
    m = DataModel("id", "type")
    m.add_relationship("refStore", "Shelf", "001")
    assert m.json() == r'{"id": "id", "type": "type", ' \
        r'"refStore": {"value": "urn:ngsi-ld:Shelf:001", "type": "Relationship"}}'


def test_add_relationship_bad_ref():
    m = DataModel("id", "type")
    with pytest.raises(NgsiException, match=r".*Bad relationship.*"):
        m.add_relationship("store", "Shelf", "001")


def test_add_dict():
    m = DataModel("id", "type")
    m.add("property", {"a": 1, "b": 2})
    assert m.json() == r'{"id": "id", "type": "type", ' \
        r'"property": {"value": {"a": 1, "b": 2}, "type": "Property"}}'


def test_add_address():
    m = DataModel("id", "type")
    addr = {"addressLocality": "London",
            "postalCode": "EC4N 8AF",
            "streetAddress": "25 Walbrook"}
    m.add_address(addr)
    assert m.json() == r'{"id": "id", "type": "type", ' \
        r'"address": {"value": {"addressLocality": "London", ' \
        r'"postalCode": "EC4N 8AF", "streetAddress": "25 Walbrook"}, ' \
        r'"type": "PostalAddress"}}'
