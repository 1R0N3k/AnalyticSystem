from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('api/revenue/', views.RevenueView.as_view(), name='revenue'),
    path('api/top-products/', views.TopProductsView.as_view(), name='top_products'),
    path('api/average-check/', views.AverageCheckView.as_view(), name='average_check'),
    path('api/customers-by-city/', views.CustomersByCityView.as_view(), name='customers_by_city'),
]