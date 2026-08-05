from django.shortcuts import render

# Create your views here.

from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View

from . import services


class RevenueView(View):
    def get(self, request):
        end_str = request.GET.get('end')
        start_str = request.GET.get('start')
        
        end_date = datetime.fromisoformat(end_str).date() if end_str else datetime.now().date()
        start_date = datetime.fromisoformat(start_str).date() if start_str else end_date - timedelta(days=30)
        
        data = services.get_revenue_data(start_date, end_date)
        return JsonResponse(data, safe=False)


class TopProductsView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        data = services.get_top_products_data(limit)
        return JsonResponse(data, safe=False)


class AverageCheckView(View):
    def get(self, request):
        end_str = request.GET.get('end')
        start_str = request.GET.get('start')
        
        end_date = datetime.fromisoformat(end_str).date() if end_str else datetime.now().date()
        start_date = datetime.fromisoformat(start_str).date() if start_str else end_date - timedelta(days=30)
        
        data = services.get_average_check_data(start_date, end_date)
        return JsonResponse(data)


class CustomersByCityView(View):
    def get(self, request):
        data = services.get_customers_by_city_data()
        return JsonResponse(data, safe=False)