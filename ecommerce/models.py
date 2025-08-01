from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    serial_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    cart_add_count = models.PositiveIntegerField(default=0)

    def get_discounted_price(self):
        return self.discount_price if self.discount_price else self.price

    def has_discount(self):
        return self.discount_price and self.discount_price < self.price

    def __str__(self):
        return self.name





class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class ShippingOption(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_time = models.CharField(max_length=100)  # e.g. "2-4 days"

    def __str__(self):
        return f"{self.name} (${self.price}) - {self.delivery_time}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_option = models.ForeignKey(ShippingOption, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ✅ Add these fields for delivery
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

    def get_total_with_shipping(self):
        if self.shipping_option:
            return self.total_price + self.shipping_option.price
        return self.total_price




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order #{self.order.id}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.percentage}% off {self.product.name} from {self.start_date} to {self.end_date}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/multiple/')

    def __str__(self):
        return f"{self.product.name} image"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'product')  # One rating per user per product

    def __str__(self):
        return f"{self.product.name} - {self.value}⭐ by {self.user.username}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Flat amount to subtract")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.code
