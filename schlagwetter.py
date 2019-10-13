#!/usr/bin/env python3

import click
import json
import sys
import xmltodict

from pathlib import Path
from provit import Provenance

PRIMARY_SOURCE_URL = "http://download.codingdavinci.de/index.php/s/YxQy9bzJSXk5cF6/download?path=%2F&files=Data_Ungluecke_2019-08-13.xml"
JSON_DATA_FILE = "mining_accidents_data.json"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("xml_data_file")
def convert(xml_data_file, json_data_file=JSON_DATA_FILE):
    """
    Converts the XML file to a JSON, s.t. I can work with it.
    """
    if not Path(xml_data_file).is_file():
        print(f"File {xml_data_file} does not exist")
        sys.exit(1)

    with open(xml_data_file) as infile:
        data = infile.read()

    dict_data = xmltodict.parse(data)

    with open(json_data_file, "w") as outfile:
        json.dump(dict_data, outfile, indent=4)

    # write provenance information
    prov = Provenance(json_data_file)
    prov.add(
        agents=["schlagwetter"],
        activity="xml_to_json_conversion",
        description="Convert provided XML-file to JSON.",
    )
    prov.add_primary_source(PRIMARY_SOURCE_URL)
    prov.add_sources([xml_data_file])
    prov.save()


if __name__ == "__main__":
    cli(obj={})
