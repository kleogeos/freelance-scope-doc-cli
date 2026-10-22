#!/usr/bin/env python3
"""Tests for scope_doc.py — run with: python3 test.py"""
import json
import subprocess
import sys
import tempfile
import os

SCRIPT = os.path.join(os.path.dirname(__file__), "scope_doc.py")


def run(args):
    return subprocess.run([sys.executable, SCRIPT] + args, capture_output=True, text=True)


def test_basic_generation():
    data = {
        "client": "Test Client",
        "from": "Me",
        "date": "2026-01-01",
        "project_summary": "Summary <script>alert(1)</script>",
        "outcome": "Outcome text",
        "approach_highlights": ["point one", "point two"],
        "scope_fee": 100,
        "detailed_scope": ["secret step 1", "secret step 2"],
        "deliverables": ["deliverable 1"],
        "timeline": "2 weeks",
    }
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.json")
        pub = os.path.join(d, "public.html")
        paid = os.path.join(d, "paid.html")
        with open(inp, "w") as f:
            json.dump(data, f)
        r = run([inp, "--public", pub, "--paid", paid])
        assert r.returncode == 0, r.stderr
        assert os.path.exists(pub)
        assert os.path.exists(paid)

        public_html = open(pub).read()
        paid_html = open(paid).read()

        # XSS escaping
        assert "<script>" not in public_html
        assert "&lt;script&gt;" in public_html

        # Public doc must NOT leak the confidential scope/deliverables
        assert "secret step 1" not in public_html
        assert "deliverable 1" not in public_html

        # Paid doc must contain the detailed scope and a confidentiality marker
        assert "secret step 1" in paid_html
        assert "CONFIDENTIAL" in paid_html
        assert "Test Client" in paid_html
    print("test_basic_generation: OK")


def test_public_only():
    data = {"client": "Solo Client", "detailed_scope": ["hidden"]}
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.json")
        pub = os.path.join(d, "public.html")
        paid = os.path.join(d, "paid.html")
        with open(inp, "w") as f:
            json.dump(data, f)
        r = run([inp, "--public", pub, "--paid", paid, "--public-only"])
        assert r.returncode == 0, r.stderr
        assert os.path.exists(pub)
        assert not os.path.exists(paid)
    print("test_public_only: OK")


def test_missing_client_errors():
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.json")
        with open(inp, "w") as f:
            json.dump({"from": "Me"}, f)
        r = run([inp])
        assert r.returncode != 0
        assert "client" in r.stderr.lower()
    print("test_missing_client_errors: OK")


def test_missing_file_errors():
    r = run(["/nonexistent/path.json"])
    assert r.returncode != 0
    assert "not found" in r.stderr.lower()
    print("test_missing_file_errors: OK")


def test_invalid_json_errors():
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "bad.json")
        with open(inp, "w") as f:
            f.write("{not valid json")
        r = run([inp])
        assert r.returncode != 0
        assert "invalid json" in r.stderr.lower()
    print("test_invalid_json_errors: OK")


if __name__ == "__main__":
    test_basic_generation()
    test_public_only()
    test_missing_client_errors()
    test_missing_file_errors()
    test_invalid_json_errors()
    print("All tests passed.")
