"""AI Code Review — Enterprise-grade review script for GitHub Actions.
Primary: Google Gemini. Fallback: NVIDIA NIM → Groq."""

import os
import sys

import httpx

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
NVIDIA_ENDPOINT = "https://api.build.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-flash"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a Staff Software Engineer conducting a code review \
at Google engineering standards.

## Review Checklist

### Design & Architecture
- Is the change well-scoped (one CL, one thing)?
- Does it fit the existing architecture or introduce unnecessary complexity?
- Is this the right time to add this change?

### Correctness & Bugs
- Logic errors, off-by-one, edge cases, null/exception paths
- Race conditions or concurrency issues
- Incorrect API usage or assumptions

### Security
- Injection vulnerabilities (shell, SQL, command, path traversal)
- Hardcoded secrets or credentials
- Unsafe deserialization or file operations

### Maintainability & Complexity
- Can it be simpler? Will others understand it quickly?
- Dead code, unused imports/variables
- Missing error handling or swallowed exceptions

### Testing
- Are there tests covering the change?
- Do tests follow 3A pattern (Arrange, Act, Assert)?
- Is there a regression test for bug fixes?
- Edge cases documented?

### Style & Convention
- Consistent with surrounding code and project style
- Names clearly express intent (variables, functions, classes)

## Severity
- (none): Required — must fix before LGTM
- Suggestion: Should consider seriously
- Nit: Minor polish, can ignore

## Rules
- Be specific: quote exact lines, suggest concrete fixes
- Praise good code too; if clean, say LGTM"""


def call_gemini(api_key: str, prompt: str) -> str | None:
    payload = {
        "contents": [{"parts": [{"text": SYSTEM_PROMPT}, {"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
    }
    resp = httpx.post(
        GEMINI_ENDPOINT,
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    if resp.status_code == 429:
        return None
    resp.raise_for_status()
    data = resp.json()
    parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [{}])
    return (parts[0].get("text", "") if parts else "") or None


def call_openai_compat(endpoint: str, api_key: str, model: str, prompt: str) -> str | None:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }
    resp = httpx.post(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    if resp.status_code == 429:
        return None
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices", [])
    return (choices[0].get("message", {}).get("content", "") if choices else "") or None


PROVIDERS = [
    ("Gemini", call_gemini, None, None),
    ("NVIDIA", call_openai_compat, NVIDIA_ENDPOINT, NVIDIA_MODEL),
    ("Groq", call_openai_compat, GROQ_ENDPOINT, GROQ_MODEL),
]


def main():
    gemini_key = os.environ.get("GOOGLE_API_KEY")
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")

    if not gemini_key and not nvidia_key and not groq_key:
        print("⚠️ No API key available. Skipping AI review.")
        return

    if len(sys.argv) < 2:
        print("Usage: code_review.py <diff_file> [title]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        diff = f.read()
    if not diff.strip():
        print("✅ No diff to review.")
        return
    if len(diff) > 80000:
        diff = diff[:80000] + "\n... (truncated)"

    title = sys.argv[2] if len(sys.argv) > 2 else ""
    prompt = f"## PR: {title}\n\n```diff\n{diff}\n```"

    result = None
    for name, fn, endpoint, model in PROVIDERS:
        key = {"Gemini": gemini_key, "NVIDIA": nvidia_key, "Groq": groq_key}[name]
        if not key:
            continue
        if endpoint and model:
            result = fn(endpoint, key, model, prompt)
        else:
            result = fn(key, prompt)
        if result is None:
            print(f"⚠️ {name} rate limited, trying next...")
        else:
            print(f"✅ Reviewed by {name}")
            break

    if result is None:
        print("⚠️ All providers rate limited. Skipping AI review this time.")
        return

    print(result)


if __name__ == "__main__":
    main()
