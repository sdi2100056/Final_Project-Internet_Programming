from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import (Product, Category, Cart, CartItem, Rating,
                     UserProfile, Wishlist, ViewHistory, Order, OrderItem)
from .forms import UserRegisterForm, UserProfileForm, ProductFilterForm

def home (request):
    """Home Page"""
    context = {
        'featured_products': Product.objects.filter(is_active=True).order_by('-created_at')[:8],
        'categories': Category.objects.filter(parent = None),
    }
    return render(request,'home.html', context)


def product_list(request):
    """Product List Page with filters"""
    products = Product.objects.filter(is_active=True)
    form = ProductFilterForm(request.GET)

    #Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(color__icontains=search_query)
        )

    #Filters
    if request.GET.get('category'):
        products = products.filter(category_id=request.GET.get('category'))
    if request.GET.get('min_price'):
        products = products.filter(price__gte=request.GET.get('min_price'))
    if request.GET.get('max_price'):
        products = products.filter(price__lte=request.GET.get('max_price'))
    if request.GET.get('size'):
        products = products.filter(size=request.GET.get('size'))
    if request.GET.get('type'):
        products = products.filter(type=request.GET.get('type'))
    if request.GET.get('season'):
        products = products.filter(season=request.GET.get('season'))

    #Sorting
    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    #Pagination
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'product_list.html')


def product_detail(request, slug):
    """Product details"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    product.increment_views()

    if request.user.is_authenticated:
        ViewHistory.objects.get_or_create(user=request.user, product=product)

    ratings = product.ratings.all().order_by('-created_at')
    user_rating = ratings.filter(user=request.user).first() if request.user.is_authenticated else None

    return render(request, 'product_detail.html', {
        'product': product,
        'ratings': ratings,
        'user_rating': user_rating,
        'avg_rating': product.average_rating(),
    })

def register(request):
    """User Registration Page"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            Cart.objects.create(user=user)
            messages.success(request,'The account has been created!')
            return redirect('login')
        else:
            form = UserRegisterForm()
        return render (request, 'register.html', {'form': form})
def user_login(request):
    """User Login Page"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'Welcome back, {user.username}!')
        else:
            messages.error(request, 'Invalid username or password.')
        return render(request, '../panathinaikos_shop/shop/templates/login.html')
def user_logout(request):
    """User Logout Page"""
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

@login_required
def profile(request):
    """User Profile Page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.email = form.cleaned_data['email']
                request.user.save()
                form.save()
                messages.success(request, 'The profiled is updated!')
                return redirect('profile')
        else:
            form = UserProfileForm(instance=profile)

        return render(request, 'profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard(request):
    """Dashboard fo user"""
    context = {
        'recent_views': ViewHistory.objects.filter(user=request.user)[:10],
        'wishlist': Wishlist.objects.filter(user=request.user)[:10],
        'recent_ratings': Rating.objects.filter(user=request.user)[:10],
        'recent_orders': Order.objects.filter(user=request.user)[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required
def cart_view(request):
    """Cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add to cart (AJAX)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to the cart!',
        'cart_count': cart.get_items_count(),
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove from cart (AJAX)"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    cart = Cart.objects.get(user=request.user)
    return JsonResponse({
        'success': True,
        'message': 'Removed from the cart',
        'cart_count': cart.get_items_count(),
    })


@login_required
def checkout(request):
    """Checkout"""
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.warning(request, 'The cart is empty!')
        return redirect('cart')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total=cart.get_total(),
            shipping_address=f"{request.user.profile.address}, {request.user.profile.city}"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()
        messages.success(request, f'Order #{order.id} is completed!')
        return redirect('dashboard')

    return render(request, 'checkout.html', {'cart': cart})


@login_required
@require_POST
def add_rating(request, product_id):
    """Add rating  (AJAX)"""
    product = get_object_or_404(Product, id=product_id)
    rating_value = int(request.POST.get('rating', 0))
    review_text = request.POST.get('review', '')

    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'success': False})

    rating, created = Rating.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={'rating': rating_value, 'review': review_text}
    )

    return JsonResponse({
        'success': True,
        'message': 'The rating is added!',
        'avg_rating': product.average_rating(),
    })
