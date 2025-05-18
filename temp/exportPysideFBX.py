import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QPushButton, QLabel, 
                             QFileDialog, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPixmap


class DropArea(QFrame):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setAcceptDrops(True)
        self.setMinimumSize(100, 100)
        self.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #aaaaaa;")
        
        # Create a layout for the label
        layout = QVBoxLayout(self)
        self.label = QLabel("Drop Folder Here", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #e0f0e0; border: 2px dashed #00aa00;")
        
    def dragLeaveEvent(self, event):
        self.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #aaaaaa;")
        
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            # We only take the first URL if multiple are dropped
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                # Update the path in the main window
                self.main_window.update_path(path)
            
        self.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #aaaaaa;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.presetpath = ""
        self.exportpath = ""
        
        self.setWindowTitle("FBX Export Tool")
        self.setMinimumSize(600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 1. Banner widget area
        self.banner = QLabel("FBX Export Tool")
        self.banner.setAlignment(Qt.AlignCenter)
        self.banner.setStyleSheet("background-color: #4a86e8; color: white; padding: 15px;")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.banner.setFont(font)
        main_layout.addWidget(self.banner)
        
        # 2. Combobox for FBX Presets
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Choose FBX Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["a", "b", "c"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        main_layout.addLayout(preset_layout)
        
        # 4. Horizontal layout for path selection and drag/drop
        path_layout = QHBoxLayout()
        
        # 4a. Button for file export path
        path_selection_layout = QVBoxLayout()
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        path_selection_layout.addWidget(self.browse_button)
        path_layout.addLayout(path_selection_layout)
        
        # 4b. Drag and drop area
        self.drop_area = DropArea(main_window=self)
        path_layout.addWidget(self.drop_area)
        
        main_layout.addLayout(path_layout)
        
        # 5. Text edit to show path
        path_label = QLabel("Selected Path:")
        main_layout.addWidget(path_label)
        
        self.path_text = QTextEdit()
        self.path_text.setReadOnly(True)
        self.path_text.setMaximumHeight(60)
        main_layout.addWidget(self.path_text)
        
        # 6 & 7. Export buttons
        buttons_layout = QHBoxLayout()
        self.export_fbx_button = QPushButton("Export FBX")
        self.export_fbx_button.clicked.connect(self.export_fbx)
        self.export_obj_button = QPushButton("Export OBJ")
        self.export_obj_button.clicked.connect(self.export_obj)
        buttons_layout.addWidget(self.export_fbx_button)
        buttons_layout.addWidget(self.export_obj_button)
        main_layout.addLayout(buttons_layout)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Initialize preset path to the first item
        self.on_preset_changed(self.preset_combo.currentText())
        
    def on_preset_changed(self, preset):
        """Method to set self.presetpath based on combobox selection"""
        self.presetpath = preset
        print(f"Preset path set to: {self.presetpath}")
        
    def browse_folder(self):
        """Open file dialog to browse for folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if folder_path:
            self.update_path(folder_path)
            
    def update_path(self, path):
        """Update the export path and display it"""
        self.exportpath = path
        self.path_text.setText(path)
        print(f"Export path set to: {self.exportpath}")
        
    def export_fbx(self):
        """Handle FBX export"""
        if not self.exportpath:
            print("Error: No export path selected")
            return
        
        print(f"Exporting FBX to {self.exportpath} with preset {self.presetpath}")
        # Here you would add the actual FBX export logic
        
    def export_obj(self):
        """Handle OBJ export"""
        if not self.exportpath:
            print("Error: No export path selected")
            return
        
        print(f"Exporting OBJ to {self.exportpath}")
        # Here you would add the actual OBJ export logic


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
