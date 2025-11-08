# 📦 Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.timezone import localtime
from django.http import JsonResponse
# 🕒 Python standard library
from datetime import datetime

# 📦 Local app models and forms
from .models import Product,Category, Cart
from .forms import ProductForm


# 🏠 Home view — accessible only to logged-in users
@login_required(login_url='login')
def home(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    return render(request, 'main/home.html', {
        'products': products,
        'query': query,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    })

@login_required
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user in product.likes.all():
        product.likes.remove(request.user)
        liked = False
    else:
        product.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': product.likes.count()})
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('home')

# 📝 Register view — creates user and logs them in
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Mobile Shopy.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})


# 🔐 Login view — shows register link only during allowed hours
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    current_hour = localtime().hour
    show_register = 8 <= current_hour <= 20

    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST':
        role = request.POST.get('role')
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")

            if role == 'admin' and user.is_staff:
                return redirect('admin_dashboard')
            elif role == 'user':
                return redirect('home')
            else:
                messages.error(request, "You are not authorized as admin.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'main/login.html', {'form': form, 'show_register': show_register})


# 🚪 Logout view — logs out and redirects to login
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# 🛠️ Admin-only view — add new product
@staff_member_required(login_url='login')
def add_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product added successfully!")
        return redirect('admin_dashboard')
    return render(request, 'main/add_product.html', {'form': form})

from django.contrib.admin.views.decorators import staff_member_required
from .models import Product

@staff_member_required(login_url='login')
def admin_dashboard(request):
    products = Product.objects.all()
    return render(request, 'main/admin_dashboard.html', {'products': products})


@login_required
def favorites(request):
    liked_products = request.user.liked_products.all()
    cart_items = Cart.objects.filter(user=request.user)
    cart_products = [item.product for item in cart_items]

    return render(request, 'main/favorites.html', {
        'liked_products': liked_products,
        'cart_products': cart_products
    })

@login_required
def remove_from_cart(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cart')

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'main/cart.html', {'cart_items': cart_items})
@login_required
def profile(request):
    return render(request, 'main/profile.html')

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')  # or 'profile', 'dashboard', etc.
    return redirect('register') 