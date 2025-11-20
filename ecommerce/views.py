from __future__ import annotations

import logging
import uuid
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from types import SimpleNamespace
from typing import Iterable, Optional
from django.db.models import Max
import stripe
from stripe import _error as stripe_error
from allauth.account.views import LoginView
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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
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

# Set Stripe API key with validation
if settings.STRIPE_SECRET_KEY:
    try:
        # Strip whitespace and newlines from the key (common issue when copying from Railway)
        cleaned_key = settings.STRIPE_SECRET_KEY.strip().replace('\n', '').replace('\r', '')
        # Validate that API key is ASCII-safe
        cleaned_key.encode('latin-1')
        stripe.api_key = cleaned_key
        logger.debug("Stripe API key configured successfully")
    except UnicodeEncodeError:
        logger.error("Stripe secret key contains non-ASCII characters - Stripe API calls will fail")
        stripe.api_key = None
else:
    stripe.api_key = None


UNLIMITED_STOCK = 10**9  # sentinel for "not tracked / unlimited"


def _ensure_session(request: HttpRequest) -> None:

    if not request.session.session_key:
        request.session.create()


def _owner_filter(request: HttpRequest) -> dict:

    if request.user.is_authenticated:
        return {"user": request.user}
    _ensure_session(request)
    return {"session_key": request.session.session_key}


def _cart_items_for(request: HttpRequest) -> Iterable[CartItem]:
    if request.user.is_authenticated:
        return (
            CartItem.objects
            .filter(user=request.user)
            .select_related("product", "variant")
            .prefetch_related(Prefetch("product__images", queryset=ProductImage.objects.all()))
        )
    _ensure_session(request)
    return (
        CartItem.objects
        .filter(session_key=request.session.session_key)
        .select_related("product", "variant")
        .prefetch_related(Prefetch("product__images", queryset=ProductImage.objects.all()))
    )


def _compute_subtotal(items: Iterable[CartItem]) -> Decimal:

    total = Decimal("0")
    for it in items:
        price = it.product.get_discounted_price() or Decimal("0")
        it.subtotal = price * it.quantity
        total += it.subtotal
    return total


def _to_cents(amount: Decimal) -> int:

    return int((amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100))


def _available_stock(product: Product, variant_id: Optional[int] = None) -> int:

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


# Checkout helper functions
def _process_coupon(coupon_code: str, subtotal: Decimal) -> tuple[Decimal, Decimal, Optional[str], Optional[str]]:
    """Process coupon code and return (new_subtotal, discount, coupon_applied, coupon_error)."""
    discount = Decimal("0.00")
    coupon_applied = None
    coupon_error = None
    
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
    
    return subtotal, discount, coupon_applied, coupon_error


def _get_shipping_option(shipping_option_id: Optional[str]) -> tuple[Optional[ShippingOption], Decimal]:
    """Get shipping option and return (shipping_option, shipping_cost)."""
    shipping_option = None
    shipping_cost = Decimal("0.00")
    
    if shipping_option_id:
        try:
            shipping_id = int(shipping_option_id)
            shipping_option = ShippingOption.objects.get(id=shipping_id)
            shipping_cost = getattr(shipping_option, "price", Decimal("0")) or Decimal("0")
        except (ValueError, TypeError, ShippingOption.DoesNotExist):
            shipping_option = None
            shipping_cost = Decimal("0.00")
    
    return shipping_option, shipping_cost


def _create_stripe_intent(amount: Decimal, session_key: Optional[str], is_guest: bool = False) -> Optional[stripe.PaymentIntent]:
    """Create Stripe PaymentIntent with error handling."""
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        logger.error("Stripe secret key is not configured")
        return None
    
    # Validate Stripe API key doesn't contain non-ASCII characters
    try:
        settings.STRIPE_SECRET_KEY.encode('latin-1')
    except UnicodeEncodeError:
        logger.error("Stripe secret key contains non-ASCII characters")
        return None
    
    try:
        # Create a safe idempotency key (only ASCII characters, no Cyrillic)
        # Use hash of session_key to avoid encoding issues
        if session_key:
            # Encode session_key to bytes, then hash it to get only ASCII characters
            try:
                session_hash = hashlib.md5(session_key.encode('utf-8')).hexdigest()
            except UnicodeEncodeError:
                # Fallback: use a hash of the repr if direct encoding fails
                session_hash = hashlib.md5(repr(session_key).encode('utf-8')).hexdigest()
        else:
            session_hash = 'nouser'
        
        idempotency_key = f"pi-{'guest' if is_guest else 'user'}-{session_hash}-{uuid.uuid4().hex}"
        
        # Ensure idempotency_key is ASCII-safe
        try:
            idempotency_key.encode('latin-1')
        except UnicodeEncodeError:
            logger.error("Idempotency key contains non-ASCII characters: %s", idempotency_key)
            # Fallback: use only hash and UUID
            idempotency_key = f"pi-{session_hash}-{uuid.uuid4().hex}"
        
        # Ensure all parameters are ASCII-safe
        intent = stripe.PaymentIntent.create(
            amount=int(_to_cents(amount)),
            currency="usd",
            idempotency_key=idempotency_key,
        )
        return intent
    except stripe_error.StripeError as e:
        logger.error("Stripe PaymentIntent creation failed: %s", str(e), exc_info=True)
        return None
    except UnicodeEncodeError as e:
        logger.error("UnicodeEncodeError creating Stripe PaymentIntent: %s", str(e), exc_info=True)
        return None
    except Exception as e:
        logger.error("Unexpected error creating Stripe PaymentIntent: %s", str(e), exc_info=True)
        return None


def _get_categories():
    """Get all categories ordered by name."""
    return Category.objects.all().order_by("name")

def home(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q")
    sort = request.GET.get("sort")
    category_slug = request.GET.get("category")

    products = (
        Product.objects
        .all()
        .select_related("category")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.all()))
    )

    selected_category = None
    if category_slug:

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
        recently_viewed_qs = (
            Product.objects
            .filter(id__in=ids)
            .select_related("category")
            .prefetch_related(Prefetch("images", queryset=ProductImage.objects.all()))
            .order_by(preserved_order)
        )

    # 🔥 Trending Now — 15 items (5 per row × 3 rows)
    POPULAR_LIMIT = 15
    popular_products = (
        Product.objects
        .select_related("category")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.all()))
        .annotate(_pop=Coalesce("cart_add_count", Value(0)))
        .order_by("-_pop", "-id")[:POPULAR_LIMIT]
    )

    # ⭐ Editors' Choice — Top 10 by total stock (product.stock + sum(variants.stock))
    editors_choice = (
        Product.objects.select_related("category")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.all()))
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
        "categories": _get_categories(),
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


def products_by_category(request: HttpRequest, pk: int) -> HttpResponse:
    category = get_object_or_404(Category, pk=pk)
    sort = request.GET.get("sort")

    products = Product.objects.filter(category=category).select_related("category")
    products = products.annotate(_eff_price=Coalesce("discount_price", "price"))
    if sort == "price_asc":
        products = products.order_by("_eff_price")
    elif sort == "price_desc":
        products = products.order_by("-_eff_price")

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
        "categories": _get_categories(),
        "selected_category": category,
        "recently_viewed": recently_viewed,
        "popular_products": popular_products,
        "favorite_ids": favorite_ids,
        "sort": sort,
    }
    
    return render(request, "home.html", context)


def product_list(request: HttpRequest) -> HttpResponse:
    selected_category = None
    category_id = request.GET.get("category")
    sort = request.GET.get("sort")

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=selected_category).select_related("category")
    else:
        products = Product.objects.all().select_related("category")

    products = products.annotate(_eff_price=Coalesce("discount_price", "price"))
    if sort == "price_asc":
        products = products.order_by("_eff_price")
    elif sort == "price_desc":
        products = products.order_by("-_eff_price")

    categories = _get_categories()
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


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product_qs = (
        Product.objects.select_related("category").prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.all().order_by('id')),
            Prefetch("variants", queryset=ProductVariant.objects.order_by("size")),
        )
    )
    product = get_object_or_404(product_qs, pk=pk)

    comments = Comment.objects.filter(product=product).order_by("-created_at")
    # Get all product images directly from database, ordered by ID to show all (old and new)
    # This ensures we get all images even if prefetch didn't work correctly
    product_images = list(ProductImage.objects.filter(product=product).order_by('id'))
    
    # Debug: log how many images we found and their paths
    logger.debug(f"Product {product.pk} ({product.name}): Found {len(product_images)} ProductImage records")
    for idx, img in enumerate(product_images):
        logger.debug(f"  Image {idx}: {img.image.name if hasattr(img, 'image') else 'NO IMAGE ATTR'}")
    
    # If product has a main image (old way) and it's not already in product_images, add it
    if product.image:
        # Check if the main image is already in product_images by comparing paths
        main_image_path = product.image.name
        image_exists = any(
            hasattr(img, 'image') and img.image.name == main_image_path 
            for img in product_images
        )
        if not image_exists:
            # Create a temporary ProductImage-like object to include the main image
            main_img_obj = SimpleNamespace(image=product.image)
            product_images.insert(0, main_img_obj)
            logger.debug(f"Added main image {main_image_path} to product_images list")
    
    # Filter out any images that don't have a valid image attribute
    product_images = [img for img in product_images if hasattr(img, 'image') and img.image]
    
    logger.debug(f"Total images for product {product.pk} after filtering: {len(product_images)}")
    rating_form = None
    categories = _get_categories()

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


def register_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not all([username, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email address.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                transaction.on_commit(lambda: user_registered.send(sender=User, user=user, request=request))
                messages.success(request, "Registration successful. You can now log in.")
                return redirect("login")

    return render(request, "register.html")


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Your account is disabled.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home")


class CustomLoginView(LoginView):
    template_name = "account/login.html"


# =============================================================================
# Favorites
# =============================================================================

@login_required
def favorites_list(request: HttpRequest) -> HttpResponse:
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "favorites.html", {"favorites": favorites})


@login_required
def toggle_favorite(request: HttpRequest, pk: int) -> HttpResponse:
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

def cart_view(request: HttpRequest) -> HttpResponse:
    cart_items = _cart_items_for(request)
    subtotal = _compute_subtotal(cart_items)
    cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)
    categories = _get_categories()

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
def update_cart_quantity(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        new_qty = int(request.POST.get("quantity"))
        if new_qty < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect("cart_view")

    owner = _owner_filter(request)
    cart_item = CartItem.objects.filter(product_id=pk, **owner).select_related("product", "variant").first()
    if not cart_item:
        messages.error(request, "Item not found in cart.")
        return redirect("cart_view")

    product = cart_item.product
    variant_id = cart_item.variant_id if cart_item.variant else None
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
def remove_from_cart(request: HttpRequest, product_id: int = None, pk: int = None) -> HttpResponse:
    product_id = product_id or pk
    owner = _owner_filter(request)
    CartItem.objects.filter(product_id=product_id, **owner).delete()
    messages.success(request, "Item removed.")
    return redirect("cart_view")


@require_POST
def add_to_cart(request: HttpRequest, pk: int) -> HttpResponse:
    # Ensure session exists before adding to cart (important for empty cart)
    _ensure_session(request)
    
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
    
    # Validate owner - ensure session_key exists for anonymous users
    if not request.user.is_authenticated:
        if not owner.get('session_key') or not request.session.session_key:
            # Force session creation and save
            _ensure_session(request)
            request.session.save()
            owner = {"session_key": request.session.session_key}
            logger.debug(f"Session recreated - new session_key: {owner['session_key']}")
    
    # Debug: log owner info for troubleshooting
    logger.debug(f"Adding to cart - owner: {owner}, product: {product.pk}, variant: {variant_id}, quantity: {quantity}")

    # CartItem has 'variant' field (ForeignKey), Django creates 'variant_id' automatically
    lookup_filter = {"product": product}
    if variant_id:
        # Get variant object to ensure it exists and belongs to product
        try:
            variant_obj = ProductVariant.objects.get(id=variant_id, product=product)
            lookup_filter["variant"] = variant_obj
        except ProductVariant.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid variant selected.'}, status=400)
            messages.error(request, "Invalid variant selected.")
            return redirect("product_detail", pk=pk)
    else:
        lookup_filter["variant"] = None

    # Ensure session is saved before creating cart item (important for empty cart)
    if not request.user.is_authenticated:
        request.session.save()
        # Double-check session_key is still valid
        if not request.session.session_key:
            logger.error("Session key is None after save!")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Session error. Please refresh the page.'}, status=500)
            messages.error(request, "Session error. Please try again.")
            return redirect("product_detail", pk=pk)
    
    try:
        cart_item, created = CartItem.objects.get_or_create(defaults={"quantity": 0}, **owner, **lookup_filter)
        logger.debug(f"Cart item {'created' if created else 'retrieved'}: {cart_item.id}, owner: {owner}, quantity before: {cart_item.quantity}")
    except Exception as e:
        logger.error(f"Error creating cart item: {e}, owner: {owner}, lookup: {lookup_filter}, session_key: {request.session.session_key}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': f'Error adding to cart: {str(e)}'}, status=500)
        messages.error(request, f"Error adding to cart: {str(e)}")
        return redirect("product_detail", pk=pk)
    
    available = _available_stock(product, variant_id=variant_id)
    current = int(cart_item.quantity or 0)
    
    # Check if this is an AJAX request (from bundle "Add to Cart")
    is_bundle_add = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if is_bundle_add:
        # For bundle items, we want to add exactly the requested quantity (usually 1)
        # Cap the quantity to add, not the total
        quantity_to_add = min(quantity, available - current) if available != UNLIMITED_STOCK else quantity
        if quantity_to_add <= 0:
            if is_bundle_add:
                return JsonResponse({'success': False, 'message': 'Този артикул е изчерпан или вече имате максимума в количката.'}, status=400)
            messages.error(request, "Този артикул е изчерпан.")
            return redirect("product_detail", pk=pk)
        requested_total = current + quantity_to_add
    else:
        # For main product form, add to existing quantity
        requested_total = current + quantity
    
    capped_total = _cap_quantity(requested_total, available)

    if capped_total == 0:
        if is_bundle_add:
            return JsonResponse({'success': False, 'message': 'Този артикул е изчерпан.'}, status=400)
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

    # Return JSON response for AJAX requests (bundle "Add to Cart")
    if is_bundle_add:
        # For bundle items, check if we added the requested quantity
        if actually_added < quantity:
            return JsonResponse({
                'success': True,
                'message': f'Налично е максимум {available}. Количеството е зададено на {capped_total}.',
                'warning': True
            })
        else:
            return JsonResponse({
                'success': True,
                'message': '✅ Добавено в количката.'
            })
    
    # Handle bundle items if they were selected
    bundle_items = request.POST.getlist('bundle_items')
    if bundle_items:
        bundle_added = []
        bundle_failed = []
        for bundle_item_str in bundle_items:
            try:
                # Format: "product_id" or "product_id:variant_id"
                parts = bundle_item_str.split(':')
                bundle_product_id = int(parts[0])
                bundle_variant_id = int(parts[1]) if len(parts) > 1 and parts[1] else None
                
                bundle_product = get_object_or_404(Product, pk=bundle_product_id)
                bundle_owner = _owner_filter(request)
                
                bundle_lookup = {"product": bundle_product}
                if bundle_variant_id:
                    try:
                        bundle_variant_obj = ProductVariant.objects.get(id=bundle_variant_id, product=bundle_product)
                        bundle_lookup["variant"] = bundle_variant_obj
                    except ProductVariant.DoesNotExist:
                        bundle_failed.append(bundle_product.name)
                        continue
                else:
                    bundle_lookup["variant"] = None
                
                bundle_cart_item, bundle_created = CartItem.objects.get_or_create(
                    defaults={"quantity": 0}, 
                    **bundle_owner, 
                    **bundle_lookup
                )
                
                bundle_available = _available_stock(bundle_product, variant_id=bundle_variant_id)
                bundle_current = int(bundle_cart_item.quantity or 0)
                bundle_quantity_to_add = min(1, bundle_available - bundle_current) if bundle_available != UNLIMITED_STOCK else 1
                
                if bundle_quantity_to_add > 0:
                    bundle_cart_item.quantity = bundle_current + bundle_quantity_to_add
                    bundle_cart_item.save(update_fields=["quantity"])
                    bundle_added.append(bundle_product.name)
                else:
                    bundle_failed.append(bundle_product.name)
            except (ValueError, Product.DoesNotExist) as e:
                logger.error(f"Error adding bundle item {bundle_item_str}: {e}")
                continue
        
        if bundle_added:
            messages.success(request, f"✅ Добавено в количката: {', '.join(bundle_added)}")
        if bundle_failed:
            messages.warning(request, f"⚠️ Не можа да се добави: {', '.join(bundle_failed)}")
    
    # Normal form submission - redirect
    if capped_total < requested_total:
        messages.warning(request, f"Налично е максимум {available}. Количеството е зададено на {capped_total}.")
    else:
        messages.success(request, "✅ Добавено в количката.")

    return redirect("product_detail", pk=pk)


# =============================================================================
# Checkout (supports guests and users)
# =============================================================================

@require_http_methods(["GET", "POST"])
def checkout_view(request: HttpRequest) -> HttpResponse:
    cart_items = _cart_items_for(request)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    # Common data
    categories = _get_categories()
    cart_count = sum(getattr(it, "quantity", 0) for it in cart_items)
    subtotal = _compute_subtotal(cart_items)
    discount = Decimal("0.00")
    coupon_applied = None
    coupon_error = None
    shipping_cost = Decimal("0.00")
    total = None
    coupon_code = ""

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

        if not request.user.is_authenticated and not email:
            messages.error(request, "Email is required for guest checkout.")
            return redirect("checkout")

        if not request.user.is_authenticated:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email address.")
                return redirect("checkout")

        # Process coupon
        subtotal, discount, coupon_applied, coupon_error = _process_coupon(coupon_code, subtotal)

        # Get shipping option
        shipping_option, shipping_cost = _get_shipping_option(shipping_option_id)
        if shipping_option_id and not shipping_option:
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
            # Validate quantities before creating order
            order_items = []
            for item in cart_items:
                if item.quantity <= 0:
                    logger.warning(f"Skipping cart item with invalid quantity: {item.id}")
                    continue
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        quantity=item.quantity
                    )
                )
            
            if order_items:
                OrderItem.objects.bulk_create(order_items)
            else:
                messages.error(request, "No valid items in cart.")
                return redirect("cart_view")
            
            cart_items.delete()
            transaction.on_commit(lambda: order_submitted.send(sender=Order, order=order, request=request))

        return redirect("order_success")

    # GET: create a PaymentIntent for the current subtotal
    intent = _create_stripe_intent(subtotal, request.session.session_key, is_guest=not request.user.is_authenticated)
    if not intent:
        messages.error(request, "Payment system error. Please try again.")
        return redirect("cart_view")

    # Validate Stripe publishable key
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY.strip() if settings.STRIPE_PUBLISHABLE_KEY else ""
    if not stripe_public_key or not stripe_public_key.startswith(('pk_test_', 'pk_live_')):
        logger.error(f"Invalid Stripe publishable key format: {stripe_public_key[:20] if stripe_public_key else 'empty'}...")
        messages.error(request, "Payment system configuration error. Please contact support.")
        return redirect("cart_view")
    
    return render(
        request,
        "checkout.html",
        {
            "categories": categories,
            "selected_category": None,
            "cart_count": cart_count,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "shipping_cost": shipping_cost,
            "coupon_applied": coupon_applied,
            "coupon_error": coupon_error,
            "coupon_code": coupon_code,
            "shipping_options": ShippingOption.objects.all().order_by("price", "name"),
            "client_secret": intent.client_secret,
            "stripe_public_key": stripe_public_key,
            "is_guest": not request.user.is_authenticated,
        },
    )
# =============================================================================
# Guest checkout (explicit guest page)
# =============================================================================

@require_http_methods(["GET", "POST"])
def guest_checkout_view(request: HttpRequest) -> HttpResponse:
    _ensure_session(request)
    cart_qs = CartItem.objects.filter(session_key=request.session.session_key).select_related("product")
    
    if not cart_qs.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart_view")

    subtotal = _compute_subtotal(cart_qs)
    discount = Decimal("0.00")
    coupon_applied = None
    coupon_error = None
    shipping_cost = Decimal("0.00")
    total = None
    coupon_code = ""

    if request.method == "POST":
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

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect("guest_checkout")

        # Process coupon
        subtotal, discount, coupon_applied, coupon_error = _process_coupon(coupon_code, subtotal)

        # Get shipping option
        shipping_option, shipping_cost = _get_shipping_option(shipping_option_id)
        if shipping_option_id and not shipping_option:
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
            # Validate quantities before creating order
            order_items = []
            for item in cart_qs:
                if item.quantity <= 0:
                    logger.warning(f"Skipping cart item with invalid quantity: {item.id}")
                    continue
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        quantity=item.quantity
                    )
                )
            
            if order_items:
                OrderItem.objects.bulk_create(order_items)
            else:
                messages.error(request, "No valid items in cart.")
                return redirect("cart_view")
            
            cart_qs.delete()
            transaction.on_commit(lambda: order_submitted.send(sender=Order, order=order, request=request))

        return redirect("order_success")

    # GET: create a PaymentIntent
    intent = _create_stripe_intent(subtotal, request.session.session_key, is_guest=True)
    if not intent:
        messages.error(request, "Payment system error. Please try again.")
        return redirect("cart_view")

    # Validate Stripe publishable key
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY.strip() if settings.STRIPE_PUBLISHABLE_KEY else ""
    if not stripe_public_key or not stripe_public_key.startswith(('pk_test_', 'pk_live_')):
        logger.error(f"Invalid Stripe publishable key format: {stripe_public_key[:20] if stripe_public_key else 'empty'}...")
        messages.error(request, "Payment system configuration error. Please contact support.")
        return redirect("cart_view")
    
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
            "coupon_code": coupon_code,
            "client_secret": intent.client_secret,
            "shipping_options": ShippingOption.objects.all().order_by("price", "name"),
            "stripe_public_key": stripe_public_key,
        },
    )


# =============================================================================
# Stripe webhook
# =============================================================================

@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
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
    except stripe_error.SignatureVerificationError as e:
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

        # NOTE: This webhook creates an Order without OrderItem-и.
        # If you need OrderItem-и, you should:
        # 1. Store cart items in session metadata when creating PaymentIntent
        # 2. Retrieve line_items from Stripe session
        # 3. Or use a different webhook event that includes product information
        # For now, this is a placeholder that logs the issue
        logger.warning(
            "Order created from Stripe webhook without OrderItem-и for user %s. "
            "Consider storing cart data in session metadata or using line_items from session.",
            user.username
        )
        
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

def payment_success(request: HttpRequest) -> HttpResponse:
    return render(request, "payment_success.html")


def notify(request: HttpRequest, level: int, msg: str) -> HttpResponse:
    messages.add_message(request, level, msg)
    return redirect("home")


def order_success(request: HttpRequest) -> HttpResponse:
    return render(request, "order_success.html")


def terms(request: HttpRequest) -> HttpResponse:
    return render(request, "legal/terms.html")


def privacy(request: HttpRequest) -> HttpResponse:
    return render(request, "legal/privacy.html")


def contact(request: HttpRequest) -> HttpResponse:
    return render(request, "legal/contact.html")

@login_required
def profile_dashboard(request: HttpRequest) -> HttpResponse:
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
    categories = _get_categories()
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
def profile_favorites(request: HttpRequest) -> HttpResponse:
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
    categories = _get_categories()
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
def profile_orders(request: HttpRequest) -> HttpResponse:
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
def profile_details(request: HttpRequest) -> HttpResponse:
    user = request.user
    return render(request, "details.html", {
        "user": user,
        "active_tab": "details",
    })

@login_required
@require_POST
def remove_from_favorites(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.filter(user=request.user, product=product).delete()

    # Prefer going back to the page the user was on (with security check)
    back = request.META.get("HTTP_REFERER")
    if back:
        # Basic security: ensure referer is from same host
        from django.utils.http import url_has_allowed_host_and_scheme
        if url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
            return redirect(back)

    # Fallback to the unified favorites page
    return redirect("profile_favorites")


# =============================================================================
# Health Check & Monitoring
# =============================================================================

def health_check(request: HttpRequest) -> JsonResponse:
    """Health check endpoint for monitoring."""
    from django.db import connection
    from django.core.cache import cache
    
    status = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status["checks"]["database"] = "ok"
    except Exception as e:
        status["status"] = "unhealthy"
        status["checks"]["database"] = f"error: {str(e)}"
    
    # Cache check (if Redis/Memcached is configured)
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            status["checks"]["cache"] = "ok"
        else:
            status["checks"]["cache"] = "not_configured"
    except Exception:
        status["checks"]["cache"] = "not_configured"
    
    # Stripe check
    try:
        if settings.STRIPE_SECRET_KEY:
            status["checks"]["stripe"] = "configured"
        else:
            status["checks"]["stripe"] = "not_configured"
    except Exception:
        status["checks"]["stripe"] = "error"
    
    http_status = 200 if status["status"] == "healthy" else 503
    return JsonResponse(status, status=http_status)


# =============================================================================
# Error Handlers
# =============================================================================

def handler404(request: HttpRequest, exception) -> HttpResponse:
    """Custom 404 error handler."""
    return render(request, '404.html', status=404)

def handler500(request: HttpRequest) -> HttpResponse:
    """Custom 500 error handler."""
    return render(request, '500.html', status=500)