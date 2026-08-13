from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('api/revenue/', views.RevenueView.as_view(), name='revenue'),
    path('api/top-products/', views.TopProductsView.as_view(), name='top_products'),
    path('api/average-check/', views.AverageCheckView.as_view(), name='average_check'),
    path('api/customers-by-city/', views.CustomersByCityView.as_view(), name='customers_by_city'),
    path('api/margin/', views.MarginView.as_view(), name='margin'),
    path('api/margin-by-day/', views.MarginByDayView.as_view(), name='margin_by_day'),
    path('api/abc-analysis/', views.ABCAnalysisView.as_view(), name='abc_analysis'),
    path('api/funnel/', views.FunnelView.as_view(), name='funnel'),
    path('api/revenue-by-day-of-week/', views.RevenueByDayOfWeekView.as_view(), name='revenue_by_day_of_week'),
    path('api/revenue-by-hour/', views.RevenueByHourView.as_view(), name='revenue_by_hour'),
    path('api/revenue-by-months/', views.RevenueByMonthView.as_view(), name='revenue_by_months'),
    path('api/top-customers/', views.TopCustomersView.as_view(), name='top_customers'),
]
