from django.contrib import admin
from .models import Payment, Order, OrderedProduct, ShipOrder


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields =('order','payment','user', 'product', 'quantity', 'price', 'amount')
    extra=0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method','status','order_placed_to','shippers_assigned','is_ordered']
    inlines=[OrderedProductInline]

class ShipOrderAdmin(admin.ModelAdmin):
    list_display= ('shipping_number','order', 'vendor', 'shipper','package_volume', 'created_at')
#     list_display_links = ('order', 'vendor', 'shipper')


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedProduct)
admin.site.register(ShipOrder, ShipOrderAdmin)
