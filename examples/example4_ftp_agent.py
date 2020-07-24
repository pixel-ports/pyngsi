#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This agent takes JSON data from JSON files hosted on a FTP server, builds NGSI entities, eventually writes to a given Sink.
# https://fiware-orion.readthedocs.io/en/2.0.0/user/walkthrough_apiv2/index.html#entity-creation

# Please have a look at the NOAA fiware agent, for a real-life agent coming with its CLI and relying on SourceFTP
# https://gitpixel.satrdlab.upv.es/fabien.battello/data-acquisition/src/master/noaafwragent

from datetime import datetime

from pyngsi.agent import NgsiAgent
from pyngsi.sources.source import Row
from pyngsi.sources.source_ftp import SourceFtp
from pyngsi.sink import SinkStdout
from pyngsi.ngsi import DataModel


def build_entity(row: Row) -> DataModel:
    rfc = row.record
    m = DataModel(id=rfc["doc_id"], type="RFC")
    m.add("dataProvider", row.provider)
    m.add("title", rfc["title"])
    m.add("publicationDate", datetime.strptime(rfc["pub_date"], "%B %Y"))
    m.add("pageCount", int(rfc["page_count"]))
    return m


def main():
    # Get two RFC descriptions (RFC959 and RFC2228) in JSON format
    # For the sake of simplicity the example use a lambda and a basic string function for the match function
    # f_match could be a real function (not just a lambda) and could make use of regular expression
    # By default user/passwd is set to anonymous/guest
    src = SourceFtp("ftp.ps.pl", paths=[
        "/pub/rfc"], f_match=lambda x: x.endswith("rfc958.json") or x.endswith("rfc2228.json"))

    # If you have an Orion server available, just replace SinkStdout() with SinkOrion()
    sink = SinkStdout()

    # The source has auto-detected that we deal with JSON files, hence has parsed json for you
    agent = NgsiAgent.create_agent(src, sink, process=build_entity).run()

    # Resources are freed. Here the agent removes the temporary directory (where files were downloaded).
    agent.close()


if __name__ == '__main__':
    main()
