from django.contrib import admin

from .models import PropertyService, Property, Transaction, ServiceType, PropertyInquiry


class PropertyInline(admin.TabularInline):
    model = Property


class TransactionInline(admin.TabularInline):
    model = Transaction


class ServiceTypeInline(admin.TabularInline):
    model = PropertyService


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    inlines = (ServiceTypeInline,)


@admin.register(PropertyService)
class PropertyServiceAdmin(admin.ModelAdmin):
    inlines = [PropertyInline]


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["location", "price", "property_type", "transaction"]
    list_filter = ["property_type", "property_type__service_type"]


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ["buyer", "property", "created_at", "state"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "agent",
        "transaction_date",
        "property",
        "total_amount",
        "property__property_type",
    ]
    list_filter = ["transaction_date", "agent", "property__property_type"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "agent",
                    "buyer",
                )
            },
        ),
        (
            "Property Details",
            {
                "fields": (
                    "property",
                    "transaction_date",
                    "contract_date",
                )
            },
        ),
    )
