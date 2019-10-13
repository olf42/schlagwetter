#!/usr/bin/env python3

import click
import json
import random
import requests
import sys
import xmltodict

from pathlib import Path
from provit import Provenance
from pprint import pprint
from time import sleep
from tqdm import tqdm

WEB_SLEEP = 0.1
PRIMARY_SOURCE_URL = "http://download.codingdavinci.de/index.php/s/YxQy9bzJSXk5cF6/download?path=%2F&files=Data_Ungluecke_2019-08-13.xml"
JSON_DATA_FILE = "mining_accidents_data.json"
COORDS_DATA_FILE = "mine_coordinates.json"
TOP_TRUMPS_DATA_FILE = "top_trumps_data.json"
GEOREFERENCE_URL = "https://nominatim.openstreetmap.org/search/'{location}'"

DATENBANK = "Datenbank"
GRUBENUNGLUECKE = "Grubenungluecke"
ORT_INDEX = "Ort_Index"
BERGWERKE_INDEX = "Bergwerke_Index"

N_CARDS = 64
N_SETS = 16
CARD_KEYS = [
    "date",
    "location",
    "no_of_wounded",
    "no_of_dead",
    "initial_cause",
    "result",
]


def get_georeference(locations_unique):
    s = requests.session()
    locations_georeferenced = dict.fromkeys(locations_unique)
    missed_locations = []
    for location in tqdm(locations_unique):
        result = s.get(
            GEOREFERENCE_URL.format(location=location), params={"format": "json"}
        )
        if result.status_code == 200:
            try:
                first_result = result.json()[0]
            except IndexError:
                missed_locations.append(location)
                tqdm.write(f"Error while georeferencing {location}")
                continue
            locations_georeferenced[location] = (
                first_result["lat"],
                first_result["lon"],
            )
        else:
            missed_locations.append(location)
            print("Error while georeferencing {location}")
        sleep(WEB_SLEEP)
    print("Missed:")
    print(json.dumps(missed_locations))
    return locations_georeferenced


def iterate_accidents(data):
    """
    Generator yielding accidents from the mining accidents database
    """
    for accident in data[DATENBANK][GRUBENUNGLUECKE]:
        yield accident


def iterate_json_file(json_data_file):
    """
    Generator yielding accidents from the mining accidents and handling the file opening.
    """
    with open(json_data_file) as infile:
        data = json.load(infile)
        for accident in iterate_accidents(data):
            yield accident


def extract_top_trumps_data(accident, card_keys=CARD_KEYS):
    """
    Extracts all required information from the raw accident data.
    """
    card = dict.fromkeys(card_keys)

    if not "Tote" in accident.keys():
        card["no_of_dead"] = 0
    else:
        if len(accident["Tote"].keys()) == 2:
            card["no_of_dead"] = accident["Tote"]["Tote_min"]
        else:
            card["no_of_dead"] = list(accident["Tote"].values())[0]

    return card


@click.group()
def cli():
    pass


@cli.command()
@click.option("--seed", default=None)
@click.argument("json_data_file", default=JSON_DATA_FILE)
@click.argument("top_trumps_data_file", default=TOP_TRUMPS_DATA_FILE)
def generate_top_trumps_data(
    seed, json_data_file, top_trumps_data_file, n_cards=N_CARDS, n_sets=N_SETS
):
    """
    Generates a random selection of mining accidents to
    with interesting properties to be used in a top trumps like card game
    """
    with open(json_data_file) as infile:
        data = json.load(infile)[DATENBANK][GRUBENUNGLUECKE]
    if not seed:
        seed = random.randint(0, 1e12)
    print(f"Generating cards using seed {seed} ...")
    random.seed(seed)
    sampled_accidents = random.sample(list(data), n_cards)
    final_cards = []
    for accident in sampled_accidents:
        final_cards.append(extract_top_trumps_data(accident))

    card_deck = {"seed": seed, "cards": final_cards}

    with open(top_trumps_data_file, "w") as outfile:
        json.dump(card_deck, outfile, indent=4)


@cli.command()
@click.argument("json_data_file", default=JSON_DATA_FILE)
def get_name_patrons(json_data_file):
    """
    Print a list of all name patrons of all mines (798 names)
    """
    name_patrons = []
    for accident in iterate_json_file(json_data_file):
        name_patrons.append(accident[BERGWERKE_INDEX])
    namelist = list(set(name_patrons))
    namelist.sort()
    pprint(namelist)


@cli.command()
@click.option("--overwrite", is_flag=True, default=False)
@click.argument("json_data_file")
def georeference(overwrite, json_data_file, coords_data_file=COORDS_DATA_FILE):
    """
    This function georeferences the places using nominatim web service
    """
    if not overwrite and Path(coords_data_file).is_file():
        print("Output file already exists. use --overwrite to replace")
        sys.exit(1)

    locations = []
    for accident in iterate_json_file(json_data_file):
        locations.append(accident[ORT_INDEX])

    locations_unique = set(locations)
    locations_with_coordinates = get_georeference(locations_unique)
    with open(coords_data_file, "w") as outfile:
        json.dump(locations_with_coordinates, outfile, indent=4)


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
