from django.contrib import admin
from .models import (
    Category,
    Product,
    Cart,
    Coupon,
    Order,
    Review,
    Wishlist
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity", "session_key")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "discount_percent", "active")
    list_filter = ("active",)
    search_fields = ("code",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "city",
        "total_amount",
        "payment_method",
        "payment_status",
        "order_status",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_status",
        "order_status",
        "city",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "razorpay_order_id",
        "razorpay_payment_id",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "name",
        "rating",
        "created_at",
    )

    list_filter = ("rating", "created_at")

    search_fields = (
        "name",
        "comment",
        "product__name",
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "session_key",
        "created_at",
    )

    list_filter = ("created_at",)

    search_fields = (
        "product__name",
        "session_key",
    )