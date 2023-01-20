from django.urls import path, include
from . import views
from accounts import views as AccountsViews

urlpatterns = [
  path('', AccountsViews.shipperDashboard, name ='shipper'),
  path('profile/', views.sprofile, name ='sprofile'),

  path('order_detail/<str:order_number>/',views.order_detail,name='shipper_order_detail'),
  path('my_orders/', views.my_orders, name='shipper_my_orders'),

 

]
