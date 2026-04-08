import re


PUBLIC_RESPONSE_TAG = "public_response"

PUBLIC_RESPONSE_PATTERN = re.compile(
    rf"^\s*<{PUBLIC_RESPONSE_TAG}>\s*(.*?)\s*</{PUBLIC_RESPONSE_TAG}>\s*$",
    re.IGNORECASE | re.DOTALL,
)

INTERNAL_RESPONSE_LEAK_PATTERNS = (
    (
        re.compile(r"^\s*let me\s+(?:start|try|check|inspect|look|read|search|dig|trace|launch|open)\b", re.IGNORECASE),
        "Public response starts with internal planning text.",
    ),
    (
        re.compile(r"^\s*i(?:'ll| will)\s+(?:check|inspect|look|read|search|dig|trace|launch|open)\b", re.IGNORECASE),
        "Public response starts with internal planning text.",
    ),
    (
        re.compile(r"^\s*i(?:'m| am)\s+(?:going to|gonna)\s+(?:check|inspect|look|read|search|dig|trace|launch|open)\b", re.IGNORECASE),
        "Public response starts with internal planning text.",
    ),
    (
        re.compile(r"\bfresh bash session\b", re.IGNORECASE),
        "Public response leaked terminal-planning text.",
    ),
    (
        re.compile(r"\btask agent\b", re.IGNORECASE),
        "Public response leaked agent-planning text.",
    ),
    (
        re.compile(r"\b(?:read_codebase_file|search_codebase|patch_codebase_file|batch_patch_codebase_files|write_working_note|read_working_notes)\b", re.IGNORECASE),
        "Public response leaked internal tool names.",
    ),
    (
        re.compile(r"\bworking scratchpad\b", re.IGNORECASE),
        "Public response leaked internal workflow text.",
    ),
)


def is_skip_response(text):
    return (text or "").strip().upper() == "SKIP"


def has_complete_public_response(text):
    return PUBLIC_RESPONSE_PATTERN.match((text or "").strip()) is not None


def extract_exact_public_response_text(text):
    match = PUBLIC_RESPONSE_PATTERN.match((text or "").strip())

    if not match:
        return ""

    return match.group(1).strip()


def find_public_response_validation_error(text):
    stripped = (text or "").strip()

    if not stripped:
        return "Public response is empty."

    for pattern, message in INTERNAL_RESPONSE_LEAK_PATTERNS:
        if pattern.search(stripped):
            return message

    return ""


def finalize_public_response_text(raw_text):
    stripped = (raw_text or "").strip()

    if is_skip_response(stripped):
        return "SKIP"

    public_text = extract_exact_public_response_text(stripped)

    if not public_text:
        raise ValueError(f"Missing exact <{PUBLIC_RESPONSE_TAG}>...</{PUBLIC_RESPONSE_TAG}> wrapper.")

    validation_error = find_public_response_validation_error(public_text)

    if validation_error:
        raise ValueError(validation_error)

    return public_text


def validate_response_file_content(text):
    stripped = (text or "").strip()

    if not stripped:
        raise ValueError("response.md is empty.")

    if is_skip_response(stripped):
        raise ValueError("response.md must not be written for SKIP.")

    if f"<{PUBLIC_RESPONSE_TAG}>" in stripped.lower() or f"</{PUBLIC_RESPONSE_TAG}>" in stripped.lower():
        raise ValueError("response.md still contains public-response wrapper tags.")

    validation_error = find_public_response_validation_error(stripped)

    if validation_error:
        raise ValueError(validation_error)