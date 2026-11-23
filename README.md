# vuln-lab

An intentionally vulnerable Flask application I build one bug class at a time to practice
finding, exploiting, fixing, and testing security vulnerabilities.

> ⚠️ Deliberately insecure. For local learning only. Never deploy it or expose it to a network.

## Bug classes
| # | Class | Vulnerable endpoint | Fix | Test | Write-up |
|---|---|---|---|---|---|
| 1 | IDOR / missing authorization | | | | |

## Run
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python app.py        # http://127.0.0.1:5000
    pytest -v
