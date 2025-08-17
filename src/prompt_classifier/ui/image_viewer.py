import os
import subprocess
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QApplication, QMenu, QStyle)
from PyQt6.QtGui import QPixmap, QIcon, QKeySequence, QShortcut, QAction
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

from src.prompt_classifier import db_manager
from src.prompt_classifier.prompt_extractor import get_positive_prompt_from_image


class ImageViewer(QWidget):
    def __init__(self, image_paths, current_index):
        super().__init__()
        self.image_paths = image_paths
        self.current_index = current_index

        self.setWindowTitle("Image Viewer")

        main_layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label, 1)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        style = self.style()
        self.prev_button = QPushButton()
        self.prev_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))
        self.prev_button.clicked.connect(self.show_previous_image)

        # --- 즐겨찾기 버튼 추가 ---
        self.fav_button = QPushButton("⭐ 즐겨찾기")
        self.fav_button.clicked.connect(self.toggle_favorite)

        self.next_button = QPushButton()
        self.next_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        self.next_button.clicked.connect(self.show_next_image)

        button_layout.addStretch()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.fav_button) # 버튼 레이아웃에 추가
        button_layout.addWidget(self.next_button)
        button_layout.addStretch()

        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)

        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.show_previous_image)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.show_next_image)

        self.update_image()
        self.showMaximized()

    def update_image(self):
        image_path = self.image_paths[self.current_index]
        pixmap = QPixmap(image_path)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        scaled_pixmap = pixmap.scaled(screen_geometry.size(),
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.image_paths) - 1)
        # --- 이미지가 업데이트될 때마다 즐겨찾기 상태 확인 ---
        self.check_favorite_status()

    def check_favorite_status(self):
        """현재 이미지의 즐겨찾기 상태를 확인하고 버튼 스타일을 업데이트합니다."""
        current_path = self.image_paths[self.current_index]
        if db_manager.is_favorited(current_path):
            self.fav_button.setText("❤️ 즐겨찾기됨")
            self.fav_button.setStyleSheet("background-color: #fecaca; color: #991b1b;")
        else:
            self.fav_button.setText("⭐ 즐겨찾기")
            self.fav_button.setStyleSheet("") # 기본 스타일로 복원

    def toggle_favorite(self):
        """즐겨찾기 버튼 클릭 시 DB에 추가 또는 삭제를 수행합니다."""
        current_path = self.image_paths[self.current_index]

        if db_manager.is_favorited(current_path):
            # 이미 즐겨찾기 상태 -> 삭제
            db_manager.remove_favorite(current_path)
            print(f"'{os.path.basename(current_path)}' 즐겨찾기에서 삭제됨.")
        else:
            # 즐겨찾기 상태 아님 -> 프롬프트 추출 후 추가
            prompt = get_positive_prompt_from_image(current_path)
            if prompt:
                db_manager.add_favorite(current_path, prompt)
                print(f"'{os.path.basename(current_path)}' 즐겨찾기에 추가됨.")
            else:
                # 프롬프트가 없는 경우 즐겨찾기에 추가하지 않음 (또는 기본값으로 추가)
                db_manager.add_favorite(current_path, "프롬프트 정보 없음")
                print("프롬프트 정보를 찾을 수 없지만, 이미지만 즐겨찾기에 추가했습니다.")

        # 버튼 상태 즉시 갱신
        self.check_favorite_status()


    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def show_next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_image()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.show_previous_image()
        else:
            self.show_next_image()
        event.accept()

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        copy_path_action = QAction("이미지 경로 복사", self)
        copy_path_action.triggered.connect(self.copy_image_path)
        open_folder_action = QAction("탐색기에서 폴더 열기", self)
        open_folder_action.triggered.connect(self.open_containing_folder)
        copy_image_action = QAction("이미지를 클립보드에 복사", self)
        copy_image_action.triggered.connect(self.copy_image_to_clipboard)
        context_menu.addAction(copy_path_action)
        context_menu.addAction(open_folder_action)
        context_menu.addAction(copy_image_action)
        context_menu.exec(self.image_label.mapToGlobal(pos))

    def copy_image_path(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.image_paths[self.current_index])

    def open_containing_folder(self):
        path = self.image_paths[self.current_index]
        folder = os.path.dirname(path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def copy_image_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.image_label.pixmap())