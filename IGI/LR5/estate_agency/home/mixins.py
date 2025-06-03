import logging
from typing import Any, Callable
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest

logger = logging.getLogger(__name__)

class CacheMixin:
    """Mixin for caching view data"""
    cache_timeout = 300

    def get_cached_data(self, cache_key: str, data_func: Callable, timeout: int = None) -> Any:
        """
        Get data from cache or compute it if not present
        """
        if timeout is None:
            timeout = self.cache_timeout

        cached_data = cache.get(cache_key)
        if cached_data is None:
            cached_data = data_func()
            cache.set(cache_key, cached_data, timeout)
            logger.debug(f"Cache miss for key: {cache_key}")
        else:
            logger.debug(f"Cache hit for key: {cache_key}")
        return cached_data

    def invalidate_cache(self, cache_key: str) -> None:
        """
        Invalidate cache for given key
        """
        cache.delete(cache_key)
        logger.debug(f"Cache invalidated for key: {cache_key}")

class LoggingMixin:
    """Mixin for enhanced logging functionality"""
    
    def log_success(self, message: str = None) -> None:
        """
        Log successful operation
        """
        if message is None:
            message = f"Operation successful for {self.__class__.__name__}"
        logger.info(message)

    def log_error(self, error: Exception, message: str = None) -> None:
        """
        Log error with optional custom message
        """
        if message is None:
            message = f"Error in {self.__class__.__name__}"
        logger.exception(f"{message}: {str(error)}")

    def log_debug(self, message: str) -> None:
        """
        Log debug message
        """
        logger.debug(f"{self.__class__.__name__}: {message}")

class QuerySetMixin:
    """Mixin for enhanced queryset operations"""
    
    def get_optimized_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Apply common optimizations to queryset
        """
        return queryset.select_related(
            'user'
        ).prefetch_related(
            'tags'
        ).order_by('-created')

    def filter_by_user(self, queryset: QuerySet, request: HttpRequest) -> QuerySet:
        """
        Filter queryset by current user
        """
        return queryset.filter(user=request.user) 