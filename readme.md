# Testral — Ecommerce QC Audit Agent (v0)

## What this agent does
- Loads an ecommerce site using Playwright
- Takes full-page screenshots as the primary source of truth
- Uses a local vision LLM (Ollama + Gemma3) to detect visual blockers and QC issues
- Interacts with the page only when a visual blocker is confirmed
- Outputs a short, screenshot-backed QC report as JSON

## What this intentionally does NOT do
- No full QA testing
- No buyer journeys or cart flows
- No DOM crawling or HTML analysis
- No test cases or assertions
- No cloud APIs or external services

## How to run
```bash
python audit.py https://examplestore.com
