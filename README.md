# schlagwetter

*schlagwetter* is a tool to work with the data on ~2300 mining accidents in Europe.
As this application aims to provide reliable results to maybe even used in a 
scientific context, all actions are documented with provenance information using
[provit](https://github.com/diggr/provit)

## Quickstart

Setup the application according as described under *Installation*. 

This repository contains a Makefile, where all important commands are to be found.
By invoking *make* without arguments the help will display all available commands.

```zsh
$ make
```

## Download the data

You can either download the data with you browser and put in in this directory,
or use the provided *download* method.

```zsh
$ make download
```

## Convert to JSON

Convert the data to JSON using the provided *convert* method

```zsh
$ make convert
```

## Installation

Clone the repository and install the requirements (inside a virtualenv/venv/... - optional, 
but strongly encouraged). 

```zsh
$ git clone https://github.com/olf42/schlagwetter
$ cd schlagwetter
$ python -m venv .
$ pip install -r requirements.txt
```

## Data Provider 

All data used in project was published und as [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) by [Montanhistorisches Dokumentationszentrum (montan.dok) beim Deutschen Bergbau-Museum Bochum](https://www.bergbaumuseum.de/en/)

## Author

Florian Rämisch

## License

* Content / Data: CC-BY 4.0
* Software: GPLv3
