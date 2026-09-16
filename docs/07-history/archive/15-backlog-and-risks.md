# 15 Backlog and Risks

## MVP Backlog

Near-MVP or adjacent backlog items:

- more blueprint families
- richer example libraries
- better Mermaid validation diagnostics
- more conversion targets after Mermaid

## Post-MVP Backlog

Examples:

- backend image or PDF export using Playwright
- backend SVG renderer
- Mermaid parser validation
- HTML document conversion
- PlantUML export
- draw.io XML import or export
- collaboration
- database persistence if ever needed

## Technical Risks

- wrong blueprint routing at high confidence
- conversion pipelines losing semantics
- preview cache inconsistency
- browser export behavior differing across environments

## AI Quality Risks

- invalid or inconsistent diagram JSON
- hallucinated nodes or relationships
- Mermaid conversion dropping labels or edges
- LLM-only conversion oversimplifying structure

## UX Risks

- unclear clarification prompts
- too much backend processing on live editing interactions
- confusion between preview, convert, and export behavior

## Mitigations

- validate after generate, edit, and convert
- use clarification when routing confidence is too low
- keep local live editing in frontend adapters
- use hybrid conversion for Mermaid Markdown by default
- keep preview loading based on `previewId`
- keep frontend export browser-based for MVP
- defer backend image or PDF rendering until there is a strong product need
