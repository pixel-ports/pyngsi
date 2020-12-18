# pyngsi 2.1.0
## December 18, 2020

- Added Python `dict` type mapping to NGSI datamodels
- Added support for transient entities (entities with expire date)
- Added statistics to HTTP responses
- Added `add_address()` and `add_date_now()` to build NGSI models
- Fixed ISO8601 DateTime format
- Fixed row provider not initialized
- Fixed wrong HTTP port in examples
- Added Known Issues to README
- Upgrade dependencies
- Removed unused dependencies
- Removed broken badge NGSIv2 in README

# pyngsi 2.0.0
## July 30, 2020

- Added `add_date()` and `add_url()` to build NGSI models
- Added facilities to create Sources from local filesystem : `from_files()`, `from_glob()`, `from_globs()`
- Extended Source Registration :
  - works with local files, HTTP server, FTP server
  - register your custom Source globally or associated with a file extension
- Added package `sources`
- Added unit tests
- Refactored

# pyngsi 1.2.6
## June 29, 2020

- Fixed [issue#1](https://github.com/pixel-ports/pyngsi-tutorial) : bad handling of array's in the DataModel

# pyngsi 1.2.5
## June 26, 2020

- Added `JSON Path` feature : JSON sources accept a json path to target incoming rows
- Added `FTPS support` to SourceFtp
- Added `relationShip attribute` type to NGSI DataModel. To reference another entity (i.e. refDevice)
- Added `Microsoft Excel support` : SourceMicrosoftExcel
- Added `Source registration` : provide your own Source and associate it with a file extension
- Deprecated Source.create_souce_from_file(). Replaced by `Source.from_file()`
- Added `side effect` feature to the Agent : allows the Agent to create additional entities
- Added `kwargs to SourceFTP` constructor
- Fixed bad JSON encoding in datamodel

# pyngsi 1.2.4
## May 18, 2020

- Added Apache 2.0 licence
- Added `docker-compose` file for Orion
- Added Travis continous integration
- Removed notebook folder. Now hosted at [github](https://github.com/pixel-ports/pyngsi-tutorial)
- Added code coverage
- Added badges
- Source methods `skip_header()` and `limit()` now return a new Source instance
- Fixed metadata unit test for NGSI compliance
- Added more info in SinkException
- Added this `RELEASE-NOTES.md` file

# pyngsi 1.2.3
## March 23, 2020

First public release
