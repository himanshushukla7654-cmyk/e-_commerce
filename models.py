from django.db import models


class Category(models.Model):

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    image_url = models.CharField(
        max_length=500,
        blank=True
    )

    address = models.CharField(
        max_length=300,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Cart(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    session_key = models.CharField(
        max_length=100
    )

    def total_price(self):

        return self.product.price * self.quantity

    def __str__(self):

        return f"{self.product.name} - {self.quantity}"


class Coupon(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_percent = models.PositiveIntegerField(
        default=10
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):

        return self.code


class Order(models.Model):

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
    )

    address = models.CharField(
        max_length=300
    )

    city = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        default="Cash on Delivery"
    )

    payment_status = models.CharField(
        max_length=50,
        default="Pending"
    )

    order_status = models.CharField(
        max_length=30,
        default="Pending"
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"Order #{self.id} - {self.name}"


class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    name = models.CharField(
        max_length=100
    )

    rating = models.PositiveIntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.product.name} - {self.rating} Stars"


class Wishlist(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    session_key = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = (
            "product",
            "session_key"
        )

    def __str__(self):

        return f"{self.product.name} - Wishlist"