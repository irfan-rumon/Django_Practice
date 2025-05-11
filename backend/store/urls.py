from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductList.as_view()),
    path('product/<int:pk>', views.ProductDetails.as_view()),
    path('collection/<int:id>', views.collection_detail)
]