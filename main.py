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
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        # --- 중앙 위젯 설정 ---
        self.gallery_widget = GalleryWidget(self)
        self.setCentralWidget(self.gallery_widget)

        # --- 상태 표시줄 설정 ---
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("준비 완료. 파일 메뉴에서 폴더를 열어주세요.")
        
        # --- 갤러리 위젯의 시그널과 상태 표시줄 업데이트 연결 ---
        self.gallery_widget.status_updated.connect(self.status_bar.showMessage)

    def open_folder(self):
        # 메뉴 액션이 발생하면 갤러리 위젯의 함수를 호출
        self.gallery_widget.open_folder_dialog()

if __name__ == '__main__':
    initialize_database()
    app = QApplication(sys.argv)
    window = GalleryApp()
    window.show()
    sys.exit(app.exec())