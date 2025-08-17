import sqlite3
import os

DB_NAME = "prompt_gallery.db"

def initialize_database():
    """
    데이터베이스와 'favorites' 테이블을 초기화합니다.
    테이블이 이미 존재하면 아무 작업도 수행하지 않습니다.
    """
    # 데이터베이스 파일이 프로젝트 루트에 생성되도록 경로 설정
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', DB_NAME)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # favorites 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT NOT NULL UNIQUE,
        full_prompt TEXT,
        classified_data TEXT,
        favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"데이터베이스 '{db_path}'가 성공적으로 초기화되었습니다.")