from django.urls import path, include
# from django.views.generic import TemplateView
from . import views
# from tpm.views import Register

urlpatterns = [
    path('load/', views.load),
    path('', views.homePage, name='home'),
    path('', include('django.contrib.auth.urls')),
    # path('register/', Register.as_view(), name='register')
]