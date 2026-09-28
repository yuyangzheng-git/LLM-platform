"""
Claim-verification experiment harness.

Runs every claim in datasets/claim_verification_dataset.json through the chat
API twice — once with tools enabled, once with tools disabled — and saves the
raw answers (plus tool-call events and token usage) for later scoring.

Failure semantics: an HTTP error, an SSE `error` event, or a stream that ends
without a `done` event marks that claim/condition as failed (recorded in the
summary CSV) and the process exits with a non-zero status.

Usage (from the repo root, with the backend running):

  python3 scripts/claim_verification.py \
      --base-url http://localhost:3211 \
      --provider openai --model gpt-4o-mini \
      --prompt-template "For the claim below, decide VERIFIED, PARTIALLY VERIFIED or UNVERIFIED and cite sources if you have them.\\n\\nClaim: {claim}"

Requirements:
  - backend running (docker-compose up -d)
  - an enabled model config for --provider (POST /api/v1/models/configs with an API key)
  - Python 3.8+ (stdlib only)

Outputs:
  data/claim_verification_outputs/tools_on/<claim_id>.json
  data/claim_verification_outputs/tools_off/<claim_id>.json
  data/claim_verification_summary.csv
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = REPO_ROOT / "datasets" / "claim_verification_dataset.json"
OUT_DIR = REPO_ROOT / "data" / "claim_verification_outputs"


def http_json(base_url: str, method: str, path: str, payload: dict = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def stream_chat(base_url: str, conversation_id: int, prompt: str, enable_tools: bool) -> dict:
    """POST /api/v1/chat/stream and collect all SSE events."""
    payload = {
        "conversation_id": conversation_id,
        "message": prompt,
        "file_ids": [],
        "stream": True,
        "enable_tools": enable_tools,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}/api/v1/chat/stream",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    events = []
    with urllib.request.urlopen(req, timeout=300) as resp:
        for raw_line in resp:
            line = raw_line.decode().strip()
            if line.startswith("data: "):
                try:
                    events.append(json.loads(line[len("data: "):]))
                except json.JSONDecodeError:
                    continue
    error_events = [e for e in events if e.get("type") == "error" or e.get("error")]
    if error_events:
        raise RuntimeError(f"SSE error event: {error_events[0]}")
    answer = "".join(
        e.get("content", "") for e in events if e.get("type") == "chunk"
    )
    tool_calls = [e for e in events if e.get("type") == "tool_call"]
    tool_results = [e for e in events if e.get("type") == "tool_result"]
    done = next((e for e in events if e.get("type") == "done"), None)
    if done is None:
        raise RuntimeError("stream ended without a done event")
    return {
        "answer": answer,
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "tokens": done.get("tokens", {}),
        "raw_events": events,
    }


def main():
    parser = argparse.ArgumentParser(description="Run the claim-verification experiment")
    parser.add_argument("--base-url", default="http://localhost:3211")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument(
        "--prompt-template",
        default=(
            "For the claim below, decide whether it is VERIFIED, PARTIALLY VERIFIED "
            "or UNVERIFIED, and explain briefly. If you use any source, cite it.\n\nClaim: {claim}"
        ),
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    failed = 0

    for claim in dataset["claims"]:
        for condition in ("tools_on", "tools_off"):
            enable_tools = condition == "tools_on"
            error = None
            result = {"answer": "", "tool_calls": [], "tool_results": [], "tokens": {}}
            try:
                conv = http_json(
                    args.base_url, "POST", "/api/v1/conversations",
                    {
                        "title": f"claim-{claim['id']}-{condition}",
                        "model_provider": args.provider,
                        "model_name": args.model,
                        "temperature": args.temperature,
                    },
                )
            except Exception as e:  # noqa: BLE001
                error = f"conversation creation failed: {e}"
                conv = None

            prompt = args.prompt_template.format(claim=claim["claim"])
            start = time.time()
            if conv is not None:
                try:
                    result = stream_chat(args.base_url, conv["id"], prompt, enable_tools)
                except Exception as e:  # noqa: BLE001
                    error = str(e)

            if error:
                failed += 1

            result["claim"] = claim
            result["condition"] = condition
            result["error"] = error
            result["elapsed_s"] = round(time.time() - start, 1)

            out_path = OUT_DIR / condition / f"claim_{claim['id']}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            summary_rows.append({
                "claim_id": claim["id"],
                "label": claim["label"],
                "condition": condition,
                "answer_length": len(result["answer"]),
                "n_tool_calls": len(result["tool_calls"]),
                "n_tool_results": len(result["tool_results"]),
                "prompt_tokens": result["tokens"].get("prompt", ""),
                "completion_tokens": result["tokens"].get("completion", ""),
                "elapsed_s": result["elapsed_s"],
                "error": error or "",
            })
            print(f"claim {claim['id']:>2} [{condition}] "
                  f"tools={len(result['tool_calls'])} elapsed={result['elapsed_s']}s"
                  f"{' ERROR: ' + error if error else ''}")

    summary_path = REPO_ROOT / "data" / "claim_verification_summary.csv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\nSummary written to {summary_path}")
    print(f"Raw answers written to {OUT_DIR}/tools_on and {OUT_DIR}/tools_off")
    if failed:
        print(f"FAILED: {failed} claim-condition run(s) did not complete successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()
