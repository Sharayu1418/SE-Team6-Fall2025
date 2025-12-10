"""
Custom pagination classes for the API.
"""
from rest_framework.pagination import PageNumberPagination


class FlexiblePageNumberPagination(PageNumberPagination):
    """Pagination class that allows client to specify page_size."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 500

