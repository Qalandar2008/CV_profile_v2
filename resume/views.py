from django.shortcuts import render

from .models import Certificate, Education, Interest, ResumeProfile, WorkExperience


def cv_home(request):
    profile = ResumeProfile.load()
    certificates = Certificate.objects.all()
    interests = Interest.objects.all()
    experiences = WorkExperience.objects.all()
    education_entries = Education.objects.all()
    return render(
        request,
        "resume/home.html",
        {
            "profile": profile,
            "certificates": certificates,
            "interests": interests,
            "experiences": experiences,
            "education_entries": education_entries,
        },
    )
