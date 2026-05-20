import time
import logging

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response['X-Response-Time'] = f'{duration_ms:.2f}ms'
        if duration_ms > 500:
            logger.warning('Slow request %s %s — %.2fms', request.method, request.path, duration_ms)
        return response
