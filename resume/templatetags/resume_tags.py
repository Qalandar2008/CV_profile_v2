from django import template
from django.utils.translation import get_language

from ..ui_strings import ui_text

register = template.Library()


@register.simple_tag
def uitext(key: str):
    return ui_text(key)


def _suffix():
    code = (get_language() or "en")[:2]
    return {"en": "_en", "uz": "_uz", "ru": "_ru"}.get(code, "_en")


@register.filter
def split_skill_tags(value):
    """Ko‘nikmalar matnini qatorlar va vergul bo‘yicha ajratadi."""
    if not value:
        return []
    out: list[str] = []
    for chunk in str(value).replace(",", "\n").split("\n"):
        s = chunk.strip()
        if s:
            out.append(s)
    return out


@register.simple_tag
def localized_field(obj, base_name: str):
    """Masalan: {% localized_field profile 'full_name' %}"""
    suf = _suffix()
    val = getattr(obj, f"{base_name}{suf}", None)
    if val is not None and str(val).strip():
        return val
    return getattr(obj, f"{base_name}_en", "") or ""
