from datetime import date
from typing import Optional, Dict, Any
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

from .utils import RestrictedAgeValidator
from .managers import CustomUserManager
from .validators import phone_regex

logger = logging.getLogger(__name__)

class BaseProfile(models.Model):
    """Abstract base class for all profile types"""
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

    def clean(self) -> None:
        """Validate profile data"""
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError(_("Birth date cannot be in the future"))

    def get_full_address(self) -> str:
        """Get formatted full address"""
        return f"{self.address}" if self.address else ""

class CustomUser(AbstractUser):
    """Extended user model with additional fields"""
    ROLE_CHOICES = {
        "employee": _("Manager"),
        "client": _("Client"),
        "admin": _("Admin"),
    }

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    objects = CustomUserManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            self._create_profile()

    def _create_profile(self) -> None:
        """Create appropriate profile based on user role"""
        if self.is_staff:
            Employee.objects.create(user=self)
        else:
            Client.objects.create(user=self)

    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"

class Client(BaseProfile):
    """Client profile model"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    preferences = models.TextField(blank=True, help_text=_("Client's property preferences"))
    budget_range = models.CharField(max_length=100, blank=True)
    preferred_property_types = models.ManyToManyField(
        'catalog.PropertyType',
        blank=True,
        related_name='interested_clients'
    )
    
    def get_preferences_list(self) -> list:
        """Get list of client preferences"""
        return [p.strip() for p in self.preferences.split(',') if p.strip()]

    def __str__(self) -> str:
        return f"{self.user.username} (Client)"

class Employee(BaseProfile):
    """Employee profile model"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    hire_date = models.DateField(auto_now_add=True)
    specialization = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    def get_experience_years(self) -> int:
        """Calculate years of experience"""
        if self.hire_date:
            return (date.today() - self.hire_date).days // 365
        return 0

    def __str__(self) -> str:
        return f"{self.user.username} ({self.position})"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender: Any, instance: CustomUser, created: bool, **kwargs: Any) -> None:
    """Signal handler for user profile creation"""
    if created:
        if instance.is_staff:
            Employee.objects.create(user=instance)
        else:
            Client.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender: Any, instance: CustomUser, **kwargs: Any) -> None:
    """Signal handler for user profile updates"""
    if hasattr(instance, 'employee'):
        instance.employee.save()
    elif hasattr(instance, 'client'):
        instance.client.save()
