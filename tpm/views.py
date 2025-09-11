
"""
TPM Views

Web interface views for TPM authentication and synchronization.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
import json


class HomePageView(TemplateView):
    """Main homepage for the TPM research application."""
    template_name = 'tpm/homePage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class LoadPageView(TemplateView):
    """TPM loading and initialization page."""
    template_name = 'tpm/load.html'


class TPMDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for TPM research and experiments."""
    template_name = 'tpm/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['has_active_session'] = self.request.user.has_active_session()
        return context


def load(request):
    """Legacy load view - redirects to LoadPageView."""
    return render(request, 'tpm/load.html')


def homePage(request):
    """Legacy home view - redirects to HomePageView."""
    return render(request, 'tpm/homePage.html')