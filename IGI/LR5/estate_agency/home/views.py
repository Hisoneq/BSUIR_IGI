import logging
from typing import Dict, Any, List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.shortcuts import render
from django.db.models import Count, Q, Prefetch
from django.core.cache import cache
from django.conf import settings
from django.contrib import messages

from .forms import ReviewForm
from .models import AboutCompany, FAQ, Vacancy, Contact, PromoCode, Review, News, Policy
from catalog.models import Property, PropertyService, PropertyInquiry
from .mixins import CacheMixin, LoggingMixin

logger = logging.getLogger(__name__)

class BaseViewMixin:
    """Base mixin for common view functionality"""
    def get_cached_data(self, cache_key: str, data_func, timeout: int = 300) -> Any:
        cached_data = cache.get(cache_key)
        if cached_data is None:
            cached_data = data_func()
            cache.set(cache_key, cached_data, timeout)
        return cached_data

class HomePageView(CacheMixin, TemplateView):
    template_name = "home.html"
    cache_timeout = 300

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        def get_featured_data():
            return {
                'featured_properties': Property.objects.select_related(
                    'property_type'
                ).prefetch_related(
                    Prefetch('propertyinquiry_set', queryset=PropertyInquiry.objects.select_related('client'))
                ).order_by('-id')[:6],
                'services': PropertyService.objects.annotate(
                    property_count=Count('property', filter=Q(property__isnull=False))
                ).order_by('-property_count')[:4]
            }
        
        context.update(self.get_cached_data('homepage_data', get_featured_data))
        return context

class DashboardView(LoggingMixin, LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = '/accounts/login/'

    def get_user_data(self) -> Dict[str, Any]:
        user = self.request.user
        if hasattr(user, 'client'):
            return self._get_client_data(user.client)
        elif hasattr(user, 'employee'):
            return self._get_employee_data(user.employee)
        return {}

    def _get_client_data(self, client) -> Dict[str, Any]:
        return {
            'recent_inquiries': client.propertyinquiry_set.select_related(
                'property', 'agent'
            ).prefetch_related(
                'property__property_type'
            ).order_by('-created_at')[:5],
            'active_transactions': client.transaction_set.select_related(
                'property', 'agent'
            ).order_by('-transaction_date')[:5]
        }

    def _get_employee_data(self, employee) -> Dict[str, Any]:
        return {
            'recent_inquiries': employee.propertyinquiry_set.select_related(
                'property', 'buyer'
            ).prefetch_related(
                'property__property_type'
            ).order_by('-created_at')[:5],
            'active_transactions': employee.transaction_set.select_related(
                'property', 'buyer'
            ).order_by('-transaction_date')[:5]
        }

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_data())
        return context

class ContentListView(ListView):
    """Base class for content listing views"""
    paginate_by = 9
    
    def get_queryset(self):
        return super().get_queryset()

class NewsListView(ContentListView):
    model = News
    template_name = "news_list.html"
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().order_by('-created')

class NewsDetailView(DetailView):
    model = News
    template_name = 'home/news_detail.html'
    context_object_name = 'news'

class FAQView(ListView):
    model = FAQ
    template_name = "faq.html"
    context_object_name = "faq_list"

class ContactListView(ContentListView):
    model = Contact
    template_name = "contact_list.html"
    paginate_by = None

class PolicyView(ContentListView):
    model = Policy
    template_name = "policy.html"
    paginate_by = None

class VacancyListView(ContentListView):
    model = Vacancy
    template_name = "vacancy_list.html"

class PromoCodeView(CacheMixin, ContentListView):
    model = PromoCode
    template_name = "promo-codes.html"
    cache_timeout = 300

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        def get_promo_data():
            return {
                "active_promos": PromoCode.objects.filter(status=True),
                "archived_promos": PromoCode.objects.filter(status=False)
            }
        
        context.update(self.get_cached_data('promo_data', get_promo_data))
        return context

class ReviewListView(ContentListView):
    model = Review
    template_name = "review_list.html"
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('user').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ReviewForm()
        return context

class ReviewActionMixin(LoggingMixin, LoginRequiredMixin):
    """Base mixin for review actions"""
    model = Review
    form_class = ReviewForm
    success_url = reverse_lazy("reviews")

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            self.log_success()
            return response
        except Exception as e:
            self.log_error(e)
            raise

class AddReviewView(ReviewActionMixin, CreateView):
    template_name = "review_add.html"

class UpdateReviewView(ReviewActionMixin, UpdateView):
    template_name = "review_edit.html"

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

class DeleteReviewView(ReviewActionMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            self.log_success()
            return response
        except Exception as e:
            self.log_error(e)
            raise

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class AboutView(ListView):
    model = News
    template_name = 'about.html'
    context_object_name = 'news_list'
    ordering = ['-created']
    paginate_by = 3

class ContactView(ListView):
    model = News
    template_name = 'contact.html'
    context_object_name = 'news_list'
    ordering = ['-created']
    paginate_by = 3

class ServicesView(ListView):
    model = News
    template_name = 'services.html'
    context_object_name = 'news_list'
    ordering = ['-created']
    paginate_by = 3

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'review_form.html'
    fields = ['title', 'content', 'rating']
    success_url = reverse_lazy('home:review_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Отзыв успешно добавлен!')
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, ListView):
    model = News
    template_name = 'dashboard.html'
    context_object_name = 'news_list'
    ordering = ['-created']
    paginate_by = 5

class PrivacyPolicyView(TemplateView):
    template_name = 'home/policy.html'
