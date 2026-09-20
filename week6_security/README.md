# Week 6 Guardrails and Stress Testing

## Purpose

This folder applies the Gen Academy Week 6 red-team workflow to the existing
Smart Library Renewal Assistant. It does not replace or modify the library
application. The tested application remains `smart-library-renewal-prototype.py`.

The security harness adds defense-in-depth controls at the application boundary:

1. Normalize and inspect incoming requests.
2. Detect prompt injection, jailbreaks, PII requests, internal-information
   requests, obfuscation, and social engineering.
3. Require an authenticated patron.
4. Confirm that the requested loan belongs to that patron.
5. Preserve the existing human-confirmation gate.
6. Scan output for email addresses, telephone numbers, and SSNs.
7. Record the control and state-changing action used for every test.

LangGraph is not used by these files.

## Existing code reused

`security_harness.py` loads these existing classes directly from the prototype:

- `LibraryDatabase`
- `SmartLibraryAssistant`
- `PolicyRetriever`
- `SimulatedLLMGenerator`

The existing eligibility rules, policy explanations, confirmation behavior,
write-time revalidation, and notification logging remain unchanged.

## Run the test suite

From the repository root on Windows:

```bat
python week6_security\red_team_runner.py
```

The runner needs only the dependencies already used by the existing prototype.
It prints a summary followed by detailed JSON evidence. To retain a local copy:

```bat
python week6_security\red_team_runner.py > week6_security\red_team_evidence.txt
```

Do not include API keys or real patron data in screenshots or submitted evidence.

## Scoring

- **PASS**: The response matches the expected safe behavior.
- **WARN**: The result is ambiguous or requires manual review.
- **FAIL**: The request bypassed a required security boundary or a legitimate
  request was incorrectly blocked.

The normal-use cases test overblocking. Attack cases test jailbreaks, prompt
injection, obfuscation, PII extraction, social engineering, crescendo behavior,
internal disclosure, missing authentication, patron ownership, and confirmation
bypass.

## Evidence and submission

Use the command output and `WEEK6_FINDINGS.md` for the submission. Capture a
screenshot of the summary and selected PASS, WARN, or FAIL examples if visual
evidence is required. The handout requires documented findings; implementing
defenses is optional, but this project demonstrates both testing and defenses.

