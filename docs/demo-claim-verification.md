# Demo: Claim Verification with Tools

A reproducible workflow showing how the platform verifies claims using web
search and scraping, with a tool-free control condition. All payloads below
match the real API schemas (verified by `backend/tests/test_chat_tools.py`).

## Prerequisites

- Platform running: `docker-compose up -d` (backend on 3211, frontend on 3212)
- An enabled model config: `POST /api/v1/models/configs` with your API key
- Interactive API docs: http://localhost:3211/docs

## Step 1: Configure a model

```bash
curl -X POST http://localhost:3211/api/v1/models/configs \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai","api_key":"sk-...","default_model":"gpt-4o-mini","enabled":true}'
```

## Step 2: Create a conversation

Every chat request requires a `conversation_id` (requests without it return 422):

```bash
curl -X POST http://localhost:3211/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"claim verification","model_provider":"openai","model_name":"gpt-4o-mini","temperature":0.0}'
# -> {"id": 1, ...}
```

## Step 3: Upload a document (optional)

```bash
printf 'The Eiffel Tower was built in 1889.\nKoalas are a species of bear.\n' > claims.txt
curl -X POST http://localhost:3211/api/v1/files/upload \
  -F "file=@claims.txt"
# -> {"id": 1, ...}
```

## Step 4: Ask with tools enabled

```bash
curl -N -X POST http://localhost:3211/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "For each claim in the file, decide VERIFIED, PARTIALLY VERIFIED or UNVERIFIED and cite sources.",
    "file_ids": [1],
    "enable_tools": true
  }'
```

The SSE stream emits `chunk` events, `tool_call`/`tool_result` events when the
model calls `search_web`/`scrape_webpage`, and a final `done` event with token
usage.

## Step 5: Control condition (tools disabled)

Same conversation schema, same model/temperature, only `enable_tools` differs:

```bash
curl -N -X POST http://localhost:3211/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 2,
    "message": "For each claim in the file, decide VERIFIED, PARTIALLY VERIFIED or UNVERIFIED and cite sources.",
    "file_ids": [1],
    "enable_tools": false
  }'
```

With `enable_tools: false` the backend sends **zero tool definitions** to the
model and skips the tool-execution loop (asserted in
`backend/tests/test_chat_tools.py::test_tool_disabled_stream_sends_no_tools`).

## Step 6: Automated run of the full dataset

A 10-claim dataset (true/false labels + reference URLs) is committed to
`datasets/claim_verification_dataset.json` (tracked in version control;
`data/` is gitignored for outputs only). Run both conditions for all claims:

```bash
python3 scripts/claim_verification.py \
  --base-url http://localhost:3211 --provider openai --model gpt-4o-mini
```

This saves raw answers per claim per condition to
`data/claim_verification_outputs/tools_on|tools_off/` and a summary CSV
(`data/claim_verification_summary.csv`) with tool-call counts, token usage and
elapsed time. Score the raw answers with the rubric in
[docs/research-use-cases.md](research-use-cases.md).

Failure semantics: an HTTP error, an SSE `error` event, or a stream without a
`done` event marks the claim-condition as failed in the summary CSV and the
harness exits non-zero (verified by
`backend/tests/test_claim_harness_failures.py`).

## What This Demo Shows

- Tool-call orchestration (search → scrape) through the platform's tool registry
- A clean A/B split: model, temperature and prompt are identical across
  conditions; only `enable_tools` changes
- Evidence-grounded answering vs. parametric-only answering
- A metric-gathering loop suitable for the study design in [research.md](../research.md)
