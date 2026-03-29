"""Ko‘p tilli maydonlar: manba + _en/_uz/_ru va fallback zanjiri."""

from __future__ import annotations

from typing import Any


def localized_model_value(obj: Any, base_name: str, lang_code: str) -> str:
    """
    1) {base}_{lang}
    2) manba maydon {base} (user yozgan asl matn)
    3) birinchi bo‘sh bo‘lmagan _en / _uz / _ru
    """
    code = (lang_code or "en")[:2]
    suf_map = {"en": "_en", "uz": "_uz", "ru": "_ru"}
    suf = suf_map.get(code, "_en")

    v = getattr(obj, f"{base_name}{suf}", None)
    if v is not None and str(v).strip():
        return str(v).strip()

    src = getattr(obj, base_name, None)
    if src is not None and str(src).strip():
        return str(src).strip()

    for fb in ("_en", "_uz", "_ru"):
        v = getattr(obj, f"{base_name}{fb}", None)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""
