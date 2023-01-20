from django.db import models
from accounts.models import User
from menu.models import Product
from vendor.models import Vendor
from shipper.models import Shipper

import simplejson as json

request_object=''  #empty variable which will be assigned by middleware

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors =models.ManyToManyField(Vendor, blank=True)  ##manyTomany
    shippers =models.ManyToManyField(Shipper, blank=True)  ##manyTomany

    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    # tax_data = models.JSONField(blank=True, help_text = "Data format: {'tax_type':{'tax_percentage':'tax_amount'}}")
    # total_tax = models.FloatField()
    total_data = models.JSONField(blank=True, null=True)

    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # Concatenate first name and last name
    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def order_placed_to(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        #get the logged in vendor
        vendor = Vendor.objects.get(user=request_object.user)  #request from custom middleware
        subtotal = 0
        tax=0
        grand_total=0
        if self.total_data:
            total_data = json.loads(self.total_data)   #load total_data from above
            print(total_data)
            data = total_data.get(str(vendor.id)) #get value from total_data key:value pair where id/key = vendor.id
            print(data)
            subtotal= data            
            grand_total = subtotal+tax

        context={
            'subtotal':subtotal,
            'tax':tax,
            'grand_total':grand_total,
        }
        return context

    def shippers_assigned(self):
        return ", ".join([str(i) for i in self.shippers.all()])

    
    def __str__(self):
        return self.order_number


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_title


class ShipOrder(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    shipping_number = models.CharField(max_length=20, default='sno')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE)
    shiporder_status = models.CharField(max_length=50, choices=STATUS, default='New')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shipping_number