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


def reviewCode(code):
    prompt = (
        "You are a senior software engineer performing a code review.\n\n"
        "Analyze the following Python code for:\n"
        "- Bugs\n"
        "- Security vulnerabilities\n"
        "- Poor coding practices\n"
        "- Potential reliability problems\n\n"
        "Important security guidance:\n"
        "- Do not flag normal use of environment variables for configuration "
        "or secrets as a vulnerability by itself.\n"
        "- Environment variables are an accepted way to provide credentials "
        "and configuration at runtime.\n"
        "- Only report a security issue when there is a concrete vulnerability, "
        "such as hardcoded secrets, SQL injection, command injection, "
        "authentication bypass, unsafe deserialization, or exposed sensitive data.\n\n"
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
        "Code to review:\n\n"
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

    reviewData = json.loads(response.json()["response"])
    review = CodeReview.model_validate(reviewData)

    return review


def makeDecision(review):
    for issue in review.issues:
        if issue.type == "security" and issue.severity in ["medium", "high"]:
            return "reject"

        if issue.severity == "high":
            return "reject"

    if review.riskLevel == "high":
        return "reject"

    return "approve"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m ai_reviewer.reviewer "
            "<python_file> [python_file ...]"
        )
        sys.exit(1)

    overallDecision = "approve"

    for filePath in sys.argv[1:]:
        print(f"\n===== Reviewing: {filePath} =====")

        with open(filePath, "r", encoding="utf-8") as file:
            code = file.read()

        review = reviewCode(code)
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