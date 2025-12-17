# Changelog

All notable changes to the Visual AutoView project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-17

### Added
- Initial release of Visual AutoView
- 45+ REST API endpoints for automation management
- Interactive graph visualization with vis-network
- Advanced search and filtering capabilities
- Automation comparison and similarity analysis
- Entity relationship mapping
- Dependency graph analysis
- Performance metrics and recommendations
- Light/dark theme system
- Comprehensive test suite (17+ tests)
- Complete documentation and API reference
- Home Assistant integration (custom component)
- TypeScript frontend with Vite
- Docker development environment
- CI/CD workflows with GitHub Actions
- HACS compatibility

### Features
- **Phase 1**: Graph parsing and visualization (4 endpoints)
- **Phase 2**: Dashboard and management (20 endpoints)
- **Phase 3**: Advanced analytics (21 endpoints)
- **Services**: 10+ backend services
- **Frontend**: 7 components with full TypeScript typing
- **Testing**: 17+ unit tests with 100% graph parser coverage

### Documentation
- Quick Start Guide
- API Implementation Complete
- Frontend Verification
- Endpoint Checklist
- Master API Index

## Versioning

- **Major.Minor.Patch** format (e.g., 1.0.0)
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

## How to Report Changes

When contributing, update this file under the appropriate section:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Example Entry

```markdown
## [1.1.0] - 2025-12-24

### Added
- New performance optimization for large automations
- Additional graph visualization options

### Fixed
- Bug in circular dependency detection
- Memory leak in graph parser

### Changed
- Improved API response times
```

## Release Schedule

Releases follow approximately a monthly schedule with:
- Week 1-2: Feature development
- Week 3: Testing and bug fixes
- Week 4: Release preparation and documentation

## Support Policy

- Latest major version receives active support
- Previous major version receives critical bug fixes only
- Older versions are no longer supported

## Migration Guide

Migration guides between major versions will be documented in the GitHub releases and in separate MIGRATION.md files.
