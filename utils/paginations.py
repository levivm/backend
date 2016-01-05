from rest_framework.pagination import PageNumberPagination


class PaginationBySize(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class MediumResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'page_size'
