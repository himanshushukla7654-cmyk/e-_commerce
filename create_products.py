from django.core.management.base import BaseCommand

from store.models import Category, Product


class Command(BaseCommand):

    help = "Create 7 default products"


    def handle(self, *args, **kwargs):

        electronics, created = Category.objects.get_or_create(
            name="Electronics"
        )

        fashion, created = Category.objects.get_or_create(
            name="Fashion"
        )


        products = [

            {
                "name": "Himanshu Buds",
                "category": electronics,
                "description": "Wireless Himanshu Buds with clear sound and comfortable design.",
                "price": 1499,
                "stock": 20,
                "image_url": "/media/products/buds_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Himanshu Earphones",
                "category": electronics,
                "description": "Himanshu Earphones with clear audio and comfortable fit.",
                "price": 999,
                "stock": 20,
                "image_url": "/media/products/phone_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Shukla Earbud",
                "category": electronics,
                "description": "Shukla Earbud with wireless connectivity and powerful sound.",
                "price": 1299,
                "stock": 20,
                "image_url": "/media/products/earbuds_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Shukla Dress",
                "category": fashion,
                "description": "Stylish Shukla Dress with comfortable and modern design.",
                "price": 2499,
                "stock": 15,
                "image_url": "/media/products/buds_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Shukla Watch",
                "category": fashion,
                "description": "Premium Shukla Watch with elegant design.",
                "price": 1999,
                "stock": 20,
                "image_url": "/media/products/phone_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Vipin Watch",
                "category": fashion,
                "description": "Vipin Watch with stylish design for everyday use.",
                "price": 2999,
                "stock": 20,
                "image_url": "/media/products/earbuds_photo.jpg",
                "address": "Delhi, India"
            },

            {
                "name": "Vipin Phone",
                "category": electronics,
                "description": "Vipin Phone with modern features and smooth performance.",
                "price": 15999,
                "stock": 10,
                "image_url": "/media/products/phone_photo.jpg",
                "address": "Delhi, India"
            }

        ]


        for data in products:

            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "description": data["description"],
                    "price": data["price"],
                    "stock": data["stock"],
                    "image_url": data["image_url"],
                    "address": data["address"]
                }
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {product.name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {product.name}"
                    )
                )


        self.stdout.write(
            self.style.SUCCESS(
                "All 7 products created successfully!"
            )
        )