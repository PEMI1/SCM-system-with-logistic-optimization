from django.contrib import admin
from vendor.models import Vendor

class VendorAdmin(admin.ModelAdmin):
    list_display= ('user', 'vendor_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name')
    list_editable = ('is_approved',) # make is_approved field be editable from the table



admin.site.register(Vendor, VendorAdmin)

