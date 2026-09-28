# Research Framing

## Research Question

How can tool-augmented LLM systems help users verify information and synthesize evidence from documents and the web?

### Sub-questions

1. Do tool-augmented answers (web search + scraping + file context) contain fewer unsupported claims than tool-free answers?
2. How does citation quality change when the model must ground claims in retrieved sources?
3. What is the latency and token-cost overhead of tool use, and when is it worth it?

## Method

Run a claim-verification experiment using this platform's built-in tools:

1. **Stimuli**: upload a document (PDF/Word/text) containing factual claims.
2. **Condition A (no tools)**: ask the model to extract and verify claims using only its parametric knowledge.
3. **Condition B (tools)**: enable web search (`search_tool`) and scraping (`web_scraper_tool`), and ask the model to verify each claim against retrieved sources.
4. **Comparison**: compare answers across conditions on factuality, citation quality, latency, and user effort.

A step-by-step protocol is in [docs/demo-claim-verification.md](docs/demo-claim-verification.md).

## Evaluation Metrics

- **Factuality**: share of verified claims that match an authoritative source (human-judged)
- **Citation quality**: presence of a URL/source per claim; source reliability
- **Coverage**: share of claims in the document that the system actually checked
- **Latency**: wall-clock time per answer with and without tools
- **Token cost**: input/output tokens per answer
- **User effort**: number of follow-up prompts needed to reach a usable answer

## Limitations

- Search quality depends on the DuckDuckGo/SearXNG backend; results can be stale or incomplete
- Web scraping may fail on JavaScript-heavy pages or paywalled content
- LLM hallucination can persist even with retrieved evidence (citation ≠ verification)
- Uploaded documents may contain sensitive data (see privacy notes in the README)
- Small-scale pilot: results will not be statistically conclusive

## Reproducibility

1. Start the platform: `docker-compose up -d` (backend on 3211, frontend on 3212).
2. Configure an enabled model (one API call, see [docs/demo-claim-verification.md](docs/demo-claim-verification.md)).
3. Run the dataset harness (raw answers saved per condition):
   ```bash
   python3 scripts/claim_verification.py --base-url http://localhost:3211
   ```
4. Score the raw answers against the labels/references in
   `datasets/claim_verification_dataset.json` (committed, tracked in git);
   record judgments in the CSV template in `docs/research-use-cases.md`.
5. Compare conditions with simple descriptive statistics (accuracy, latency, tool-call counts).

Note: `enable_tools` is the only difference between conditions — model,
temperature, prompt, and conversation schema stay identical.

## Future Work

- Automatic citation extraction from tool outputs
- Retrieval-augmented answer layer with in-context source snippets
- Evaluation harness that runs both conditions programmatically via `/api/v1/chat/stream`
