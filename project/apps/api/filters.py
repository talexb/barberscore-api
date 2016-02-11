from rest_framework import filters
import django_filters

from .models import (
    Convention,
    Person,
)

# class CoalesceFilterBackend(filters.BaseFilterBackend):
#     """
#     Support Ember Data coalesceFindRequests.

#     """
#     def filter_queryset(self, request, queryset, view):
#         id_list = request.query_params.getlist('ids[]')
#         if id_list:
#             queryset = queryset.filter(slug__in=id_list)
#         return queryset


class ConventionFilter(filters.FilterSet):
    class Meta:
        model = Convention
        fields = [
            'status',
        ]


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = Person
        fields = {
            'name': [
                'exact',
                'icontains',
            ],
        }
