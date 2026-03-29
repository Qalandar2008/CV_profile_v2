from django import template
from django.utils.translation import get_language

from ..i18n_field import localized_model_value
from ..ui_strings import ui_text

register = template.Library()


@register.simple_tag
def uitext(key: str):
    return ui_text(key)


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
    """Tanlangan til → _lang; bo‘sh bo‘lsa manba maydon; yana bo‘sh bo‘lsa boshqa til."""
    code = (get_language() or "en")[:2]
    return localized_model_value(obj, base_name, code)


@register.simple_tag
def localized_field_lang(obj, base_name: str, lang_code: str):
    """Ro‘yxatlar uchun aniq til kodi (masalan: panel til)."""
    return localized_model_value(obj, base_name, (lang_code or "en")[:2])
