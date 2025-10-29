# ecommerce/context_processors.py
from django.urls import resolve
from django.db.models import Sum
from ecommerce.models import Product, Category, CartItem


def breadcrumbs(request):
    """
    Build simple breadcrumbs:
    - Home
    - Category (when on products_by_category)
    - Category -> Product (when on product_detail)
    """
    trail = [{"name": "Home", "url": "/"}]

    try:
        match = resolve(request.path_info)
    except Exception:
        # If we cannot resolve, don't inject partial breadcrumbs
        return {"breadcrumbs": trail}

    if match.url_name == "products_by_category":
        cat_id = match.kwargs.get("pk")
        category = Category.objects.filter(pk=cat_id).first()
        if category:
            trail.append({"name": category.name, "url": request.path})

    elif match.url_name == "product_detail":
        product_id = match.kwargs.get("pk")
        product = (
            Product.objects.select_related("category")
            .filter(pk=product_id)
            .first()
        )
        if product and product.category:
            trail.append({"name": product.category.name, "url": f"/category/{product.category.pk}/"})
            trail.append({"name": product.name, "url": request.path})

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
