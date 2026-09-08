import json
import sys

import requests
from pydantic import BaseModel


class ReviewIssue(BaseModel):
    severity: str
    type: str
    description: str
    recommendation: str


class CodeReview(BaseModel):
    riskLevel: str
    issues: list[ReviewIssue]
    recommendation: str


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"


def reviewCode(code, reviewType="code"):
    if reviewType == "diff":
        reviewTarget = (
            "The following is a Git diff containing changes to Python code. "
            "Review the changes carefully. Focus on problems introduced by "
            "the changes rather than unrelated issues in unchanged code.\n\n"
            "Git diff to review:\n\n"
        )
    else:
        reviewTarget = (
            "The following is Python code. Review the complete code.\n\n"
            "Code to review:\n\n"
        )

    prompt = (
        "You are a senior software engineer performing a code review.\n\n"
        + reviewTarget
        + "Analyze for:\n"
        "- Bugs\n"
        "- Security vulnerabilities\n"
        "- Poor coding practices\n"
        "- Potential reliability problems\n\n"
        "Important security guidance:\n"
        "- Do not flag normal use of environment variables for configuration "
        "or secrets as a vulnerability by itself.\n"
        "- Environment variables are an accepted way to provide credentials "
        "and configuration at runtime.\n"
        "Only report a security issue when there is a concrete and exploitable "
        "vulnerability, such as hardcoded secrets, SQL injection, command injection, "
        "authentication bypass, unsafe deserialization, or exposed sensitive data.\n"
        "- Do not classify normal JSON parsing, validation, exception handling, "
        "retry logic, or multiple independent validation attempts as security "
        "vulnerabilities unless there is a specific exploitable attack path.\n"
        "- Do not report speculative vulnerabilities based only on the possibility "
        "of an exception or malformed input.\n"
        "- For Git diffs, evaluate only problems introduced by the changed lines.\n\n"
        "Return ONLY valid JSON. Do not include markdown, explanations, "
        "or code fences.\n\n"
        "Use exactly this JSON structure:\n"
        "{\n"
        '  "riskLevel": "low|medium|high",\n'
        '  "issues": [\n'
        "    {\n"
        '      "severity": "low|medium|high",\n'
        '      "type": "bug|security|quality|reliability",\n'
        '      "description": "description of the problem",\n'
        '      "recommendation": "recommended fix"\n'
        "    }\n"
        "  ],\n"
        '  "recommendation": "approve|reject"\n'
        "}\n\n"
        + code
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    rawResponse = response.json()["response"]

    try:
        reviewData = json.loads(rawResponse)
        return CodeReview.model_validate(reviewData)
    except (json.JSONDecodeError, ValueError):
        retryPrompt = (
            prompt
            + "\n\nYour previous response was invalid. "
            "Return ONLY JSON matching the exact schema. "
            "The 'issues' field must contain ONLY objects with "
            "severity, type, description, and recommendation. "
            "Do not place strings or other fields inside 'issues'."
        )

        retryResponse = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": retryPrompt,
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )

        retryResponse.raise_for_status()

        retryData = json.loads(retryResponse.json()["response"])
        return CodeReview.model_validate(retryData)


def makeDecision(review):
    for issue in review.issues:
        if issue.type == "security" and issue.severity in ["medium", "high"]:
            return "reject"

    return "approve"

    if review.riskLevel == "high":
        return "reject"

    return "approve"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m ai_reviewer.reviewer "
            "[--diff] <python_file> [python_file ...]"
        )
        sys.exit(1)

    reviewType = "code"

    if sys.argv[1] == "--diff":
        reviewType = "diff"
        code = sys.stdin.read()

        if not code.strip():
            print("No diff provided for review.")
            sys.exit(0)

        review = reviewCode(code, reviewType)
        decision = makeDecision(review)

        print("\n===== Reviewing Git diff =====")
        print(review.model_dump_json(indent=2))
        print()
        print("Pipeline Decision:", decision.upper())

        if decision == "reject":
            sys.exit(1)

    else:
        overallDecision = "approve"

        for filePath in sys.argv[1:]:
            print(f"\n===== Reviewing: {filePath} =====")

            with open(filePath, "r", encoding="utf-8") as file:
                code = file.read()

            review = reviewCode(code, reviewType)
            decision = makeDecision(review)

            print(review.model_dump_json(indent=2))
            print()
            print("Pipeline Decision:", decision.upper())

            if decision == "reject":
                overallDecision = "reject"

        print("\n===== Overall Pipeline Decision =====")
        print(overallDecision.upper())

        if overallDecision == "reject":
            sys.exit(1)
