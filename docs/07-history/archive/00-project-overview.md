# 00 Project Overview

## Executive Summary

GraphPilot is an internal AI-first diagramming tool. It is like draw.io with AI, with two main usage paths:

1. use it from an IDE through MCP
2. use it from a visual web UI

It combines MCP-based generation, GraphPilot JSON, preview URLs, backend validation, and a React Flow editor so teams can move from rough idea to editable diagram quickly.

## Problem Statement

Teams often have ideas for system designs, workflows, ERDs, and architecture diagrams, but manually drawing them takes too long.

## Current Pain Points

- draw.io is free but manual
- Lucidchart is useful but not everyone has a license and seats cost money
- AI-generated Mermaid or Markdown can have syntax or layout issues
- reprompting can break parts that were already correct
- users want diagram generation directly from the IDE
- visual cleanup is still needed even when AI gets most of the design right

## Opportunity

There is an opportunity to create an internal workflow that combines:

- AI-assisted diagram generation
- a visual editor like draw.io
- semantic local JSON files
- IDE integration through MCP
- fast preview and export options

## Proposed Solution

GraphPilot is an MCP-first, database-free, local-file-based architecture for internal AI diagram generation.

Core elements:

- MCP tools for generate, edit, and convert
- GraphPilot JSON as the canonical semantic diagram format
- preview URLs backed by a temporary preview cache
- a React Flow visual editor for manual refinement
- backend-owned blueprint files under `backend/blueprints/`
- browser export for visual image formats in MVP

## Goals

- make diagram creation faster than manual drawing from scratch
- support IDE-first workflows
- support browser-based visual editing and export
- preserve semantic structure through GraphPilot JSON
- reduce paid diagramming seat dependency for basic internal use

## Non-Goals

- full draw.io feature parity
- full Lucidchart feature parity
- collaboration in the MVP
- database persistence in the MVP
- users and auth in the MVP
- backend PNG or PDF rendering in the MVP

## MVP Summary

GraphPilot follows this architecture:

- Cursor / IDE -> MCP Server -> GraphPilot Core
- React UI -> Local HTTP API -> GraphPilot Core
- GraphPilot Core -> Azure OpenAI + local blueprint files + temporary preview cache

Additional MVP assumptions:

- no database required
- no users or auth required
- frontend and backend are separately deployable
- frontend handles visual export in browser
- backend handles generate, edit, convert, and preview cache
- diagrams are generated artifacts returned in responses
- diagrams are only written to the filesystem if `outputPath` is provided, when the user exports, or when preview cache is needed

## Success Criteria

GraphPilot is successful if users can:

- generate a useful first-pass diagram quickly
- open the result from a preview URL
- edit the diagram manually
- ask AI to edit the current diagram
- export GraphPilot JSON and visual outputs
- use the tool from the IDE or the web UI
