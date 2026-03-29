"""Matnni avtomatik tarjima qilish (Deep Translator / Google)."""

from __future__ import annotations

from typing import Any

# deep_translator — tarmoq talab qiladi; xatolikda jim ishlaydi
try:
    from deep_translator import GoogleTranslator
except ImportError:  # pragma: no cover
    GoogleTranslator = None  # type: ignore[misc, assignment]


def _translator(source: str, target: str) -> Any:
    if GoogleTranslator is None:
        raise RuntimeError("deep_translator o‘rnatilmagan")
    src = source if source != "auto" else "auto"
    return GoogleTranslator(source=src, target=target)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    source_lang / target_lang: 'en' | 'uz' | 'ru'
    """
    text = (text or "").strip()
    if not text or source_lang == target_lang:
        return text
    if GoogleTranslator is None:
        return ""
    try:
        tr = _translator(source_lang, target_lang)
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


def fill_empty_language_fields(
    obj: Any,
    source_lang: str,
    bases: list[str],
) -> None:
    """
    Har bir `base` uchun `{base}_en`, `{base}_uz`, `{base}_ru` maydonlari.
    source_lang dagi qiymat bo‘sh emas bo‘lsa, qolgan tillarda bo‘sh bo‘lganlarini tarjima qilib to‘ldiradi.
    """
    if source_lang not in ("en", "uz", "ru"):
        return
    for base in bases:
        src_key = f"{base}_{source_lang}"
        src_val = getattr(obj, src_key, None)
        if src_val is None:
            continue
        src_str = str(src_val).strip()
        if not src_str:
            continue
        for lang in ("en", "uz", "ru"):
            if lang == source_lang:
                continue
            key = f"{base}_{lang}"
            cur = getattr(obj, key, None)
            cur_str = (str(cur).strip() if cur is not None else "")
            if cur_str:
                continue
            translated = translate_text(src_str, source_lang, lang)
            if translated:
                setattr(obj, key, translated)
