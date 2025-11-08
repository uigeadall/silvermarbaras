# admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.contrib import messages
import csv

from .models import (
    Category, Product, ProductImage, ProductVariant,
    CartItem, Order, OrderItem, Favorite, Discount, ShippingOption, Coupon, ProductBundleItem
)
from .utils.emailing import send_order_shipped_email

# ---------- Inlines ----------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 10

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("size", "stock", "price_override", "sku")

class ProductBundleItemInline(admin.TabularInline):
    model = ProductBundleItem
    fk_name = "product"                 # edit bundle items from the main product page
    extra = 1
    autocomplete_fields = ["item"]      # quick search for products
    fields = ("item", "position", "is_active", "note")
    ordering = ("position",)

    # Optional: don't allow selecting the same product as the item
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            # instance is available on change form; on add it won't exist yet
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                kwargs["queryset"] = Product.objects.exclude(pk=obj_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline, ProductBundleItemInline]
    list_display = ("name", "serial_number", "price", "discount_price", "category", "brand", "cart_add_count")
    list_filter = ("category", "brand")

    # Exact match on serial (fast) + partials on name/brand/serial
    # '=' prefix => exact; '^' => startswith; full field name => icontains
    search_fields = ("=serial_number", "^name", "name", "serial_number", "brand", "category__name")
    search_help_text = "Search by exact serial (best), name, brand, or category."

    list_select_related = ("category",)

    # (Optional) Bubble exact serial hits to the top even when other terms are present
    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            exact = queryset.model.objects.filter(serial_number__iexact=search_term)
            qs = exact | qs
        return qs, use_distinct


# Optional registrations (or remove if only via inline)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Favorite)
admin.site.register(Discount)
admin.site.register(ShippingOption)


# ---------- Orders (no custom template) ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "full_name",
        "email",
        "total_price",
        "shipping_option",
        "coupon_code",
        "items_count",
    )
    # date_hierarchy = "created_at"  # Disabled due to MySQL timezone issues
    search_fields = ("id", "full_name", "email", "phone", "address", "city", "postal_code")
    list_filter = ("shipping_option", "coupon", "created_at")
    list_select_related = ("shipping_option", "coupon", "user")
    readonly_fields = ()

    actions = ["export_orders_csv", "send_shipped_email"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_items_count=Count("items"))

    @admin.display(description="Items")
    def items_count(self, obj):
        return getattr(obj, "_items_count", 0)

    @admin.display(description="Coupon")
    def coupon_code(self, obj):
        return obj.coupon.code if obj.coupon else "-"

    def send_shipped_email(self, request, queryset):
        """Admin action to send 'order shipped' email to selected orders."""
        base_url = f"{request.scheme}://{request.get_host()}"
        sent_count = 0
        failed_count = 0
        
        for order in queryset:
            recipient = getattr(order, "email", None) or getattr(getattr(order, "user", None), "email", None)
            if not recipient:
                failed_count += 1
                continue
            
            if send_order_shipped_email(order, base_url):
                sent_count += 1
            else:
                failed_count += 1
        
        if sent_count > 0:
            self.message_user(
                request,
                f"✅ Изпратени са {sent_count} имейла за изпратени поръчки.",
                messages.SUCCESS
            )
        if failed_count > 0:
            self.message_user(
                request,
                f"⚠️ {failed_count} имейла не можаха да бъдат изпратени (липсва email адрес или грешка).",
                messages.WARNING
            )
    
    send_shipped_email.short_description = "Изпрати имейл 'Поръчката е изпратена'"

    def export_orders_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "id", "created_at", "full_name", "email", "phone",
            "address", "city", "postal_code",
            "shipping_option", "coupon", "total_price", "items_count"
        ])

        counts = (
            OrderItem.objects
            .filter(order__in=queryset)
            .values("order_id")
            .annotate(c=Sum("quantity"))
        )
        counts_map = {row["order_id"]: row["c"] for row in counts}

        for o in queryset.select_related("shipping_option", "coupon"):
            writer.writerow([
                o.id, o.created_at, o.full_name, o.email, o.phone,
                o.address, o.city, o.postal_code,
                (o.shipping_option.name if o.shipping_option else ""),
                (o.coupon.code if o.coupon else ""),
                o.total_price,
                counts_map.get(o.id, 0),
            ])
        return response

    export_orders_csv.short_description = "Export selected orders to CSV"


# ---------- Coupons ----------
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "percent_off", "amount_off", "active", "starts_at", "ends_at", "used_count", "usage_limit")
    search_fields = ("code",)
    list_filter = ("active",)

