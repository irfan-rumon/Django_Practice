from rest_framework import serializers
from .models import Product, Collection, Review
from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        read_only_fields = ['id']



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'unit_price', 'inventory', 'collection']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']
        read_only_fields = ['id']

    def create(self, validated_date):
        product_id = self.context['product_id']  #retrieve the 'product_id' passed from view 
        return Review.objects.create(product_id=product_id, **validated_date)

       



# ===============================================================



       
    #price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'unit_price')
    #collection = CollectionSerializer()


# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2, source = 'unit_price')
#     price_with_tax = serializers.SerializerMethodField(method_name = 'calculate_tax')
#     #collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
#     #collection = serializers.StringRelatedField()
#     collection = CollectionSerializer()

#     def calculate_tax(self, product:Product):
#         return product.unit_price * Decimal(1.1)