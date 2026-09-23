"""Smoke-test Jev Noul questions: yes/no probabilities over the same state."""

from __future__ import annotations

import time

from client import system_one

YES = 0.8
NO = 0.2


def print_case(title: str, payload: dict, elapsed_s: float) -> None:
    print(f"\n=== {title} ===")
    print(f"model: {payload.get('model')}")
    print(f"latency: {elapsed_s * 1000:.0f} ms")
    answers = payload.get("answers", {})
    for question_id, answer in answers.items():
        value = answer.get("noul")
        if value is None:
            print(f"  {question_id}: {answer}")
            continue
        if value >= YES:
            label = "yes"
        elif value <= NO:
            label = "no"
        else:
            label = "uncertain"
        print(f"  {question_id}: {value:.3f} ({label})")
    usage = payload.get("usage")
    if usage:
        print(f"usage: {usage}")


def check_support_message() -> None:
    state = (
        "Hi, I've been trying to connect my Stripe account for 3 days and the "
        "integration keeps failing. I'm losing sales. Please help ASAP."
    )
    questions = {
        "is_urgent": {
            "type": "noul",
            "instructions": "Does this message express urgency?",
            "criteria": {
                "true": "Explicitly time-sensitive",
                "false": "No urgency expressed",
            },
        },
        "is_billing": {
            "type": "noul",
            "instructions": "Is this ticket about billing, payments, or charges?",
        },
        "is_technical": {
            "type": "noul",
            "instructions": "Is this ticket about a technical bug or integration failure?",
        },
        "requests_human": {
            "type": "noul",
            "instructions": "Does the customer ask to speak with a person?",
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("urgent support message (several nouls, one request)", payload, elapsed_s)


def check_calm_message() -> None:
    state = "How do I reset my password?"
    questions = {
        "is_urgent": {
            "type": "noul",
            "instructions": "Does this message express urgency?",
        },
        "requests_human": {
            "type": "noul",
            "instructions": "Does the customer ask to speak with a person?",
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("calm how-to question", payload, elapsed_s)


def check_structured_ticket() -> None:
    state = {
        "ticket": {
            "subject": "Duplicate charge",
            "messages": [
                {
                    "from": "customer",
                    "text": "I was charged twice for order A-104. Please refund the duplicate.",
                },
                {"from": "support", "text": "We are checking the charges."},
            ],
        },
        "order": {
            "id": "A-104",
            "charges": [
                {"amount_usd": 49, "status": "captured"},
                {"amount_usd": 49, "status": "captured"},
            ],
        },
        "refund_policy": "Duplicate charges are eligible for a refund.",
    }
    questions = {
        "refund_requested": {
            "type": "noul",
            "instructions": "Does `ticket.messages[0].text` request a refund?",
        },
        "policy_supports_refund": {
            "type": "noul",
            "instructions": (
                "Does `refund_policy` support the refund requested in "
                "`ticket.messages[0].text`, given `order.charges`?"
            ),
        },
        "contains_pii": {
            "type": "noul",
            "instructions": (
                "Does `ticket.messages[0].text` contain personally identifiable "
                "information such as a legal name, email, phone number, or SSN?"
            ),
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("structured ticket with field paths", payload, elapsed_s)


def main() -> None:
    started = time.perf_counter()
    check_support_message()
    check_calm_message()
    check_structured_ticket()
    total_s = time.perf_counter() - started
    print(f"\ntotal: {total_s * 1000:.0f} ms")


if __name__ == "__main__":
    main()
