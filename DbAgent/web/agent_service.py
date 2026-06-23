"""
Agent pipeline service — wraps the existing DbAgent modules for the web interface.

Provides the 3-step pipeline (generate SQL → execute → summarise) as
reusable functions callable from Django views.
"""
import traceback

from prompt_templates import SQL_GENERATION_PROMPT, SUMMARY_PROMPT, DB_SCHEMA
from llm_client import (
    query_ollama, extract_sql_from_response, wait_for_ollama, pull_model
)
from db_connector import execute_sql_query


def format_rows(rows: list[tuple], max_rows: int = 5) -> str:
    """Format rows for the summary prompt."""
    if not rows:
        return "[]"
    lines = []
    for row in rows[:max_rows]:
        lines.append(str(row))
    return "\n".join(lines)


def check_connections() -> dict:
    """Check Ollama and database connectivity. Returns status dict."""
    result = {
        "ollama": False,
        "db": False,
        "model_loaded": False,
    }
    # Check Ollama
    ollama_ok = wait_for_ollama()
    result["ollama"] = ollama_ok

    if ollama_ok:
        # Check model
        from llm_client import OLLAMA_MODEL
        result["model_name"] = OLLAMA_MODEL

    # Check DB
    try:
        rows, _ = execute_sql_query("SELECT 1;")
        result["db"] = rows is not None and len(rows) > 0
    except Exception:
        result["db"] = False

    return result


def pull_ollama_model() -> dict:
    """Load the Ollama model if not already present."""
    success = pull_model()
    return {"success": success}


def run_pipeline(user_query: str) -> dict:
    """
    Execute the full 3-step agent pipeline.

    Returns a dict with keys:
        success: bool
        sql: str | None
        rows: list | None
        column_names: list | None
        total_rows: int
        summary: str | None
        error: str | None
        steps: list of completed step names
    """
    result = {
        "success": False,
        "sql": None,
        "rows": None,
        "column_names": None,
        "total_rows": 0,
        "summary": None,
        "error": None,
        "steps": [],
    }

    try:
        # ---- Step 1: Generate SQL ----
        sql_prompt = SQL_GENERATION_PROMPT.format(
            db_schema=DB_SCHEMA,
            user_query=user_query
        )
        llm_response = query_ollama(sql_prompt)

        if not llm_response:
            result["error"] = "Не удалось получить ответ от Ollama."
            return result

        sql = extract_sql_from_response(llm_response)
        if not sql:
            result["error"] = (
                "Не удалось извлечь SQL из ответа модели.\n"
                f"Ответ модели: {llm_response[:300]}..."
            )
            return result

        result["sql"] = sql
        result["steps"].append("sql_generated")

        # ---- Step 2: Execute SQL ----
        try:
            rows, column_names = execute_sql_query(sql)
        except Exception as e:
            # Try to get error explanation from LLM
            error_prompt = (
                f"Пользователь задал вопрос: {user_query}\n"
                f"Был сгенерирован SQL: {sql}\n"
                f"При выполнении произошла ошибка: {e}\n\n"
                f"Объясни пользователю ошибку простым языком на русском."
            )
            error_explanation = query_ollama(error_prompt)
            if error_explanation:
                result["error"] = f"Ошибка БД:\n{error_explanation}"
            else:
                result["error"] = f"Ошибка БД: {e}"
            return result

        total_rows = len(rows)
        result["rows"] = rows[:5]  # first 5 rows
        result["column_names"] = column_names
        result["total_rows"] = total_rows
        result["steps"].append("sql_executed")

        # ---- Step 3: Summarize ----
        summary_prompt = SUMMARY_PROMPT.format(
            user_query=user_query,
            sql_query=sql,
            first_5_rows=format_rows(rows[:5]),
            total_rows=total_rows
        )
        summary = query_ollama(summary_prompt)

        if summary:
            result["summary"] = summary
        else:
            result["summary"] = (
                "Не удалось сгенерировать суммаризацию. "
                "Результаты отображены в таблице выше."
            )

        result["success"] = True
        result["steps"].append("summarized")

    except Exception as e:
        result["error"] = f"{e}\n{traceback.format_exc()}"

    return result