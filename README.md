# panopticas

Discover insights into the types of data and functions used in your code.

Inspired by tools like [enry](https://github.com/go-enry/go-enry) and [linguist](https://github.com/github-linguist/linguist)

Features: language detector and metadata identifiers, based on the filename extension, filename details and the shebang line. Detects build configurations, dependency manifests, CI pipeline files, and binary file types.

The official documentation can be found at [panopticas.io](https://panopticas.io)

## Installation

```bash
pip install panopticas
```

## Usage

Change into the directory you want to check the file types of and then run:

```bash
panopticas assess
```

To check a single file and get some metadata:

```bash
panopticas file FILENAME
```

To find URLs in files:

```bash
panopticas urls /path/to/directory
```

## Development

If you want to check out the [panopticas repo](https://github.com/kospex/panopticas) and work on bug fixes, use the pip "editable" install:

```bash
pip install -e .
```

### Running Tests

```bash
pytest -v
```

### Building and Publishing

```bash
python -m build
twine upload dist/*
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT
