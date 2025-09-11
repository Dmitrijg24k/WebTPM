from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Main pages
    path('', views.HomePageView.as_view(), name='home'),
    path('load/', views.LoadPageView.as_view(), name='load'),
    path('dashboard/', views.TPMDashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('login/', LoginView.as_view(template_name='tpm/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('', include('django.contrib.auth.urls')),
]