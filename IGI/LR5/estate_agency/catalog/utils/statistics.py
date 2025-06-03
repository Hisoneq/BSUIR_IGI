from typing import Dict, List, Tuple, Any
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import logging

from ..models import Property, PropertyService, Transaction, PropertyInquiry

logger = logging.getLogger(__name__)

class StatisticsCalculator:
    """Enhanced statistics calculator with caching and optimization"""
    
    @staticmethod
    def get_property_stats() -> Dict[str, Any]:
        """Get comprehensive property statistics"""
        return {
            'total_properties': Property.objects.count(),
            'active_listings': Property.objects.exclude(
                id__in=Transaction.objects.values_list('property_id', flat=True)
            ).count(),
            'avg_price': Property.objects.aggregate(avg=Avg('price'))['avg'],
            'price_range': {
                'min': Property.objects.aggregate(min=Min('price'))['min'],
                'max': Property.objects.aggregate(max=Max('price'))['max']
            }
        }

    @staticmethod
    def get_transaction_stats() -> Dict[str, Any]:
        """Get transaction statistics with time-based analysis"""
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        
        return {
            'total_transactions': Transaction.objects.count(),
            'monthly_transactions': Transaction.objects.filter(
                transaction_date__gte=month_ago
            ).count(),
            'avg_transaction_value': Transaction.objects.aggregate(
                avg=Avg('total_amount')
            )['avg'],
            'monthly_trend': Transaction.objects.annotate(
                month=TruncMonth('transaction_date')
            ).values('month').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            ).order_by('month')
        }

    @staticmethod
    def get_service_performance() -> List[Dict[str, Any]]:
        """Get detailed service performance metrics"""
        return PropertyService.objects.annotate(
            total_transactions=Count('property__transaction'),
            total_revenue=Sum('property__transaction__total_amount'),
            avg_processing_time=Avg(
                F('property__transaction__transaction_date') - 
                F('property__propertyinquiry__created_at')
            )
        ).values(
            'title', 'total_transactions', 'total_revenue', 'avg_processing_time'
        ).order_by('-total_revenue')

    @staticmethod
    def get_employee_performance() -> List[Dict[str, Any]]:
        """Get employee performance metrics"""
        return Transaction.objects.values(
            'agent__user__username'
        ).annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount'),
            avg_deal_size=Avg('total_amount'),
            client_satisfaction=Avg('property__propertyinquiry__rating')
        ).order_by('-total_revenue')

    @staticmethod
    def get_market_trends() -> Dict[str, Any]:
        """Get market trend analysis"""
        return {
            'property_types': Property.objects.values(
                'property_type__title'
            ).annotate(
                count=Count('id'),
                avg_price=Avg('price')
            ).order_by('-count'),
            'price_trends': Property.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                avg_price=Avg('price'),
                count=Count('id')
            ).order_by('month'),
            'inquiry_trends': PropertyInquiry.objects.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
        }

    @staticmethod
    def get_client_insights() -> Dict[str, Any]:
        """Get client behavior insights"""
        return {
            'preferred_properties': Property.objects.filter(
                propertyinquiry__isnull=False
            ).values(
                'property_type__title'
            ).annotate(
                inquiry_count=Count('propertyinquiry'),
                conversion_rate=Count('transaction') * 100.0 / Count('propertyinquiry')
            ).order_by('-inquiry_count'),
            'client_segments': Transaction.objects.values(
                'buyer__preferences'
            ).annotate(
                count=Count('id'),
                avg_transaction=Avg('total_amount')
            ).order_by('-count')
        } 