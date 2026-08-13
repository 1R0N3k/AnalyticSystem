from django.contrib import admin

from .models import Customer

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'city')
    list_filter = ('city',)
    search_fields = ('name', 'surname', 'email')
    ordering = ('-id',)

    list_display_links = ('name', 'surname')
