import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QAction

from src.prompt_classifier.database import initialize_database
from src.prompt_classifier.ui.gallery_widget import GalleryWidget

class GalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Prompt Gallery")
        self.setGeometry(100, 100, 1280, 720)

        # --- 메뉴 바 설정 ---
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일(&F)")

        open_folder_action = QAction("폴더 열기(&O)...", self)
        # 메뉴 액션을 갤러리 위젯의 함수에 직접 연결
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        # --- 중앙 위젯 설정 ---
        # 갤러리 위젯을 생성하여 중앙에 배치
        self.gallery_widget = GalleryWidget(self)
        self.setCentralWidget(self.gallery_widget)

        # --- 상태 표시줄 설정 ---
        self.status_bar = self.statusBar()
        # 갤러리 위젯의 상태 메시지를 상태 표시줄에 연결
        self.gallery_widget.status_updated.connect(self.status_bar.showMessage)
        self.status_bar.showMessage("준비 완료. '파일 > 폴더 열기'로 시작하세요.")

    def open_folder(self):
        """메뉴의 '폴더 열기'가 클릭되면 갤러리 위젯의 폴더 선택 함수를 호출합니다."""
        self.gallery_widget.open_folder_dialog()

if __name__ == '__main__':
    initialize_database()
    app = QApplication(sys.argv)
    window = GalleryApp()
    window.show()
    sys.exit(app.exec())
