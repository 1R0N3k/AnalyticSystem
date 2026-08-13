from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'cost')

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'created_at', 'status_colored', 'due')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'customer__name', 'customer__surname', 'customer__email')
    ordering = ('-created_at',)
    readonly_fields = ('due',)

    inlines = [OrderItemInline]

    def customer_name(self, obj):
        return f"{obj.customer.name} {obj.customer.surname}"
    customer_name.short_description = 'Клиент'

    def status_colored(self, obj):
        colors = {
            'new': 'blue',
            'paid': 'orange',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'black')
        status_display = dict(Order.Status.choices).get(obj.status, obj.status)
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, status_display)
    status_colored.short_description = 'Статус'

    @admin.action(description='Пометить выбранные заказы как "Доставлен"')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'Успешно обновлено {updated} заказов.')

    actions = ['mark_as_delivered']
