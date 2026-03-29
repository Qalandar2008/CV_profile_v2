"""Matnni avtomatik tarjima qilish va manba maydonlardan _en/_uz/_ru to‘ldirish."""

from __future__ import annotations

from typing import Any

try:
    from deep_translator import GoogleTranslator
except ImportError:  # pragma: no cover
    GoogleTranslator = None  # type: ignore[misc, assignment]

_MAX_LEN: dict[str, int] = {
    "full_name": 200,
    "headline": 300,
    "location": 200,
    "title": 300,
    "issuer": 200,
    "company": 200,
    "role": 300,
    "institution": 300,
    "degree": 300,
    "label": 200,
}


def _clip(base: str, text: str) -> str:
    text = (text or "").strip()
    m = _MAX_LEN.get(base)
    if m and len(text) > m:
        return text[:m]
    return text


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    text = (text or "").strip()
    if not text or source_lang == target_lang:
        return text
    if GoogleTranslator is None:
        return ""
    try:
        tr = GoogleTranslator(source=source_lang if source_lang != "auto" else "auto", target=target_lang)
        if len(text) <= 4500:
            return (tr.translate(text) or "").strip()
        chunks: list[str] = []
        for part in text.split("\n\n"):
            p = part.strip()
            if not p:
                chunks.append("")
                continue
            piece = p[:4500] if len(p) > 4500 else p
            chunks.append((tr.translate(piece) or "").strip())
        return "\n\n".join(chunks).strip()
    except Exception:
        return ""


def translate_text_auto(text: str, target_lang: str) -> str:
    text = (text or "").strip()
    if not text or GoogleTranslator is None:
        return ""
    if target_lang not in ("en", "uz", "ru"):
        return ""
    try:
        tr = GoogleTranslator(source="auto", target=target_lang)
        if len(text) <= 4500:
            return (tr.translate(text) or "").strip()
        out: list[str] = []
        for part in text.split("\n\n"):
            p = part.strip()
            if not p:
                out.append("")
                continue
            piece = p[:4500] if len(p) > 4500 else p
            out.append((tr.translate(piece) or "").strip())
        return "\n\n".join(out).strip()
    except Exception:
        return ""


def sync_translations_from_source(obj: Any, bases: list[str]) -> None:
    """Manba maydon + bo‘sh {base}_lang slotlarini to‘ldiradi; xato bo‘lsa manba nusxa."""
    for base in bases:
        src = ""
        raw_base = getattr(obj, base, None)
        if raw_base is not None and str(raw_base).strip():
            src = str(raw_base).strip()
        else:
            for suf in ("_en", "_uz", "_ru"):
                v = getattr(obj, f"{base}{suf}", None)
                if v is not None and str(v).strip():
                    src = str(v).strip()
                    setattr(obj, base, _clip(base, src))
                    break
        if not src:
            continue

        cur_src = getattr(obj, base, None)
        if cur_src is not None and str(cur_src).strip():
            setattr(obj, base, _clip(base, str(cur_src)))
            src = str(getattr(obj, base)).strip()

        for lang in ("en", "uz", "ru"):
            key = f"{base}_{lang}"
            if not hasattr(obj, key):
                continue
            cur = getattr(obj, key, None)
            if cur is not None and str(cur).strip():
                continue
            tr = translate_text_auto(src, lang)
            final = tr if tr else src
            if base in _MAX_LEN:
                final = _clip(base, final)
            setattr(obj, key, final)


def fill_empty_language_fields(obj: Any, source_lang: str, bases: list[str]) -> None:
    sync_translations_from_source(obj, bases)
