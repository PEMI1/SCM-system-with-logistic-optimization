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

]
