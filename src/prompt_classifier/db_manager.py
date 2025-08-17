import sqlite3
import os

DB_NAME = "prompt_gallery.db"
db_path = os.path.join(os.path.dirname(__file__), '..', '..', DB_NAME)

def get_db_connection():
    """데이터베이스 연결 객체를 반환합니다."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def add_favorite(image_path: str, full_prompt: str):
    """
    이미지를 즐겨찾기에 추가합니다.
    이미 경로가 존재하면 아무 작업도 수행하지 않습니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO favorites (image_path, full_prompt) VALUES (?, ?)",
            (image_path, full_prompt)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"'{os.path.basename(image_path)}'는 이미 즐겨찾기에 있습니다.")
    finally:
        conn.close()

def remove_favorite(image_path: str):
    """이미지를 즐겨찾기에서 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE image_path = ?", (image_path,))
    conn.commit()
    conn.close()

def is_favorited(image_path: str) -> bool:
    """이미지가 즐겨찾기에 있는지 확인합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE image_path = ?", (image_path,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_all_favorites():
    """모든 즐겨찾기 목록을 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites ORDER BY favorited_at DESC")
    favorites = cursor.fetchall()
    conn.close()
    return favorites

def update_classified_data(image_path: str, classified_data: str):
    """
    특정 이미지의 분류된 프롬프트 데이터를 업데이트합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE favorites SET classified_data = ? WHERE image_path = ?",
        (classified_data, image_path)
    )
    conn.commit()
    conn.close()
    print(f"'{os.path.basename(image_path)}'의 분류 데이터가 업데이트되었습니다.")
