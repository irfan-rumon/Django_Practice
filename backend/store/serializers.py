from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem, Customer
from decimal import Decimal
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


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
    


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price'] 


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']



class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):   #AddCartItemSerializer, you overrode save() to decide whether to update or create a CartItem.
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            #update an existing item
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            #create a new item
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
       



       



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