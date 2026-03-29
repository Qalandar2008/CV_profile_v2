"""
Django LocaleMiddleware (prefix_default_language=False) prefiksiz URL da
get_language_from_request natijasini LANGUAGE_CODE bilan almashtiradi —
cookie (set_language) e'tiborga olinmaydi. Shuning uchun til tugmalari ishlamay qoladi.
Bu yerda cookie bo'yicha tilni tiklaymiz.
"""

from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware
from django.utils import translation


class CookieAwareLocaleMiddleware(LocaleMiddleware):
    def process_request(self, request):
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(urlconf)
        language = translation.get_language_from_request(request, check_path=i18n_patterns_used)
        language_from_path = translation.get_language_from_path(request.path_info)
        if (
            not language_from_path
            and i18n_patterns_used
            and not prefixed_default_language
        ):
            cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if cookie_lang and translation.check_for_language(cookie_lang):
                language = cookie_lang
            else:
                language = settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
