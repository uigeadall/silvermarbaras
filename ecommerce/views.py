from __future__ import annotations

import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Optional
from django.db.models import Max
import stripe
from allauth.account.views import LoginView
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers import registry
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import (
    Avg,
    Case,
    F,
    IntegerField,
    Prefetch,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import RatingForm
from .models import (
    CartItem,
    Category,
    Comment,
    Coupon,
    Favorite,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductVariant,
    Rating,
    ShippingOption, ProductBundleItem,
)
from .signals import order_submitted, user_registered

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# =============================================================================
# Helpers
# =============================================================================

UNLIMITED_STOCK = 10**9  # sentinel for "not tracked / unlimited"


def _ensure_session(request: HttpRequest) -> None:
    """Guarantee the request has a usable session key."""
    if not request.session.session_key:
        request.session.create()


def _owner_filter(request: HttpRequest) -> dict:
    """Identify the cart owner by user or session."""
    if request.user.is_authenticated:
        return {"user": request.user}
    _ensure_session(request)
    return {"session_key": request.session.session_key}


def _cart_items_for(request: HttpRequest):
    """Return cart items for the current owner with product preloaded."""
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user).select_related("product")
    _ensure_session(request)
    return CartItem.objects.filter(session_key=request.session.session_key).select_related("product")


def _compute_subtotal(items: Iterable[CartItem]) -> Decimal:
    """Compute cart subtotal and set per-item 'subtotal' attribute (not saved)."""
    total = Decimal("0")
    for it in items:
        price = it.product.get_discounted_price() or Decimal("0")
        it.subtotal = price * it.quantity
        total += it.subtotal
    return total


def _to_cents(amount: Decimal) -> int:
    """Convert Decimal amount to Stripe-friendly integer cents."""
    return int((amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100))


def _available_stock(product: Product, variant_id: Optional[int] = None) -> int:
    """
    Determine available stock.

    Priority:
      1) If variant_id provided -> that variant's stock.
      2) If product has variants -> sum their stock.
      3) If product has a stock-like field -> use it.
      4) Otherwise -> treat as unlimited (not tracked).
    """
    if variant_id:
        return int(
            ProductVariant.objects.filter(id=variant_id, product=product)
            .values_list("stock", flat=True)
            .first()
            or 0
        )

    try:
        if hasattr(product, "variants") and product.variants.exists():
            agg = product.variants.aggregate(total=Sum("stock"))
            return int(agg["total"] or 0)
    except Exception:
        pass

    for field in ("stock", "quantity", "inventory"):
        if hasattr(product, field):
            val = getattr(product, field, None)
            if val is not None:
                return int(val or 0)

    return UNLIMITED_STOCK


def _cap_quantity(requested_total: int, available: int) -> int:
    """Clamp requested_total to [0, available]."""
    try:
        requested_total = int(requested_total)
    except Exception:
        requested_total = 0
    try:
        available = int(available)
    except Exception:
        available = 0

    if available < 0:
        available = 0
    if requested_total < 0:
        requested_total = 0
    return min(requested_total, available)


# =============================================================================
# Public pages
# =============================================================================

def home(request: HttpRequest):
    query = request.GET.get("q")
    sort = request.GET.get("sort")
    category_slug = request.GET.get("category")

    products = Product.objects.all().select_related("category")

    selected_category = None
    if category_slug:
        # Try slug first; if pk was passed, fallback still works.
        selected_category = Category.objects.filter(slug=category_slug).first()
        if not selected_category:
            selected_category = get_object_or_404(Category, pk=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Robust price sorting using effective price = discount_price or price
    products = products.annotate(_eff_price=Coalesce("discount_price", "price"))
    if sort == "price_asc":
        products = products.order_by("_eff_price")
    elif sort == "price_desc":
        products = products.order_by("-_eff_price")

    # Recently viewed (preserve session order)
    ids = [int(pk) for pk in request.session.get("recently_viewed", []) if str(pk).isdigit()]
    recently_viewed_qs = Product.objects.none()
    if ids:
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(ids)], output_field=IntegerField())
        recently_viewed_qs = Product.objects.filter(id__in=ids).order_by(preserved_order)

    # 🔥 Trending Now — 15 items (5 per row × 3 rows)
    POPULAR_LIMIT = 15
    popular_products = (
        Product.objects.annotate(_pop=Coalesce("cart_add_count", Value(0))).order_by("-_pop", "-id")[:POPULAR_LIMIT]
    )

    # ⭐ Editors’ Choice — Top 10 by total stock (product.stock + sum(variants.stock))
    editors_choice = (
        Product.objects.select_related("category")
        .annotate(
            variant_stock=Coalesce(Sum("variants__stock"), Value(0)),
            base_stock=Coalesce(F("stock"), Value(0)),
        )
        .annotate(total_stock=F("base_stock") + F("variant_stock"))
        .order_by("-total_stock", "name", "-id")[:10]
    )

    context = {
        "products": products,
        "recently_viewed_products": list(recently_viewed_qs[:5]),
        "recently_viewed_full_count": recently_viewed_qs.count(),
        "categories": Category.objects.all(),
        "favorite_ids": (
            list(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
            if request.user.is_authenticated
            else []
        ),
        "popular_products": popular_products,
        "editors_choice": editors_choice,
        "sort": sort,
        "query": query,
        "selected_category": selected_category,
    }

    if request.headers.get("HX-Request") == "true":
        return render(request, "home_partial.html", context)
    return render(request, "home.html", context)


def products_by_category(request: HttpRequest, pk: int):
    category = get_object_or_404(Category, pk=pk)
    sort = request.GET.get("sort")

    products = list(Product.objects.filter(category=category).select_related("category"))
    if sort == "price_asc":
        products.sort(key=lambda p: p.get_discounted_price())
    elif sort == "price_desc":
        products.sort(key=lambda p: p.get_discounted_price(), reverse=True)

    recently_viewed_ids = request.session.get("recently_viewed", [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)

    popular_products = Product.objects.order_by("-cart_add_count")[:10]
    favorite_ids = (
        list(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
        if request.user.is_authenticated
        else []
    )

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "selected_category": category,
        "recently_viewed": recently_viewed,
        "popular_products": popular_products,
        "favorite_ids": favorite_ids,
        "sort": sort,
    }
    # Reuse home template layout for category pages.
    return render(request, "home.html", context)


def product_list(request: HttpRequest):
    selected_category = None
    category_id = request.GET.get("category")
    sort = request.GET.get("sort")

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = list(Product.objects.filter(category=selected_category).select_related("category"))
    else:
        products = list(Product.objects.all().select_related("category"))

    if sort == "price_asc":
        products.sort(key=lambda p: p.get_discounted_price())
    elif sort == "price_desc":
        products.sort(key=lambda p: p.get_discounted_price(), reverse=True)

    categories = Category.objects.all()
    recently_viewed_ids = request.session.get("recently_viewed", [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)
    recently_viewed = sorted(recently_viewed, key=lambda x: recently_viewed_ids.index(x.id))

    return render(
        request,
        "product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": selected_category,
            "recently_viewed": recently_viewed,
            "sort": sort,
        },
    )


def product_detail(request: HttpRequest, pk: int):
    product_qs = (
        Product.objects.select_related("category").prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.all()),
            Prefetch("variants", queryset=ProductVariant.objects.order_by("size")),
        )
    )
    product = get_object_or_404(product_qs, pk=pk)

    comments = Comment.objects.filter(product=product).order_by("-created_at")
    product_images = list(product.images.all())
    rating_form = None
    categories = Category.objects.all()

    # Ratings + comments handling
    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(user=request.user, product=product).first()
        rating_form = RatingForm(instance=existing_rating)

        if request.method == "POST":
            value = request.POST.get("value")
            if value:
                rating_form = RatingForm(request.POST, instance=existing_rating)
                if rating_form.is_valid():
                    rating = rating_form.save(commit=False)
                    rating.user = request.user
                    rating.product = product
                    rating.save()

            comment_text = (request.POST.get("comment") or "").strip()
            if comment_text:
                Comment.objects.create(product=product, user=request.user, text=comment_text)

            return redirect("product_detail", pk=pk)

    average_rating = product.ratings.aggregate(Avg("value"))["value__avg"]

    # Recently viewed (preserve order from session)
    rv = [int(i) for i in request.session.get("recently_viewed", []) if str(i).isdigit()]
    pk_i = int(pk)
    if pk_i in rv:
        rv.remove(pk_i)
    rv.insert(0, pk_i)
    request.session["recently_viewed"] = rv[:10]

    preserved = Case(*[When(id=pid, then=pos) for pos, pid in enumerate(rv)], output_field=IntegerField())
    recently_viewed_products = (
        Product.objects.filter(pk__in=rv)
        .exclude(pk=product.pk)
        .select_related("category")
        .order_by(preserved)
    )

    # You Might Also Like (same category as current product)
    you_might_like = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .annotate(_pop=Coalesce("cart_add_count", Value(0, output_field=IntegerField())))
        .order_by("-_pop", "-id")[:10]
    )

    # ===== Buy as a set — ONLY manual picks; quick-add metadata for each item =====
    manual_links = (
        ProductBundleItem.objects
        .filter(product=product, is_active=True)
        .select_related("item__category")
        .order_by("position", "id")
    )
    bundle_ids = [lnk.item_id for lnk in manual_links]

    bundle_items = []
    bundle_items_data = []  # [{ "product": p, "qa": {...} }, ...]
    if bundle_ids:
        preserved_bundle = Case(
            *[When(id=pid, then=pos) for pos, pid in enumerate(bundle_ids)],
            output_field=IntegerField()
        )
        bundle_qs = (
            Product.objects
            .filter(pk__in=bundle_ids)
            .select_related("category")
            .prefetch_related(Prefetch("variants", queryset=ProductVariant.objects.order_by("size")))
            .order_by(preserved_bundle)
        )

        for p in bundle_qs:
            qa = {"can": False, "variant_id": None, "needs_size": False, "disabled": False, "reason": ""}
            # If the Product model has a related_name "variants" for ProductVariant; adjust if different
            variants_mgr = getattr(p, "variants", None)
            variants = list(variants_mgr.all()) if variants_mgr is not None else []

            if variants:
                in_stock = [v for v in variants if (getattr(v, "stock", 0) or 0) > 0]
                if len(in_stock) == 1:
                    qa["can"] = True
                    qa["variant_id"] = in_stock[0].id
                elif len(in_stock) == 0:
                    qa["disabled"] = True
                    qa["reason"] = "Out of stock"
                else:
                    qa["needs_size"] = True
            else:
                # No variants → quick add if stock > 0
                if (p.stock or 0) > 0:
                    qa["can"] = True
                else:
                    qa["disabled"] = True
                    qa["reason"] = "Out of stock"

            bundle_items.append(p)
            bundle_items_data.append({"product": p, "qa": qa})

    show_bundle = bool(bundle_items)

    context = {
        "product": product,
        "product_images": product_images,
        "comments": comments,
        "favorite_ids": (
            list(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
            if request.user.is_authenticated
            else []
        ),
        "rating_form": rating_form,
        "average_rating": average_rating,
        "recently_viewed_products": recently_viewed_products,
        "you_might_like": you_might_like,
        "bundle_items": bundle_items,              # keeps compatibility if you still loop this anywhere
        "bundle_items_data": bundle_items_data,    # <-- NEW: for quick-add buttons in template
        "show_bundle": show_bundle,
        "categories": categories,
        "selected_category": product.category,
    }
    return render(request, "product_detail.html", context)






def register_view(request: HttpRequest):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not all([username, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            transaction.on_commit(lambda: user_registered.send(sender=User, user=user, request=request))
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")

    return render(request, "register.html")


def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password.")

    socialaccount_providers = registry.get_class_list()
    return render(request, "login.html", {"socialaccount_providers": socialaccount_providers})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("home")


class CustomLoginView(LoginView):
    template_name = "account/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["socialaccount_providers"] = [
            app.get_provider(self.request) for app in SocialApp.objects.filter(sites__id=settings.SITE_ID)
        ]
        return context


# =============================================================================
# Favorites
# =============================================================================

@login_required
def favorites_list(request: HttpRequest):
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "favorites.html", {"favorites": favorites})


@login_required
def remove_from_favorites(request: HttpRequest, pk: int):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect("favorites_list")


@login_required
def toggle_favorite(request: HttpRequest, pk: int):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()
        return redirect("product_detail", pk=pk)
    return JsonResponse({"error": "Invalid request"}, status=400)


# =============================================================================
# Cart
# =============================================================================

def cart_view(request: HttpRequest):
    cart_items = _cart_items_for(request)
    subtotal = _compute_subtotal(cart_items)


    cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)


    categories = Category.objects.order_by("name")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "is_guest": not request.user.is_authenticated,
        "categories": categories,
        "selected_category": None,
        "cart_count": cart_count,
        "show_sidebars": True,
    }
    return render(request, "cart.html", context)


@require_POST
def update_cart_quantity(request: HttpRequest, pk: int):

    try:
        new_qty = int(request.POST.get("quantity"))
        if new_qty < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect("cart_view")

    owner = _owner_filter(request)


    cart_item = CartItem.objects.filter(product_id=pk, **owner).select_related("product").first()
    if not cart_item:
        messages.error(request, "Item not found in cart.")
        return redirect("cart_view")

    product = cart_item.product

    # If you store per-variant stock and CartItem has 'variant_id', pass it in:
    variant_id = getattr(cart_item, "variant_id", None)

    available = _available_stock(product, variant_id=variant_id)
    capped = _cap_quantity(new_qty, available)

    if capped == 0:
        cart_item.delete()
        messages.warning(request, "Item removed (out of stock).")
        return redirect("cart_view")

    cart_item.quantity = capped
    cart_item.save(update_fields=["quantity"])

    if capped < new_qty:
        messages.warning(request, f"Only {available} available. Quantity set to {capped}.")
    else:
        messages.success(request, "Cart updated.")

    return redirect("cart_view")


@require_POST
def remove_from_cart(request: HttpRequest, product_id: int = None, pk: int = None):
    product_id = product_id or pk
    owner = _owner_filter(request)
    CartItem.objects.filter(product_id=product_id, **owner).delete()
    messages.success(request, "Item removed.")
    return redirect("cart_view")


@require_POST
def add_to_cart(request: HttpRequest, pk: int):
    product = get_object_or_404(Product, pk=pk)


    raw_variant = request.POST.get("variant_id")
    try:
        variant_id = int(raw_variant) if raw_variant not in (None, "", "None") else None
    except (TypeError, ValueError):
        variant_id = None


    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    owner = _owner_filter(request)


    lookup_filter = {"product": product}
    if "variant" in [f.name for f in CartItem._meta.fields]:
        lookup_filter["variant_id"] = variant_id

    cart_item, _ = CartItem.objects.get_or_create(defaults={"quantity": 0}, **owner, **lookup_filter)


    available = _available_stock(product, variant_id=variant_id)
    current = int(cart_item.quantity or 0)
    requested_total = current + quantity
    capped_total = _cap_quantity(requested_total, available)

    if capped_total == 0:
        messages.error(request, "Този артикул е изчерпан.")
        return redirect("product_detail", pk=pk)

    # Persist capped quantity
    cart_item.quantity = capped_total
    cart_item.save(update_fields=["quantity"])

    # Increment product.cart_add_count by the *actual* delta added
    actually_added = capped_total - current
    if actually_added > 0:
        product.cart_add_count = (product.cart_add_count or 0) + actually_added
        product.save(update_fields=["cart_add_count"])

    if capped_total < requested_total:
        messages.warning(request, f"Налично е максимум {available}. Количеството е зададено на {capped_total}.")
    else:
        messages.success(request, "✅ Добавено в количката.")

    return redirect("product_detail", pk=pk)


# =============================================================================
# Checkout (supports guests and users)
# =============================================================================

@require_http_methods(["GET", "POST"])
def checkout_view(request: HttpRequest):
    cart_items = _cart_items_for(request)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    # Common data
    categories = Category.objects.order_by("name")
    cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)

    subtotal = _compute_subtotal(cart_items)
    discount = Decimal("0.00")
    coupon_applied = None
    coupon_error = None
    shipping_cost = Decimal("0.00")
    total = None
    coupon_code = ""  # keep input filled on template

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        address = (request.POST.get("address") or "").strip()
        city = (request.POST.get("city") or "").strip()
        postal_code = (request.POST.get("postal_code") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        shipping_option_id = request.POST.get("shipping_option")
        email = request.user.email if request.user.is_authenticated else (request.POST.get("email") or "").strip()
        coupon_code = (request.POST.get("coupon") or "").strip().upper()

        if not all([full_name, address, city, postal_code, phone]):
            messages.error(request, "All fields are required.")
            return redirect("checkout")

        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon and coupon.is_valid_now():
                new_subtotal = coupon.apply(subtotal)
                discount = subtotal - new_subtotal
                subtotal = new_subtotal
                coupon.used_count += 1
                coupon.save(update_fields=["used_count"])
                coupon_applied = coupon.code
            else:
                coupon_error = "Invalid or expired coupon."

        shipping_option = None
        if shipping_option_id:
            try:
                shipping_option = ShippingOption.objects.get(id=shipping_option_id)
                shipping_cost = getattr(shipping_option, "price", Decimal("0")) or Decimal("0")
            except ShippingOption.DoesNotExist:
                messages.error(request, "Invalid shipping option.")
                return redirect("checkout")

        total = (subtotal + shipping_cost).quantize(Decimal("0.01"))

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=email,
                full_name=full_name,
                address=address,
                city=city,
                postal_code=postal_code,
                phone=phone,
                shipping_option=shipping_option,
                total_price=total,
            )
            OrderItem.objects.bulk_create(
                [OrderItem(order=order, product=item.product, quantity=item.quantity) for item in cart_items]
            )
            cart_items.delete()
            transaction.on_commit(lambda: order_submitted.send(sender=Order, order=order, request=request))

        return redirect("order_success")

    # GET: create a PaymentIntent for the current subtotal (shipping added later)
    intent = stripe.PaymentIntent.create(
        amount=_to_cents(subtotal),
        currency="usd",
        metadata={"user_id": request.user.id if request.user.is_authenticated else "guest"},
        idempotency_key=f"pi-{request.session.session_key or 'nouser'}-{uuid.uuid4()}",
    )

    return render(
        request,
        "checkout.html",
        {
            # sidebars
            "categories": categories,
            "selected_category": None,
            "cart_count": cart_count,

            # order + form
            "cart_items": cart_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "shipping_cost": shipping_cost,
            "coupon_applied": coupon_applied,
            "coupon_error": coupon_error,
            "coupon_code": coupon_code,  # keeps the input value

            # stripe
            "shipping_options": ShippingOption.objects.all().order_by("price", "name"),
            "client_secret": intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
            "is_guest": not request.user.is_authenticated,
        },
    )
# =============================================================================
# Guest checkout (explicit guest page)
# =============================================================================

@require_http_methods(["GET", "POST"])
def guest_checkout_view(request: HttpRequest):
    _ensure_session(request)
    cart_qs = CartItem.objects.filter(session_key=request.session.session_key).select_related("product")
    subtotal = _compute_subtotal(cart_qs)

    discount = Decimal("0.00")
    coupon_applied = None
    coupon_error = None
    shipping_cost = Decimal("0.00")
    total = None

    if request.method == "POST":
        if not cart_qs.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart_view")

        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        address = (request.POST.get("address") or "").strip()
        city = (request.POST.get("city") or "").strip()
        postal_code = (request.POST.get("postal_code") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        shipping_option_id = request.POST.get("shipping_option")
        coupon_code = (request.POST.get("coupon") or "").strip().upper()

        if not all([full_name, email, address, city, postal_code, phone]):
            messages.error(request, "All fields are required.")
            return redirect("guest_checkout")

        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon and coupon.is_valid_now():
                new_subtotal = coupon.apply(subtotal)
                discount = subtotal - new_subtotal
                subtotal = new_subtotal
                coupon.used_count += 1
                coupon.save(update_fields=["used_count"])
                coupon_applied = coupon.code
            else:
                coupon_error = "Invalid or expired coupon."

        shipping_option = None
        if shipping_option_id:
            try:
                shipping_option = ShippingOption.objects.get(id=shipping_option_id)
                shipping_cost = getattr(shipping_option, "price", Decimal("0")) or Decimal("0")
            except ShippingOption.DoesNotExist:
                messages.error(request, "Invalid shipping option.")
                return redirect("guest_checkout")

        total = (subtotal + shipping_cost).quantize(Decimal("0.01"))

        with transaction.atomic():
            order = Order.objects.create(
                user=None,
                email=email,
                full_name=full_name,
                address=address,
                city=city,
                postal_code=postal_code,
                phone=phone,
                shipping_option=shipping_option,
                total_price=total,
            )
            OrderItem.objects.bulk_create(
                [OrderItem(order=order, product=item.product, quantity=item.quantity) for item in cart_qs]
            )
            cart_qs.delete()
            transaction.on_commit(lambda: order_submitted.send(sender=Order, order=order, request=request))

        return redirect("order_success")

    intent = stripe.PaymentIntent.create(
        amount=_to_cents(subtotal),
        currency="usd",
        idempotency_key=f"pi-guest-{request.session.session_key or 'nouser'}-{uuid.uuid4()}",
    )

    return render(
        request,
        "guest_checkout.html",
        {
            "cart_items": cart_qs,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "shipping_cost": shipping_cost,
            "coupon_applied": coupon_applied,
            "coupon_error": coupon_error,
            "client_secret": intent.client_secret,
            "shipping_options": ShippingOption.objects.all(),
            "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


# =============================================================================
# Stripe webhook
# =============================================================================

@csrf_exempt
def stripe_webhook(request: HttpRequest):
    endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return HttpResponse(status=400)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error("Invalid payload: %s", str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid Stripe signature: %s", str(e))
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        if not customer_email:
            logger.warning("No customer email in Stripe session.")
            return HttpResponse(status=200)

        user = User.objects.filter(email=customer_email).first()
        if not user:
            logger.info("Stripe session completed for unknown email %s (guest flow).", customer_email)
            return HttpResponse(status=200)

        Order.objects.create(
            user=user,
            stripe_checkout_id=session["id"],
            total_price=Decimal(session["amount_total"]) / Decimal("100"),
        )
        logger.info("✅ Order created from Stripe webhook for %s", user.username)

    return HttpResponse(status=200)


# =============================================================================
# Misc pages
# =============================================================================

def payment_success(request: HttpRequest):
    return render(request, "payment_success.html")


def notify(request: HttpRequest, level: int, msg: str):
    messages.add_message(request, level, msg)
    return redirect("home")


def order_success(request: HttpRequest):
    return render(request, "order_success.html")


def terms(request: HttpRequest):
    return render(request, "legal/terms.html")


def privacy(request: HttpRequest):
    return render(request, "legal/privacy.html")


def contact(request: HttpRequest):
    return render(request, "legal/contact.html")

@login_required
def profile_dashboard(request):
    # Dashboard stats
    fav_count = Favorite.objects.filter(user=request.user).count()
    order_qs = Order.objects.filter(user=request.user).order_by("-created_at")
    order_count = order_qs.count()
    total_spent = order_qs.aggregate(s=Sum("total_price"))["s"] or 0

    recent_orders = (
        order_qs
        .select_related("shipping_option", "coupon")
        [:5]
    )

    # Sidebars context (required by _profile_base.html)
    categories = Category.objects.order_by("name")
    cart_items = _cart_items_for(request)                 # your helper
    cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)

    return render(request, "dashboard.html", {
        "fav_count": fav_count,
        "order_count": order_count,
        "total_spent": total_spent,
        "recent_orders": recent_orders,
        "active_tab": "dashboard",

        # left/right rails
        "categories": categories,
        "cart_count": cart_count,
    })

@login_required
def profile_favorites(request):
    # Build the product queryset the user has favorited
    qs = (
        Product.objects
        .filter(favorited_by__user=request.user)
        .select_related("category")
        .prefetch_related("images")
        .annotate(last_fav_at=Max("favorited_by__created_at"))  # newest favorite timestamp
        .order_by("-last_fav_at", "-id")
    )

    paginator = Paginator(qs, 12)
    products_page = paginator.get_page(request.GET.get("page"))

    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list("product_id", flat=True)
    )

    # For sidebars (right search/cart/auth & left categories)
    categories = Category.objects.order_by("name")
    try:
        cart_items = _cart_items_for(request)          # reuse your helper if available
        cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)
    except NameError:
        # fallback if helper isn't imported in this scope
        cart_count = 0

    return render(request, "favorites.html", {
        "products_page": products_page,
        "favorite_ids": favorite_ids,
        "categories": categories,
        "cart_count": cart_count,
        "active_tab": "favorites",
    })


@login_required
def profile_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related("shipping_option", "coupon")
        .order_by("-created_at")
    )
    paginator = Paginator(orders, 10)
    page = request.GET.get("page")
    orders_page = paginator.get_page(page)

    
    item_counts = (
        OrderItem.objects
        .filter(order__in=orders_page.object_list)
        .values("order_id")
        .annotate(c=Sum("quantity"))
    )
    counts_map = {row["order_id"]: row["c"] for row in item_counts}

    return render(request, "orders.html", {
        "orders_page": orders_page,
        "counts_map": counts_map,
        "active_tab": "orders",
    })


@login_required
def profile_details(request):

    user = request.user
    return render(request, "details.html", {
        "user": user,
        "active_tab": "details",
    })

@login_required
@require_POST
def remove_from_favorites(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.filter(user=request.user, product=product).delete()

    # Prefer going back to the page the user was on
    back = request.META.get("HTTP_REFERER")
    if back:
        return redirect(back)

    # Fallback to the unified favorites page
    return redirect("profile_favorites")