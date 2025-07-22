from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Favorite, Order, CartItem, Comment
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY



from .models import Product, Category

def home(request):
    products = Product.objects.all()[:6]  # Featured products
    categories = Category.objects.all()

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'favorite_ids': favorite_ids,
    })


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

@login_required
def cart_view(request):
    if request.method == 'POST':
        for item_id, quantity in request.POST.items():
            if item_id.startswith('quantity_'):
                pk = item_id.split('_')[1]
                try:
                    cart_item = CartItem.objects.get(user=request.user, product__pk=pk)
                    cart_item.quantity = int(quantity)
                    cart_item.save()
                except CartItem.DoesNotExist:
                    continue
        return redirect('cart_view')

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    for item in cart_items:
        item.subtotal = item.quantity * item.product.price

    total_price = sum(item.subtotal for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    CartItem.objects.filter(user=request.user, product=product).delete()
    return redirect('cart_view')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = Comment.objects.filter(product=product).order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        comment_text = request.POST.get('comment')
        if comment_text:
            Comment.objects.create(
                product=product,
                user=request.user,
                text=comment_text
            )
            return redirect('product_detail', pk=pk)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments
    })





@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('product_detail', pk=pk)

@login_required
def add_to_favorites(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', pk=pk)

@login_required
def checkout_view(request):
    return render(request, 'checkout.html')


def products_by_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'selected_category': category,
    })

@login_required
def create_checkout_session(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.product.price * 100),
                'product_data': {
                    'name': item.product.name,
                },
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )

    return redirect(session.url, code=303)


def success_view(request):
    return render(request, 'success.html')




