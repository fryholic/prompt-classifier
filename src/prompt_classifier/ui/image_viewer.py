from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QApplication, QStyle)
from PyQt6.QtGui import QPixmap, QIcon, QKeySequence, QShortcut
from PyQt6.QtCore import Qt

class ImageViewer(QWidget):
    def __init__(self, image_paths, current_index):
        super().__init__()
        self.image_paths = image_paths
        self.current_index = current_index

        self.setWindowTitle("Image Viewer")
        self.setMinimumSize(800, 600)

        # 레이아웃 설정
        main_layout = QVBoxLayout(self)
        
        self.image_label = QLabel("이미지를 불러오는 중...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label, 1) # 공간을 최대한 차지

        # 하단 버튼 레이아웃
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        style = self.style() # 시스템 기본 아이콘 사용
        self.prev_button = QPushButton()
        self.prev_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))
        self.prev_button.clicked.connect(self.show_previous_image)

        self.fav_button = QPushButton("⭐ 즐겨찾기")
        self.fav_button.clicked.connect(self.toggle_favorite)

        self.next_button = QPushButton()
        self.next_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        self.next_button.clicked.connect(self.show_next_image)

        button_layout.addStretch()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.fav_button)
        button_layout.addWidget(self.next_button)
        button_layout.addStretch()

        # 키보드 단축키 설정 (좌/우 방향키)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.show_previous_image)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.show_next_image)

        self.update_image()

    def update_image(self):
        """현재 인덱스의 이미지를 화면에 표시합니다."""
        image_path = self.image_paths[self.current_index]
        pixmap = QPixmap(image_path)
        
        # 창 크기에 맞게 이미지 스케일 조정
        scaled_pixmap = pixmap.scaled(self.image_label.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
        # 버튼 활성화/비활성화 상태 업데이트
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.image_paths) - 1)
        
        # TODO: DB를 확인하여 즐겨찾기 여부 표시
        # is_favorited = check_db_for_favorite(image_path)
        # self.update_fav_button_style(is_favorited)

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def show_next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_image()
            
    def toggle_favorite(self):
        """즐겨찾기 버튼 클릭 시 호출될 함수 (Phase 3에서 구현)"""
        current_path = self.image_paths[self.current_index]
        print(f"'{current_path}' 즐겨찾기 상태 토글!")
        # TODO: DB 저장/삭제 로직, 버튼 스타일 업데이트 로직 추가
        
    def resizeEvent(self, event):
        """창 크기가 변경될 때마다 이미지를 다시 스케일링합니다."""
        self.update_image()
        super().resizeEvent(event)