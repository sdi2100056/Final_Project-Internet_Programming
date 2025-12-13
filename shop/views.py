from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import (Product, Category, Cart, CartItem, Rating,
                     UserProfile, Wishlist, ViewHistory, Order, OrderItem)
from .forms import UserRegisterForm, UserProfileForm, ProductFilterForm


def home(request):
    """Αρχική σελίδα"""
    context = {
        'featured_products': Product.objects.filter(is_active=True).order_by('-created_at')[:8],
        'categories': Category.objects.filter(parent=None),
    }
    return render(request, 'home.html', context)


def product_list(request):
    """Λίστα προϊόντων με φίλτρα"""
    products = Product.objects.filter(is_active=True)
    form = ProductFilterForm(request.GET)

    # Αναζήτηση
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(color__icontains=search_query)
        )

    # Φίλτρα
    category_id = request.GET.get('category', '').strip()
    if category_id:
        products = products.filter(category_id=category_id)

    min_price = request.GET.get('min_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    size = request.GET.get('size', '').strip()
    if size:
        products = products.filter(size=size)

    product_type = request.GET.get('type', '').strip()
    if product_type:
        products = products.filter(type=product_type)

    season = request.GET.get('season', '').strip()
    if season:
        products = products.filter(season=season)

    color = request.GET.get('color', '').strip()
    if color:
        products = products.filter(color__icontains=color)

    # Ταξινόμηση
    sort_by = request.GET.get('sort_by', '').strip()
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product_list.html', {
        'page_obj': page_obj,
        'form': form,
        'search_query': search_query,
        'categories': Category.objects.all(),
    })


def product_detail(request, slug):
    """Λεπτομέρειες προϊόντος"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    product.increment_views()

    if request.user.is_authenticated:
        ViewHistory.objects.get_or_create(user=request.user, product=product)

    ratings = product.ratings.all().order_by('-created_at')
    user_rating = ratings.filter(user=request.user).first() if request.user.is_authenticated else None

    # Similar products
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'ratings': ratings,
        'user_rating': user_rating,
        'avg_rating': product.average_rating(),
        'similar_products': similar_products,
    })


def register(request):
    """Εγγραφή χρήστη"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            Cart.objects.create(user=user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    """Σύνδεση"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'login.html')


def user_logout(request):
    """Αποσύνδεση"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@login_required
def profile(request):
    """Προφίλ χρήστη"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard(request):
    """Dashboard χρήστη"""
    context = {
        'recent_views': ViewHistory.objects.filter(user=request.user).select_related('product')[:10],
        'wishlist': Wishlist.objects.filter(user=request.user).select_related('product')[:10],
        'recent_ratings': Rating.objects.filter(user=request.user).select_related('product')[:10],
        'recent_orders': Order.objects.filter(user=request.user).prefetch_related('items__product')[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required
def cart_view(request):
    """Καλάθι"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@csrf_exempt
def add_to_cart(request, product_id):
    """Προσθήκη στο καλάθι - ΔΙΟΡΘΩΜΕΝΟ"""
    # Manual έλεγχος αν είναι logged in
    if not request.user.is_authenticated:
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': 'Not authenticated'}, status=401)
        else:
            return redirect(f'/login/?next=/cart/add/{product_id}/')

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': cart.get_items_count(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@login_required
def update_cart(request, item_id):
    """Ενημέρωση ποσότητας στο καλάθι (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    cart = Cart.objects.get(user=request.user)
    return JsonResponse({
        'success': True,
        'cart_total': float(cart.get_total()),
        'item_subtotal': float(cart_item.get_subtotal()) if quantity > 0 else 0,
    })


@csrf_exempt
@login_required
def remove_from_cart(request, item_id):
    """Αφαίρεση από καλάθι (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    cart = Cart.objects.get(user=request.user)
    return JsonResponse({
        'success': True,
        'message': 'Product removed from cart',
        'cart_count': cart.get_items_count(),
        'cart_total': float(cart.get_total()),
    })


@login_required
def checkout(request):
    """Checkout"""
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')

    if request.method == 'POST':
        # Δημιουργία παραγγελίας
        order = Order.objects.create(
            user=request.user,
            total=cart.get_total(),
            shipping_address=f"{request.user.profile.address}, {request.user.profile.city}"
        )

        # Δημιουργία order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Καθαρισμός καλαθιού
        cart.items.all().delete()

        messages.success(request, f'Order #{order.id} completed successfully!')
        return redirect('dashboard')

    return render(request, 'checkout.html', {'cart': cart})


@csrf_exempt
@login_required
def add_rating(request, product_id):
    """Προσθήκη rating (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    rating_value = int(request.POST.get('rating', 0))
    review_text = request.POST.get('review', '')

    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'success': False, 'message': 'Invalid rating'})

    rating, created = Rating.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={'rating': rating_value, 'review': review_text}
    )

    return JsonResponse({
        'success': True,
        'message': 'Your rating has been saved!',
        'avg_rating': product.average_rating(),
        'rating_count': product.ratings.count(),
    })


@csrf_exempt
@login_required
def toggle_wishlist(request, product_id):
    """Toggle wishlist (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        in_wishlist = False
        message = 'Removed from favorites'
    else:
        Wishlist.objects.create(user=request.user, product=product)
        in_wishlist = True
        message = 'Added to favorites'

    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'message': message,
    })