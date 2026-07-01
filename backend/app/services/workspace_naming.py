"""Workspace naming strategy.

Derives a company-oriented default workspace name at registration time.

Heuristic (kept deliberately simple and swappable):
  - infer a company label from the email's domain (e.g. acme.com -> "Acme");
  - for personal/free email providers or undeterminable domains, fall back to
    the previous "<user>'s Workspace" behaviour to preserve backward
    compatibility.

This does not change any API contract: the request/response shapes are
unchanged, only the *value* of the auto-generated workspace name differs.
"""

import re

# Common personal/free email providers -> treat as "no company".
_PERSONAL_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "yahoo.com",
        "ymail.com",
        "icloud.com",
        "me.com",
        "mac.com",
        "aol.com",
        "proton.me",
        "protonmail.com",
        "gmx.com",
        "mail.com",
        "zoho.com",
        "yandex.com",
        "hey.com",
    }
)

# Second-level labels that are not the company (e.g. acme.co.uk -> "acme").
_REGISTRY_LABELS = frozenset({"co", "com", "org", "net", "gov", "edu", "ac"})

_WORD_SPLIT = re.compile(r"[-_]+")


def _company_label_from_domain(domain: str) -> str | None:
    domain = domain.strip().lower()
    if not domain or domain in _PERSONAL_EMAIL_DOMAINS:
        return None

    parts = [p for p in domain.split(".") if p]
    if len(parts) < 2:
        return None

    label = parts[-2]
    if label in _REGISTRY_LABELS and len(parts) >= 3:
        label = parts[-3]
    return label or None


def _prettify(label: str) -> str:
    words = [w for w in _WORD_SPLIT.split(label) if w]
    return " ".join(word.capitalize() for word in words) or label.capitalize()


def derive_workspace_name(*, email: str, full_name: str | None) -> str:
    """Return a company-oriented workspace name, with a personal fallback."""
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""
    label = _company_label_from_domain(domain)
    if label:
        return f"{_prettify(label)} Workspace"

    # Backward-compatible fallback for personal / unknown-domain emails.
    if full_name and full_name.strip():
        base = full_name.strip()
    elif email and "@" in email:
        base = email.split("@")[0]
    else:
        base = "My"
    return f"{base}'s Workspace"
