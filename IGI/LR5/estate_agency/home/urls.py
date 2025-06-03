from django.urls import path, re_path
from . import views

app_name = 'home'

urlpatterns = [
    re_path(r'^$', views.HomePageView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('policy/', views.PrivacyPolicyView.as_view(), name='policy'),
    path('faq/', views.FAQView.as_view(), name='faq'),
]
