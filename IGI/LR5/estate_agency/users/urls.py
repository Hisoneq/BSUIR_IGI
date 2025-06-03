from django.contrib.auth.views import LoginView, LogoutView
from django.urls import re_path

from . import views

app_name = 'users'

urlpatterns = [
    re_path(r'^login/$', LoginView.as_view(template_name='login.html'), name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^signup/$', views.ClientSignUpView.as_view(), name='signup'),
    re_path(r'^profile/(?P<pk>\d+)$', views.ProfileView.as_view(), name='profile'),
]
