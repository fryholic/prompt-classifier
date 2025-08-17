import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
from src.prompt_classifier.database import initialize_database

class GalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 윈도우 기본 설정
        self.setWindowTitle("AI Prompt Gallery")
        self.setGeometry(100, 100, 1280, 720) # x, y, width, height

        # 초기 메시지 설정
        central_widget = QLabel("갤러리 구현 예정. 메뉴에서 폴더를 열어주세요.")
        central_widget.setStyleSheet("font-size: 20px; color: grey;")
        central_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    # 애플리케이션 시작 전 데이터베이스 초기화
    initialize_database()

    app = QApplication(sys.argv)
    window = GalleryApp()
    window.show()
    sys.exit(app.exec())