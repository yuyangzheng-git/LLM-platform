# Improvement Plan for RA Applications

## Current Status

This is a strong full-stack LLM project. It demonstrates FastAPI, React, streaming chat, file attachments, web search, web scraping, persistent history, Docker deployment, and multi-provider LLM support.

## Best Research Fit

- Human-AI collaboration
- LLM tool use
- Information verification
- AI workflow prototyping
- Responsible AI systems

Best professor matches:

- Mary-Anne Williams
- Shan Pan
- Peter Leonard
- Sam Kirshner

## Main Issues

- The project looks like an application platform, but the research use case is not yet explicit.
- `backend/pyproject.toml` contains placeholder author metadata.
- There are no visible screenshots or demo examples.
- There is no evaluation of tool calling, web search quality, or file-processing reliability.
- The README does not clearly say what you personally built.

## Highest Priority Improvements

1. Replace placeholder metadata in `backend/pyproject.toml`.
2. Add screenshots or a demo GIF.
3. Add a `research.md` or `experiments.md` file.
4. Add a reproducible demo workflow.
5. Add basic backend tests and document how to run them.

## Recommended Research Framing

Possible research question:

> How can tool-augmented LLM systems help users verify information and synthesize evidence from documents and the web?

Possible experiment:

- Upload a PDF or text file.
- Ask the system to extract factual claims.
- Use web search or scraping tools to verify the claims.
- Compare answers with and without tools.
- Measure factuality, citation quality, latency, and user effort.

## Concrete Tasks

- Add `/docs/research-use-cases.md`.
- Add `/docs/demo-claim-verification.md`.
- Add `/docs/images/` with screenshots.
- Add a test command for FastAPI routes.
- Add a smoke test for model-provider configuration.
- Add privacy notes for uploaded files and API keys.
- Add a `My Contribution` section to the README.

## Suggested README Pitch

Add this near the top:

> This project is a full-stack LLM platform for streaming chat, file analysis, web search, and tool-augmented reasoning. I built it as a research prototype for studying how users interact with AI systems that combine language models with external tools.

## RA Application Value

Current value: High

This should be one of your pinned repositories after cleanup and research framing.

