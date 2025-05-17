from django.urls import path
from . import views


from rest_framework_nested import routers


# Define parent router
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)

#parent router, parent prefix, lookup parameter [product_pk]
products_router = routers.NestedDefaultRouter(router, 'products',  lookup='product')
#register child resources
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

# {base_url/store} / carts / [cart_pk] / items / [item-id]
carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')


#summation
urlpatterns = router.urls + products_router.urls  + carts_router.urls