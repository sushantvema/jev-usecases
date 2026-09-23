# Jev use cases

Scratch space for exploring TypeSafe System One, starting with Jev: small typed judgments (Noul, Choice, Score) that software can compose instead of prompt-and-parse.

Scripts send independent questions that share one `state` in a single API request.

- **Noul** — yes/no questions that return a probability.
- **Choice** — pick one option from a defined set; the answer includes the winner, a full probability distribution, and confidence.

## Setup

Copy `.env.example` to `.env` and set `JEV_API_KEY`. `.env` is gitignored.

```bash
python3 noul_checks.py
python3 choice_checks.py
```

Calls `POST https://api.typesafe.ai/v1/systemone` with the stdlib HTTP client. Each case prints model, round-trip latency, answers, and token usage.
