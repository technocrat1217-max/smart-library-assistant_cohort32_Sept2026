"""Security test adapter for the existing Smart Library prototype.

This module deliberately does not replace or modify the library application.
It validates a request, enforces patron ownership, invokes the existing Python
workflow, and checks the returned text for accidental sensitive-data leakage.
"""

from __future__ import annotations

import base64
import importlib.util
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_PATH = PROJECT_ROOT / "smart-library-renewal-prototype.py"


def _load_prototype():
    spec = importlib.util.spec_from_file_location("smart_library_prototype", PROTOTYPE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load prototype from {PROTOTYPE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prototype = _load_prototype()


@dataclass
class SecurityResponse:
    status: str
    allowed: bool
    response: str
    control: str
    action_taken: str = "NONE"
    loan_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SecurityHarness:
    """Defense-in-depth wrapper used only by the Week 6 test suite."""

    INJECTION_PATTERNS = (
        r"ignore (all |any )?(previous|prior|system) (instructions|rules)",
        r"i[\W_]*g[\W_]*n[\W_]*o[\W_]*r[\W_]*e.{0,30}(instructions|rules)",
        r"override (the )?(system|safety|policy|rules)",
        r"developer mode",
        r"do anything now",
        r"bypass (the )?(confirmation|authorization|guardrail|rules)",
        r"b[\W_]*y[\W_]*p[\W_]*a[\W_]*s[\W_]*s.{0,30}(confirmation|authorization|guardrail|rules)",
        r"pretend (that )?(you are|i am)",
        r"reveal (your )?(system prompt|hidden instructions|internal instructions)",
    )
    INTERNAL_PATTERNS = (
        r"system prompt",
        r"hidden instructions",
        r"tool (names|schema|list)",
        r"internal policy",
        r"reasoning chain",
        r"chain of thought",
    )
    PII_PATTERNS = (
        r"(?:show|give|reveal|list|tell).{0,35}(email|phone|address|patron data|personal data)",
        r"(?:email|phone|address).{0,35}(?:another|other|patron|customer)",
        r"\b\d{3}-\d{2}-\d{4}\b",
    )
    SOCIAL_ENGINEERING_PATTERNS = (
        r"(?:i am|i'm) (?:the )?(librarian|administrator|admin|manager|police)",
        r"(?:urgent|emergency).{0,45}(skip|bypass|override|without)",
        r"(?:trust me|don't verify|do not verify)",
    )
    OUTPUT_PII = (
        (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[EMAIL REDACTED]"),
        (re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"), "[PHONE REDACTED]"),
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN REDACTED]"),
    )

    def __init__(self) -> None:
        self.db = prototype.LibraryDatabase()
        self.assistant = prototype.SmartLibraryAssistant(self.db)

    @staticmethod
    def _normalize(prompt: str) -> str:
        normalized = unicodedata.normalize("NFKC", prompt).lower()
        normalized = " ".join(normalized.split())

        # Inspect a plausible Base64 payload as well as the visible request.
        tokens = re.findall(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{16,}={0,2}(?![A-Za-z0-9+/])", prompt)
        decoded = []
        for token in tokens:
            try:
                value = base64.b64decode(token, validate=True).decode("utf-8")
                if value.isprintable():
                    decoded.append(value.lower())
            except (ValueError, UnicodeDecodeError):
                continue
        return normalized + (" " + " ".join(decoded) if decoded else "")

    @staticmethod
    def _matches(text: str, patterns: tuple[str, ...]) -> bool:
        return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)

    def _input_guardrail(self, prompt: str) -> Optional[SecurityResponse]:
        text = self._normalize(prompt)
        if self._matches(text, self.PII_PATTERNS):
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="I cannot provide personal information. I can help with loans belonging to the authenticated patron.",
                control="PII_HANDLING",
            )
        if self._matches(text, self.INTERNAL_PATTERNS):
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="I cannot disclose internal instructions, policies, or implementation details.",
                control="POLICY_FILTERING",
            )
        if self._matches(text, self.INJECTION_PATTERNS):
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="I cannot follow instructions that attempt to bypass the library's authorization or confirmation controls.",
                control="INPUT_GUARDRAIL",
            )
        if self._matches(text, self.SOCIAL_ENGINEERING_PATTERNS):
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="Claimed authority does not replace authentication and authorization.",
                control="AUTHORIZATION_POLICY",
            )
        return None

    def _safe_output(self, text: str) -> tuple[str, bool]:
        changed = False
        for pattern, replacement in self.OUTPUT_PII:
            updated = pattern.sub(replacement, text)
            changed = changed or updated != text
            text = updated
        return text, changed

    def handle_request(
        self,
        *,
        prompt: str,
        authenticated_patron_id: Optional[str],
        loan_id: Optional[str],
        user_confirmation: bool,
    ) -> SecurityResponse:
        blocked = self._input_guardrail(prompt)
        if blocked:
            blocked.loan_id = loan_id
            return blocked

        if not authenticated_patron_id:
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="Authentication is required before viewing or changing a loan.",
                control="AUTHENTICATION",
                loan_id=loan_id,
            )

        if not loan_id or loan_id not in self.db.loans:
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="A valid loan belonging to the authenticated patron is required.",
                control="INPUT_VALIDATION",
                loan_id=loan_id,
            )

        loan = self.db.loans[loan_id]
        if loan.patron_id != authenticated_patron_id:
            return SecurityResponse(
                status="BLOCKED",
                allowed=False,
                response="You are not authorized to access or renew this loan.",
                control="OBJECT_LEVEL_AUTHORIZATION",
                loan_id=loan_id,
            )

        result = self.assistant.process_loan_action(loan_id, user_confirmation)
        response_text, redacted = self._safe_output(str(result.get("explanation", result)))
        return SecurityResponse(
            status="ALLOWED_WITH_REDACTION" if redacted else "ALLOWED",
            allowed=True,
            response=response_text,
            control="OUTPUT_GUARDRAIL" if redacted else "AUTHORIZED_WORKFLOW",
            action_taken=str(result.get("action_taken", "NONE")),
            loan_id=loan_id,
        )
