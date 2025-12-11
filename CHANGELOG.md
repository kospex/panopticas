# Changelog

The format of this changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 0.0.15 - 2025-12-13

### Changed
 - [Remove package build and twine from dependencies](https://github.com/kospex/panopticas/issues/14)
 - [Version pin direct dependencies in pyproject.toml](https://github.com/kospex/panopticas/issues/13)

## 0.0.14 - 2025-11-24

### Added
 - [Added bare LICENSE filename detection](https://github.com/kospex/panopticas/issues/12)
 - [added groovy types and .properties files](https://github.com/kospex/panopticas/issues/11)

## 0.0.13 - 2025-10-01

### Added
 - [Added binary types](https://github.com/kospex/panopticas/issues/7)
 - [added a switch to skip shebang detection for filenname only tests](https://github.com/kospex/panopticas/issues/8)


## 0.0.12 - 2025-09-17

### Added
 - [Added more CI pipeline configuration files](https://github.com/kospex/panopticas/issues/5)

## 0.0.11 - 2025-09-05

### Added
  - added PowerShell .ps1 as a type
  - Added .exe, .jar and .zip as types (also tagged as binary)
### Changed
 - [Return 'Unknown' instead None type for unknown file types](https://github.com/kospex/panopticas/issues/4)

## 0.0.10 - 2025-05-09

  - added uv.lock as a type (from [Astral uv](https://docs.astral.sh/uv/))
  - added CNAME as github pages and other tools use this for domain mapping
  - added .sarif extension
  - added .python-version (for detecting pinned dependencies)

### Changed
  - moved the version function to use the click implementation


### Added
 - Added .gitleaksignore file
 - Added yarn.lock
 - Added optional line counting feature with `--lines` flag for assess command

### Changed
 - Restructured package layout to follow Python best practices with proper src/panopticas/ structure

## 0.0.9 - 2025-01-12

### Added
  - new function extract_urls_from_file

### Changed
  - changed panopticas file to use extract_urls_from_file

## 0.0.8 - 2025-01-12

### Added
  - .travis.yml identification for [Travis CI](https://www.travis-ci.com/)

### Changed
  - improved pip requirements detection to be regular expression based


## VERSION - DATE
## [Unreleased]

### Added

### Changed
