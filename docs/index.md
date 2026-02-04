---
layout: default
title: Panopticas
---

# panopticas

Panopticas helps understand file types with metadata tags, similar to tools like [enry](https://github.com/go-enry/go-enry) and [linguist](https://github.com/github-linguist/linguist)

The core functionality is a language detector and metadata identifier, based on the filename extension, filename details and the shebang line. 

## Why another detector?

The metadata tagging is where panopticas differs from other tools. 

Some files have a "langauge" like XML or YAML, but the filetype is actually a specific product file.

For example:
- pom.xml is a Maven project file, but the language is XML.
- package.json is a Node.js project file, but the language is JSON.
- requirements.txt is a pip project file, but the language is text.
- .github/workflows/python.yml is a GitHub Actions workflow file, but the language is YAML, but it's specific to GitHub Actions.

Panopticas helps provide more context for files that are not just a language, but a specific product file.

## Installation

> pip install panopticas

## Usage

Change into the directory you want check the file types of and then run

> panopticas assess

To check a single file and get some metadata

> panopticas file FILENAME

### API reference
\\
Check out the simple explanation of the [API reference](/api), and if you need more detail, check out the few python classes in /src/panopticas/
