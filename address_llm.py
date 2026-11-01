import json
import re
import urllib.request
import urllib.error


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def address_heuristic(address, city="", state="", pincode=""):
    text = str(address or "").strip().lower()
    flags = []

    if not text:
        flags.append("Address is empty")

    vague_terms = [
        "near temple", "mandir ke paas", "mandir ke pass",
        "ghar ke samne", "gali ke paas", "nearby",
        "landmark only", "call me", "xyz"
    ]

    if any(term in text for term in vague_terms):
        flags.append("Address contains vague landmark or relative-location wording")

    if len(text) < 15:
        flags.append("Address is unusually short")

    pin = re.sub(r"\D", "", str(pincode or ""))
    if len(pin) != 6:
        flags.append("PIN code is missing or invalid")

    return {
        "ambiguous": bool(flags),
        "reason": flags
    }


def analyze_address(address, city="", state="", pincode=""):
    heuristic = address_heuristic(address, city, state, pincode)

    prompt = f"""
You are validating an Indian e-commerce delivery address.

Address: {address}
City: {city}
State: {state}
PIN code: {pincode}

A landmark-only or relative-location description is ambiguous.
Do not assume that a landmark makes an address complete.
Do not invent house numbers, street names, or missing details.

Return ONLY valid JSON with these fields:
{{
  "is_address_ambiguous": true,
  "missing_information": ["specific missing details"],
  "normalized_address": "cleaned version without inventing details",
  "recommendation": "specific next action"
}}
"""

    try:
        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0}
        }).encode("utf-8")

        request = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))

        llm_result = json.loads(result["response"])

        llm_ambiguous = bool(llm_result.get("is_address_ambiguous", True))

        # A deterministic warning cannot be overruled by the LLM.
        review_required = heuristic["ambiguous"] or llm_ambiguous

        return {
            "available": True,
            "is_address_ambiguous": llm_ambiguous,
            "review_required": review_required,
            "missing_information": llm_result.get("missing_information", []),
            "normalized_address": llm_result.get("normalized_address", address),
            "recommendation": (
                "Manual address confirmation required."
                if heuristic["ambiguous"]
                else llm_result.get("recommendation", "Review address.")
            ),
            "heuristic_flag": heuristic["ambiguous"],
            "heuristic_reason": heuristic["reason"],
            "source": "Local Ollama + deterministic safeguard"
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        ValueError,
        KeyError,
        TypeError
    ) as exc:
        return {
            "available": False,
            "is_address_ambiguous": None,
            "review_required": heuristic["ambiguous"],
            "missing_information": [],
            "normalized_address": address,
            "recommendation": (
                "Manual address review required."
                if heuristic["ambiguous"]
                else "LLM unavailable. Continue with existing validation rules."
            ),
            "heuristic_flag": heuristic["ambiguous"],
            "heuristic_reason": heuristic["reason"],
            "error": str(exc),
            "source": "Deterministic fallback"
        }
