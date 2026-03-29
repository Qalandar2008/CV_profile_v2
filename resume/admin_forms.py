from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Certificate, Education, Interest, Portfolio, ResumeProfile, WorkExperience
from .translate_service import sync_translations_from_source


class ResumeProfileForm(forms.ModelForm):
    class Meta:
        model = ResumeProfile
        fields = (
            "full_name",
            "headline",
            "about",
            "location",
            "skills",
            "photo",
            "email",
            "phone",
            "linkedin",
            "github",
        )
        labels = {
            "full_name": _("Full name"),
            "headline": _("Headline / role"),
            "about": _("About"),
            "location": _("Location"),
            "skills": _("Skills"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_translations_from_source(
            obj,
            ["full_name", "headline", "about", "location", "skills"],
        )
        if commit:
            obj.save()
        return obj


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ("title", "url", "image", "sort_order")
        labels = {
            "title": _("Title (optional)"),
            "url": _("Project URL"),
            "image": _("Preview image"),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = (
            "title",
            "issuer",
            "description",
            "image",
            "document",
            "issued_on",
            "sort_order",
        )
        labels = {
            "title": _("Title"),
            "issuer": _("Issuer / organization"),
            "description": _("Description"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_translations_from_source(obj, ["title", "issuer", "description"])
        if commit:
            obj.save()
        return obj


class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ("label", "detail", "sort_order")
        labels = {
            "label": _("Interest"),
            "detail": _("Details"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_translations_from_source(obj, ["label", "detail"])
        if commit:
            obj.save()
        return obj


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = (
            "company",
            "role",
            "description",
            "start_date",
            "end_date",
            "is_current",
            "sort_order",
        )
        labels = {
            "company": _("Company / organization"),
            "role": _("Role / title"),
            "description": _("Description"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_translations_from_source(obj, ["company", "role", "description"])
        if commit:
            obj.save()
        return obj


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = (
            "institution",
            "degree",
            "description",
            "start_date",
            "end_date",
            "sort_order",
        )
        labels = {
            "institution": _("Institution"),
            "degree": _("Degree / program"),
            "description": _("Description"),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        sync_translations_from_source(obj, ["institution", "degree", "description"])
        if commit:
            obj.save()
        return obj
