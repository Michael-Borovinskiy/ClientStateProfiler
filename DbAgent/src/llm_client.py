import requests
import json
import os
import time
from dotenv import load_dotenv
from pathlib import Path

current_dir = Path(__file__).resolve().parent
dotenv_path = current_dir.parent / 'config' / '.env'
load_dotenv(dotenv_path=dotenv_path)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
MAX_RETRIES = 3
RETRY_DELAY = 2


def query_ollama(prompt: str, system_prompt: str = "") -> str | None:
    """
    Отправляет запрос к Ollama API и возвращает текст ответа.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"[LLM] Ошибка запроса к Ollama (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None


def extract_sql_from_response(response: str) -> str | None:
    """
    Извлекает SQL-запрос из ответа LLM.
    Ищет блок ```sql ... ``` или просто текст, начинающийся с SELECT/INSERT/UPDATE/DELETE.
    """
    if not response:
        return None

    # Поиск в markdown-блоке ```sql ... ```
    if "```sql" in response.lower():
        start = response.lower().find("```sql") + 6
        end = response.find("```", start)
        if end != -1:
            sql = response[start:end].strip()
            return sql

    # Поиск в markdown-блоке ``` ... ```
    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            sql = response[start:end].strip()
            return sql

    # Если просто SQL-команда
    for kw in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH"]:
        if response.upper().strip().startswith(kw):
            # Берём первую строку или всё до точки с запятой
            return response.strip()

    return None


def wait_for_ollama() -> bool:
    """Ожидает, пока Ollama станет доступен."""
    url = f"{OLLAMA_BASE_URL}/api/tags"
    for attempt in range(30):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                print("[LLM] Ollama доступен.")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"[LLM] Ожидание Ollama... (попытка {attempt + 1}/30)")
        time.sleep(3)
    return False


def pull_model() -> bool:
    """Загружает указанную модель в Ollama, если её ещё нет."""
    print(f"[LLM] Проверяю наличие модели {OLLAMA_MODEL}...")
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        resp = requests.get(url, timeout=10)
        models = resp.json().get("models", [])
        for m in models:
            if OLLAMA_MODEL in m.get("name", ""):
                print(f"[LLM] Модель {OLLAMA_MODEL} уже загружена.")
                return True
    except Exception as e:
        print(f"[LLM] Не удалось проверить список моделей: {e}")

    print(f"[LLM] Загружаю модель {OLLAMA_MODEL} (может занять несколько минут)...")
    url = f"{OLLAMA_BASE_URL}/api/pull"
    try:
        resp = requests.post(url, json={"name": OLLAMA_MODEL}, timeout=300)
        if resp.status_code == 200:
            print(f"[LLM] Модель {OLLAMA_MODEL} успешно загружена.")
            return True
        else:
            print(f"[LLM] Ошибка загрузки модели: {resp.status_code} {resp.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[LLM] Ошибка при загрузке модели: {e}")
        return False
