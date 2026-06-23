"""
Django views for the DbAgent web interface.

Provides:
- index: Main chat-like page
- api_query: POST endpoint to run the agent pipeline
- api_status: GET endpoint to check connectivity
- api_pull_model: POST endpoint to pull the Ollama model
"""
import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .agent_service import run_pipeline, check_connections, pull_ollama_model

logger = logging.getLogger(__name__)


def index(request):
    """Render the main chat interface page."""
    return render(request, 'web/index.html')


def api_status(request):
    """
    GET /api/status
    Returns JSON with connection status for Ollama and PostgreSQL.
    """
    status = check_connections()
    return JsonResponse(status)


@csrf_exempt
def api_pull_model(request):
    """
    POST /api/pull-model
    Triggers Ollama model pull. Returns JSON result.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    result = pull_ollama_model()
    return JsonResponse(result)


@csrf_exempt
def api_query(request):
    """
    POST /api/query
    Runs the full 3-step agent pipeline on the provided query text.

    Expects JSON body: {"query": "user question"}
    Returns JSON with pipeline results.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_query = body.get('query', '').strip()
    if not user_query:
        return JsonResponse(
            {"error": "Пожалуйста, введите запрос."}, status=400
        )

    logger.info(f"Processing query: {user_query[:100]}")

    # Run the full pipeline — this may take a while
    result = run_pipeline(user_query)

    return JsonResponse(result)