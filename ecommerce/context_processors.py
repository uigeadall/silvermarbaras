# ecommerce/context_processors.py
from django.urls import resolve, reverse
from django.db.models import Sum
from ecommerce.models import Product, Category, CartItem


def breadcrumbs(request):
    """
    Build breadcrumbs for all pages:
    - Home (always first)
    - Category (when on products_by_category or product_detail)
    - Product (when on product_detail)
    - Cart, Checkout, Profile pages, etc.
    """
    try:
        home_url = reverse("home")
    except Exception:
        home_url = "/"
    
    trail = [{"name": "Начало", "url": home_url}]

    try:
        match = resolve(request.path_info)
    except Exception:
        # If we cannot resolve, return just Home
        return {"breadcrumbs": trail}

    url_name = match.url_name

    # Home page - no additional breadcrumbs
    if url_name == "home":
        return {"breadcrumbs": trail}

    # Category page
    if url_name == "products_by_category":
        cat_id = match.kwargs.get("pk")
        category = Category.objects.filter(pk=cat_id).first()
        if category:
            trail.append({"name": category.name, "url": request.path})
        return {"breadcrumbs": trail}

    # Product detail page
    if url_name == "product_detail":
        product_id = match.kwargs.get("pk")
        product = (
            Product.objects.select_related("category")
            .filter(pk=product_id)
            .first()
        )
        if product:
            if product.category:
                trail.append({
                    "name": product.category.name,
                    "url": reverse("products_by_category", kwargs={"pk": product.category.pk})
                })
            # Truncate product name if too long
            product_name = product.name
            if len(product_name) > 50:
                product_name = product_name[:47] + "..."
            trail.append({"name": product_name, "url": request.path})
        return {"breadcrumbs": trail}

    # Cart
    if url_name == "cart_view":
        trail.append({"name": "Количка", "url": request.path})
        return {"breadcrumbs": trail}

    # Checkout
    if url_name in ("checkout", "guest_checkout"):
        trail.append({"name": "Поръчка", "url": request.path})
        return {"breadcrumbs": trail}

    # Order success
    if url_name in ("order_success", "success", "payment_success"):
        trail.append({"name": "Успешна поръчка", "url": request.path})
        return {"breadcrumbs": trail}

    # Favorites
    if url_name in ("favorites_list", "profile_favorites"):
        trail.append({"name": "Любими", "url": request.path})
        return {"breadcrumbs": trail}

    # Profile pages
    if url_name == "profile_dashboard":
        trail.append({"name": "Профил", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "profile_orders":
        trail.append({"name": "Профил", "url": reverse("profile_dashboard")})
        trail.append({"name": "Поръчки", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "profile_details":
        trail.append({"name": "Профил", "url": reverse("profile_dashboard")})
        trail.append({"name": "Детайли", "url": request.path})
        return {"breadcrumbs": trail}

    # Auth pages
    if url_name in ("account_login", "login"):
        trail.append({"name": "Вход", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "account_signup":
        trail.append({"name": "Регистрация", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "register":
        trail.append({"name": "Регистрация", "url": request.path})
        return {"breadcrumbs": trail}

    # Legal pages
    if url_name == "terms":
        trail.append({"name": "Условия", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "privacy":
        trail.append({"name": "Поверителност", "url": request.path})
        return {"breadcrumbs": trail}

    if url_name == "contact":
        trail.append({"name": "Контакт", "url": request.path})
        return {"breadcrumbs": trail}

    # Product list
    if url_name == "product_list":
        trail.append({"name": "Продукти", "url": request.path})
        return {"breadcrumbs": trail}

    # Default: return trail with Home only
    return {"breadcrumbs": trail}


def cart_count(request):
    """
    Return the TOTAL quantity of items in the cart for the current visitor.

    - Authenticated users: sum quantities for rows tied to the user.
    - Anonymous users: ensure a session exists, then sum quantities for rows tied to session_key.
    - Never raises; falls back to 0 if anything goes wrong.
    """
    try:
        if request.user.is_authenticated:
            total = (
                CartItem.objects
                .filter(user=request.user)
                .aggregate(c=Sum("quantity"))
                .get("c") or 0
            )
            return {"cart_count": int(total)}

        # Guest: ensure a session exists so we can track their cart
        if not request.session.session_key:
            request.session.create()

        total = (
            CartItem.objects
            .filter(session_key=request.session.session_key)
            .aggregate(c=Sum("quantity"))
            .get("c") or 0
        )
        return {"cart_count": int(total)}

    except Exception:
        # Never break rendering because of cart issues
        return {"cart_count": 0}
