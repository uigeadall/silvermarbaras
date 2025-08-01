
from .models import Comment
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import stripe
from django.conf import settings
from django.http import  HttpRequest
from django.views.decorators.http import require_POST
import logging
from django.db.models import Case, When
from .models import Rating
from .forms import RatingForm
from django.db.models import Avg
from .models import  Order, OrderItem, ShippingOption

from django.contrib.auth.decorators import login_required
import openai


openai.api_key = "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"
stripe.api_key = settings.STRIPE_SECRET_KEY


logger = logging.getLogger(__name__)

def home(request: HttpRequest):
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    category_slug = request.GET.get('category')  # ✅ new

    # Base queryset
    products = Product.objects.all()

    # Apply category filter
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Apply search filter
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Apply sorting
    if sort == 'price_asc':
        products = products.order_by('discount_price', 'price')
    elif sort == 'price_desc':
        products = products.order_by('-discount_price', '-price')

    # Recently viewed logic
    recently_viewed_ids = [int(pk) for pk in request.session.get('recently_viewed', [])][::-1]
    recently_viewed_display = []
    recently_viewed_full_count = 0
    if recently_viewed_ids:
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recently_viewed_ids)])
        recently_viewed_qs = Product.objects.filter(id__in=recently_viewed_ids).order_by(preserved_order)
        recently_viewed_full_count = recently_viewed_qs.count()
        recently_viewed_display = list(recently_viewed_qs[:5])

    popular_products = Product.objects.order_by('-cart_add_count')[:5]

    context = {
        'products': products,
        'recently_viewed': recently_viewed_display,
        'recently_viewed_full_count': recently_viewed_full_count,
        'categories': Category.objects.all(),
        'favorite_ids': [fav.product.id for fav in Favorite.objects.filter(user=request.user)] if request.user.is_authenticated else [],
        'popular_products': popular_products,
        'sort': sort,
        'query': query,
        'selected_category': selected_category,  # ✅ optional, useful in template
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'home_partial.html', context)

    return render(request, 'home.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'favorites.html', {'favorites': favorites})



@login_required
def remove_from_favorites(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect('favorites_list')







from django.views.decorators.csrf import csrf_exempt  # if needed

@login_required
def cart_view(request):
    print("🛒 CART_VIEW user:", request.user)
    print("🛒 Authenticated:", request.user.is_authenticated)

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    for item in cart_items:
        item.subtotal = item.product.get_discounted_price() * item.quantity

    subtotal = sum(item.subtotal for item in cart_items)

    print("🛒 Cart items count:", cart_items.count())
    for item in cart_items:
        print("🛒", item.product.name, "-", item.quantity)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
    })

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    CartItem.objects.filter(user=request.user, product=product).delete()
    return redirect('cart_view')

def product_list(request):
    selected_category = None
    category_id = request.GET.get('category')
    sort = request.GET.get('sort')

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = list(Product.objects.filter(category=selected_category))
    else:
        products = list(Product.objects.all())

    # Sort using discounted price
    if sort == 'price_asc':
        products.sort(key=lambda p: p.get_discounted_price())
    elif sort == 'price_desc':
        products.sort(key=lambda p: p.get_discounted_price(), reverse=True)

    categories = Category.objects.all()

    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)

    # Preserve original viewing order
    recently_viewed = sorted(
        recently_viewed,
        key=lambda x: recently_viewed_ids.index(x.id)
    )

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'recently_viewed': recently_viewed,
        'sort': sort,
    })



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = Comment.objects.filter(product=product).order_by('-created_at')
    product_images = product.images.all()
    rating_form = None
    categories = Category.objects.all()



    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(user=request.user, product=product).first()
        rating_form = RatingForm(instance=existing_rating)

        if request.method == 'POST':

            value = request.POST.get('value')
            if value:
                rating_form = RatingForm(request.POST, instance=existing_rating)
                if rating_form.is_valid():
                    rating = rating_form.save(commit=False)
                    rating.user = request.user
                    rating.product = product
                    rating.save()


            comment_text = request.POST.get('comment')
            if comment_text and comment_text.strip():
                Comment.objects.create(
                    product=product,
                    user=request.user,
                    text=comment_text.strip()
                )

            return redirect('product_detail', pk=pk)


    average_rating = product.ratings.aggregate(Avg('value'))['value__avg']

    recently_viewed = request.session.get('recently_viewed', [])

    pk = int(pk)  # ensure it's an integer
    recently_viewed = [int(i) for i in recently_viewed if str(i).isdigit()]

    if pk in recently_viewed:
        recently_viewed.remove(pk)
    recently_viewed.insert(0, pk)

    # Optional: Limit to last 10 viewed
    recently_viewed = recently_viewed[:10]

    request.session['recently_viewed'] = recently_viewed

    recently_viewed_products = Product.objects.filter(pk__in=recently_viewed).exclude(pk=product.pk)

    context = {
        'product': product,
        'product_images': product_images,
        'comments': comments,
        'favorite_ids': [fav.product.id for fav in Favorite.objects.filter(user=request.user)] if request.user.is_authenticated else [],
        'rating_form': rating_form,
        'average_rating': average_rating,
        'recently_viewed_products': recently_viewed_products,
        'categories': categories,
'selected_category': product.category
    }

    return render(request, 'product_detail.html', context)





from django.http import HttpResponse
from django.shortcuts import redirect


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    product.cart_add_count += 1
    product.save()


    quantity = 1
    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity  # ✅ increment instead of replace
        cart_item.save()

    messages.success(request, "✅ Product added to cart!")
    return redirect('product_detail', pk=pk)
@require_POST
def update_cart_quantity(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to update your cart.")
        return redirect('login')

    try:
        quantity = int(request.POST.get('quantity'))
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "Invalid quantity.")
        return redirect('cart_view')

    cart_item = CartItem.objects.filter(user=request.user, product_id=pk).first()
    if cart_item:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart updated.")
    else:
        messages.error(request, "Item not found in cart.")

    return redirect('cart_view')


@login_required
def toggle_favorite(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            favorite.delete()

        return redirect('product_detail', pk=pk)


    return JsonResponse({'error': 'Invalid request'}, status=400)




from .models import  CartItem

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from .models import Category, Product, Favorite

def products_by_category(request: HttpRequest, pk):
    category = get_object_or_404(Category, pk=pk)
    sort = request.GET.get('sort')

    products = list(Product.objects.filter(category=category))  # Convert to list for Python sorting

    # 🔽 Sort using discounted price method
    if sort == 'price_asc':
        products.sort(key=lambda p: p.get_discounted_price())
    elif sort == 'price_desc':
        products.sort(key=lambda p: p.get_discounted_price(), reverse=True)

    categories = Category.objects.all()

    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recently_viewed_ids)

    popular_products = Product.objects.order_by('-cart_add_count')[:10]

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'recently_viewed': recently_viewed,
        'popular_products': popular_products,
        'favorite_ids': favorite_ids,
        'sort': sort,
    }

    return render(request, 'home.html', context)
@login_required
def checkout_view(request):


    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    print("🛒 Cart items count:", cart_items.count())
    for item in cart_items:
        print("🛒", item.product.name, "-", item.quantity)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_view')

    # Calculate subtotal
    for item in cart_items:
        item.subtotal = item.product.get_discounted_price() * item.quantity
    subtotal = sum(item.subtotal for item in cart_items)

    if request.method == 'POST':
        print("📦 POST received")
        full_name = request.POST.get('full_name', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_option_id = request.POST.get('shipping_option')
        payment_intent_id = request.POST.get('payment_intent_id')

        if not all([full_name, address, city, postal_code, phone]):
            messages.error(request, "All fields are required.")
            return redirect('checkout')

        # Get shipping option
        shipping_option = None
        if shipping_option_id:
            try:
                shipping_option = ShippingOption.objects.get(id=shipping_option_id)
            except ShippingOption.DoesNotExist:
                messages.error(request, "Invalid shipping option.")
                return redirect('checkout')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            city=city,
            postal_code=postal_code,
            phone=phone,
            shipping_option=shipping_option,
            total_price=subtotal,
        )

        # Add items to order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Clear cart
        cart_items.delete()

        return redirect('order_success')

    # Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=int(subtotal * 100),
        currency='usd',
        metadata={'user_id': request.user.id}
    )

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_options': ShippingOption.objects.all(),
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    })







stripe.api_key = settings.STRIPE_SECRET_KEY



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid Stripe signature: %s", str(e))
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')
        if not customer_email:
            logger.warning("No customer email in Stripe session.")
            return HttpResponse(status=400)

        user = User.objects.filter(email=customer_email).first()
        if not user:
            logger.warning(f"No user found with email: {customer_email}")
            return HttpResponse(status=200)


        order = Order.objects.create(
            user=user,
            stripe_checkout_id=session['id'],
            total=session['amount_total'] / 100
        )


        cart_items = CartItem.objects.filter(user=user).select_related('product')
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
        cart_items.delete()

        logger.info(f"✅ Order #{order.id} created for user {user.username}")

    return HttpResponse(status=200)




def payment_success(request):
    return render(request, 'payment_success.html')

def notify(request, level, msg):
    messages.add_message(request, level, msg)

def order_success(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # You could save this to a model, send a confirmation email, etc.
        print(full_name, email, phone, address)

        messages.success(request, "Your shipping details have been received!")
        return redirect('product_list')  # or show a thank-you page

    return render(request, 'order_success.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai




