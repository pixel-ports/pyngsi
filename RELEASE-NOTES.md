# pyngsi 1.2.5
## June 19, 2020

- Added `JSON Path` feature : JSON sources accept a json path to target incoming rows
- Added `FTPS support` to SourceFtp
- Added `relationShip attribute` type to NGSI DataModel. To reference another entity (i.e. refDevice)
- Added `Microsoft Excel support` : SourceMicrosoftExcel
- Added `Source registration` : provide your own Source and associate it with a file extension (example7)
- Deprecated Source.create_souce_from_file(). Replaced by `Source.from_file()`
- Added `side effect` feature to the Agent : allows the Agent to create additional entities (example8)
- Added `kwargs to SourceFTP` constructor

# pyngsi 1.2.4
## May 18, 2020

- Added Apache 2.0 licence
- Added `docker-compose` file for Orion
- Added Travis continous integration
- Removed notebook folder. Now hosted at https://github.com/pixel-ports/pyngsi-tutorial
- Added code coverage
- Added badges
- Source methods `skip_header()` and `limit()` now return a new Source instance
- Fixed metadata unit test for NGSI compliance
- Added more info in SinkException
- Added this `RELEASE-NOTES.md` file

# pyngsi 1.2.3
## March 23, 2020

First public release
