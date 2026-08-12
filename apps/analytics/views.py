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


class MarginView(View):
    def get(self, request):
        end_str = request.GET.get('end')
        start_str = request.GET.get('start')
        
        end_date = datetime.fromisoformat(end_str).date() if end_str else datetime.now().date()
        start_date = datetime.fromisoformat(start_str).date() if start_str else end_date - timedelta(days=30)
        
        margin = services.get_margin_summary(start_date, end_date)
        data = margin.model_dump()
        return JsonResponse(data, safe=False)


class MarginByDayView(View):
    def get(self, request):
        end_str = request.GET.get('end')
        start_str = request.GET.get('start')
        
        end_date = datetime.fromisoformat(end_str).date() if end_str else datetime.now().date()
        start_date = datetime.fromisoformat(start_str).date() if start_str else end_date - timedelta(days=30)
        
        margins = services.get_margin_by_day(start_date, end_date)
        data = [item.model_dump() for item in margins]
        return JsonResponse(data, safe=False)


class ABCAnalysisView(View):
    def get(self, request):
        abc_analysis = services.get_abc_analysis()
        data = [item.model_dump() for item in abc_analysis]
        return JsonResponse(data, safe=False)


class FunnelView(View):
    def get(self, request):
        funnel = services.get_funnel_data()
        data = [item.model_dump() for item in funnel]
        return JsonResponse(data, safe=False)


class RevenueByDayOfWeekView(View):
    def get(self, request):
        revenue = services.get_revenue_by_day_of_week()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)


class RevenueByHourView(View):
    def get(self, request):
        revenue = services.get_revenue_by_hour()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)

    
class RevenueByMonthView(View):
    def get(self, request):
        revenue = services.get_revenue_by_month()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)


class TopCustomersView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 100))
        customers = services.get_top_customers_data()
        data = [item.model_dump() for item in customers]
        return JsonResponse(data, safe=False)