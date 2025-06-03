from typing import Optional
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

class CustomUserManager(BaseUserManager):
    """Custom user manager with enhanced functionality"""
    
    def create_user(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields) -> 'CustomUser':
        """
        Create and save a regular user
        """
        from .models import CustomUser
        if not username:
            raise ValueError(_('Username is required'))
        
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: Optional[str] = None, password: Optional[str] = None, **extra_fields) -> 'CustomUser':
        """
        Create and save a superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, email, password, **extra_fields)

    def get_active_users(self) -> QuerySet:
        """
        Get all active users
        """
        return self.filter(is_active=True)

    def get_staff_users(self) -> QuerySet:
        """
        Get all staff users
        """
        return self.filter(is_staff=True)

    def get_clients(self) -> QuerySet:
        """
        Get all client users
        """
        return self.filter(role='client')

    def get_employees(self) -> QuerySet:
        """
        Get all employee users
        """
        return self.filter(role='employee') 