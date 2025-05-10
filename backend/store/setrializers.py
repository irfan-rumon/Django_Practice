from rest_framework import serializers
from .models import Product, Collection
from decimal import Decimal

class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name = 'calculate_tax')
    #collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    #collection = serializers.StringRelatedField()
    collection = CollectionSerializer()

    def calculate_tax(self, product:Product):
        return product.unit_price * Decimal(1.1)