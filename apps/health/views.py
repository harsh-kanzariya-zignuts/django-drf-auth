import logging

from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Lightweight health check endpoint for Docker/load balancer probes.
    Returns 200 if all critical services are reachable, 503 otherwise.
    """
    checks = {}
    is_healthy = True

    # --- Database check ---
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except OperationalError as e:
        logger.error("Health check: database unreachable — %s", e)
        checks["database"] = "unavailable"
        is_healthy = False

    # --- Cache / Redis check ---
    try:
        cache.set("health_check_probe", "1", timeout=5)
        result = cache.get("health_check_probe")
        if result == "1":
            checks["cache"] = "ok"
        else:
            raise ValueError("Cache read returned unexpected value")
    except Exception as e:
        logger.error("Health check: cache unreachable — %s", e)
        checks["cache"] = "unavailable"
        is_healthy = False

    status = 200 if is_healthy else 503
    return JsonResponse(
        {"status": "ok" if is_healthy else "degraded", "checks": checks}, status=status
    )
