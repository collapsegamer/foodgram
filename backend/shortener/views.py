from django.shortcuts import get_object_or_404, redirect
from .models import ShortLink


def redirect_short_link(request, code):
    link = get_object_or_404(ShortLink, code=code)
    return redirect(link.target_path)
