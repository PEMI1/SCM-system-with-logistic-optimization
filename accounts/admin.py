from django.contrib import admin
from .models import User, UserProfile, RoadsData
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

class RoadsDataAdmin(LeafletGeoAdmin):
    list_display =('osm_id', 'code', 'fclass', 'name', 'ref', 'oneway',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(RoadsData, RoadsDataAdmin)
