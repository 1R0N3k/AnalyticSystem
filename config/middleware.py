import logging
import time

logger = logging.getLogger("api")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = (time.perf_counter() - start) * 1000

        if not (request.path.startswith("/analytics/") or request.path.startswith("/api/")):
            return response

        user = request.user
        username = user.username if user.is_authenticated else "anon"

        logger.info(
            "%s %s -> %s (%.0fms) user=%s",
            request.method,
            request.path,
            response.status_code,
            duration,
            username,
        )

        return response
