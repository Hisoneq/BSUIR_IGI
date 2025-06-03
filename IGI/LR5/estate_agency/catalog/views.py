import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.conf import settings
from users.models import Client, Employee

from .forms import PropertyInquiryForm, PropertyForm
from .models import ServiceType, PropertyService, Property, Transaction, PropertyInquiry, PropertyType
from .utils import Plotter, StatisticsCalculator, MapboxClient
from .utils.plotter import create_property_type_chart

logger = logging.getLogger(__name__)


class PropertyServiceListView(ListView):
    model = PropertyService
    template_name = "service_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        logger.debug(f"Getting queryset of service list")

        service_category = self.request.GET.get("service_category")
        if service_category:
            logger.debug(f"Filtering by service_category: {service_category}")
            queryset = queryset.filter(category_id=service_category)

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if min_price:
            logger.debug(f"Filtering by min_price: {min_price}")
            queryset = queryset.filter(cost__gte=float(min_price))

        if max_price:
            logger.debug(f"Filtering by max_price: {max_price}")
            queryset = queryset.filter(cost__lte=float(max_price))

        logger.info("PropertyServiceListView queryset prepared")
        return queryset.select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_categories"] = ServiceType.objects.all()
        return context


class AvailablePropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "estate_list.html"
    paginate_by = 9
    ordering = "-price"
    login_url = '/accounts/login/'

    def get_queryset(self):
        logger.debug("Fetching queryset for AvailablePropertyListView")
        sold_properties_ids = Transaction.objects.all().values_list("property_id", flat=True)
        queryset = Property.objects.exclude(id__in=sold_properties_ids).select_related(
            "category"
        )

        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(address__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__title__icontains=search_query)
            )

        category_id = self.request.GET.get("category")
        if category_id:
            logger.debug(f"Filtering by category_id: {category_id}")
            queryset = queryset.filter(category_id=category_id)

        service_category_id = self.request.GET.get("service_category")
        if service_category_id:
            logger.debug(f"Filtering by service_category_id: {service_category_id}")
            queryset = queryset.filter(category__category_id=service_category_id)

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            logger.debug(f"Filtering by min_price: {min_price}")
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            logger.debug(f"Filtering by max_price: {max_price}")
            queryset = queryset.filter(price__lte=max_price)

        sort = self.request.GET.get("sort")
        if sort:
            logger.debug(f"Sorting by: {sort}")
            sort_options = {
                "price_asc": "price",
                "price_desc": "-price",
                "area_asc": "square_meters",
                "area_desc": "-square_meters",
            }
            if sort in sort_options:
                queryset = queryset.order_by(sort_options[sort])
            else:
                logger.warning(f"Invalid sort option: {sort}")
                queryset = queryset.order_by(self.ordering)
        else:
            queryset = queryset.order_by(self.ordering)

        logger.info("AvailablePropertyListView queryset prepared")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = PropertyService.objects.all()
        context["service_categories"] = ServiceType.objects.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["current_sort"] = self.request.GET.get("sort")
        return context


class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    template_name = "estate_detail.html"
    context_object_name = "property"

    def get_context_data(self, **kwargs):
        logger.debug(
            f"Preparing context for PropertyDetailView, property_id={self.kwargs.get('pk')}"
        )
        context = super().get_context_data(**kwargs)
        context["form"] = PropertyInquiryForm(initial={"property": self.object.id})
        if self.request.user.is_authenticated and hasattr(self.request.user, "client"):
            context["request_exists"] = PropertyInquiry.objects.filter(
                client=self.request.user.client, property=self.object
            ).exists()
            logger.debug(
                f"Checked request_exists for user {self.request.user.username}: {context['request_exists']}"
            )
        else:
            context["request_exists"] = False
            logger.warning(
                "User not authenticated or no client, request_exists set to False"
            )

        if self.request.user.is_authenticated:
            context["map_image_url"] = MapboxClient.get_map_image_url(
                self.object.address
            )
            logger.debug(
                f"Map image URL for property {self.object.id}: {context['map_image_url']}"
            )

        logger.info("PropertyDetailView context prepared")
        return context


class CreatePropertyInquiryView(LoginRequiredMixin, CreateView):
    model = PropertyInquiry
    form_class = PropertyInquiryForm
    template_name = "estate_detail.html"

    def form_valid(self, form):
        logger.debug(
            f"User {self.request.user.username} submitting PropertyInquiry for property_id={self.kwargs['pk']}"
        )

        if self.request.user.is_authenticated and hasattr(self.request.user, "client"):
            form.instance.client = self.request.user.client
            form.instance.property_id = self.kwargs["pk"]

            if PropertyInquiry.objects.filter(
                client=self.request.user.client, property_id=self.kwargs["pk"]
            ).exists():
                logger.error(
                    f"Duplicate PropertyInquiry for property {form.instance.property_id} and client {form.instance.client}"
                )
            else:
                PropertyInquiry.objects.create_with_assignment(
                    client=self.request.user.client,
                    property_id=self.kwargs["pk"],
                    inquiry_text=form.cleaned_data["inquiry_text"],
                )
                logger.info(
                    f"PropertyInquiry created by {self.request.user.username}: property={form.instance.property}"
                )
        else:
            logger.error(f"User not authenticated or no client")

        return redirect(self.get_success_url())

    def get_success_url(self):
        logger.debug(f"Redirecting to property_detail for property_id={self.kwargs['pk']}")
        return reverse_lazy("property_detail", kwargs={"pk": self.kwargs["pk"]})


class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "client_dashboard.html"

    def get_context_data(self, **kwargs):
        logger.debug(
            f"Preparing context for ClientDashboardView, user={self.request.user.username}"
        )
        context = super().get_context_data(**kwargs)

        if hasattr(self.request.user, "client"):
            context["requests"] = PropertyInquiry.objects.filter(
                client=self.request.user.client
            ).select_related("property", "employee")

            context["sales"] = Transaction.objects.filter(
                client=self.request.user.client
            ).select_related("property", "employee")

            logger.info(
                f"ClientDashboardView context prepared for user {self.request.user.username}"
            )
        else:
            logger.warning(f"User {self.request.user.username} has no client assigned")
            messages.error(self.request, "You have not client assigned.")

        return context

    def post(self, request, *args, **kwargs):
        logger.debug(
            f"Processing POST request for ClientDashboardView, user={request.user.username}"
        )
        action = request.POST.get("action")
        request_id = request.POST.get("request_id")

        if not request_id:
            logger.error("No request_id provided in POST request")
            messages.error(request, "Incorrect request.")
            return redirect("client_dashboard")

        property_inquiry = get_object_or_404(
            PropertyInquiry, pk=request_id, client=self.request.user.client
        )

        if action == "buy":
            if property_inquiry.status in ["new", "in_progress"]:
                logger.debug(f"Creating Transaction for PropertyInquiry id={request_id}")
                Transaction.objects.create(
                    client=property_inquiry.client,
                    employee=property_inquiry.employee,
                    property=property_inquiry.property,
                )

                property_inquiry.status = "completed"
                property_inquiry.save()
                logger.info(
                    f"Transaction created and PropertyInquiry id={request_id} marked as completed"
                )
            else:
                logger.warning(f"PropertyInquiry id={request_id} already completed")
                messages.error(request, "This purchase is already completed.")

        elif action == "cancel":
            if property_inquiry.status in ["new", "in_progress"]:
                logger.debug(f"Cancelling PropertyInquiry id={request_id}")
                property_inquiry.status = "completed"
                property_inquiry.save()
            else:
                logger.warning(f"PropertyInquiry id={request_id} already completed")
                messages.error(request, "This purchase is already completed.")

        return redirect("client_dashboard")


class EmployeeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "employee_dashboard.html"

    def get_context_data(self, **kwargs):
        logger.debug(
            f"Preparing context for EmployeeDashboardView, user={self.request.user.username}"
        )
        context = super().get_context_data(**kwargs)

        if hasattr(self.request.user, "employee"):
            context["clients"] = Client.objects.filter(
                propertyinquiry__employee=self.request.user.employee,
                propertyinquiry__status__in=["new", "in_progress"],
            ).distinct()

            context["requests"] = PropertyInquiry.objects.filter(
                employee=self.request.user.employee, status__in=["new", "in_progress"]
            ).select_related("property", "client")

            context["sales"] = Transaction.objects.filter(
                employee=self.request.user.employee
            ).select_related("property", "client")

            logger.info(
                f"EmployeeDashboardView context prepared for user {self.request.user.username}"
            )
        else:
            logger.warning(f"User {self.request.user.username} is not an employee")
            messages.error(self.request, "You must be employee.")

        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        logger.info(
            f"Preparing context for StatisticsView, user={self.request.user.username}"
        )
        context = super().get_context_data(**kwargs)

        cost_stats, service_stats = StatisticsCalculator.get_sale_cost_stats()
        client_stats = StatisticsCalculator.get_client_stats()
        services_by_sold_count, counts = (
            StatisticsCalculator.get_services_by_sold_count()
        )
        services_by_service_profit, service_profits = (
            StatisticsCalculator.get_services_by_service_profit()
        )
        services_by_full_costs, full_costs = (
            StatisticsCalculator.get_services_by_full_costs()
        )
        employee_service_stats, employee_service_costs = (
            StatisticsCalculator.get_employees_by_service_profit()
        )
        employee_total_stats, total_costs = (
            StatisticsCalculator.get_employees_by_full_costs()
        )

        image_paths = {
            "services_by_sold_count": f"{settings.MEDIA_URL}services_by_sold_count.jpg",
            "services_by_service_profit": f"{settings.MEDIA_URL}services_by_service_profit.jpg",
            "employee_service_stats": f"{settings.MEDIA_URL}employee_service_stats.jpg",
            "employee_total_stats": f"{settings.MEDIA_URL}employee_total_stats.jpg",
            "services_by_full_costs": f"{settings.MEDIA_URL}services_by_full_costs.jpg",
        }

        Plotter.plt_bars(
            counts,
            path=image_paths["services_by_sold_count"][1:],
            categories=(str(s)[:12] for s in services_by_sold_count),
        )
        Plotter.plt_bars(
            service_profits,
            path=image_paths["services_by_service_profit"][1:],
            categories=(str(s)[:12] for s in services_by_sold_count),
        )
        Plotter.plt_bars(
            employee_service_costs,
            path=image_paths["employee_service_stats"][1:],
            categories=(e.user.username for e in employee_service_stats),
        )
        Plotter.plt_bars(
            total_costs,
            path=image_paths["employee_total_stats"][1:],
            categories=(e.user.username for e in employee_total_stats),
        )
        Plotter.plt_bars(
            full_costs,
            path=image_paths["services_by_full_costs"][1:],
            categories=(str(s)[:12] for s in services_by_full_costs),
        )

        context.update(
            {
                "cost_stats": cost_stats,
                "service_stats": service_stats,
                "client_stats": client_stats,
                "popular_category": services_by_sold_count.first(),
                "profitable_service": services_by_service_profit.first(),
                "employee_service_stats": employee_service_stats,
                "employee_total_stats": employee_total_stats,
                "highest_cost_service": services_by_full_costs.first(),
                "chart_images": image_paths,
            }
        )

        logger.info(
            f"StatisticsViewContext prepared for user: {self.request.user.username}"
        )
        return context


class PropertyTypeView(LoginRequiredMixin, ListView):
    model = PropertyType
    template_name = "property_type_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        logger.debug(f"Getting queryset of property type list")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PropertyTypeDetailView(LoginRequiredMixin, DetailView):
    model = PropertyType
    template_name = "property_type_detail.html"
    context_object_name = "property_type"

    def get_context_data(self, **kwargs):
        logger.debug(
            f"Preparing context for PropertyTypeDetailView, property_type_id={self.kwargs.get('pk')}"
        )
        context = super().get_context_data(**kwargs)
        return context


class PropertyTypeCreateView(LoginRequiredMixin, CreateView):
    model = PropertyType
    form_class = PropertyForm
    template_name = "property_type_form.html"

    def form_valid(self, form):
        logger.debug(
            f"User {self.request.user.username} submitting PropertyType for property_type_id={self.kwargs['pk']}"
        )

        if self.request.user.is_authenticated and hasattr(self.request.user, "employee"):
            form.instance.employee = self.request.user.employee
            form.instance.property_type_id = self.kwargs["pk"]

            if PropertyType.objects.filter(
                employee=self.request.user.employee, property_type_id=self.kwargs["pk"]
            ).exists():
                logger.error(
                    f"Duplicate PropertyType for property_type {form.instance.property_type_id} and employee {form.instance.employee}"
                )
            else:
                PropertyType.objects.create(
                    employee=self.request.user.employee,
                    property_type_id=self.kwargs["pk"],
                    **form.cleaned_data,
                )
                logger.info(
                    f"PropertyType created by {self.request.user.username}: property_type={form.instance.property_type}"
                )
        else:
            logger.error(f"User not authenticated or no employee")

        return redirect(self.get_success_url())

    def get_success_url(self):
        logger.debug(f"Redirecting to property_type_detail for property_type_id={self.kwargs['pk']}")
        return reverse_lazy("property_type_detail", kwargs={"pk": self.kwargs["pk"]})


class PropertyTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = PropertyType
    form_class = PropertyForm
    template_name = "property_type_form.html"

    def form_valid(self, form):
        logger.debug(
            f"User {self.request.user.username} updating PropertyType for property_type_id={self.kwargs['pk']}"
        )

        if self.request.user.is_authenticated and hasattr(self.request.user, "employee"):
            form.instance.employee = self.request.user.employee
            form.instance.property_type_id = self.kwargs["pk"]

            if PropertyType.objects.filter(
                employee=self.request.user.employee, property_type_id=self.kwargs["pk"]
            ).exists():
                logger.error(
                    f"Duplicate PropertyType for property_type {form.instance.property_type_id} and employee {form.instance.employee}"
                )
            else:
                PropertyType.objects.update(
                    employee=self.request.user.employee,
                    property_type_id=self.kwargs["pk"],
                    **form.cleaned_data,
                )
                logger.info(
                    f"PropertyType updated by {self.request.user.username}: property_type={form.instance.property_type}"
                )
        else:
            logger.error(f"User not authenticated or no employee")

        return redirect(self.get_success_url())

    def get_success_url(self):
        logger.debug(f"Redirecting to property_type_detail for property_type_id={self.kwargs['pk']}")
        return reverse_lazy("property_type_detail", kwargs={"pk": self.kwargs["pk"]})


class PropertyTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = PropertyType
    template_name = "property_type_confirm_delete.html"
    success_url = reverse_lazy("property_type_list")

    def get_context_data(self, **kwargs):
        logger.debug(
            f"Preparing context for PropertyTypeDeleteView, property_type_id={self.kwargs['pk']}"
        )
        context = super().get_context_data(**kwargs)
        return context
