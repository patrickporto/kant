# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [3.0.0]
### Added
- Add CHANGELOG
- Initial configuration for sphinx

### Removed
- Remove event dependencies
- Remove declarative events

### Changed
- Improves the contribute guide

## [2.1.0] - 2018-02-16
### Added
- Add close on EventStoreConnection

## [2.0.2] - 2018-02-09
### Fixed
- Manager default connection

## [2.0.1] - 2018-02-09
### Fixed
- Move get_pk to Aggregate

## [2.0.0] - 2018-02-08
### Added
- Add EventStoreConnection
- Add new constructor from_stream on Aggregate
- Add list support on dispatch
- SQLAlchemy Projections
- Add Manager for easier the connection
- Add refresh_from_db on Aggregate
- Add only option on json method

### Changed
- Rename EventModel to Event

### Fixed
- Side effect on EventStream

### Removed
- Remove EventModelEncoder

## [1.1.2] - 2018-01-29
### Fixed
- The library requires async_generator

## [1.1.1] - 2018-01-29
### Fixed
- Async Generator on Python 3.5 

## [1.1.0] - 2018-01-29
### Changed
- The database schema was using a connection instead of cursor 

## [1.0.4] - 2018-01-27
### Fixed
- Version number

## [1.0.3] - 2018-01-27
### Fixed
- Some packages were not included in the setup

## [1.0.2] - 2018-01-27
### Fixed
- Some packages were not included in the setup

## [1.0.1] - 2018-01-27
### Fixed
- Version number

## [1.0.0] - 2018-01-26
### Added
- Add minimal documentation
- Add consistency mechanism for events

### Changed
- Rename TrackedEntity to Aggregate
- Rename from_dict to make
- Improve error handling
- Rename EventModelMeta to ModelMeta
- Rename EventFieldMapping to FieldMapping

### Removed
- SQLAlchemy as the main dependency
- `event_name` in favour of __class__.__name__

## [0.3.0] - 2018-01-16
### Added
- Add EventStream
- Add Pessimistic Concurrency

## [0.2.1] - 2018-01-16
### Fixed
- The get of EventStore was not working

## [0.2.0] - 2018-01-15
### Added
- Add CUIDField

### Removed
- Remove UUIDField

## [0.1.4] - 2018-01-12
### Added
- Add the library license

## [0.1.3] - 2018-01-11
### Fixed
- The packages were not included in the setup

## [0.1.2] - 2018-01-11
### Added
- Setup the new version release by master

### Fixed
- Some codes were still with the literal string interpolation

## [0.1.1] - 2018-01-11
### Changed
- Replace literal string interpolation to oldest string format

## [0.0.1] - 2018-01-11
### Added
- Add Data Mapper for JSON
- Add declarative events for serialization
- Add JSONEncoder for json library
- Add EventStore on SQLAlchemy
