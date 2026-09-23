"""Smoke-test Jev Choice questions: one option from a defined set."""

from __future__ import annotations

import time

from client import system_one

HIGH_CONFIDENCE = 0.7
LOW_CONFIDENCE = 0.3


def print_case(title: str, payload: dict, elapsed_s: float) -> None:
    print(f"\n=== {title} ===")
    print(f"model: {payload.get('model')}")
    print(f"latency: {elapsed_s * 1000:.0f} ms")
    answers = payload.get("answers", {})
    for question_id, answer in answers.items():
        if answer.get("type") != "choice":
            print(f"  {question_id}: {answer}")
            continue
        chosen = answer.get("choice")
        confidence = answer.get("confidence")
        if confidence is None:
            band = "?"
        elif confidence >= HIGH_CONFIDENCE:
            band = "high"
        elif confidence <= LOW_CONFIDENCE:
            band = "low"
        else:
            band = "medium"
        print(f"  {question_id}: {chosen}  confidence={confidence:.2f} ({band})")
        probabilities = answer.get("probabilities") or {}
        ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
        dist = ", ".join(f"{name}={prob:.2f}" for name, prob in ranked)
        print(f"    {dist}")
    usage = payload.get("usage")
    if usage:
        print(f"usage: {usage}")


def check_clear_routing() -> None:
    state = (
        "Hi, I've been trying to connect my Stripe account for 3 days and the "
        "integration keeps failing. I'm losing sales. Please help ASAP."
    )
    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which team should handle this ticket?",
            "criteria": {
                "billing": "Payments, invoicing, refunds, charges",
                "technical": "Bugs, outages, integrations, account connection failures",
                "sales": "Pricing, upgrades, new accounts",
                "other": "Does not fit any of the teams above",
            },
        },
        "tone": {
            "type": "choice",
            "instructions": "What is the customer's tone?",
            "criteria": {"calm": None, "frustrated": None, "angry": None},
        },
        "channel_fit": {
            "type": "choice",
            "instructions": "How should this be handled?",
            "criteria": {
                "bot": "A self-serve or bot reply is enough",
                "agent": "A human support agent should take it",
                "engineering": "This needs an engineer, not frontline support",
            },
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("clear technical ticket (several choices, one request)", payload, elapsed_s)


def check_ambiguous_ticket() -> None:
    state = (
        "The jacket I ordered is the wrong size, and I was also charged twice. "
        "The tracking page still says it's in transit even though it arrived yesterday. "
        "Not sure if I want a refund or an exchange."
    )
    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which team should handle this?",
            "criteria": {
                "returns": "Exchanges, wrong or damaged items",
                "shipping": "Delivery status, delays, lost packages",
                "billing": "Charges, invoices, payment problems",
            },
        },
        "return_reason": {
            "type": "choice",
            "instructions": "If the customer wants to return something, why?",
            "criteria": {
                "wrong_size": "The item doesn't fit",
                "wrong_item": "A different product was delivered",
                "damaged": "The item arrived broken or faulty",
                "changed_mind": "The item is fine, the customer no longer wants it",
                "other": "A return reason that fits none of the above",
            },
        },
        "shipping_issue": {
            "type": "choice",
            "instructions": "If this is a shipping problem, which kind is it?",
            "criteria": {
                "not_delivered": "The package never arrived",
                "delayed": "The package is late but still on its way",
                "wrong_address": "The package went to the wrong place",
                "damaged_in_transit": "The package arrived damaged",
                "other": "A shipping problem that fits none of the above",
            },
        },
        "requested_resolution": {
            "type": "choice",
            "instructions": "What does the customer want to happen?",
            "criteria": {
                "exchange": "Swap the item for a different one",
                "refund": "Money back",
                "replacement": "The same item sent again",
                "information": "Just an answer, no action needed",
            },
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("ambiguous ticket (split teams + speculative choices)", payload, elapsed_s)


def check_none_of_the_above() -> None:
    state = {
        "message": "Can you wish me a happy birthday? It's my birthday today.",
        "product": "payments API",
    }
    questions = {
        "intent": {
            "type": "choice",
            "instructions": "What is `message` asking about, relative to `product`?",
            "criteria": {
                "bug_report": "Something is broken",
                "how_to": "How to use a feature",
                "pricing": "Cost, plans, or billing for the product",
                "other": "Not about the product at all",
            },
        },
        "language": {
            "type": "choice",
            "instructions": "Which language is `message` written in?",
            "criteria": {
                "en": "English",
                "es": "Spanish",
                "fr": "French",
                "other": "Another language",
            },
        },
    }
    payload, elapsed_s = system_one(state, questions)
    print_case("off-topic message should pick other", payload, elapsed_s)


def main() -> None:
    started = time.perf_counter()
    check_clear_routing()
    check_ambiguous_ticket()
    check_none_of_the_above()
    total_s = time.perf_counter() - started
    print(f"\ntotal: {total_s * 1000:.0f} ms")


if __name__ == "__main__":
    main()
