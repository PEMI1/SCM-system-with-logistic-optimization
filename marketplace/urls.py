from django.urls import path,include
from . import views  



urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    #we are creating this path from vendor slug inorder to show the vendor's menu
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    #CART
    path('add_to_cart/<int:product_id>/',views.add_to_cart, name= 'add_to_cart'),
    path('decrease_cart/<int:product_id>/',views.decrease_cart, name= 'decrease_cart'),
    #delete cart item from cart page
    path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart' ),

] 
