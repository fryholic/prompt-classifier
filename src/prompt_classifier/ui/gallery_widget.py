import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                             QFileDialog, QApplication)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from .image_viewer import ImageViewer # 이미지 뷰어 임포트

class GalleryWidget(QWidget):
    # 상태 메시지를 메인 윈도우로 보내기 위한 시그널
    status_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0) # 여백 제거

        self.image_paths = [] # 현재 로드된 이미지 경로 리스트

        # QListWidget으로 갤러리 구현
        self.gallery_list_widget = QListWidget()
        self.gallery_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.gallery_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.gallery_list_widget.setMovement(QListWidget.Movement.Static)
        self.gallery_list_widget.setIconSize(QSize(200, 200))
        self.gallery_list_widget.setSpacing(10)
        self.layout.addWidget(self.gallery_list_widget)

        # 썸네일 더블클릭 시 이미지 뷰어 열기
        self.gallery_list_widget.itemDoubleClicked.connect(self.show_image_viewer)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "이미지 폴더 선택")
        if folder_path:
            self.load_images(folder_path)

    def load_images(self, folder_path):
        self.status_updated.emit(f"'{folder_path}' 폴더에서 이미지 스캔 중...")
        QApplication.processEvents() # UI가 멈추지 않도록 이벤트 처리

        self.gallery_list_widget.clear()
        self.image_paths = self.find_image_files_recursively(folder_path)
        
        total_images = len(self.image_paths)
        if total_images == 0:
            self.status_updated.emit("폴더에서 이미지를 찾을 수 없습니다.")
            return

        for idx, image_path in enumerate(self.image_paths):
            self.status_updated.emit(f"이미지 로드 중... ({idx + 1}/{total_images})")
            
            item = QListWidgetItem()
            icon = QIcon(image_path)
            item.setIcon(icon)
            item.setText(os.path.basename(image_path))
            # 나중에 경로를 쉽게 찾기 위해 UserRole에 전체 경로 저장
            item.setData(Qt.ItemDataRole.UserRole, image_path)
            
            self.gallery_list_widget.addItem(item)
            if idx % 20 == 0: # 20개마다 UI 업데이트
                QApplication.processEvents()

        self.status_updated.emit(f"총 {total_images}개의 이미지를 로드했습니다.")

    def find_image_files_recursively(self, folder_path):
        """지정된 폴더와 모든 하위 폴더에서 이미지 파일을 찾습니다."""
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp')
        image_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(supported_formats):
                    image_files.append(os.path.join(root, file))
        return sorted(image_files) # 이름순으로 정렬

    def show_image_viewer(self, item):
        """이미지 뷰어 창을 띄웁니다."""
        clicked_image_path = item.data(Qt.ItemDataRole.UserRole)
        current_index = self.image_paths.index(clicked_image_path)
        
        # 새 뷰어 창 생성 및 표시
        self.viewer = ImageViewer(self.image_paths, current_index)
        self.viewer.show()