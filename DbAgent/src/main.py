import sys
import traceback

from prompt_templates import SQL_GENERATION_PROMPT, SUMMARY_PROMPT, DB_SCHEMA
from llm_client import query_ollama, extract_sql_from_response, wait_for_ollama, pull_model
from db_connector import execute_sql_query


def format_rows(rows: list[tuple], column_names: list[str]) -> str:
    """Форматирует строки результата для передачи в промпт суммаризации."""
    if not rows:
        return "[]"

    lines = []
    for i, row in enumerate(rows[:5]):  # только первые 5 строк
        lines.append(str(row))

    return "\n".join(lines)


def run_agent():
    print("=" * 60)
    print("  DB Agent — AI-помощник для работы с PostgreSQL")
    print("  Модель: Ollama (qwen2.5-coder:7B)")
    print("  Для выхода введите: exit, quit или Ctrl+C")
    print("=" * 60)
    print()

    # Ожидаем Ollama
    if not wait_for_ollama():
        print("[ОШИБКА] Не удалось подключиться к Ollama. Завершение.")
        sys.exit(1)

    # Загружаем модель, если ещё не загружена
    if not pull_model():
        print("[ОШИБКА] Не удалось загрузить модель. Завершение.")
        sys.exit(1)

    while True:
        try:
            user_query = input("\nВведите ваш запрос: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ("exit", "quit"):
                print("До свидания!")
                break

            # Шаг 1: Генерация SQL через LLM
            print("\n[1/3] Генерирую SQL-запрос...")
            sql_prompt = SQL_GENERATION_PROMPT.format(
                db_schema=DB_SCHEMA,
                user_query=user_query
            )
            llm_response = query_ollama(sql_prompt)

            if not llm_response:
                print("[ОШИБКА] Не удалось получить ответ от Ollama.")
                continue

            sql = extract_sql_from_response(llm_response)
            if not sql:
                print("[ОШИБКА] Не удалось извлечь SQL из ответа модели.")
                print(f"Ответ модели: {llm_response[:200]}...")
                continue

            print(f"  SQL: {sql}")

            # Шаг 2: Выполнение SQL
            print("\n[2/3] Выполняю SQL-запрос к БД...")
            try:
                rows, column_names = execute_sql_query(sql)
            except Exception as e:
                print(f"[ОШИБКА БД] {e}")
                # Пытаемся получить объяснение ошибки от LLM
                error_prompt = (
                    f"Пользователь задал вопрос: {user_query}\n"
                    f"Был сгенерирован SQL: {sql}\n"
                    f"При выполнении произошла ошибка: {e}\n\n"
                    f"Объясни пользователю ошибку простым языком на русском."
                )
                error_explanation = query_ollama(error_prompt)
                if error_explanation:
                    print(f"\n[Объяснение ошибки]: {error_explanation}")
                else:
                    print(f"\n[Ошибка]: {e}")
                continue

            total_rows = len(rows)
            first_5 = rows[:5]
            print(f"  Получено строк: {total_rows}")

            # Шаг 3: Суммаризация результата
            print("\n[3/3] Суммаризирую результат...")
            summary_prompt = SUMMARY_PROMPT.format(
                user_query=user_query,
                sql_query=sql,
                first_5_rows=format_rows(first_5, column_names),
                total_rows=total_rows
            )
            summary = query_ollama(summary_prompt)

            print("\n" + "=" * 60)
            print("  ОТВЕТ:")
            print("=" * 60)
            if summary:
                print(summary)
            else:
                print("Не удалось сгенерировать суммаризацию. Вывожу сырые данные:")
                print(f"  Всего строк: {total_rows}")
                for i, row in enumerate(first_5):
                    print(f"  {i + 1}. {row}")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"\n[НЕОЖИДАННАЯ ОШИБКА] {e}")
            traceback.print_exc()
            continue


if __name__ == "__main__":
    run_agent()