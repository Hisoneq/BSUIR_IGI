import logging
from datetime import timedelta

import pandas as pd
from django.db.models import Count, Sum, F
from django.utils import timezone
from users.models import Client, Employee

from ..models import Transaction, PropertyService

logger = logging.getLogger(__name__)


class StatisticsCalculator(object):
    @staticmethod
    def get_transaction_price_stats():
        logger.info("StatisticCalculator.get_transaction_price_stats()")
        transactions = Transaction.objects.all()

        property_df = pd.Series([float(t.price) for t in transactions])
        full_price_stats = {
            "mean_price": property_df.mean() or 0,
            "median_price": property_df.median() or 0,
            "mode_price": property_df.mode().get(0) or 0,
        }
        logger.debug(f"full_price_stats: {full_price_stats}")

        service_df = pd.Series([float(t.property.service_type.price) for t in transactions])
        service_price_stats = {
            "mean_price": service_df.mean() or 0,
            "median_price": service_df.median() or 0,
            "mode_price": service_df.mode().get(0) or 0,
        }
        logger.debug(f"service_price_stats: {service_price_stats}")

        return full_price_stats, service_price_stats

    @staticmethod
    def get_client_stats():
        logger.info("StatisticCalculator.get_client_ages()")

        clients = Client.objects.filter(user__birth_date__isnull=False)
        today = timezone.now().date()
        ages = [
            today.year
            - client.user.birth_date.year
            - (
                (today.month, today.day)
                < (client.user.birth_date.month, client.user.birth_date.day)
            )
            for client in clients
        ]
        logger.debug(f"ages: {ages}")

        ages_df = pd.Series(ages)
        client_stats = {"mean_age": ages_df.mean(), "median_age": ages_df.median()}
        logger.debug(f"client_stats: {client_stats}")

        return client_stats

    @staticmethod
    def get_services_by_sold_count():
        logger.info("StatisticCalculator.get_services_sold_property_count()")

        services = (
            PropertyService.objects.filter(property__transaction__isnull=False)
            .annotate(count=Count("property"))
            .order_by("-count")
        )
        counts = services.values_list("count", flat=True)
        logger.debug(f"services: {services}")

        return services, counts

    @staticmethod
    def get_services_by_service_profit():
        logger.info("StatisticCalculator.get_services_by_service_profit()")

        services_by_service_profit = (
            PropertyService.objects.filter(
                property__transaction__isnull=False,
            )
            .annotate(total_service_price=Sum("property__service_type__price"))
            .order_by("-total_service_price")
        )
        service_profits = services_by_service_profit.values_list(
            "total_service_price", flat=True
        )

        logger.debug(f"services_by_service_profit: {services_by_service_profit}")

        return services_by_service_profit, service_profits

    @staticmethod
    def get_services_by_full_prices():
        logger.info("StatisticCalculator.get_services_by_full_prices()")

        services_by_full_prices = (
            PropertyService.objects.filter(property__transaction__isnull=False)
            .annotate(total_value=Sum("property__price") + Sum("price"))
            .order_by("-total_value")
        )
        profits = services_by_full_prices.values_list("total_value", flat=True)
        logger.debug(f"services_by_full_prices: {services_by_full_prices}")

        return services_by_full_prices, profits

    @staticmethod
    def get_employees_by_service_profit(days_ago=30):
        logger.info("StatisticCalculator.get_employees_by_service_profit()")

        time_ago = timezone.now() - timedelta(days=days_ago)
        employee_service_stats = (
            Employee.objects.filter(transaction__date_of_transaction__gte=time_ago)
            .annotate(total_service_price=Sum("transaction__property__service_type__price"))
            .order_by("-total_service_price")
        )
        prices = employee_service_stats.values_list("total_service_price", flat=True)
        logger.debug(f"employee_service_stats: {employee_service_stats}")

        return employee_service_stats, prices

    @staticmethod
    def get_employees_by_full_prices(days_ago=30):
        logger.info("StatisticCalculator.get_employees_by_full_prices()")

        time_ago = timezone.now() - timedelta(days=days_ago)
        employee_total_stats = (
            Employee.objects.filter(transaction__date_of_transaction__gte=time_ago)
            .annotate(
                total_price=Sum("transaction__price"))
            .order_by("-total_price")
        )
        prices = employee_total_stats.values_list("total_price", flat=True)
        logger.debug(f"employee_total_stats: {employee_total_stats}")

        return employee_total_stats, prices
