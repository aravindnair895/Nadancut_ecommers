from math import trunc

from django.db import models
from django.db.models import Model


# Create your models here.



class TableReg(models.Model):
    username=models.CharField(max_length=100,null=True)
    email=models.EmailField(null=True,unique=True)
    phone=models.IntegerField(null=True)
    password=models.CharField(max_length=100,null=True)

class TableCategory(models.Model):
    category=models.CharField(max_length=100,null=True)
    image=models.ImageField(upload_to="media",null=True)
    status=models.CharField(max_length=100,null=True)

class TableSubcategory(models.Model):
    category=models.ForeignKey(TableCategory,on_delete=models.CASCADE,null=True)
    subcategory=models.CharField(max_length=100,null=True)
    image=models.ImageField(upload_to="media",null=True)
    status=models.CharField(max_length=100,null=True)

class TableProduct(models.Model):
    category=models.ForeignKey(TableCategory,on_delete=models.CASCADE,null=True)
    subcat=models.ForeignKey(TableSubcategory,on_delete=models.CASCADE,null=True)
    prod=models.CharField(max_length=100,null=True)
    image=models.ImageField(upload_to="media",null=True)
    slug=models.CharField(max_length=100,null=True)
    description=models.CharField(max_length=200,null=True)
    sku_code=models.CharField(max_length=100, null=True)
    price=models.FloatField(null=True)
    discount=models.FloatField(null=True)
    status=models.CharField(max_length=100,null=True)
    stock=models.IntegerField(default=0)
    date=models.DateField(auto_now_add=True,null=True)

class TableCoupon(models.Model):
    code=models.CharField(max_length=50, null=True)
    price=models.CharField(max_length=100, null=True)

class TableCart(models.Model):
    product = models.ForeignKey(TableProduct, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(TableReg, on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=100, null=True)
    quantity = models.IntegerField(null=True)
    session_key = models.CharField(max_length=100, null=True)

    def total(self):
        return self.quantity * self.product.price

    def discount(self):
        return self.quantity * self.product.discount

class TableAddress(models.Model):
    user=models.ForeignKey(TableReg,on_delete=models.CASCADE,null=True)
    fname = models.CharField(max_length=100, null=True)
    sname = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=300, null=True)
    phone = models.CharField(null=True)
    landmark = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    pincode = models.CharField(max_length=100, null=True)

class TableBuy(models.Model):
    user=models.ForeignKey(TableReg,on_delete=models.CASCADE,null=True)
    address=models.ForeignKey(TableAddress,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(TableProduct,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(null=True)
    disc_price=models.FloatField(null=True)
    orderID = models.CharField(max_length=100, null=True)
    paymentID = models.CharField(max_length=100, null=True)
    order_status = models.CharField(max_length=100, null=True)
    payment_status = models.CharField(max_length=100, null=True)
    payment_method = models.CharField(max_length=100, null=True)
    invoiceID = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True, auto_now_add=True)
    coupon = models.ForeignKey(TableCoupon, on_delete=models.CASCADE, null=True)

class TableCheckoutList(models.Model):
    user=models.ForeignKey(TableReg,on_delete=models.CASCADE, null=True)
    product=models.ForeignKey(TableProduct,on_delete=models.CASCADE, null=True)
    quantity=models.IntegerField(null=True)
    buy=models.ForeignKey(TableBuy,on_delete=models.CASCADE, null=True)

class TableReview(models.Model):
    user = models.ForeignKey(TableReg, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(TableProduct, on_delete=models.CASCADE, null=True)
    image1=models.ImageField(upload_to="media",null=True)
    image2=models.ImageField(upload_to="media",null=True)
    rating = models.IntegerField(null=True)
    review = models.CharField(max_length=300, null=True)
    date = models.DateField(auto_now_add=True, null=True)

