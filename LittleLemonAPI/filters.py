from django_filters import rest_framework

from . import models


class MenuItemFilter(rest_framework.FilterSet):
    category = rest_framework.CharFilter(
        field_name="category__title",
        lookup_expr="icontains",
    )

    class Meta:
        model = models.MenuItem
        fields = ["category", "title", "featured"]
