"""Tanlangan tilda CV PDF (ReportLab)."""

from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .i18n_field import localized_model_value
from .models import Certificate, Education, Interest, ResumeProfile, WorkExperience


def _rtext(text: str, style) -> Paragraph:
    """Oddiy matn (HTML teglarsiz)."""
    t = escape(text or "").replace("\n", "<br/>")
    return Paragraph(t, style)


def _rbold(label: str, style) -> Paragraph:
    return Paragraph(f"<b>{escape(label)}</b>", style)


def build_cv_pdf_bytes(lang: str) -> bytes:
    lang = (lang or "en")[:2]
    if lang not in ("en", "uz", "ru"):
        lang = "en"

    profile = ResumeProfile.load()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(name="H1", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    h2 = ParagraphStyle(name="H2", parent=styles["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6)
    body = ParagraphStyle(name="B", parent=styles["Normal"], fontSize=10, spaceAfter=4)
    small = ParagraphStyle(name="S", parent=styles["Normal"], fontSize=8, textColor="#555555", spaceBefore=8)

    story: list = []
    name = localized_model_value(profile, "full_name", lang)
    story.append(_rbold(name or "CV", h1))
    headline = localized_model_value(profile, "headline", lang)
    if headline:
        story.append(_rtext(headline, body))
    story.append(Spacer(1, 6))

    about = localized_model_value(profile, "about", lang)
    if about:
        story.append(_rbold("About", h2))
        story.append(_rtext(about, body))

    loc = localized_model_value(profile, "location", lang)
    if profile.email or profile.phone or loc:
        story.append(_rbold("Contact", h2))
        if profile.email:
            story.append(_rtext(profile.email, body))
        if profile.phone:
            story.append(_rtext(profile.phone, body))
        if loc:
            story.append(_rtext(loc, body))

    skills = localized_model_value(profile, "skills", lang)
    if skills:
        story.append(_rbold("Skills", h2))
        for line in skills.replace(",", "\n").split("\n"):
            s = line.strip()
            if s:
                story.append(_rtext(f"• {s}", body))

    exps = WorkExperience.objects.all()
    if exps.exists():
        story.append(_rbold("Experience", h2))
        for e in exps:
            r = localized_model_value(e, "role", lang)
            c = localized_model_value(e, "company", lang)
            d = localized_model_value(e, "description", lang)
            line = f"{r} — {c}".strip(" —")
            story.append(_rtext(line, body))
            if d:
                story.append(_rtext(d, body))

    edus = Education.objects.all()
    if edus.exists():
        story.append(_rbold("Education", h2))
        for ed in edus:
            deg = localized_model_value(ed, "degree", lang)
            ins = localized_model_value(ed, "institution", lang)
            story.append(_rtext(f"{deg} — {ins}".strip(" —"), body))
            desc = localized_model_value(ed, "description", lang)
            if desc:
                story.append(_rtext(desc, body))

    certs = Certificate.objects.all()
    if certs.exists():
        story.append(_rbold("Certificates", h2))
        for cert in certs:
            t = localized_model_value(cert, "title", lang)
            iss = localized_model_value(cert, "issuer", lang)
            story.append(_rtext(f"• {t} — {iss}".strip(" —") if iss else f"• {t}", body))

    ints = Interest.objects.all()
    if ints.exists():
        story.append(_rbold("Interests", h2))
        for it in ints:
            lab = localized_model_value(it, "label", lang)
            det = localized_model_value(it, "detail", lang)
            story.append(_rtext(f"• {lab}", body))
            if det:
                story.append(_rtext(det, body))

    story.append(Spacer(1, 8))
    story.append(_rtext(f"Generated {timezone.now().strftime('%Y-%m-%d')}", small))
    doc.build(story)
    return buf.getvalue()
