# src/prompt_classifier/ui/favorites_window.py

import json
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
                             QLabel, QTextEdit, QPushButton, QSplitter, 
                             QListWidgetItem, QMessageBox, QScrollArea)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, QCoreApplication

from src.prompt_classifier import db_manager
from src.prompt_classifier.gemini_classifier import classify_prompt_with_gemini

class FavoritesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("즐겨찾기 뷰어")
        
        # --- UI 레이아웃 설정 ---
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 왼쪽: 썸네일 리스트 및 이미지 뷰어
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.favorites_list = QListWidget()
        self.favorites_list.setIconSize(QSize(150, 150))
        self.favorites_list.itemClicked.connect(self.on_favorite_selected)
        
        self.image_viewer = QLabel("이미지를 선택하세요.")
        self.image_viewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_layout.addWidget(QLabel("즐겨찾기 목록"))
        left_layout.addWidget(self.favorites_list, 1)
        left_layout.addWidget(self.image_viewer, 4) # 이미지 뷰어 영역 확장

        # 오른쪽: 정보 패널
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.prompt_display = QTextEdit()
        self.prompt_display.setReadOnly(True)
        
        self.classify_button = QPushButton("프롬프트 분류 실행 (Gemini API)")
        self.classify_button.clicked.connect(self.run_classification)
        
        # 분류 결과를 표시할 스크롤 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.results_widget)

        right_layout.addWidget(QLabel("전체 프롬프트"))
        right_layout.addWidget(self.prompt_display, 1)
        right_layout.addWidget(self.classify_button)
        right_layout.addWidget(QLabel("분류 결과"))
        right_layout.addWidget(self.scroll_area, 3)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400]) # 초기 스플리터 크기 조절
        main_layout.addWidget(splitter)
        
        self.current_item_data = None
        self.load_favorites()
        
        # 전체 화면으로 시작
        self.showMaximized()

    def load_favorites(self):
        """DB에서 즐겨찾기 목록을 불러와 리스트에 표시합니다."""
        self.favorites_list.clear()
        favorites = db_manager.get_all_favorites()
        for fav in favorites:
            item = QListWidgetItem(QIcon(fav['image_path']), fav['image_path'])
            item.setData(Qt.ItemDataRole.UserRole, fav) # 모든 DB 데이터 저장
            self.favorites_list.addItem(item)

    def on_favorite_selected(self, item):
        """리스트에서 항목 선택 시 이미지와 정보를 업데이트합니다."""
        self.current_item_data = item.data(Qt.ItemDataRole.UserRole)
        
        # 이미지 표시
        pixmap = QPixmap(self.current_item_data['image_path'])
        scaled_pixmap = pixmap.scaled(self.image_viewer.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
        self.image_viewer.setPixmap(scaled_pixmap)
        
        # 프롬프트 표시
        self.prompt_display.setText(self.current_item_data['full_prompt'])
        
        # 저장된 분류 데이터가 있으면 표시
        if self.current_item_data['classified_data']:
            self.display_classification_results(json.loads(self.current_item_data['classified_data']))
        else:
            # 기존 결과 초기화
            self.clear_results_layout()
            self.results_layout.addWidget(QLabel("분류를 실행해 주세요."))
            
    def run_classification(self):
        """Gemini API를 호출하여 프롬프트를 분류합니다."""
        if not self.current_item_data:
            QMessageBox.warning(self, "오류", "먼저 즐겨찾기 목록에서 이미지를 선택하세요.")
            return

        prompt_to_classify = self.current_item_data['full_prompt']
        if not prompt_to_classify or prompt_to_classify == "프롬프트 정보 없음":
            QMessageBox.information(self, "알림", "분류할 프롬프트 정보가 없습니다.")
            return
            
        self.classify_button.setText("분류 중...")
        self.classify_button.setEnabled(False)
        QCoreApplication.processEvents() # UI 갱신

        # API 호출
        result = classify_prompt_with_gemini(prompt_to_classify)
        
        self.classify_button.setText("프롬프트 분류 실행 (Gemini API)")
        self.classify_button.setEnabled(True)

        if "error" in result:
            QMessageBox.critical(self, "API 오류", f"프롬프트 분류에 실패했습니다:\n{result['error']}")
        else:
            # 결과 표시 및 DB 업데이트
            self.display_classification_results(result)
            db_manager.update_classified_data(self.current_item_data['image_path'], json.dumps(result))
            QMessageBox.information(self, "성공", "프롬프트 분류가 완료되었습니다.")
            
    def display_classification_results(self, data: dict):
        """분류된 결과를 UI에 보기 좋게 표시합니다."""
        self.clear_results_layout()
        
        category_names = {
            "style_artist": "🎨 스타일 및 작가", "quality_rendering": "✨ 품질 및 렌더링", "subject": "👤 피사체",
            "body_appearance": "👀 신체적 특징 및 외모", "pose_gaze": "🤸 포즈 및 시선", "clothing_accessories": "👕 의상 및 액세서리",
            "action_situation": "🎬 행동 및 상황", "background_props": "🏞️ 배경 및 소품", "technical_elements": "🔧 기술적 요소"
        }
        
        for key, name in category_names.items():
            tags = data.get(key)
            if tags: # 태그가 있는 경우에만 표시
                self.results_layout.addWidget(QLabel(f"<b>{name}</b>"))
                tags_text = ", ".join(tags)
                tag_label = QTextEdit(tags_text)
                tag_label.setReadOnly(True)
                tag_label.setFixedHeight(tag_label.fontMetrics().height() * (tags_text.count('\n') + 3))
                self.results_layout.addWidget(tag_label)

    def clear_results_layout(self):
        """결과 레이아웃의 모든 위젯을 삭제합니다."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def resizeEvent(self, event):
        """창 크기 변경 시 이미지도 다시 스케일링합니다."""
        if self.current_item_data:
            pixmap = QPixmap(self.current_item_data['image_path'])
            scaled_pixmap = pixmap.scaled(self.image_viewer.size(), 
                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
            self.image_viewer.setPixmap(scaled_pixmap)
        super().resizeEvent(event)