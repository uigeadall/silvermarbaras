from django.contrib import admin
from .models import (
    Category, Product, ProductImage, CartItem, Order,
    OrderItem, Favorite, Discount, ShippingOption
)

class ProductImageInline(admin.TabularInline):  # or StackedInline
    model = ProductImage
    extra = 1  # how many empty forms to show
    max_num = 10  # optional: max images

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Category)

admin.site.register(ProductImage)  # optional: you can remove this if you use the inline
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Favorite)
admin.site.register(Discount)
admin.site.register(ShippingOption)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'category', 'brand')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'serial_number', 'brand')