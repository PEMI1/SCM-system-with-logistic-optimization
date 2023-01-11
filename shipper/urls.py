from django.urls import path, include
from . import views
from accounts import views as AccountsViews

urlpatterns = [
  path('', AccountsViews.shipperDashboard, name ='shipper'),
  path('profile/', views.sprofile, name ='sprofile'),

 

]
