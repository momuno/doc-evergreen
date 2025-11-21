# Changelog

All notable changes to doc-evergreen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-21

### Added
- **Standalone installation**: Install globally with `pipx install doc-evergreen`
- **Convention-based discovery**: Templates in `.doc-evergreen/` directory
- **Init command**: `doc-evergreen init` to bootstrap new projects
- **Short-form commands**: `doc-evergreen regen-doc readme` finds `.doc-evergreen/readme.json`
- **Improved CLI help**: Better formatting with clear line breaks
- **Comprehensive documentation**: Installation guide, troubleshooting, and uninstall instructions
- **Development history**: Copied all planning artifacts to `.ai_working/` for transparency
- **RELEASE_NOTES.md**: Comprehensive release documentation
- **CHANGELOG.md**: This file

### Changed
- **BREAKING**: Source paths now relative to project root (cwd), not template location
- **BREAKING**: Requires installation (pip/pipx) - no longer run from source only
- **Improved**: CLI help text formatting (no text wrapping, clear sections)
- **Improved**: Quick Start only in README, USER_GUIDE is reference documentation
- **Improved**: Documentation structure (README = tutorial, USER_GUIDE = reference)
- **Standardized**: Naming convention (doc-evergreen, not doc_evergreen)
- **Updated**: All version references to 0.4.0

### Fixed
- ISSUE-011: Project root support (superseded by convention-based cwd approach)
- ISSUE-004: CLI help text unclear (improved formatting and structure)
- Removed all external project references from documentation
- Fixed version inconsistencies (v0.3.0 → v0.4.0)

### Deprecated
- `doc-update` command (use `regen-doc` instead - provides preview and approval)

### Removed
- Migration guide reference (file didn't exist)
- External references to amplifier and ai_working paths
- Duplication between README and USER_GUIDE
- Quick Start from USER_GUIDE (now only in README)

---

## [0.3.0] - 2025-11-20

### Added
- Template-based regeneration with JSON templates
- Change detection with unified diff preview
- Manual regeneration command (`regen-doc`)
- User approval workflow
- Progress feedback during generation
- Iterative refinement workflow
- Source specification per section
- Comprehensive documentation (TEMPLATES.md, USER_GUIDE.md, BEST_PRACTICES.md)
- Real-world template examples
- 119 integration tests

### Changed
- Improved error messages with actionable guidance

### Fixed
- ISSUE-001: Empty context handling (source validation)
- ISSUE-003: No feedback when globs match zero files
- ISSUE-004: CLI help text unclear
- ISSUE-005: No example templates or documentation
- ISSUE-006: Source specification unclear (template vs CLI)
- ISSUE-007: No progress feedback during generation

---

## [0.2.0] - 2025-11-19

### Added
- Section-level prompts (explicit control per section)
- Sequential DFS generation
- Context flow between sections
- Section review checkpoints

### Changed
- Chunked generation instead of single-shot
- Enhanced source validation

---

## [0.1.0] - 2025-11-18

### Added
- Initial template-based document structure
- Source resolution with glob patterns
- Hierarchical source inheritance
- Single-shot full-document generation
- Preview & accept workflow
- Basic CLI interface

---

## Development Philosophy

This project follows these principles:

- **Ruthless Simplicity**: 16% of explored features implemented (18 of 72)
- **Trust in Emergence**: Features prove necessity through use
- **Present-Moment Focus**: Solve current problems, defer speculation
- **Data-Driven**: "Reconsider when" conditions based on actual usage

See [.ai_working/convergence/MASTER_BACKLOG.md](./.ai_working/convergence/MASTER_BACKLOG.md) for complete feature history and 72 deferred features.

---

[0.4.0]: https://github.com/YOUR_ORG/doc-evergreen/releases/tag/v0.4.0
[0.3.0]: https://github.com/YOUR_ORG/doc-evergreen/releases/tag/v0.3.0
[0.2.0]: https://github.com/YOUR_ORG/doc-evergreen/releases/tag/v0.2.0
[0.1.0]: https://github.com/YOUR_ORG/doc-evergreen/releases/tag/v0.1.0
