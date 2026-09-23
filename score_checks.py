"""Smoke-test Jev Score questions: position on ordered, described levels."""

from __future__ import annotations

import time

from client import system_one

HIGH_CONFIDENCE = 0.7
LOW_CONFIDENCE = 0.3

BUG_SEVERITY = [
    "Cosmetic; no impact to functionality",
    "Broken or degraded feature, but workaround exists",
    "Blocking issue; no workaround exists",
]


def confidence_band(confidence: float | None) -> str:
    if confidence is None:
        return "?"
    if confidence >= HIGH_CONFIDENCE:
        return "high"
    if confidence <= LOW_CONFIDENCE:
        return "low"
    return "medium"


def nearest_level(score: float, legend: dict) -> str:
    numbered = {int(key): text for key, text in legend.items()}
    if not numbered:
        return "?"
    closest = min(numbered, key=lambda level: abs(level - score))
    return f"{closest}: {numbered[closest]}"


def print_case(title: str, payload: dict, elapsed_s: float) -> None:
    print(f"\n=== {title} ===")
    print(f"model: {payload.get('model')}")
    print(f"latency: {elapsed_s * 1000:.0f} ms")
    answers = payload.get("answers", {})
    for question_id, answer in answers.items():
        if answer.get("type") != "score":
            print(f"  {question_id}: {answer}")
            continue
        score = answer.get("score")
        confidence = answer.get("confidence")
        legend = answer.get("legend") or {}
        probabilities = answer.get("probabilities") or {}
        top = max((int(key) for key in legend), default=0)
        normalized = score / top if top else score
        print(
            f"  {question_id}: score={score:.2f}  "
            f"normalized={normalized:.2f}  "
            f"confidence={confidence:.2f} ({confidence_band(confidence)})"
        )
        print(f"    nearest: {nearest_level(score, legend)}")
        ranked = sorted(probabilities.items(), key=lambda item: int(item[0]))
        parts = []
        for level, prob in ranked:
            label = legend.get(level, legend.get(str(level), ""))
            short = label.split(";")[0][:40]
            parts.append(f"{level}={prob:.2f} ({short})")
        print(f"    {', '.join(parts)}")
    usage = payload.get("usage")
    if usage:
        print(f"usage: {usage}")


def check_severity_spectrum() -> None:
    """Three reports, one request each, same severity scale — endpoints and a split."""
    cases = [
        (
            "cosmetic misaligned button",
            "The export button is misaligned by a few pixels on the settings page.",
        ),
        (
            "safari crash with chrome workaround",
            (
                "The export button crashes the settings page in Safari. It works in "
                "Chrome, but a few of our customers only use Safari."
            ),
        ),
        (
            "everyone locked out",
            "Nobody on our team can log in since this morning. We get a 500 error on every attempt.",
        ),
    ]
    for title, state in cases:
        questions = {
            "bug_severity": {
                "type": "score",
                "instructions": "How severe is the reported issue?",
                "criteria": BUG_SEVERITY,
            },
        }
        payload, elapsed_s = system_one(state, questions)
        print_case(title, payload, elapsed_s)


def check_split_dimensions() -> None:
    state = {
        "ticket": (
            "PDF export hangs on a spinner. Third time I've written in. I can still "
            "export CSV and convert it, which takes ages. Repro: Settings → Export → "
            "PDF on Chrome 128 / macOS 14. I'm done waiting."
        ),
        "product": "admin dashboard",
    }
    questions = {
        "severity": {
            "type": "score",
            "instructions": "How severe is the issue in `ticket` for `product`?",
            "criteria": BUG_SEVERITY,
        },
        "frustration": {
            "type": "score",
            "instructions": "How frustrated does the customer appear in `ticket`?",
            "criteria": [
                "Calm, just stating facts",
                "Frustrated but civil",
                "Very angry, strong language or threatening to leave",
            ],
        },
        "report_quality": {
            "type": "score",
            "instructions": "How much does `ticket` give an engineer to work with?",
            "criteria": [
                "No detail; just says something is broken",
                "Names the feature but no steps or environment",
                "Steps to reproduce or environment, but not both",
                "Steps to reproduce and environment",
            ],
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("one ticket, three score dimensions (composite inputs)", payload, elapsed_s)


def check_between_and_resume() -> None:
    state = {
        "resume_excerpt": (
            "Used Python weekly in notebooks for analysis. Have not shipped a "
            "production service. Mentions pandas and matplotlib, no distributed systems."
        ),
        "role": "backend engineer",
    }
    questions = {
        "python_experience": {
            "type": "score",
            "instructions": (
                "How much Python experience does `resume_excerpt` show for a `role` hire?"
            ),
            "criteria": [
                "No Python mentioned",
                "Coursework or hobby only",
                "Used Python at work for scripts or analysis, not production services",
                "Shipped production Python services",
            ],
        },
        "role_fit": {
            "type": "score",
            "instructions": "How well does `resume_excerpt` match a `role` backend hire?",
            "criteria": [
                "Unrelated background",
                "Some adjacent skills, not backend",
                "Partial backend overlap",
                "Clear backend production experience",
            ],
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("resume excerpt: experience vs role fit", payload, elapsed_s)


def main() -> None:
    started = time.perf_counter()
    check_severity_spectrum()
    check_split_dimensions()
    check_between_and_resume()
    total_s = time.perf_counter() - started
    print(f"\ntotal: {total_s * 1000:.0f} ms")


if __name__ == "__main__":
    main()
