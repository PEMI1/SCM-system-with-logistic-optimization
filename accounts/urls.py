from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.myAccount),

    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerMerchant/', views.registerMerchant, name='registerMerchant'),

    path('registerVendor/', views.registerVendor, name='registerVendor'),
    path('registerShipper/', views.registerShipper, name='registerShipper'),

    
    path('login/', views.login, name= 'login'),
    path('logout/', views.logout, name= 'logout'),
    path('myAccount/',views.myAccount, name ='myAccount'),
    path('custDashboard/', views.custDashboard, name= 'custDashboard'),
    path('vendorDashboard/', views.vendorDashboard, name= 'vendorDashboard'),
    path('shipperDashboard/', views.shipperDashboard, name= 'shipperDashboard'),


    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('forgot_password/',views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>',views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/',views.reset_password, name='reset_password'),

    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
    path('shipper/', include('shipper.urls')),

    path('localAddress_data/', views.localAddress_data, name= 'localAddress_data'),
    path('counties_data/', views.counties_data, name= 'counties_data'),


]

