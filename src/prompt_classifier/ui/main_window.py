# src/prompt_classifier/ui/main_window.py

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction

from src.prompt_classifier.ui.gallery_widget import GalleryWidget
from src.prompt_classifier.ui.favorites_window import FavoritesWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Prompt Gallery")
        self.setGeometry(100, 100, 1280, 720)

        # --- 메뉴 바 설정 ---
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일(&F)")
        
        # --- 즐겨찾기 메뉴 추가 ---
        favorites_menu = menubar.addMenu("즐겨찾기(&V)")

        open_folder_action = QAction("폴더 열기(&O)...", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        # --- 즐겨찾기 창 열기 액션 추가 ---
        open_favorites_action = QAction("즐겨찾기 보기(&F)...", self)
        open_favorites_action.triggered.connect(self.open_favorites_window)
        favorites_menu.addAction(open_favorites_action)
        
        # --- 중앙 위젯 설정 ---
        self.gallery_widget = GalleryWidget(self)
        self.setCentralWidget(self.gallery_widget)

        # --- 상태 표시줄 설정 ---
        self.status_bar = self.statusBar()
        self.gallery_widget.status_updated.connect(self.status_bar.showMessage)
        self.status_bar.showMessage("준비 완료. '파일 > 폴더 열기'로 시작하세요.")

        # 즐겨찾기 창을 저장할 변수
        self.favorites_win = None

    def open_folder(self):
        """갤러리 위젯의 폴더 선택 함수를 호출합니다."""
        self.gallery_widget.open_folder_dialog()

    def open_favorites_window(self):
        """즐겨찾기 뷰어 창을 엽니다."""
        if self.favorites_win is None or not self.favorites_win.isVisible():
            self.favorites_win = FavoritesWindow()
            self.favorites_win.show()
        else:
            self.favorites_win.activateWindow()