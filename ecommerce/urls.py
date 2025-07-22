from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/remove/<int:pk>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('favorites/add/<int:pk>/', views.add_to_favorites, name='add_to_favorites'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('category/<int:pk>/', views.products_by_category, name='products_by_category'),
path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
path('success/', views.success_view, name='success'),







]
