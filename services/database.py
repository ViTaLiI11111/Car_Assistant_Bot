import os
import psycopg2
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Не знайдено DATABASE_URL. Перевірте ваш .env файл.")


def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Помилка підключення до PostgreSQL: {e}")
        return None


def initialize_db():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_cases (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                telegram_photo_id TEXT NOT NULL,
                car_brand TEXT,
                damage_description TEXT,
                estimated_cost_min INTEGER,
                estimated_cost_max INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
        conn.close()
        logger.info("База даних успішно ініціалізована.")


def add_user_case(case_data: dict):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO user_cases (user_id, telegram_photo_id, car_brand, damage_description, estimated_cost_min, estimated_cost_max)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                case_data.get('user_id'),
                case_data.get('telegram_photo_id'),
                case_data.get('car_brand'),
                case_data.get('damage_description'),
                case_data.get('estimated_cost_min'),
                case_data.get('estimated_cost_max')
            ))
            conn.commit()
        conn.close()


def get_user_case_by_page(user_id: int, page: int = 1) -> tuple[dict | None, int]:
    offset = page - 1
    conn = get_db_connection()
    if not conn:
        return None, 0

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(id) FROM user_cases WHERE user_id = %s", (user_id,))
            total_items = cur.fetchone()[0]

            if total_items == 0:
                return None, 0

            cur.execute("""
                SELECT id, telegram_photo_id, car_brand, damage_description, estimated_cost_min, estimated_cost_max, created_at
                FROM user_cases
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1 OFFSET %s
            """, (user_id, offset))

            case_row = cur.fetchone()

            if not case_row:
                return None, total_items

            columns = [desc[0] for desc in cur.description]
            case_dict = dict(zip(columns, case_row))
            return case_dict, total_items
    finally:
        conn.close()