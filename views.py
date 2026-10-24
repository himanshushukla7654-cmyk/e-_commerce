from decimal import Decimal

import razorpay

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Cart,
    Category,
    Coupon,
    Order,
    Product,
    Review,
    Wishlist,
)


# =========================================================
# HOME
# =========================================================

def home(request):

    products = Product.objects.all().order_by("-created_at")
    categories = Category.objects.all()

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    if query:
        products = products.filter(
            name__icontains=query
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    paginator = Paginator(
        products,
        8
    )

    page_number = request.GET.get("page")

    products = paginator.get_page(
        page_number
    )

    return render(
        request,
        "home.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
        },
    )


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id,
    )

    reviews = Review.objects.filter(
        product=product
    ).order_by(
        "-created_at"
    )

    review_count = reviews.count()

    if review_count > 0:

        total_rating = sum(
            review.rating
            for review in reviews
        )

        average_rating = round(
            total_rating / review_count,
            1,
        )

    else:

        average_rating = 0

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        rating = request.POST.get(
            "rating",
            "",
        ).strip()

        comment = request.POST.get(
            "comment",
            "",
        ).strip()

        if not name or not rating or not comment:

            return render(
                request,
                "product_detail.html",
                {
                    "product": product,
                    "reviews": reviews,
                    "average_rating": average_rating,
                    "review_count": review_count,
                    "review_error": (
                        "Please fill all fields."
                    ),
                },
            )

        try:
            rating = int(rating)
        except ValueError:
            rating = 0

        if rating < 1 or rating > 5:

            return render(
                request,
                "product_detail.html",
                {
                    "product": product,
                    "reviews": reviews,
                    "average_rating": average_rating,
                    "review_count": review_count,
                    "review_error": (
                        "Rating must be between 1 and 5."
                    ),
                },
            )

        Review.objects.create(
            product=product,
            name=name,
            rating=rating,
            comment=comment,
        )

        return redirect(
            "product_detail",
            id=product.id,
        )

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "average_rating": average_rating,
            "review_count": review_count,
        },
    )


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, id):

    product = get_object_or_404(
        Product,
        id=id,
    )

    if product.stock <= 0:

        return redirect(
            "product_detail",
            id=product.id,
        )

    if not request.session.session_key:
        request.session.create()

    cart_item, created = Cart.objects.get_or_create(
        product=product,
        session_key=request.session.session_key,
    )

    if created:

        cart_item.quantity = 1

    elif cart_item.quantity < product.stock:

        cart_item.quantity += 1

    cart_item.save()

    return redirect("cart")


# =========================================================
# CART
# =========================================================

def cart(request):

    if not request.session.session_key:
        request.session.create()

    cart_items = Cart.objects.filter(
        session_key=request.session.session_key
    ).select_related(
        "product"
    )

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


# =========================================================
# INCREASE QUANTITY
# =========================================================

def increase_quantity(request, id):

    if not request.session.session_key:
        request.session.create()

    cart_item = get_object_or_404(
        Cart,
        id=id,
        session_key=request.session.session_key,
    )

    if cart_item.quantity < cart_item.product.stock:

        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


# =========================================================
# DECREASE QUANTITY
# =========================================================

def decrease_quantity(request, id):

    if not request.session.session_key:
        request.session.create()

    cart_item = get_object_or_404(
        Cart,
        id=id,
        session_key=request.session.session_key,
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    else:

        cart_item.delete()

    return redirect("cart")


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(request, id):

    if not request.session.session_key:
        request.session.create()

    cart_item = get_object_or_404(
        Cart,
        id=id,
        session_key=request.session.session_key,
    )

    cart_item.delete()

    return redirect("cart")


# =========================================================
# CHECKOUT
# =========================================================

def checkout(request):

    if not request.session.session_key:
        request.session.create()

    cart_items = Cart.objects.filter(
        session_key=request.session.session_key
    ).select_related(
        "product"
    )

    if not cart_items.exists():

        return redirect("cart")

    # -----------------------------------------------------
    # STOCK CHECK
    # -----------------------------------------------------

    for item in cart_items:

        if item.quantity > item.product.stock:

            return render(
                request,
                "checkout.html",
                {
                    "cart_items": cart_items,
                    "subtotal": Decimal("0.00"),
                    "discount": Decimal("0.00"),
                    "total": Decimal("0.00"),
                    "coupon_code": "",
                    "checkout_error": (
                        f"Insufficient stock for "
                        f"{item.product.name}."
                    ),
                },
            )

    # -----------------------------------------------------
    # SUBTOTAL
    # -----------------------------------------------------

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    # -----------------------------------------------------
    # COUPON
    # -----------------------------------------------------

    discount = Decimal("0.00")

    coupon_code = request.session.get(
        "coupon_code",
        "",
    )

    if coupon_code:

        try:

            coupon = Coupon.objects.get(
                code=coupon_code,
                active=True,
            )

            discount = (
                subtotal
                * Decimal(
                    coupon.discount_percent
                )
                / Decimal("100")
            )

        except Coupon.DoesNotExist:

            request.session.pop(
                "coupon_code",
                None,
            )

            coupon_code = ""

    total = subtotal - discount

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        # ================================================
        # APPLY COUPON
        # ================================================

        if request.POST.get("apply_coupon"):

            entered_code = request.POST.get(
                "coupon_code",
                "",
            ).strip().upper()

            try:

                coupon = Coupon.objects.get(
                    code=entered_code,
                    active=True,
                )

                request.session["coupon_code"] = (
                    coupon.code
                )

                return redirect("checkout")

            except Coupon.DoesNotExist:

                return render(
                    request,
                    "checkout.html",
                    {
                        "cart_items": cart_items,
                        "subtotal": subtotal,
                        "discount": Decimal("0.00"),
                        "total": subtotal,
                        "coupon_error": (
                            "Invalid or inactive coupon code."
                        ),
                        "coupon_code": entered_code,
                    },
                )

        # ================================================
        # REMOVE COUPON
        # ================================================

        if request.POST.get("remove_coupon"):

            request.session.pop(
                "coupon_code",
                None,
            )

            return redirect("checkout")

        # ================================================
        # CUSTOMER DETAILS
        # ================================================

        name = request.POST.get(
            "name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        address = request.POST.get(
            "address",
            "",
        ).strip()

        city = request.POST.get(
            "city",
            "",
        ).strip()

        pincode = request.POST.get(
            "pincode",
            "",
        ).strip()

        payment_method = request.POST.get(
            "payment_method",
            "Cash on Delivery",
        )

        # ================================================
        # VALIDATION
        # ================================================

        if not all(
            [
                name,
                email,
                phone,
                address,
                city,
                pincode,
            ]
        ):

            return render(
                request,
                "checkout.html",
                {
                    "cart_items": cart_items,
                    "subtotal": subtotal,
                    "discount": discount,
                    "total": total,
                    "coupon_code": coupon_code,
                    "checkout_error": (
                        "Please fill all delivery details."
                    ),
                },
            )

        # =================================================
        # ONLINE PAYMENT
        # =================================================

        if payment_method == "Online Payment":

            try:

                # -----------------------------------------
                # Razorpay client
                # -----------------------------------------

                client = razorpay.Client(
                    auth=(
                        settings.RAZORPAY_KEY_ID,
                        settings.RAZORPAY_KEY_SECRET,
                    )
                )

                # -----------------------------------------
                # Create Razorpay order
                # -----------------------------------------

                razorpay_order = client.order.create(
                    {
                        "amount": int(total * 100),
                        "currency": "INR",
                        "receipt": (
                            f"receipt_"
                            f"{request.session.session_key}"
                        ),
                    }
                )

                # -----------------------------------------
                # Save local order
                # -----------------------------------------

                order = Order.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                    pincode=pincode,
                    total_amount=total,
                    payment_method=(
                        "Online Payment"
                    ),
                    payment_status="Pending",
                    order_status="Pending",
                    razorpay_order_id=(
                        razorpay_order["id"]
                    ),
                )

                # -----------------------------------------
                # Open Razorpay checkout page
                # -----------------------------------------

                return render(
                    request,
                    "payment.html",
                    {
                        "order": order,
                        "razorpay_order_id": (
                            razorpay_order["id"]
                        ),
                        "razorpay_key_id": (
                            settings.RAZORPAY_KEY_ID
                        ),
                        "amount": (
                            int(total * 100)
                        ),
                    },
                )

            except razorpay.errors.BadRequestError:

                return render(
                    request,
                    "checkout.html",
                    {
                        "cart_items": cart_items,
                        "subtotal": subtotal,
                        "discount": discount,
                        "total": total,
                        "coupon_code": coupon_code,
                        "checkout_error": (
                            "Razorpay authentication failed. "
                            "Please check your Test Mode "
                            "Key ID and Secret."
                        ),
                    },
                )

            except Exception:

                return render(
                    request,
                    "checkout.html",
                    {
                        "cart_items": cart_items,
                        "subtotal": subtotal,
                        "discount": discount,
                        "total": total,
                        "coupon_code": coupon_code,
                        "checkout_error": (
                            "Online payment is temporarily "
                            "unavailable. Please use "
                            "Cash on Delivery."
                        ),
                    },
                )

        # =================================================
        # CASH ON DELIVERY
        # =================================================

        order = Order.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            total_amount=total,
            payment_method="Cash on Delivery",
            payment_status="Pending",
            order_status="Pending",
        )

        # Reduce stock
        for item in cart_items:

            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()

        # Clear coupon
        request.session.pop(
            "coupon_code",
            None,
        )

        return render(
            request,
            "order_success.html",
            {
                "order": order,
            },
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "coupon_code": coupon_code,
        },
    )


# =========================================================
# RAZORPAY PAYMENT SUCCESS
# =========================================================

def payment_success(request):

    if request.method != "POST":

        return redirect("checkout")

    payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    signature = request.POST.get(
        "razorpay_signature"
    )

    if not payment_id or not razorpay_order_id or not signature:

        return render(
            request,
            "checkout.html",
            {
                "checkout_error": (
                    "Invalid payment response."
                ),
            },
        )

    order = get_object_or_404(
        Order,
        razorpay_order_id=razorpay_order_id,
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )

    try:

        # IMPORTANT:
        # Verify Razorpay signature on server
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": (
                    razorpay_order_id
                ),
                "razorpay_payment_id": (
                    payment_id
                ),
                "razorpay_signature": (
                    signature
                ),
            }
        )

        # Payment successful
        order.razorpay_payment_id = payment_id
        order.payment_status = "Paid"
        order.order_status = "Confirmed"

        order.save()

        # ---------------------------------------------
        # Reduce stock
        # ---------------------------------------------

        cart_items = Cart.objects.filter(
            session_key=request.session.session_key
        ).select_related(
            "product"
        )

        for item in cart_items:

            if item.quantity <= item.product.stock:

                item.product.stock -= item.quantity
                item.product.save()

        # ---------------------------------------------
        # Clear cart
        # ---------------------------------------------

        cart_items.delete()

        request.session.pop(
            "coupon_code",
            None,
        )

        return render(
            request,
            "order_success.html",
            {
                "order": order,
            },
        )

    except razorpay.errors.SignatureVerificationError:

        order.payment_status = "Failed"
        order.order_status = "Failed"

        order.save()

        return render(
            request,
            "checkout.html",
            {
                "checkout_error": (
                    "Payment verification failed. "
                    "The order was not confirmed."
                ),
            },
        )


# =========================================================
# MY ORDERS
# =========================================================

def my_orders(request):

    orders = Order.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "my_orders.html",
        {
            "orders": orders,
        },
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:

        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

            return redirect("home")

        return render(
            request,
            "login.html",
            {
                "error": (
                    "Invalid username or password."
                ),
            },
        )

    return render(
        request,
        "login.html",
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("home")


# =========================================================
# SIGNUP
# =========================================================

def signup(request):

    if request.user.is_authenticated:

        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        if not username or not email or not password:

            return render(
                request,
                "signup.html",
                {
                    "error": (
                        "All fields are required."
                    ),
                },
            )

        if password != confirm_password:

            return render(
                request,
                "signup.html",
                {
                    "error": (
                        "Passwords do not match."
                    ),
                },
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "signup.html",
                {
                    "error": (
                        "Username already exists."
                    ),
                },
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(
            request,
            user,
        )

        return redirect("home")

    return render(
        request,
        "signup.html",
    )


# =========================================================
# ADD TO WISHLIST
# =========================================================

def add_to_wishlist(request, id):

    product = get_object_or_404(
        Product,
        id=id,
    )

    if not request.session.session_key:

        request.session.create()

    Wishlist.objects.get_or_create(
        product=product,
        session_key=request.session.session_key,
    )

    return redirect("wishlist")


# =========================================================
# WISHLIST
# =========================================================

def wishlist(request):

    if not request.session.session_key:

        request.session.create()

    wishlist_items = Wishlist.objects.filter(
        session_key=request.session.session_key
    ).select_related(
        "product"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items,
        },
    )


# =========================================================
# REMOVE FROM WISHLIST
# =========================================================

def remove_from_wishlist(request, id):

    if not request.session.session_key:

        request.session.create()

    wishlist_item = get_object_or_404(
        Wishlist,
        id=id,
        session_key=request.session.session_key,
    )

    wishlist_item.delete()

    return redirect("wishlist")