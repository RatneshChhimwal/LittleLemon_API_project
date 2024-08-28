from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_menuitem_title', 'quantity', 'price')

    def get_menuitem_title(self, obj):
        return obj.menuitem.title
    get_menuitem_title.short_description = 'Menu Item Title'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'delivery_crew', 'status', 'total', 'date')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_menuitem_title', 'quantity', 'price')

    def get_menuitem_title(self, obj):
        return obj.menuitem.title
    get_menuitem_title.short_description = 'Menu Item Title'
