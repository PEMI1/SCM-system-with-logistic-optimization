from django.urls import path, include
from . import views
from accounts import views as AccountsViews

urlpatterns = [
  path('', AccountsViews.vendorDashboard, name ='vendor'),
  path('profile/', views.vprofile, name='vprofile'),
  path('menu-builder/', views.menu_builder, name='menu_builder'),
  path('menu-builder/category/<int:pk>/', views.products_by_category, name='products_by_category'),
  

  #category CRUD
  path('menu-builder/category/add/', views.add_category, name ='add_category'),
  path('menu-builder/category/edit/<int:pk>/', views.edit_category, name ='edit_category'),
  path('menu-builder/category/delete/<int:pk>/', views.delete_category, name ='delete_category'),

  #product CRUD
  path('menu-builder/product/add/', views.add_product, name ='add_product'),
  path('menu-builder/product/edit/<int:pk>/', views.edit_product, name ='edit_product'),
  path('menu-builder/product/delete/<int:pk>/', views.delete_product, name ='delete_product'),


  path('order_detail/<str:order_number>/',views.order_detail,name='vendor_order_detail'),
  path('my_orders/', views.my_orders, name='vendor_my_orders'),

  #SHIPPING
  path('assign_shipper/<str:order_number>/', views.assign_shipper, name='assign_shipper'),
  path('confirm_shipper/<int:shipper_id>/<str:order_number>', views.confirm_shipper, name='confirm_shipper'),
]
