import django_filters
from django.db import models
from .models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    """
    Product filter for advanced filtering
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.filter(is_active=True))
    
    # Price filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name='price')
    
    # Rating filter
    min_rating = django_filters.NumberFilter(field_name='average_rating', lookup_expr='gte')
    
    # Stock filters
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    featured = django_filters.BooleanFilter(field_name='is_featured')
    
    # Date filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'min_price', 'max_price',
            'price_range', 'min_rating', 'in_stock', 'on_sale',
            'featured', 'created_after', 'created_before'
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                models.Q(track_inventory=False) | 
                models.Q(track_inventory=True, stock_quantity__gt=0)
            )
        return queryset.filter(track_inventory=True, stock_quantity=0)

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.exclude(compare_price__isnull=True).filter(
                price__lt=models.F('compare_price')
            )
        return queryset