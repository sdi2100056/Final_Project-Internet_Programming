
from django.contrib import admin
from .models import (Category, Product, UserProfile, Rating, Cart, CartItem, Wishlist, ViewHistory, Order, OrderItem)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    #Admin categories
    list_display = ['name','parent','slug']
    prepopulated_fields = {'slug':('name',)}
    list_filter = ['parent']
    search_fields = ['name' , 'description']

@admin.register(Product)
#Admin products (list display, filters,search, editable fields)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'size', 'type', 'season', 'is_active', 'views']
    list_filter = ['category', 'is_active', 'size', 'type', 'season', 'created_at']
    search_fields = ['name', 'description', 'color']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['views', 'created_at', 'updated_at']

#Fieldset grouping for better organization
fieldsets = [
    ('Basic Informations', {
        'fields': [
            'name', 'slug', 'category', 'description', 'image_url'
        ],
    }),
    ('Characteristics', {
        'fields': ['size', 'type', 'season', 'brand', 'color']
    }),
    ('Status', {
        'fields': ['is_active', 'views', 'created_at', 'updated_at']
    }),
]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    #User Profiles
    list_display = ['user', 'phone', 'city', 'postal_code']
    search_fields = ['user__username' , 'user__email' , 'phone' , 'city']
    list_filter = ['city']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    #Product Ratings
    list_display = ['product' , 'user' , 'rating' , 'created_at']
    list_filter = ['rating' , 'created_at']
    search_fields = ['product__name' , 'user__username' , 'review']
    readonly_fields = ['created_at']

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product' , 'quantity']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    #Shopping carts (display with item and total)
    list_display = ['id' , 'user', 'created_at' , 'get_items_count' , 'get_total']
    search_fields = ['user__username']
    readonly_fields = ['created_at' , 'updated_at']
    inlines = [CartItemInline]

    def get_items_count(self, obj):
        return obj.get_items_count()
    get_items_count.short_description = 'Number of items'

    def get_total(self, obj):
        return f"€{obj.get_total()}"
    get_total.short_description = 'Total'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    #whishlist items (display user or product)
    list_display =['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']

@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    #Product view history and user views
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['viewed_at']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product' , 'quantity', 'price', 'get_subtotal']
    def get_subtotal(self, obj):
        return f"€{obj.get_subtotal()}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    #Admin orders (display with status filter)
    list_display = ['id', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'shipping_address']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
#Organized fieldset structure
    fieldsets = (
        ('Order details', {
            'fields': ('user', 'status', 'total')
        }),
        ('Send', {
            'fields': ('shipping_address',)
        }),
        ('Time details', {
            'fields': ('created_at', 'updated_at')
        }),
    )