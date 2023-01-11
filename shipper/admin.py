from django.contrib import admin
from shipper.models import Shipper

class ShipperAdmin(admin.ModelAdmin):
    list_display= ('user', 'shipper_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'shipper_name')
    list_editable = ('is_approved',) # make is_approved field be editable from the table

admin.site.register(Shipper, ShipperAdmin)
