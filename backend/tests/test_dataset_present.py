"""
Fresh-clone check: the claim-verification dataset must exist in the tracked
`datasets/` directory and satisfy the schema expected by the harness. Fails
if the dataset was not committed (e.g. left behind in gitignored data/).
"""
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = REPO_ROOT / "datasets" / "claim_verification_dataset.json"

REQUIRED_CLAIM_KEYS = {"id", "claim", "label", "reference_url"}
ALLOWED_LABELS = {"true", "false", "unverified", "disputed"}


def test_dataset_exists_in_tracked_directory():
    assert DATASET_PATH.is_file(), (
        f"dataset missing at {DATASET_PATH}; it must be committed in datasets/ "
        "(data/ is gitignored)"
    )


def test_dataset_schema():
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    claims = dataset.get("claims", [])
    assert len(claims) >= 10, "expected at least 10 claims"

    ids = set()
    for claim in claims:
        missing = REQUIRED_CLAIM_KEYS - set(claim.keys())
        assert not missing, f"claim {claim.get('id')} missing keys: {missing}"
        assert claim["label"] in ALLOWED_LABELS, f"bad label: {claim['label']}"
        assert claim["id"] not in ids, f"duplicate claim id: {claim['id']}"
        ids.add(claim["id"])


def test_harness_points_to_same_dataset():
    harness = REPO_ROOT / "scripts" / "claim_verification.py"
    text = harness.read_text(encoding="utf-8")
    assert 'datasets' in text, "harness must load the dataset from datasets/"
