import csv
from datetime import timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import TruncMonth
from django.utils import timezone
from idlelib.rpc import request_queue
import razorpay
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from pyexpat.errors import messages
from .models import *
from django.contrib import messages
import json
import re

# Create your views here.

razorpay_client = razorpay.Client(auth=('rzp_test_9zruMnoLDlsCLG','oXUZ9Mf5zhjoZsTFLc7RpABO'))


def index(request):
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"index.html",{"cart_count":cart_count})

def about(request):
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"about.html",{"cart_count":cart_count})

def service(request):
    return render(request,"service.html")

def shop(request):
    cata = TableCategory.objects.filter(status="available")
    subcat = TableSubcategory.objects.filter(status="available")
    product=TableProduct.objects.filter(status="available").select_related("category","subcat").only("id","prod","image","price","discount","slug","category__id","subcat__id")
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"shop.html",{"product":product,"cata":cata,"subcat":subcat,"cart_count":cart_count})

def shop_subcat(request, pro_id):
    cata = TableCategory.objects.filter(status="available")
    subcat = TableSubcategory.objects.filter(status="available")
    product = TableProduct.objects.filter(subcat_id=pro_id,status="available").select_related("category","subcat").only("id","prod","image","price","discount","slug","category__id","subcat__id")
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()

    return render(request, "shop.html", {"product": product,"cata":cata,"subcat":subcat,"cart_count":cart_count})

def login_view(request):
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"login.html",{"cart_count":cart_count})

def signup(request):
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"signup.html",{"cart_count":cart_count})


EMAIL_RE = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
PHONE_RE = re.compile(r'^[0-9]{10}$')
PASSWORD_RE = re.compile(r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@]{8,}$')

def save_reg(request):
    if request.method!="POST":
        return redirect("/signup/")

    email=request.POST.get("email","").strip()
    phone = request.POST.get("phone","").strip()
    password= request.POST.get("password","")
    con_password=request.POST.get("con_password","")

    if not email or not password or not con_password:
        messages.error(request, "Please fill all required fields.")
        return redirect("/signup/")

    if not EMAIL_RE.match(email):
        messages.error(request,"Invalid email format")
        return redirect("/signup/")

    if not PHONE_RE.match(phone):
        messages.error(request,"Phone number must be exactly 10 digits.")
        return redirect("/signup/")

    if not PASSWORD_RE.match(password):
        messages.error(request,"Password must contain 1 uppercase letter, 1 number and be at least 8 characters long.")
        return redirect("/signup/")

    if con_password!=password:
        messages.error(request,"Password do not match")
        return redirect("/signup/")

    if TableReg.objects.filter(email=email).exists():
        messages.error(request,"User already exists")
        return redirect("/signup/")

    else:
        tab_obj=TableReg()
        tab_obj.username=request.POST.get("username").strip()
        tab_obj.email=email
        tab_obj.phone=phone
        tab_obj.password=make_password(password)   #for security reasons hashing
        tab_obj.save()
        messages.success(request,"Account created successfully!")
        return redirect("/login/")

def check_log(request):
    if request.method=="POST":
        email= request.POST.get("email")
        password=request.POST.get("password")

        try:
            u=User.objects.get(email=email)
            user=authenticate(request,username=u.username,password=password)
        except User.DoesNotExist:
            user=None

        if user is not None:
            login(request, user)
            return redirect("/admin_home/")
        try:
            usr=TableReg.objects.get(email=email)
        except TableReg.DoesNotExist:
            messages.error(request,"Email does not exist")
            return redirect("/login/")
        if check_password(password,usr.password):
            request.session["userid"]=usr.id
            messages.success(request,"Sign in successfully")
            return redirect("/")

        else:
            messages.error(request,"Invalid username or password")
            return redirect("/login/")

@staff_member_required(login_url="/admin/login/")
def admin_home(request):

    sales = (
        TableBuy.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("disc_price"))
        .order_by("month")
    )
    recent_sales = (
        TableBuy.objects
        .select_related("user")
        .order_by("-date")[:5]
    )
    pro = TableProduct.objects.all()
    total_stock = sum(i.stock or 0 for i in pro)
    data = TableBuy.objects.all()
    sales_count = data.count()
    total_sale = sum(i.disc_price for i in data)

    months = [s["month"].strftime("%b") for s in sales]
    totals = [float(s["total"]) for s in sales]

    return render(request, "admin_home.html", {
        "months": months,
        "totals": totals,
        "recent_sales":recent_sales,
        "total_stock":total_stock,
        "sales_count":sales_count,
        "total_sale":total_sale
    })


@staff_member_required(login_url="/admin/login/")
def categories(request):
    cate=TableCategory.objects.all()
    return render(request,"categories.html",{"cate":cate})

@staff_member_required(login_url="/admin/login/")
def add_category(request):
    return render(request,"add_category.html")

@staff_member_required(login_url="/admin/login/")
def save_category(request):
    if request.method=="POST":
        tab_obj=TableCategory()
        tab_obj.category=request.POST.get("category")
        tab_obj.image=request.FILES.get("image")
        tab_obj.status=request.POST.get("status")
        tab_obj.save()
        return redirect("/categories/")

@staff_member_required(login_url="/admin/login/")
def edit_category(request,cat_id):
    data=TableCategory.objects.get(id=cat_id)
    return render(request,"edit_category.html",{"data":data})

@staff_member_required(login_url="/admin/login/")
def update_category(request,cat_id):
    if request.method=="POST":
        data=TableCategory.objects.get(id=cat_id)
        data.category=request.POST.get("category")
        if request.FILES.get("image"):
            data.image=request.FILES.get("image")
        data.status=request.POST.get("status")
        data.save()
        return redirect("/categories/")

@user_passes_test(lambda u: u.is_superuser, login_url="/admin/login/")
def delete_category(request,cat_id):
    data=TableCategory.objects.get(id=cat_id)
    data.delete()
    return redirect("/categories/")

@staff_member_required(login_url="/admin/login/")
def sub_categories(request):
    subcat=TableSubcategory.objects.all()
    return render(request,"sub_categories.html",{"subcat":subcat})

@staff_member_required(login_url="/admin/login/")
def add_subcategory(request):
    cat=TableCategory.objects.all()
    return render(request,"add_subcategory.html",{"cat":cat})

@staff_member_required(login_url="/admin/login/")
def save_subcategory(request):
    if request.method=="POST":


        tab_obj=TableSubcategory()
        tab_obj.category_id=request.POST.get("category_id")
        tab_obj.subcategory=request.POST.get("subcategory")
        tab_obj.image=request.FILES.get("image")
        tab_obj.status=request.POST.get("status")
        tab_obj.save()
        return redirect("/sub_categories/")

@staff_member_required(login_url="/admin/login/")
def edit_subcategory(request,subcat_id):
    subcat=TableSubcategory.objects.get(id=subcat_id)
    cat=TableCategory.objects.all()
    return render(request,"edit_subcategory.html",{"subcat":subcat,"cat":cat})

@staff_member_required(login_url="/admin/login/")
def update_subcategory(request,subcat_id):
    if request.method=="POST":
        data=TableSubcategory.objects.get(id=subcat_id)
        data.category_id=request.POST.get("category_id")
        data.subcategory=request.POST.get("subcategory")
        if request.FILES.get("image"):
            data.image=request.FILES.get("image")
        data.status=request.POST.get("status")
        data.save()
        return redirect("/sub_categories/")

@user_passes_test(lambda u: u.is_superuser, login_url="/admin/login/")
def delete_subcategory(request,subcat_id):
    data=TableSubcategory.objects.get(id=subcat_id)
    data.delete()
    return redirect("/sub_categories/")

@staff_member_required(login_url="/admin/login/")
def products(request):
    data=TableProduct.objects.all()
    return render(request,"products.html",{"data":data})

@staff_member_required(login_url="/admin/login/")
def add_product(request):
    subcat=TableSubcategory.objects.all()
    cat=TableCategory.objects.all()
    return render(request,"add_product.html",{"subcat":subcat,"cat":cat})

@staff_member_required(login_url="/admin/login/")
def save_product(request):
    if request.method=="POST":
        product=request.POST.get("product")
        slug=product.replace(" ","+")
        tab_obj=TableProduct()
        tab_obj.category_id=request.POST.get("category_id")
        tab_obj.subcat_id=request.POST.get("subcategory_id")
        tab_obj.prod=request.POST.get("product")
        if request.FILES.get("image"):
            tab_obj.image=request.FILES.get("image")
        tab_obj.slug=slug
        tab_obj.sku_code = request.POST.get("sku_code")
        tab_obj.description=request.POST.get("description")
        tab_obj.price=request.POST.get("price")
        tab_obj.discount=request.POST.get("discount")
        tab_obj.status=request.POST.get("status")
        tab_obj.stock=request.POST.get("stock")
        tab_obj.save()
        return redirect("/products/")

@staff_member_required(login_url="/admin/login/")
def edit_product(request,prod_id):
    prod=TableProduct.objects.get(id=prod_id)
    subcat=TableSubcategory.objects.all()
    cat= TableCategory.objects.all()
    return render(request,"edit_product.html",{"prod":prod,"subcat":subcat,"cat":cat})

@staff_member_required(login_url="/admin/login/")
def update_product(request,prod_id):
    if request.method=="POST":
        product=request.POST.get("product")
        slug=product.replace(" ","+")
        tab_obj=TableProduct.objects.get(id=prod_id)
        tab_obj.category_id=request.POST.get("category_id")
        tab_obj.subcat_id=request.POST.get("subcategory_id")
        tab_obj.prod=product
        if request.FILES.get("image"):
            tab_obj.image=request.FILES.get("image")
        tab_obj.slag=slug
        tab_obj.sku_code=request.POST.get("sku_code")
        tab_obj.description=request.POST.get("description")
        tab_obj.price=request.POST.get("price")
        tab_obj.discount=request.POST.get("discount")
        tab_obj.stock=request.POST.get("stock")
        tab_obj.status=request.POST.get("status")
        tab_obj.save()
        return redirect("/products/")

@user_passes_test(lambda u: u.is_superuser, login_url="/admin/login/")
def delete_product(request,prod_id):
    data=TableProduct.objects.get(id=prod_id)
    data.delete()
    return redirect("/products/")

@staff_member_required(login_url="/admin/login/")
def admin_signout(request):
    logout(request)
    return redirect("/")

def cart(request):
    if request.session.get("userid"):
        cart_items=TableCart.objects.filter(user=request.session["userid"])
        cart_subtotal=sum(i.total() for i in cart_items)
        cart_totdisc=sum(i.discount() for i in cart_items)
        discount = cart_subtotal - cart_totdisc
        cart_count = TableCart.objects.filter(user=request.session["userid"]).count()

    else:
        cart_items=TableCart.objects.filter(session_key=request.session.session_key)
        cart_subtotal=sum(i.total() for i in cart_items)
        cart_totdisc=sum(i.discount() for i in cart_items)
        discount=cart_subtotal-cart_totdisc
        cart_count = TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"cart.html",{
        "cart_items":cart_items,
        "cart_subtotal":cart_subtotal,
        "cart_totdisc":cart_totdisc,
        "discount":discount,
        "cart_count":cart_count})

def cart_delete(request,pro_id):
    data=TableCart.objects.get(id=pro_id)
    data.delete()
    return redirect("/cart/")

@staff_member_required(login_url="/admin/login/")
def coupons(request):
    data=TableCoupon.objects.all()
    return render(request,"coupons.html",{"data":data})

@staff_member_required(login_url="/admin/login/")
def add_coupon(request):
    return render(request,"add_coupon.html")

@staff_member_required(login_url="/admin/login/")
def save_coupon(request):
    if request.method=="POST":
        tab_obj=TableCoupon()
        tab_obj.code=request.POST.get("code")
        tab_obj.price=request.POST.get("discount")
        tab_obj.save()
        return redirect("/coupons/")

@staff_member_required(login_url="/admin/login/")
def edit_coupon(request,code_id):
    data=TableCoupon.objects.get(id=code_id)
    return render(request,"edit_coupon.html",{"data":data})

@staff_member_required(login_url="/admin/login/")
def update_coupon(request,code_id):
    if request.method=="POST":
        tab_obj=TableCoupon.objects.get(id=code_id)
        tab_obj.code=request.POST.get("coupon")
        tab_obj.price=request.POST.get("discount")
        tab_obj.save()
        return redirect("/coupons/")

@user_passes_test(lambda u: u.is_superuser, login_url="/admin/login/")
def delete_coupon(request,code_id):
    data=TableCoupon.objects.get(id=code_id)
    data.delete()
    return redirect("/coupons/")

def single_product(request,prod_id):
    data=TableProduct.objects.get(id=prod_id)
    review=TableReview.objects.filter(product=data)
    if request.session.get("userid"):
        cart_count=TableCart.objects.filter(user=request.session["userid"]).count()
    else:
        cart_count=TableCart.objects.filter(session_key=request.session.session_key).count()
    return render(request,"single_product.html",{"data":data,"review":review,"cart_count":cart_count})

def add_to_cart(request):
    if request.method == "POST":

        data = json.loads(request.body)

        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        size = data.get("size")

        # safety
        if quantity < 1:
            quantity = 1

        product = TableProduct.objects.get(id=product_id)

        user = None
        session_key = None

        # LOGGED-IN USER
        if request.session.get("userid"):
            user = TableReg.objects.get(id=request.session["userid"])

        # GUEST USER
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

        # CHECK EXISTING CART ITEM
        cart_item = TableCart.objects.filter(
            product=product,
            user=user,
            session_key=session_key,
            size=size
        ).first()

        if cart_item:
            cart_item.quantity = (cart_item.quantity or 0) + quantity
            cart_item.save()
        else:
            TableCart.objects.create(
                product=product,
                user=user,
                session_key=session_key,
                size=size,
                quantity=quantity
            )

        if user:
            cart_count = TableCart.objects.filter(user=user).count()
        else:
            cart_count = TableCart.objects.filter(session_key=session_key).count()

        return JsonResponse({
            "status": "success",
            "message": "Added to cart",
             "cart_count":cart_count
        })

    return JsonResponse({"status": "error"})

def update_cart_qty(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cart_id = data.get("cart_id")
        change = int(data.get("change", 0))

        cart_item = TableCart.objects.get(id=cart_id)

        # update quantity with limits
        new_qty = cart_item.quantity + change
        if new_qty < 1:
            new_qty = 1
        if new_qty > 100:
            new_qty = 100

        cart_item.quantity = new_qty
        cart_item.save()

        # RECALCULATE CART TOTALS
        if cart_item.user:
            cart_items = TableCart.objects.filter(user=cart_item.user)
        else:
            cart_items = TableCart.objects.filter(
                session_key=cart_item.session_key
            )

        cart_subtotal = sum(i.total() for i in cart_items)
        cart_totdisc = sum(i.discount() for i in cart_items)
        discount = cart_subtotal - cart_totdisc

        return JsonResponse({
            "status": "success",
            "quantity": new_qty,
            "item_total": cart_item.discount(),
            "cart_subtotal": cart_subtotal,
            "cart_discount": discount,
            "cart_total": cart_totdisc
        })

    return JsonResponse({"status": "error"})


def buy_now(request, prod_id):
    if not request.session.get("userid"):
        return redirect("/login/")

    if request.method == "POST":
        address = TableAddress.objects.filter(user=request.session["userid"])
        product = TableProduct.objects.get(id=prod_id)
        quantity = int(request.POST.get("quantity", 1))
        cart_count = TableCart.objects.filter(user=request.session["userid"]).count()

        total = product.discount * quantity
        tax = total * 0.18
        total_price = total + tax


        if total_price < 500:
            subtotal = total_price + 100
        else:
            subtotal = total_price



        currency = "INR"


        return render(request, "buy_now.html", {
            "address": address,
            "product": product,
            "quantity": quantity,
            "total": total,
            "total_price":total_price,
            "tax": tax,
            "subtotal": subtotal,

            "razorpay_merchant_key": "rzp_test_9zruMnoLDlsCLG",

             "currency": currency,
            "cart_count":cart_count

        })

    else:
        return redirect("/shop/")

def create_razorpay_order(request):
    if request.method == "POST":
        try:
            amount = float(request.POST.get("amount"))
        except:
            return JsonResponse({"status": "error", "message": "Invalid amount"})

        if amount <= 0:
            return JsonResponse({"status": "error", "message": "Amount must be greater than 0"})

        currency = "INR"
        razorpay_amount = int(amount * 100)  # convert to paise

        order = razorpay_client.order.create({
            "amount": razorpay_amount,
            "currency": currency,
            "payment_capture": "0"
        })

        return JsonResponse({
            "status": "success",
            "order_id": order["id"],
            "amount": razorpay_amount
        })

    return JsonResponse({"status": "error", "message": "Invalid request"})



def check_coupon(request):
    code = request.GET.get("code")
    total = request.GET.get("total")

    if not TableCoupon.objects.filter(code=code).exists():
        return JsonResponse({"status": "error"})

    c_code = TableCoupon.objects.get(code=code)

    total = float(total)

    # Percentage coupon
    if "%" in c_code.price:
        percentage = int(c_code.price.replace("%", ""))
        discount = (percentage / 100) * total
        amount = total - discount
    else:
        amount = total - int(c_code.price)

    if amount <= 0:
        return JsonResponse({"status": "not_eligible"})

    return JsonResponse({
        "status": "success",
        "amount": round(amount, 2),
        "code": code
    })

def checkout_buy(request,pro_id):
    if request.method=="POST":

        razorpay_order_id = request.POST.get('order_id')
        payment_id = request.POST.get('payment_id')
        amount = int(float(request.POST.get('amount'))*100)
        address_id = request.POST.get("address_id")
        quantity = int(request.POST.get("quantity", 1))
        coupon = request.POST.get("applied_coupon")
        final_price=int(amount/100)

        if not payment_id:
            return HttpResponse("Payment not completed", status=400)

        razorpay_client.payment.capture(payment_id, amount)


        if not TableAddress.objects.filter(id=address_id).exists():
            Tab_add = TableAddress()
            Tab_add.user_id = request.session["userid"]
            Tab_add.fname = request.POST.get("fname")
            Tab_add.sname = request.POST.get("sname")
            Tab_add.address = request.POST.get("address")
            Tab_add.phone = request.POST.get("phone")
            Tab_add.landmark = request.POST.get("landmark")
            Tab_add.city = request.POST.get("city")
            Tab_add.state = request.POST.get("state")
            Tab_add.pc = request.POST.get("pincode")
            Tab_add.save()

            Tab_buy=TableBuy()
            Tab_buy.user_id=request.session["userid"]
            Tab_buy.address_id=Tab_add.id
            Tab_buy.product_id=pro_id
            Tab_buy.quantity=quantity
            Tab_buy.disc_price=final_price
            Tab_buy.orderID=razorpay_order_id
            Tab_buy.paymentID=payment_id
            Tab_buy.order_status="ordered"
            Tab_buy.payment_status="paid"
            Tab_buy.payment_method="online"
            Tab_buy.invoiceID="INV"+razorpay_order_id
            if coupon:
                try:
                    Tab_buy.coupon = TableCoupon.objects.get(code=coupon)
                except TableCoupon.DoesNotExist:
                    Tab_buy.coupon = None
            else:
                Tab_buy.coupon = None
            Tab_buy.save()

            Tab_prod=TableProduct.objects.get(id=pro_id)
            Tab_prod.stock-=int(request.POST.get("quantity"))
            Tab_prod.save()

            return redirect("/")

        else:
            Tab_buy = TableBuy()
            Tab_buy.user_id = request.session["userid"]
            Tab_buy.address_id = address_id
            Tab_buy.product_id = pro_id
            Tab_buy.quantity = quantity
            Tab_buy.disc_price = final_price
            Tab_buy.orderID = razorpay_order_id
            Tab_buy.paymentID = payment_id
            Tab_buy.order_status = "ordered"
            Tab_buy.payment_status = "paid"
            Tab_buy.payment_method = "online"
            Tab_buy.invoiceID = "INV" + razorpay_order_id
            if coupon:
                try:
                    Tab_buy.coupon = TableCoupon.objects.get(code=coupon)
                except TableCoupon.DoesNotExist:
                    Tab_buy.coupon = None
            else:
                Tab_buy.coupon = None
            Tab_buy.save()

            Tab_prod = TableProduct.objects.get(id=pro_id)
            Tab_prod.stock -= int(request.POST.get("quantity"))
            Tab_prod.save()

            return redirect("/")


def cart_buynow(request):
    if request.session.get("userid"):
        address=TableAddress.objects.filter(user=request.session["userid"])
        cart_items=TableCart.objects.filter(user=request.session["userid"])
        cart_count = TableCart.objects.filter(user=request.session["userid"]).count()
        cart_total=sum(i.total() for i in cart_items)
        cart_discount=sum(i.discount() for i in cart_items)
        discount= cart_total - cart_discount
        tax= cart_discount * 0.18
        if cart_discount < 500:
            subtotal=int(cart_discount) + 100 + int(tax)
        else:
            subtotal=int(cart_discount) + int(tax)
        currency="INR"
        amount=int(float(subtotal)*100)
        return render(request,"cart_buynow.html",{
            "address":address,
            "cart_items":cart_items,
            "cart_count":cart_count,
            "cart_total":cart_total,
            "cart_discount":cart_discount,
            "tax":tax,
            "razorpay_merchant_key": "rzp_test_9zruMnoLDlsCLG",
            "subtotal":subtotal,
            "currency":currency,
            "amount":amount})
    else:
        return redirect("/login/")

def checkout_cart(request):
    if request.method=="POST":

        razorpay_order_id = request.POST.get('order_id')
        payment_id = request.POST.get('payment_id')
        amount = int(float(request.POST.get('amount'))*100)
        address_id = request.POST.get("address_id")
        quantity = request.POST.get("quantity", 1)
        coupon = request.POST.get("applied_coupon")
        final_price=int(amount/100)

        if not payment_id:
            return HttpResponse("Payment not completed", status=400)

        razorpay_client.payment.capture(payment_id, amount)

        if not TableAddress.objects.filter(id=address_id).exists():
            Tab_add = TableAddress()
            Tab_add.user_id = request.session["userid"]
            Tab_add.fname = request.POST.get("fname")
            Tab_add.sname = request.POST.get("sname")
            Tab_add.address = request.POST.get("address")
            Tab_add.phone = request.POST.get("phone")
            Tab_add.landmark = request.POST.get("landmark")
            Tab_add.city = request.POST.get("city")
            Tab_add.state = request.POST.get("state")
            Tab_add.pc = request.POST.get("pincode")
            Tab_add.save()

            Tab_buy = TableBuy()
            Tab_buy.user_id = request.session["userid"]
            Tab_buy.address_id = Tab_add.id
            Tab_buy.disc_price = final_price
            Tab_buy.orderID = razorpay_order_id
            Tab_buy.paymentID = payment_id
            Tab_buy.order_status = "ordered"
            Tab_buy.payment_status = "paid"
            Tab_buy.payment_method = "online"
            Tab_buy.invoiceID = "INV" + razorpay_order_id
            if coupon:
                try:
                    Tab_buy.coupon = TableCoupon.objects.get(code=coupon)
                except TableCoupon.DoesNotExist:
                    Tab_buy.coupon = None
            else:
                Tab_buy.coupon = None
            Tab_buy.save()
            cart_items=TableCart.objects.filter(user=request.session["userid"])
            for i in cart_items:
                Tab_lis=TableCheckoutList()
                Tab_lis.user=i.user
                Tab_lis.product=i.product
                Tab_lis.quantity=i.quantity
                Tab_lis.buy_id=Tab_buy.id
                Tab_lis.save()

                Tab_pro=TableProduct.objects.get(id=i.product.id)
                Tab_pro.stock-= int(i.quantity)

            cart_items.delete()
            return redirect("/")


        else:
            Tab_buy = TableBuy()
            Tab_buy.user_id = request.session["userid"]
            Tab_buy.address_id = address_id
            Tab_buy.disc_price = final_price
            Tab_buy.orderID = razorpay_order_id
            Tab_buy.paymentID = payment_id
            Tab_buy.order_status = "ordered"
            Tab_buy.payment_status = "paid"
            Tab_buy.payment_method = "online"
            Tab_buy.invoiceID = "INV" + razorpay_order_id
            if coupon:
                try:
                    Tab_buy.coupon = TableCoupon.objects.get(code=coupon)
                except TableCoupon.DoesNotExist:
                    Tab_buy.coupon = None
            else:
                Tab_buy.coupon = None
            Tab_buy.save()

            cart_items = TableCart.objects.filter(user=request.session["userid"])
            for i in cart_items:
                Tab_lis = TableCheckoutList()
                Tab_lis.user = i.user
                Tab_lis.product = i.product
                Tab_lis.quantity = i.quantity
                Tab_lis.buy_id = Tab_buy.id
                Tab_lis.save()

                Tab_pro = TableProduct.objects.get(id=i.product.id)
                Tab_pro.stock -= int(i.quantity)

            cart_items.delete()
            return redirect("/")

def profile(request):
    user=TableReg.objects.get(id=request.session["userid"])
    address=TableAddress.objects.filter(user=request.session["userid"])
    checkout=TableCheckoutList.objects.filter(user=request.session["userid"])
    buy=TableBuy.objects.filter(user=request.session["userid"])
    return render(request,"profile.html",{
        "user":user,
        "address":address,
        "checkout":checkout,
        "buy":buy})


def log_out(request):
    del request.session["userid"]
    return redirect("/")

def add_address(request):
    if request.method == "POST":
        Tab_add=TableAddress()
        Tab_add.user_id= request.session["userid"]
        Tab_add.fname=request.POST.get("fname")
        Tab_add.sname = request.POST.get("sname")
        Tab_add.phone = request.POST.get("phone")
        Tab_add.email = request.POST.get("email")
        Tab_add.pincode = request.POST.get("pincode")
        Tab_add.city = request.POST.get("city")
        Tab_add.state = request.POST.get("state")
        Tab_add.address = request.POST.get("address")
        Tab_add.landmark = request.POST.get("landmark")
        Tab_add.save()
        return redirect("/profile/")

def update_account(request):
    if request.method =="POST":
        Tab_reg=TableReg.objects.get(id=request.session["userid"])

        email=request.POST.get("email")
        password=request.POST.get("password")
        c_password=request.POST.get("cpassword")

        if email:
            if not EMAIL_RE.match(email):
                return HttpResponse("Invalid email format")
            Tab_reg.email=email

        if password:
            if not PASSWORD_RE.match(password):
                return HttpResponse("Password must be 8+ chars, 1 capital, 1 number")

            if password != c_password:
                return HttpResponse("Passwords do not match")
            Tab_reg.password=make_password(password)

        Tab_reg.save()
        return redirect("/profile/")

def add_review(request):
    if request.method == "POST":
        user_id = request.session["userid"]
        product_id = request.POST.get("product_id")

        exists = TableReview.objects.filter(
            user_id=user_id,
            product_id=product_id).exists()

        if exists:
            return HttpResponse("You have already reviewed this product.")

        product = TableProduct.objects.get(id=product_id)

        Tab_rev = TableReview()
        Tab_rev.user_id = user_id
        Tab_rev.product = product
        Tab_rev.image1 = request.FILES.get("img1")
        Tab_rev.image2 = request.FILES.get("img2")
        Tab_rev.rating = int(request.POST.get("rating"))
        Tab_rev.review = request.POST.get("review")
        Tab_rev.save()

        return redirect("/profile/")

def stock_update(request):
    prod=TableProduct.objects.all()
    return render(request,"stock_updates.html",{"prod":prod})

def save_stock(request):
    if request.method=="POST":
        product=request.POST.get("product")
        stock=request.POST.get("stock")
        Tab_pro=TableProduct.objects.get(id=product)
        Tab_pro.stock += int(stock)
        Tab_pro.save()
        return redirect("/products/")

def inventory_report(request):
    cat=TableCategory.objects.all()
    pro=TableProduct.objects.all()
    pro_count=pro.count()
    total_stock=sum(i.stock or 0 for i in pro)
    days=timezone.now()
    monthly_stock = TableProduct.objects.filter(
        date__year=days.year, date__month=days.month
    ).aggregate(Sum("stock"))
    stock_value=monthly_stock["stock__sum"] or 0

    return render(request,"inventory_report.html",{
        "pro":pro,
        "cat":cat,
        "pro_count":pro_count,
        "total_stock": total_stock,
        "stock_value": stock_value,

        "s_cat": None,
        "sku": None,
        "month": None,
        "prod": None,
        "date": None,
    })

def search_month(request):
    month=request.POST.get("month")
    if month:
        year,month=month.split("-")
        pro=TableProduct.objects.filter(date__month=int(month),date__year=int(year))

    else:
        pro=TableProduct.objects.all()
    pro_count=pro.count()
    cat = TableCategory.objects.all()
    total_stock = sum(i.stock for i in pro)
    days = timezone.now()
    monthly_stock = TableProduct.objects.filter(date__year=days.year, date__month=days.month).aggregate(Sum("stock"))
    stock_value = monthly_stock["stock__sum"]
    return render(request,"inventory_report.html",{
        "pro":pro,
        "cat":cat,
        "pro_count":pro_count,
        "total_stock":total_stock,
        "stock_value":stock_value,
        "month":month,

        "s_cat": None,
        "sku": None,
        "prod": None,
        "date": None,
    })

def search_date(request):
    date = request.POST.get("date")

    if date:
        pro = TableProduct.objects.filter(date=date)
    else:
        pro = TableProduct.objects.all()
    pro_count = pro.count()
    cat = TableCategory.objects.all()
    total_stock = sum(i.stock for i in pro)
    days = timezone.now()
    monthly_stock = TableProduct.objects.filter(date__year=days.year, date__month=days.month).aggregate(Sum("stock"))
    stock_value = monthly_stock["stock__sum"]
    return render(request,"inventory_report.html",{
        "pro":pro,
        "cat":cat,
        "pro_count":pro_count,
        "total_stock":total_stock,
        "stock_value":stock_value,
        "date":date,

        "s_cat": None,
        "sku": None,
        "month": None,
        "prod": None
    })

def search_sku(request):
    sku = request.POST.get("sku")

    if sku:
        pro = TableProduct.objects.filter(sku_code=sku)
    else:
        pro = TableProduct.objects.all()

    pro_count = pro.count()
    cat = TableCategory.objects.all()
    total_stock = sum(i.stock or 0 for i in pro)

    days = timezone.now()
    monthly_stock = TableProduct.objects.filter(
        date__year=days.year, date__month=days.month
    ).aggregate(Sum("stock"))
    stock_value = monthly_stock["stock__sum"] or 0

    return render(request, "inventory_report.html", {
        "pro": pro,
        "cat": cat,
        "pro_count": pro_count,
        "total_stock": total_stock,
        "stock_value": stock_value,
        "sku": sku,

        # send all filter vars for download link
        "s_cat": None,
        "month": None,
        "prod": None,
        "date": None,
    })

def search_product(request):
    prod = request.POST.get("product")
    if prod:
        pro = TableProduct.objects.filter(prod=prod)
    else:
        pro = TableProduct.objects.all()
    pro_count = pro.count()
    cat = TableCategory.objects.all()
    total_stock = sum(i.stock for i in pro)
    days = timezone.now()
    monthly_stock = TableProduct.objects.filter(date__year=days.year, date__month=days.month).aggregate(Sum("stock"))
    stock_value = monthly_stock["stock__sum"]
    return render(request,"inventory_report.html",{
        "pro":pro,
        "cat":cat,
        "pro_count":pro_count,
        "total_stock":total_stock,
        "stock_value":stock_value,
        "prod":prod,

        "s_cat": None,
        "sku": None,
        "month": None,
        "date": None,
    })

def search_cate(request):
    s_cat=request.POST.get("select_category")
    if s_cat:
        pro=TableProduct.objects.filter(category=s_cat)
    else:
        pro = TableProduct.objects.all()
    pro_count = pro.count()
    cat=TableCategory.objects.all()
    total_stock = sum(i.stock for i in pro)
    days = timezone.now()
    monthly_stock = TableProduct.objects.filter(date__year=days.year, date__month=days.month).aggregate(Sum("stock"))
    stock_value = monthly_stock["stock__sum"]
    return render(request,"inventory_report.html",{
        "pro":pro,
        "cat":cat,
        "s_cat":s_cat,
        "pro_count":pro_count,
        "total_stock":total_stock,
        "stock_value":stock_value,

        "month": None,
        "sku": None,
        "prod": None,
        "date": None
    })

def export_inventory_report(request):
    category = request.GET.get("s_cat")
    product  = request.GET.get("prod")
    sku      = request.GET.get("sku")
    date     = request.GET.get("date")
    month    = request.GET.get("month")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=inventory_report.csv"
    writer = csv.writer(response)

    writer.writerow([
        "ID", "CATEGORY", "SUBCATEGORY", "PRODUCT",
        "DATE", "SKU", "PRICE", "DISCOUNT", "STOCK", "STATUS"
    ])

    pro = TableProduct.objects.all()

    if category and category != "None":
        pro = pro.filter(category=int(category))

    if product and product != "None":
        pro = pro.filter(prod=product)

    if sku and sku != "None":
        pro = pro.filter(sku_code=sku)

    if date and date != "None":
        pro = pro.filter(date=date)

    if month and month != "None":
        if "-" in month:
            year, m = month.split("-")
            pro = pro.filter(date__year=int(year), date__month=int(m))
        else:
            pro= pro.filter(date__month=int(month))

    for i in pro:
        writer.writerow([
            i.id,
            i.category.category,
            i.subcat.subcategory,
            i.prod,
            i.date,
            i.sku_code,
            i.price,
            i.discount,
            i.stock or 0,
            i.status,
        ])

    return response

def order_management(request):
    order_buy= TableBuy.objects.annotate(cart_count=Count("tablecheckoutlist")).filter(cart_count=0)
    order_cart= TableBuy.objects.annotate(cart_count=Count("tablecheckoutlist")).filter(cart_count__gt=0)
    return render(request,"order_management.html",{"order_buy":order_buy, "order_cart":order_cart})

def cart_order_items(request, order_id):
    items = TableCheckoutList.objects.filter(buy_id=order_id)

    data = []
    for i in items:
        data.append({
            "name": i.product.prod,
            "image": i.product.image.url,
            "qty": i.quantity,
            "price": i.product.discount,
            "subtotal": i.quantity * i.product.discount
        })

    return JsonResponse({"items": data})

def change_status(request,order_id):
    if request.method=="POST":
        data=TableBuy.objects.get(id=order_id)
        data.order_status=request.POST.get("status")
        data.save()
        return redirect("/order_management/")

def order_delete(request,order_id):
    data=TableBuy.objects.get(id=order_id)
    data.delete()
    return redirect("/order_management/")

def order_invoice(request,order_id):
    data=TableBuy.objects.get(id=order_id)
    check=TableCheckoutList.objects.filter(buy_id=order_id)
    if check:
        check_total=0
        check_quantity=0
        for item in check:
            check_quantity+=item.quantity
            check_total += item.quantity * item.product.discount  # ✅ FIX
        tax=round(check_total*0.18,2)
        total = data.disc_price
        # tax=int(total*0.18)
        return render(request,"order_invoice.html",{
            "data":data,
            "check":check,
            "tax":tax,
            "total":total
        })
    else:
        pro_quantity=data.quantity
        pro_disc=pro_quantity*data.product.discount
        print(pro_quantity)
        print(pro_disc)
        tax=round(pro_disc*0.18,2)
        total = data.disc_price
        return render(request, "order_invoice.html", {
            "data": data,
            "check": check,
            "tax": tax,
            "total": total
        })

def user_review(request):
    data=TableReview.objects.all()
    return render(request,"user_review.html",{"data":data})

def delete_review(request,review_id):
    data=TableReview.objects.get(id=review_id)
    data.delete()
    return redirect("/user_review/")

def sales_report(request):
    prod=TableProduct.objects.all()
    data=TableBuy.objects.all()
    sales_count=data.count()
    total_sale=sum(i.disc_price for i in data)
    return render(request,"sales_report.html",{
        "data":data,
        "sales_count":sales_count,
        "total_sales":total_sale,
        "prod":prod,
        "user":None,
        "status":None,
        "pro":None

    })

def searchby_user(request):
    prod=TableProduct.objects.all()
    user=request.POST.get("user")
    if user:
        data=TableBuy.objects.filter(user__username=user)
    else:
        data=TableBuy.objects.all()
    sales_count = data.count()
    total_sale = sum(i.disc_price for i in data)
    return render(request, "sales_report.html", {
        "data": data,
        "sales_count": sales_count,
        "total_sales": total_sale,
        "prod":prod,
        "user": user,
        "status": None,
        "pro": None
    })

def searchby_status(request):
    prod = TableProduct.objects.all()
    status=request.POST.get("status")
    if status:
        data=TableBuy.objects.filter(order_status=status)
    else:
        data=TableBuy.objects.all()
    sales_count = data.count()
    total_sale = sum(i.disc_price for i in data)
    return render(request, "sales_report.html", {
        "data": data,
        "sales_count": sales_count,
        "total_sales": total_sale,
        "prod": prod,
        "user":None,
        "status":status,
        "pro":None
    })


def searchby_product(request):
    prod = TableProduct.objects.all()
    pro=request.POST.get("product")
    if pro:
        data=TableBuy.objects.filter(product=pro)
    else:
        data=TableBuy.objects.all()
    sales_count = data.count()
    total_sale = sum(i.disc_price for i in data)
    return render(request, "sales_report.html", {
        "data": data,
        "sales_count": sales_count,
        "total_sales": total_sale,
        "prod": prod,
        "user": None,
        "status": None,
        "pro": pro
    })

def export_sales_report(request):
    prod = request.GET.get("prod")
    status = request.GET.get("status")
    user = request.GET.get("user")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=sales_report.csv"
    writer = csv.writer(response)

    writer.writerow(["ID", "PRODUCT", "USER", "DATE", "PRICE", "STATUS"])

    data = TableBuy.objects.all()

    if prod and prod != "None":
        data = data.filter(product_id=prod)

    if status and status != "None":
        data = data.filter(order_status=status)

    if user and user != "None":
        data = data.filter(user__username=user)

    for i in data:
        writer.writerow([
            i.id,
            i.product.prod if i.product else "Product is in cart",
            i.user.username if i.user else "Guest",
            i.date,
            i.disc_price or 0,
            i.order_status or "N/A",
        ])

    return response







