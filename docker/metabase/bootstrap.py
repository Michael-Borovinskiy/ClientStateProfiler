#!/usr/bin/env python3
"""Bootstrap Metabase with expertise dashboards.

This script waits for Metabase to become available, completes the initial
setup (if needed), creates the PostgreSQL connection, defines two gauge
questions sourced from the EXPERTISES table, and assembles them into a
dashboard that refreshes every two minutes.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus


def _ensure_requests():
    """Import ``requests`` lazily, installing it if necessary."""

    try:
        import requests  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - runtime dependency installation
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir", "requests"]
        )
        import requests  # type: ignore

    return requests


requests = _ensure_requests()


logging.basicConfig(
    level=os.environ.get("METABASE_BOOTSTRAP_LOG_LEVEL", "INFO"),
    format="[%(asctime)s] %(levelname)s %(message)s",
)
LOGGER = logging.getLogger("metabase_bootstrap")


BASE_URL = os.getenv("METABASE_BASE_URL").rstrip("/")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

METABASE_EMAIL = os.getenv("METABASE_EMAIL")
METABASE_PASSWORD = os.getenv("METABASE_PASSWORD")
METABASE_DB_NAME = os.getenv("METABASE_DB_NAME")
METABASE_DASHBOARD_NAME = os.getenv("METABASE_DASHBOARD_NAME")
METABASE_SITE_NAME = os.getenv("METABASE_SITE_NAME").strip()
REFRESH_SECONDS = int(os.getenv("METABASE_REFRESH_SECONDS"))


CARD_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "Total Expertises Over Time (Monthly)",
        "description": "Total number of expertises over time, grouped by month and status.",
        "sql": """
SELECT
  date_trunc('month', dt_expertise_status) AS month,
  status,
  count(*) AS total_expertises
FROM expertises
GROUP BY
  date_trunc('month', dt_expertise_status),
  status
ORDER BY
  month, status;
        """,
        "display": "line",
        "position": {"col": 0, "row": 8, "sizeX": 24, "sizeY": 16},
        "visualization_settings": {
            "graph.metrics": ["total_expertises"],
            "graph.dimensions": ["month"],
            "graph.series_dimension": "status",
            "graph.show_values": False,
            "graph.x_axis.axis_separator_enabled": "show",
            "graph.x_axis.axis_separator_frequency": "month",
            "graph.y_axis.auto_range": True,
            "graph.y_axis.scale": "linear",
            "graph.y_axis.labels_enabled": True,
            "graph.type": "line",
            "series_settings": {},
            "stack_type": "none",
            "show_goal": False,
            "show_trend": False,
            "show_mini_bar": False,
            "show_values": False,
            "show_labels": True,
            "label_type": "none",
            "line_display_mode": "lines",
            "area_display_mode": "none",
            "show_area": False,
            "curve": "linear",
            "show_dots": True,
            "x_axis_scale": "timeseries",
            "y_axis_scale": "linear",
            "x_axis_offset": 0,
            "y_axis_offset": 0,
            "x_axis_label": "Month",
            "y_axis_label": "Total Expertises",
            "series_colors": {},
            "column_settings": {},
            "show_legend": True,
            "legend_position": "right",
            "legend_text_color": "#333333",
            "legend_background_color": "transparent",
            "legend_border_color": "transparent",
            "legend_font_size": 12,
            "legend_font_weight": "normal",
            "legend_item_spacing": 10,
            "legend_item_width": 100,
            "legend_item_height": 20,
            "legend_item_border_radius": 3,
            "legend_item_background_color": "transparent",
            "legend_item_border_color": "transparent",
            "legend_item_text_color": "#333333",
            "legend_item_font_size": 12,
            "legend_item_font_weight": "normal",
            "legend_item_hover_background_color": "#f5f5f5",
            "legend_item_hover_border_color": "#f5f5f5",
            "legend_item_hover_text_color": "#333333",
            "legend_item_hover_font_size": 12,
            "legend_item_hover_font_weight": "normal",
            "legend_item_active_background_color": "#e0e0e0",
            "legend_item_active_border_color": "#e0e0e0",
            "legend_item_active_text_color": "#333333",
            "legend_item_active_font_size": 12,
            "legend_item_active_font_weight": "normal"
        },
    },
    {
        "name": "Total Expertises",
        "description": "Total number of records in the EXPERTISES table.",
        "sql": "SELECT COUNT(*)::int AS total_expertises FROM expertises;",
        "display": "gauge",
        "position": {"col": 0, "row": 0},
    },
    {
        "name": "Closed Expertises (%)",
        "description": (
            "Percentage of expertise records currently marked as CLOSED."
        ),
        "sql": (
            "SELECT COALESCE(ROUND((COUNT(*) FILTER (WHERE status = 'CLOSED')::numeric / "
            "NULLIF(COUNT(*), 0)) * 100, 2), 0) AS closed_percentage FROM expertises;"
        ),
        "display": "gauge",
        "position": {"col": 12, "row": 0},
    },
]


def api_request(
    method: str,
    endpoint: str,
    *,
    session_id: Optional[str] = None,
    expected_status: Optional[List[int]] = None,
    **kwargs: Any,
):
    """Execute an HTTP request against the Metabase API."""

    expected = set(expected_status or [200, 201, 202, 204])
    url = f"{BASE_URL}{endpoint}"
    headers = kwargs.pop("headers", {})
    if session_id:
        headers["X-Metabase-Session"] = session_id
    if "json" in kwargs:
        headers.setdefault("Content-Type", "application/json")

    response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
    if response.status_code not in expected:
        LOGGER.debug("Response body: %s", response.text)
        raise RuntimeError(
            f"{method} {endpoint} failed (status={response.status_code}): {response.text}"
        )
    return response


def wait_for_metabase(timeout: int = 600) -> None:
    """Wait for the Metabase health endpoint to report ready."""

    LOGGER.info("Waiting for Metabase to become healthy at %s", BASE_URL)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = api_request("GET", "/api/health", expected_status=[200])
            if response.json().get("status") == "ok":
                LOGGER.info("Metabase is healthy.")
                return
        except Exception as exc:  # pragma: no cover - transient container state
            LOGGER.debug("Metabase not ready yet: %s", exc)
        time.sleep(5)

    raise RuntimeError("Metabase did not become ready within the allotted time")


def run_initial_setup() -> str:
    """Complete the first-time Metabase setup and return the session id."""

    LOGGER.info("Running first-time Metabase setup")
    properties_resp = api_request("GET", "/api/session/properties")
    token = properties_resp.json().get("setup-token")
    if not token:
        raise RuntimeError("Unable to fetch setup token from Metabase")

    db_details = {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "ssl": False,
        "tunnel-enabled": False,
        "let-user-control-scheduling": False,
    }

    payload = {
        "token": token,
        "user": {
            "email": METABASE_EMAIL,
            "password": METABASE_PASSWORD,
            "first_name": "ClientState",
            "last_name": "Admin",
        },
        "database": {
            "name": METABASE_DB_NAME,
            "engine": "postgres",
            "details": db_details,
        },
        "prefs": {
            "site_name": "ClientStateProfiler",
            "site_locale": "en",
            "allow_tracking": False,
        },
    }

    response = api_request("POST", "/api/setup", json=payload, expected_status=[200])
    session_id = response.json().get("id")
    if not session_id:
        raise RuntimeError("Setup response did not include a session id")
    LOGGER.info("Metabase setup completed")
    return session_id


def login_or_setup() -> str:
    """Obtain a Metabase session, performing setup if required."""

    # Try login first — handles the case where a previous bootstrap attempt
    # created the user but failed before completing (e.g. due to a bug),
    # leaving the setup-token still present but /api/setup returning 403.
    LOGGER.info("Attempting to log in to Metabase")
    try:
        response = api_request(
            "POST",
            "/api/session",
            json={"username": METABASE_EMAIL, "password": METABASE_PASSWORD},
        )
        session_id = response.json().get("id")
        if session_id:
            LOGGER.info("Authenticated with existing Metabase user")
            return session_id
    except RuntimeError:
        LOGGER.info("Login failed, Metabase may not be configured yet")

    # Login didn't work — check if setup is needed
    properties = api_request("GET", "/api/session/properties").json()
    if properties.get("setup-token"):
        LOGGER.info("Metabase instance not configured yet. Running initial setup")
        return run_initial_setup()

    raise RuntimeError(
        "Failed to authenticate to Metabase using METABASE_EMAIL / "
        "METABASE_PASSWORD. Please ensure these environment variables "
        "match the existing admin credentials or reset the Metabase "
        "application data volume."
    )


def ensure_database(session_id: str) -> int:
    """Create (or reuse) the PostgreSQL database connection."""

    LOGGER.info("Ensuring PostgreSQL database connection exists in Metabase")
    response = api_request("GET", "/api/database", session_id=session_id)
    for database in response.json().get("data", []):
        if database.get("name") == METABASE_DB_NAME:
            LOGGER.info("Reusing existing Metabase database '%s'", METABASE_DB_NAME)
            return database["id"]

    payload = {
        "name": METABASE_DB_NAME,
        "engine": "postgres",
        "details": {
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "dbname": POSTGRES_DB,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "ssl": False,
            "tunnel-enabled": False,
            "let-user-control-scheduling": False,
        },
        "is_full_sync": True,
        "is_on_demand": False,
        "schedules": {
            "cache_field_values": {"enabled": True, "schedule_type": "daily"}
        },
    }

    create_resp = api_request(
        "POST", "/api/database", session_id=session_id, json=payload
    )
    database_id = create_resp.json().get("id")
    if not database_id:
        raise RuntimeError("Failed to create Metabase database connection")
    LOGGER.info("Created Metabase database '%s' (id=%s)", METABASE_DB_NAME, database_id)
    return database_id


def search_resource(session_id: str, resource_type: str, name: str) -> Optional[int]:
    """Return an existing resource id matching ``name``."""

    query = quote_plus(name)
    endpoint = f"/api/search?q={query}&models={resource_type}&archived=false"
    response = api_request("GET", endpoint, session_id=session_id)
    for item in response.json().get("data", []):
        if item.get("model") == resource_type and item.get("name") == name:
            return item.get("id")
    return None


def ensure_card(
    session_id: str, database_id: int, definition: Dict[str, Any]
) -> int:
    """Create or update a Metabase card (question)."""

    payload = {
        "name": definition["name"],
        "description": definition.get("description"),
        "display": definition.get("display", "gauge"),
        "dataset_query": {
            "type": "native",
            "native": {
                "query": definition["sql"],
                "template-tags": {},
            },
            "database": database_id,
        },
        "visualization_settings": definition.get("visualization_settings", {}),
        "collection_id": None,
        "parameters": [],
    }

    existing_id = search_resource(session_id, "card", definition["name"])
    if existing_id:
        LOGGER.info("Updating existing card '%s' (id=%s)", definition["name"], existing_id)
        api_request("PUT", f"/api/card/{existing_id}", session_id=session_id, json=payload)
        return existing_id

    LOGGER.info("Creating new card '%s'", definition["name"])
    response = api_request("POST", "/api/card", session_id=session_id, json=payload)
    card_id = response.json().get("id")
    if not card_id:
        raise RuntimeError(f"Failed to create card {definition['name']}")
    LOGGER.info("Created card '%s' (id=%s)", definition["name"], card_id)
    return card_id


def ensure_dashboard(session_id: str) -> int:
    """Create or reuse the dashboard that hosts the expertise gauges."""

    existing_id = search_resource(session_id, "dashboard", METABASE_DASHBOARD_NAME)
    if existing_id:
        LOGGER.info(
            "Found existing dashboard '%s' (id=%s)", METABASE_DASHBOARD_NAME, existing_id
        )
        return existing_id

    payload = {
        "name": METABASE_DASHBOARD_NAME,
        "description": "Auto-generated overview of expertise health.",
        "parameters": [],
    }
    response = api_request("POST", "/api/dashboard", session_id=session_id, json=payload)
    dashboard_id = response.json().get("id")
    if not dashboard_id:
        raise RuntimeError("Failed to create dashboard")
    LOGGER.info(
        "Created dashboard '%s' (id=%s)", METABASE_DASHBOARD_NAME, dashboard_id
    )
    return dashboard_id


def get_dashboard(session_id: str, dashboard_id: int) -> Dict[str, Any]:
    response = api_request(
        "GET", f"/api/dashboard/{dashboard_id}", session_id=session_id
    )
    return response.json()


def ensure_dashcards(
    session_id: str,
    dashboard_id: int,
    cards: Dict[int, Dict[str, int]],
) -> None:
    """Place the specified cards on the dashboard if missing."""

    def clean_dashcards(dashcards):
        cleaned = []
        for dashcard in dashcards:
            cleaned_dashcard = dashcard.copy()
            cleaned_dashcard.pop("card", None)
            cleaned_dashcard.pop("series", None)
            # The API expects snake_case keys, but returns camelCase keys.
            if "sizeX" in cleaned_dashcard:
                cleaned_dashcard["size_x"] = cleaned_dashcard.pop("sizeX")
            if "sizeY" in cleaned_dashcard:
                cleaned_dashcard["size_y"] = cleaned_dashcard.pop("sizeY")
            cleaned.append(cleaned_dashcard)
        return cleaned

    dashboard = get_dashboard(session_id, dashboard_id)
    existing_dashcards = dashboard.get("ordered_cards", [])
    cleaned_existing_dashcards = clean_dashcards(existing_dashcards)
    existing_card_ids = {dashcard.get("card_id") for dashcard in cleaned_existing_dashcards}

    cards_to_add = []
    for i, (card_id, position) in enumerate(cards.items()):
        if card_id not in existing_card_ids:
            LOGGER.info("Queuing card %s for dashboard placement", card_id)
            cards_to_add.append(
                {
                    "id": -(i + 1),  # Assign a temporary negative ID
                    "card_id": card_id,
                    "col": position.get("col", 0),
                    "row": position.get("row", 0),
                    "size_x": position.get("sizeX", 12),
                    "size_y": position.get("sizeY", 8),
                }
            )

    if not cards_to_add:
        LOGGER.info("All cards already on dashboard")
        return

    updated_dashcards = cleaned_existing_dashcards + cards_to_add
    payload = {"cards": updated_dashcards}

    api_request(
        "PUT",
        f"/api/dashboard/{dashboard_id}/cards",
        session_id=session_id,
        json=payload,
        expected_status=[200],
    )
    LOGGER.info("Placed %d new card(s) on dashboard", len(cards_to_add))


def set_dashboard_refresh(session_id: str, dashboard_id: int) -> None:
    """Attempt to configure the dashboard auto-refresh interval."""

    payload = {"id": dashboard_id, "refresh_interval": REFRESH_SECONDS}
    try:
        api_request(
            "PUT",
            f"/api/dashboard/{dashboard_id}",
            session_id=session_id,
            json=payload,
        )
        LOGGER.info(
            "Configured dashboard auto-refresh interval to %s seconds", REFRESH_SECONDS
        )
    except RuntimeError as exc:
        LOGGER.warning(
            "Unable to set dashboard auto-refresh automatically: %s", exc
        )


def write_dashboard_info(slug: str, dashboard_id: int) -> None:
    """Persist dashboard metadata for operators."""

    output_path = Path(__file__).resolve().parent / "dashboard_info.json"
    payload = {
        "dashboard_id": dashboard_id,
        "slug": slug,
        "url": f"{BASE_URL}/dashboard/{dashboard_id}-{slug}?refresh={REFRESH_SECONDS}",
        "generated_at": int(time.time()),
        "refresh_seconds": REFRESH_SECONDS,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    LOGGER.info("Dashboard info written to %s", output_path)


def main() -> None:
    wait_for_metabase()
    session_id = login_or_setup()
    database_id = ensure_database(session_id)

    card_positions: Dict[int, Dict[str, int]] = {}
    for definition in CARD_DEFINITIONS:
        card_id = ensure_card(session_id, database_id, definition)
        position = {
            "col": definition["position"].get("col", 0),
            "row": definition["position"].get("row", 0),
            "sizeX": definition["position"].get("sizeX", 12),
            "sizeY": definition["position"].get("sizeY", 8),
        }
        card_positions[card_id] = position

    dashboard_id = ensure_dashboard(session_id)
    ensure_dashcards(session_id, dashboard_id, card_positions)
    set_dashboard_refresh(session_id, dashboard_id)

    dashboard = get_dashboard(session_id, dashboard_id)
    slug = dashboard.get("slug", "expertise-health-overview")
    write_dashboard_info(slug, dashboard_id)

    LOGGER.info(
        "Metabase dashboard ready: %s/dashboard/%s-%s?refresh=%s",
        BASE_URL,
        dashboard_id,
        slug,
        REFRESH_SECONDS,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - top-level safety
        LOGGER.error("Metabase bootstrap failed: %s", exc)
        sys.exit(1)