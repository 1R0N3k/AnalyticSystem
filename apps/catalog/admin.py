from django.contrib import admin
from .models import Category, Product
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cost')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('-id',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category')
        }),
        ('Финансы', {
            'fields': ('price', 'cost'),
            'classes': ('collapse',)
        }),
    )