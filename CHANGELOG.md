# Changelog

All notable changes to this project will be documented in this file.

## [v1.1.0]

### Added
- Re-introduced the Linux build to the GitHub Actions workflow.
- The release process now automatically builds and attaches both Windows and Linux executables.

### Fixed
- Corrected GitHub Actions workflow permissions to allow release creation.
- Resolved build hanging issue by creating separate CI setup scripts (`setup_ci.sh`, `setup_ci.ps1`) that do not launch the main application.
- Made Pygame audio initialization optional to prevent crashes in headless environments like GitHub runners.

## [v1.0.0]

### Added
- Initial release of the Pygame Chess application.
- Game playable against a Stockfish engine with adjustable, human-like difficulty.
- Full UI with menus for selecting time control, difficulty, and player side.
- Real-time evaluation bar and timers.
- Board flipping functionality.
- Sound effects for game events.
- Automated asset management (download or generate fallbacks).
- PyInstaller build scripts for creating executables.
- GitHub Actions workflow for automated releases.
