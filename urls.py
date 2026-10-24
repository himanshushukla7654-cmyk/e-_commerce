from django.urls import path

from . import views


urlpatterns = [

    # HOME
    path(
        "",
        views.home,
        name="home",
    ),

    # PRODUCTS
    path(
        "product/<int:id>/",
        views.product_detail,
        name="product_detail",
    ),

    # CART
    path(
        "cart/",
        views.cart,
        name="cart",
    ),

    path(
        "cart/add/<int:id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/increase/<int:id>/",
        views.increase_quantity,
        name="increase_quantity",
    ),

    path(
        "cart/decrease/<int:id>/",
        views.decrease_quantity,
        name="decrease_quantity",
    ),

    path(
        "cart/remove/<int:id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),

    # CHECKOUT
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    # RAZORPAY
    path(
        "payment/success/",
        views.payment_success,
        name="payment_success",
    ),

    # ORDERS
    path(
        "orders/",
        views.my_orders,
        name="my_orders",
    ),

    # AUTH
    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "signup/",
        views.signup,
        name="signup",
    ),

    # WISHLIST
    path(
        "wishlist/",
        views.wishlist,
        name="wishlist",
    ),

    path(
        "wishlist/add/<int:id>/",
        views.add_to_wishlist,
        name="add_to_wishlist",
    ),

    path(
        "wishlist/remove/<int:id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
]