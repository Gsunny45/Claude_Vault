# AGENT HANDOFF: Hermetic OS Design System

**Last Updated**: 2026-06-06 | **Orchestrator**: Hermes
**Allowed Delegates**: [Claude (Desktop), Codex, Skywork, Hermes]

## 1. Boundary Enforcement (STRICT)
- **READ**: `tokens.yaml`, `ARCHITECTURE.md`, `sync-tokens.py`
- **WRITE**: `compose/`, `obsidian/`, `snygg/` (ONLY via `sync-tokens.py` execution)
- **BLOCKED**: `tokens.yaml` (do not hand-edit unless adding new semantic/primitives), `sync-tokens.py` (core pipeline logic).

## 2. Current State
- **Active Goal**: Design system is fully scaffolded with zero placeholders. Claude Desktop successfully generated the master `tokens.yaml` (26KB), `sync-tokens.py` pipeline, and initial target files.
- **Pending Tasks**: 
  - Run `python sync-tokens.py` to populate the empty `compose/`, `obsidian/`, and `snygg/` directories.
  - Validate generated Kotlin/CSS/JSON files against AGP 8.x / Obsidian standards.
- **Known Failures**: None.

## 3. Execution Rules
- **Max Output Tokens**: N/A (Pipeline handles generation).
- **Required Toolsets**: `terminal`, `file`
- **Forbidden Actions**: Do not manually edit generated files. Do not introduce new colors outside the 4-core palette (Void, Violet, Sky, Amber).

## 4. Response Format
- Provide a bulleted summary of pipeline execution results.
- Update this `AGENT_HANDOFF.md` file with the new state before terminating.