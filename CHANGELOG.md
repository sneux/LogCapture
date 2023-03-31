# Changelog
All notable changes will be documented in this file.

## [Unreleased]
- Fix bug where exception is thrown when streaming is enabled but no port is 
provided.

## [1.2.1] - 2021-10-22
- Fixed `-d/--delete` flag. No longer need to provide additional information to
use the flag.

## [1.2.0] - 2021-08-20
### Added
- Stream .raw file from device to client instead of storing it on device.
- Added flag to enable deleting generated files from device when complete.

## [1.1.0] - 2021-08-18
### Added
- Support for capturing on multiple FXS ports.

### Changed
- This feature required a change in the order of the CLI arguments.

## [1.0.2] - 2021-08-14
### Added
- A changelog :)
- Better documentation on invocation of script.
- CLI argument parsing through the use of the argparse library.

### Changed
- Local IP is now passed via CLI arguments.
- Removed support for specifying device by network interface.

### Fixed
- Fixed a bug where script was not creating the `Logs` directory on Windows.

## [1.0.1] - 2021-08-13
### Changed
- Refactored code to increase readability.

## [1.0.0] - 2021-08-11
### Added
- No changes, project was simply adopted by new developers.
- Added project to source control and created a new repository for the lab.
