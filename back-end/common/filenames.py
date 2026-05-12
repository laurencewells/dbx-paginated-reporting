import re


def safe_filename(name: str) -> str:
    """Normalise a user-supplied name into a safe filename for MIME headers.

    Replaces anything outside word chars, dash, and dot with underscores; trims
    leading/trailing underscores; falls back to "report" if the result is empty.
    Prevents header injection (CR/LF) and malformed Content-Disposition values.
    """
    return re.sub(r'[^\w\-.]', '_', name).strip('_') or "report"
