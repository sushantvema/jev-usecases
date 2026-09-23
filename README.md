# Jev use cases

Scratch space for exploring TypeSafe System One, starting with Jev: small typed judgments (Noul, Choice, Score) that software can compose instead of prompt-and-parse.

The first scripts are Noul checks — yes/no questions that return a probability. Independent questions share one `state` and run in a single API request.

## Setup

Copy `.env.example` to `.env` and set `JEV_API_KEY`. `.env` is gitignored.

```bash
python3 noul_checks.py
```

Calls `POST https://api.typesafe.ai/v1/systemone` with the stdlib HTTP client. Each case prints model, round-trip latency, noul values, and token usage.
