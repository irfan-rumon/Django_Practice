from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Order, OrderItem, Customer
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, CustomerSerializer
from rest_framework.views import APIView
from django.db.models import Count

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from django_filters.rest_framework import DjangoFilterBackend
from store.filters import ProductFilter

from rest_framework.filters import SearchFilter, OrderingFilter

#from rest_framework.pagination import PageNumberPagination

from .pagination import DefaultPagination


class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


    
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #filterset_fields = ['collection_id', 'unit_price']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')

    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id = collection_id)

    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs['pk'])
        if OrderItem.objects.filter(product_id=kwargs['pk']).exists():
            return Response(
                {'error': 'Product cannot be deleted because it is associated with an order item.'}, 
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)                         
    
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate( products_count=Count('products') ).all()
    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if Product.objects.filter(collection_id=kwargs['pk']).exists():
            return Response(
                {'error': 'Collection cannot be deleted as it includes one or more products.'}, 
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)
    

class ReviewViewSet(ModelViewSet):
    #queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}   #pass this dictionary to serializer
    

class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer



class CartItemViewSet(ModelViewSet):
    #serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'path', 'delete']
   
    def get_queryset(self):    # take data from database 
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

    
    def get_serializer_class(self): #define serializer 
        if self.request.method == 'POST':
            return CartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):  #pass data to seriazer (like url query paramas)
        return {'cart_id' : self.kwargs['cart_pk']}
    

    
#==============================================================================================================================

    
# annotate() is a Django ORM method that allows you to add calculated fields to your queryset results.
# products_count=Count('products') is creating a new field called products_count for each Collection instance in the queryset.
# Count('products') is counting the number of related Product objects for each Collection.
# The 'products' refers to the related_name you defined in your Product model


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related('collection').all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return {'request': self.request}
    

# class ProductDetails(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     #lookup_field = 'id'

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted as it is associated with order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    





    
