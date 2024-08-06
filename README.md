# panopticas

Discover insights into the types of data and functions used in your code.

Inspired by tools like [enry](https://github.com/go-enry/go-enry) and [linguist](https://github.com/github-linguist/linguist)

Initial feaures: language detector and metadata identifiers, based on the filename extension, filename details and the shebang line. 

The official documentation can be found at [panopticas.io](https://panopticas.io)

## Installation

> pip install panopticas

## Usage

Change into the directory you want check the file types of and then run

> panopticas assess

To check a single file and get some metadata

> panopticas file FILENAME

## Development 

If you want to check out the [panopitcas repo](https://github.com/kospex/panopticas) and work on bug fixes, use the pip "editable" install to set up the _panopticas_ CLI for your shell using:
> pip install -e .



