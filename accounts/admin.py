from django.contrib import admin
from .models import User, UserProfile, LocalAddress
from django.contrib.auth.admin import UserAdmin

from leaflet.admin import LeafletGeoAdmin
# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display =('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    ordering=('-date_joined',)
    filter_horizontal=()
    list_filter=()
    fieldsets =()

class UserProfileAdmin(LeafletGeoAdmin):
    list_display =('user', 'address', 'location', 'created_at')

class LocalAddressAdmin(LeafletGeoAdmin):
    list_display =('province', 'district', 'unit_type', 'unit_name', 'district_c')
    list_display_links = ( 'district','unit_name')





admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(LocalAddress, LocalAddressAdmin)
