from datetime import date, datetime, timedelta
from functools import wraps

from django.http import JsonResponse
from django.views import View

from apps.auth_api.mixins import TokenRequiredMixin

from . import services

DEFAULT_RANGE_DAYS = 30


class BadRequestError(Exception):
    """Ошибка валидации параметров запроса."""


def _bad_request(message: str) -> JsonResponse:
    return JsonResponse({"success": False, "error": message}, status=400)


def _handle_bad_request(view_method):
    @wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        try:
            return view_method(self, request, *args, **kwargs)
        except BadRequestError as exc:
            return _bad_request(str(exc))

    return wrapper


def _get_date_range(request) -> tuple[date, date]:
    end_str = request.GET.get("end")
    start_str = request.GET.get("start")

    try:
        end_date = datetime.fromisoformat(end_str).date() if end_str else datetime.now().date()
        start_date = (
            datetime.fromisoformat(start_str).date() if start_str else end_date - timedelta(days=DEFAULT_RANGE_DAYS)
        )
    except ValueError as exc:
        raise BadRequestError("Параметры start/end должны быть датами в формате YYYY-MM-DD") from exc

    return start_date, end_date


def _get_limit(request, default: int) -> int:
    raw = request.GET.get("limit")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise BadRequestError("Параметр limit должен быть целым числом") from exc


class RevenueView(TokenRequiredMixin, View):
    required_role = "analyst"

    @_handle_bad_request
    def get(self, request):
        start_date, end_date = _get_date_range(request)
        data = services.get_revenue_data(start_date, end_date)
        return JsonResponse(data, safe=False)


class TopProductsView(TokenRequiredMixin, View):
    required_role = "analyst"

    @_handle_bad_request
    def get(self, request):
        limit = _get_limit(request, 10)
        data = services.get_top_products_data(limit)
        return JsonResponse(data, safe=False)


class AverageCheckView(TokenRequiredMixin, View):
    required_role = "analyst"

    @_handle_bad_request
    def get(self, request):
        start_date, end_date = _get_date_range(request)
        data = services.get_average_check_data(start_date, end_date)
        return JsonResponse(data)


class CustomersByCityView(TokenRequiredMixin, View):
    required_role = "analyst"

    def get(self, request):
        data = services.get_customers_by_city_data()
        return JsonResponse(data, safe=False)


class MarginView(TokenRequiredMixin, View):
    required_role = "manager"

    @_handle_bad_request
    def get(self, request):
        start_date, end_date = _get_date_range(request)
        margin = services.get_margin_summary(start_date, end_date)
        data = margin.model_dump()
        return JsonResponse(data, safe=False)


class MarginByDayView(TokenRequiredMixin, View):
    required_role = "manager"

    @_handle_bad_request
    def get(self, request):
        start_date, end_date = _get_date_range(request)
        margins = services.get_margin_by_day(start_date, end_date)
        data = [item.model_dump() for item in margins]
        return JsonResponse(data, safe=False)


class ABCAnalysisView(TokenRequiredMixin, View):
    required_role = "manager"

    def get(self, request):
        abc_analysis = services.get_abc_analysis()
        data = [item.model_dump() for item in abc_analysis]
        return JsonResponse(data, safe=False)


class FunnelView(TokenRequiredMixin, View):
    required_role = "analyst"

    def get(self, request):
        funnel = services.get_funnel_data()
        data = [item.model_dump() for item in funnel]
        return JsonResponse(data, safe=False)


class RevenueByDayOfWeekView(TokenRequiredMixin, View):
    required_role = "manager"

    def get(self, request):
        revenue = services.get_revenue_by_day_of_week()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)


class RevenueByHourView(TokenRequiredMixin, View):
    required_role = "manager"

    def get(self, request):
        revenue = services.get_revenue_by_hour()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)


class RevenueByMonthView(TokenRequiredMixin, View):
    required_role = "manager"

    def get(self, request):
        revenue = services.get_revenue_by_month()
        data = [item.model_dump() for item in revenue]
        return JsonResponse(data, safe=False)


class TopCustomersView(TokenRequiredMixin, View):
    required_role = "manager"

    @_handle_bad_request
    def get(self, request):
        limit = _get_limit(request, 100)
        customers = services.get_top_customers_data(limit)
        data = [item.model_dump() for item in customers]
        return JsonResponse(data, safe=False)
