from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from urllib.parse import quote

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .admin_content_lang import SESSION_KEY, SESSION_KEY_UI, VALID, get_content_lang, get_ui_lang
from .dashboard_i18n import get_dashboard_strings
from .admin_forms import (
    CertificateForm,
    EducationForm,
    InterestForm,
    ResumeProfileForm,
    WorkExperienceForm,
)
from .dashboard_forms import SiteSettingsForm
from .dashboard_style import apply_dashboard_field_styles, field_placeholder
from .models import Certificate, Education, Interest, ResumeProfile, SiteSettings, WorkExperience


def staff_required(view_func):
    """Login + is_staff."""

    def _wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('dashboard:login')}?next={quote(request.path)}")
        if not request.user.is_staff:
            messages.error(request, "Kirish huquqi yo‘q. Faqat xodimlar.")
            return redirect("dashboard:login")
        return view_func(request, *args, **kwargs)

    return _wrap


def _dash_msg(request, key: str) -> str:
    return get_dashboard_strings(get_ui_lang(request)).get(key, key)


def _admin_session_from_query(request):
    """?content_lang= / ?ui_lang= ni sessiyaga yozib, query dan olib tashlaydi."""
    if request.method != "GET":
        return None
    changed = False
    cl = request.GET.get("content_lang") or request.GET.get("lang")
    if cl in VALID:
        request.session[SESSION_KEY] = cl
        changed = True
    ul = request.GET.get("ui_lang")
    if ul in VALID:
        request.session[SESSION_KEY_UI] = ul
        changed = True
    if not changed:
        return None
    q = request.GET.copy()
    for k in ("content_lang", "lang", "ui_lang"):
        if k in q:
            del q[k]
    url = request.path
    if q:
        url = f"{url}?{q.urlencode()}"
    return redirect(url)


@staff_required
def dashboard_index(request):
    profile = ResumeProfile.load()
    return render(
        request,
        "dashboard/index.html",
        {
            "section": "dashboard",
            "cert_count": Certificate.objects.count(),
            "interest_count": Interest.objects.count(),
            "experience_count": WorkExperience.objects.count(),
            "education_count": Education.objects.count(),
            "profile": profile,
        },
    )


@staff_required
def dashboard_profile(request):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    profile = ResumeProfile.load()
    if request.method == "POST":
        form = ResumeProfileForm(request.POST, request.FILES, instance=profile, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_profile_saved"))
            return redirect("dashboard:profile")
    else:
        form = ResumeProfileForm(instance=profile, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "full_name": "Masalan: Ali Valiyev",
            "headline": "Masalan: Senior Python dasturchi",
            "about": "O‘zingiz, tajriba va maqsadlaringiz haqida qisqa yozing…",
            "skills": "Python\nDjango\nREST API",
            "location": "Masalan: Toshkent, O‘zbekiston",
            "email": "you@example.com",
            "phone": "+998 90 123 45 67",
            "website": "https://",
            "linkedin": "https://linkedin.com/in/…",
            "github": "https://github.com/…",
        },
    )

    return render(
        request,
        "dashboard/profile.html",
        {
            "section": "profile",
            "form": form,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
def certificate_list(request):
    lang = get_content_lang(request)
    certificates = Certificate.objects.all()
    return render(
        request,
        "dashboard/certificates/list.html",
        {
            "section": "certificates",
            "certificates": certificates,
            "list_lang": lang,
        },
    )


@staff_required
def certificate_create(request):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = Certificate()
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_cert_added"))
            return redirect("dashboard:certificates")
    else:
        form = CertificateForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "title": "Sertifikat nomi",
            "issuer": "Kim tomonidan berilgan (masalan, Coursera)",
            "description": "Qisqa tavsif…",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/certificates/form.html",
        {
            "section": "certificates",
            "form": form,
            "is_edit": False,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
def certificate_edit(request, pk):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = get_object_or_404(Certificate, pk=pk)
    if request.method == "POST":
        form = CertificateForm(request.POST, request.FILES, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_saved"))
            return redirect("dashboard:certificates")
    else:
        form = CertificateForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "title": "Sertifikat nomi",
            "issuer": "Beruvchi tashkilot",
            "description": "Tavsif…",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/certificates/form.html",
        {
            "section": "certificates",
            "form": form,
            "is_edit": True,
            "object": obj,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def certificate_delete(request, pk):
    obj = get_object_or_404(Certificate, pk=pk)
    lang = get_content_lang(request)
    display_title = getattr(obj, f"title_{lang}", "") or obj.title_en or f"#{obj.pk}"

    if request.method == "POST":
        obj.delete()
        messages.success(request, _dash_msg(request, "msg_deleted"))
        return redirect("dashboard:certificates")

    return render(
        request,
        "dashboard/certificates/confirm_delete.html",
        {
            "section": "certificates",
            "object": obj,
            "display_title": display_title,
        },
    )


@staff_required
def interest_list(request):
    lang = get_content_lang(request)
    interests = Interest.objects.all()
    return render(
        request,
        "dashboard/interests/list.html",
        {
            "section": "interests",
            "interests": interests,
            "list_lang": lang,
        },
    )


@staff_required
def interest_create(request):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = Interest()
    if request.method == "POST":
        form = InterestForm(request.POST, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_int_added"))
            return redirect("dashboard:interests")
    else:
        form = InterestForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "label": "Masalan: Fotografiya, o‘qish…",
            "detail": "Batafsil (ixtiyoriy)",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/interests/form.html",
        {
            "section": "interests",
            "form": form,
            "is_edit": False,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
def interest_edit(request, pk):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = get_object_or_404(Interest, pk=pk)
    if request.method == "POST":
        form = InterestForm(request.POST, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_saved"))
            return redirect("dashboard:interests")
    else:
        form = InterestForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "label": "Qiziqish nomi",
            "detail": "Batafsil",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/interests/form.html",
        {
            "section": "interests",
            "form": form,
            "is_edit": True,
            "object": obj,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def interest_delete(request, pk):
    obj = get_object_or_404(Interest, pk=pk)
    lang = get_content_lang(request)
    display_label = getattr(obj, f"label_{lang}", "") or obj.label_en or f"#{obj.pk}"

    if request.method == "POST":
        obj.delete()
        messages.success(request, _dash_msg(request, "msg_deleted"))
        return redirect("dashboard:interests")

    return render(
        request,
        "dashboard/interests/confirm_delete.html",
        {
            "section": "interests",
            "object": obj,
            "display_label": display_label,
        },
    )


@staff_required
def experience_list(request):
    lang = get_content_lang(request)
    items = WorkExperience.objects.all()
    return render(
        request,
        "dashboard/experience/list.html",
        {
            "section": "experience",
            "items": items,
            "list_lang": lang,
        },
    )


@staff_required
def experience_create(request):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = WorkExperience()
    if request.method == "POST":
        form = WorkExperienceForm(request.POST, request.FILES, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_exp_added"))
            return redirect("dashboard:experience")
    else:
        form = WorkExperienceForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "company": "ACME Inc.",
            "role": "Senior Developer",
            "description": "Responsibilities…",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/experience/form.html",
        {
            "section": "experience",
            "form": form,
            "is_edit": False,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
def experience_edit(request, pk):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = get_object_or_404(WorkExperience, pk=pk)
    if request.method == "POST":
        form = WorkExperienceForm(request.POST, request.FILES, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_saved"))
            return redirect("dashboard:experience")
    else:
        form = WorkExperienceForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "company": "",
            "role": "",
            "description": "",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/experience/form.html",
        {
            "section": "experience",
            "form": form,
            "is_edit": True,
            "object": obj,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def experience_delete(request, pk):
    obj = get_object_or_404(WorkExperience, pk=pk)
    lang = get_content_lang(request)
    role = getattr(obj, f"role_{lang}", "") or obj.role_en or ""
    company = getattr(obj, f"company_{lang}", "") or obj.company_en or ""
    display_title = " — ".join(p for p in (role, company) if p).strip() or f"#{obj.pk}"

    if request.method == "POST":
        obj.delete()
        messages.success(request, _dash_msg(request, "msg_deleted"))
        return redirect("dashboard:experience")

    return render(
        request,
        "dashboard/experience/confirm_delete.html",
        {
            "section": "experience",
            "object": obj,
            "display_title": display_title,
        },
    )


@staff_required
def education_list(request):
    lang = get_content_lang(request)
    items = Education.objects.all()
    return render(
        request,
        "dashboard/education/list.html",
        {
            "section": "education",
            "items": items,
            "list_lang": lang,
        },
    )


@staff_required
def education_create(request):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = Education()
    if request.method == "POST":
        form = EducationForm(request.POST, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_edu_added"))
            return redirect("dashboard:education")
    else:
        form = EducationForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "institution": "MIT",
            "degree": "B.Sc. Computer Science",
            "description": "",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/education/form.html",
        {
            "section": "education",
            "form": form,
            "is_edit": False,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
def education_edit(request, pk):
    redir = _admin_session_from_query(request)
    if redir:
        return redir

    obj = get_object_or_404(Education, pk=pk)
    if request.method == "POST":
        form = EducationForm(request.POST, instance=obj, request=request)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_saved"))
            return redirect("dashboard:education")
    else:
        form = EducationForm(instance=obj, request=request)
        apply_dashboard_field_styles(form)

    field_placeholder(
        form,
        {
            "institution": "",
            "degree": "",
            "description": "",
            "sort_order": "0",
        },
    )

    return render(
        request,
        "dashboard/education/form.html",
        {
            "section": "education",
            "form": form,
            "is_edit": True,
            "object": obj,
            "content_lang": get_content_lang(request),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def education_delete(request, pk):
    obj = get_object_or_404(Education, pk=pk)
    lang = get_content_lang(request)
    inst = getattr(obj, f"institution_{lang}", "") or obj.institution_en or ""
    deg = getattr(obj, f"degree_{lang}", "") or obj.degree_en or ""
    display_title = " — ".join(p for p in (deg, inst) if p).strip() or f"#{obj.pk}"

    if request.method == "POST":
        obj.delete()
        messages.success(request, _dash_msg(request, "msg_deleted"))
        return redirect("dashboard:education")

    return render(
        request,
        "dashboard/education/confirm_delete.html",
        {
            "section": "education",
            "object": obj,
            "display_title": display_title,
        },
    )


@staff_required
def dashboard_settings(request):
    settings_obj = SiteSettings.load()
    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=settings_obj)
        apply_dashboard_field_styles(form)
        if form.is_valid():
            form.save()
            messages.success(request, _dash_msg(request, "msg_settings_saved"))
            return redirect("dashboard:settings")
    else:
        form = SiteSettingsForm(instance=settings_obj)
        apply_dashboard_field_styles(form)

    return render(
        request,
        "dashboard/settings.html",
        {
            "section": "settings",
            "form": form,
        },
    )


class DashboardLoginView(LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        r = _admin_session_from_query(request)
        if r:
            return r
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        n = self.request.GET.get("next") or self.request.POST.get("next")
        if n and url_has_allowed_host_and_scheme(
            n,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return n
        return reverse("dashboard:index")

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff:
            messages.error(self.request, "Bu panel faqat xodimlar uchun.")
            return self.form_invalid(form)
        return super().form_valid(form)


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard:login")


@staff_required
def sample_list_page(request):
    return render(
        request,
        "dashboard/samples/list.html",
        {"section": "dashboard"},
    )


@staff_required
def sample_form_page(request):
    return render(
        request,
        "dashboard/samples/form.html",
        {"section": "dashboard"},
    )

