from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.AvailablePropertyListView.as_view(), name='property_list'),
    path('services/', views.PropertyServiceListView.as_view(), name='service_list'),
    path('property/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('property/<int:pk>/inquiry/', views.CreatePropertyInquiryView.as_view(), name='create_inquiry'),
    path('client/dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),
    path('employee/dashboard/', views.EmployeeDashboardView.as_view(), name='employee_dashboard'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]