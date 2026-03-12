# django_app/apps/core/services/contentsafety.py
"""
Azure AI Content Safety wrapper.
Moderates user-supplied text before processing.
Falls back gracefully if the service is not configured.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def moderate_text(text: str) -> tuple[bool, str]:
    """
    Returns (is_safe: bool, reason: str).
    If Content Safety is not configured, passes through (safe=True).
    """
    endpoint = getattr(settings, 'CONTENT_SAFETY_ENDPOINT', None)
    key = getattr(settings, 'CONTENT_SAFETY_KEY', None)

    if not endpoint or not key or 'your-' in (endpoint or ''):
        logger.info("[Content Safety] Not configured — skipping moderation (dev mode).")
        return True, "Content Safety not configured"

    try:
        from azure.ai.contentsafety import ContentSafetyClient
        from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
        from azure.core.credentials import AzureKeyCredential

        client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        request = AnalyzeTextOptions(text=text[:1000])  # API limit
        response = client.analyze_text(request)

        # Block if any category scores above threshold (2 = low, 4 = medium, 6 = high)
        THRESHOLD = 4
        for item in response.categories_analysis:
            if item.severity is not None and item.severity >= THRESHOLD:
                reason = f"{item.category} content detected (severity: {item.severity})"
                logger.warning(f"[Content Safety] BLOCKED: {reason}")
                return False, reason

        logger.info("[Content Safety] Text passed moderation.")
        return True, "OK"

    except ImportError:
        logger.warning("[Content Safety] azure-ai-contentsafety package not installed. Skipping.")
        return True, "Package not installed"
    except Exception as e:
        logger.error(f"[Content Safety] Error during moderation: {str(e)}")
        # Fail open — don't block users if the safety service is down
        return True, f"Moderation error (fail-open): {str(e)}"
