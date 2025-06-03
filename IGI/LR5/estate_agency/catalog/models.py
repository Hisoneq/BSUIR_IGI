from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, F, Q
from django.urls import reverse
from django.conf import settings
from users.models import Employee, Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class PropertyType(models.Model):
    title = models.CharField(max_length=200, help_text="Property type name")
    description = models.TextField(blank=True, help_text="Description of the property type")

    class Meta:
        verbose_name_plural = "Property Types"

    def __str__(self):
        return self.title


class Property(models.Model):
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        help_text="Property price in currency units",
        validators=[MinValueValidator(0.01)],
    )
    square_meters = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        help_text="Total area in square meters",
        validators=[MinValueValidator(0.01)],
    )
    property_type = models.ForeignKey(
        "PropertyService",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Type of property service",
    )
    details = models.TextField(
        max_length=2000, help_text="Detailed property description"
    )
    photo = models.ImageField(blank=True, null=True, upload_to="properties/")
    location = models.CharField(max_length=200)

    def get_photo_url(self):
        if self.photo and hasattr(self.photo, "url"):
            return self.photo.url
        return settings.MEDIA_URL + "default_property.jpg"

    class Meta:
        ordering = ("-id",)
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.location}: {self.price}"

    def get_absolute_url(self):
        return reverse("estate-detail", args=[str(self.pk)])


class ServiceType(models.Model):
    title = models.CharField(max_length=200, help_text="Service type name")

    class Meta:
        verbose_name_plural = "Service Types"

    def __str__(self):
        return self.title


class PropertyService(models.Model):
    title = models.CharField(max_length=200, help_text="Property service name")
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        related_name="property_services",
    )
    service_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        ordering = ["service_type__title", "title"]
        verbose_name_plural = "Property Services"

    def __str__(self):
        return f"({str(self.service_type)[:2]}) - {self.title}"


class Transaction(models.Model):
    buyer = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    contract_date = models.DateField(auto_now_add=True)
    transaction_date = models.DateField(auto_now_add=True)
    property = models.OneToOneField(Property, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, auto_created=True)

    def save(self, *args, **kwargs):
        service_fee = 0
        if self.property.property_type:
            service_fee = self.property.property_type.service_fee

        self.total_amount = service_fee + self.property.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agent.user.username} - {self.contract_date}"


class PropertyInquiryManager(models.Manager):
    def create_with_agent_assignment(self, **kwargs):
        active_states = ["pending", "processing"]
        agent = (
            Employee.objects.annotate(
                inquiry_count=Count(
                    "propertyinquiry",
                    filter=Q(propertyinquiry__state__in=active_states),
                )
            )
            .order_by("inquiry_count")
            .first()
        )

        if agent:
            kwargs["agent"] = agent
        else:
            raise ValueError("No available agents found.")

        return self.create(**kwargs)


class PropertyInquiry(models.Model):
    STATE_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    inquiry_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="pending")

    objects = PropertyInquiryManager()

    class Meta:
        unique_together = ["property", "buyer"]
        verbose_name_plural = "Property Inquiries"

    def __str__(self):
        return f"{self.property} - {self.buyer.user.username}"
