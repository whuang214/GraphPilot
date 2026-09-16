# GraphPilot

**Create diagrams with your AI assistant. Refine them visually.**

GraphPilot is a local-first diagramming tool that connects AI-assisted generation through
the Model Context Protocol (MCP) with an interactive browser editor. Create activity,
use case, and block definition diagrams, refine their layout and content, and export
them as SVG or PNG.

[Quickstart](#quickstart) · [Documentation](#documentation)

<!-- Add an editor screenshot or a short demo GIF here. -->

## Features

- **Generate with AI** — use an MCP-compatible assistant to turn your ideas or repository
  context into a structured diagram draft.
- **Edit visually** — move and resize nodes, edit labels, connect elements, and refine
  diagrams with undo/redo, a notation-aware palette, and a property inspector.
- **Validate and arrange** — check diagram structure and notation, then automatically
  lay out generated diagrams before opening them in the editor.
- **Save and export** — keep editable `.gp.json` files in your workspace and export SVG
  or PNG for documentation, presentations, and sharing.

## How it works

Your AI host authors the draft; GraphPilot handles validation, layout, rendering, and
storage deterministically. GraphPilot itself makes no model calls and needs no model
API key. You can also create and edit diagrams directly in the browser without an AI host.

The MCP interface and browser API share one Django service layer and the same local
diagram format. A generated diagram stays editable as you move between the assistant
and the canvas, while a shared renderer keeps browser exports consistent with the
backend's SVG output.

**Built with:** Python · Django REST Framework · TypeScript · React · React Flow ·
PyGraphviz · MCP

## Quickstart

Install [uv](https://docs.astral.sh/uv/) and [Node.js 24](https://nodejs.org/).
`uv` manages the project's Python 3.14 environment; the Python dependencies include
the layout engine.

```sh
git clone https://github.com/whuang214/GraphPilot.git
cd GraphPilot
uv venv
uv pip install -r requirements.txt
cd frontend
npm install
cd ..
uv run python run.py
```

The launcher starts both services, configures their connection, and opens the editor
in your browser. Press **Ctrl+C** to stop them. After the first setup, start it again
with `uv run python run.py`.

For AI-assisted generation, connect your host using the
[MCP server setup instructions](backend/README.md#setup). Platform details, manual
development servers, and environment overrides are covered in the setup guide below.

## Documentation

| Explore | Guide |
| --- | --- |
| Product behavior and design | [Documentation index](docs/README.md) |
| Components and data flow | [Architecture](docs/02-architecture/02-system-design.md) |
| Installation and configuration | [Setup guide](docs/04-development/01-environment.md) |
| Automated checks and verification | [Testing](docs/04-development/02-testing-strategy.md) |

AI coding agents: start with [AGENTS.md](AGENTS.md).
