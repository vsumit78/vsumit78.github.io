import datetime

from django.db import models
from .product import Product
from .customer import Customer
import datetime


class Order(models.Model):

    product = models.ForeignKey(Product , on_delete=models.CASCADE)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    price = models.IntegerField()

    address = models.CharField(max_length=100,default="  ")

    phone = models.CharField(max_length=11,default="*********")

    date = models.DateField(default=datetime.datetime.today)

    razorpay_order_id = models.CharField(max_length=100, null=True,blank= True)
    razorpay_payment_id = models.CharField(max_length=100, null=True,blank= True)
    razorpay_payment_signature = models.CharField(max_length=100, null=True,blank= True)
    status = models.BooleanField(default=False)

    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order\
            .objects\
            .filter(customer=customer_id)\
            .order_by('-date')


