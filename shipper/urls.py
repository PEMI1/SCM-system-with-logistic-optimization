from django.urls import path, include
from . import views
from accounts import views as AccountsViews

urlpatterns = [
  path('', AccountsViews.shipperDashboard, name ='shipper'),
  path('profile/', views.sprofile, name ='sprofile'),

  path('order_detail/<str:order_number>/',views.order_detail,name='shipper_order_detail'),
  path('my_orders/', views.my_orders, name='shipper_my_orders'),

  path('optimize_container/', views.optimize_container, name='optimize_container'),
  path('dispatch_container/', views.dispatch_container, name='dispatch_container'),
  path('route_road/', views.route_road, name= 'route_road'),
  path('nearest_neighbor_endpoint/', views.nearest_neighbor_endpoint, name="nearest_neighbor_endpoint"),


]
