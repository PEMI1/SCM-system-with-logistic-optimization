from django.db import models

from accounts.models import User
from menu.models import Product

class Cart(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):  #string representation
        return self.user
