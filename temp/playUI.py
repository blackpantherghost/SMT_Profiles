import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QCheckBox, QComboBox, QFrame, QTabWidget, 
                               QGridLayout, QSizePolicy, QSpacerItem, QTextEdit,
                               QScrollArea, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon

class SeparatorLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("""
            QFrame {
                color: #d0d0d0;
                background-color: #d0d0d0;
                border: none;
                height: 1px;
                margin: 10px 0px;
            }
        """)

class LogWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(350, 400)
        
        # Setup UI
        self.setup_ui()
        
        # Animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Initially hidden
        self.hide()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Validation Log")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2196F3; margin-bottom: 10px;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        close_btn.clicked.connect(self.slide_out)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        # Log content
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        # Sample log messages
        log_messages = [
            "[INFO] Starting validation process...",
            "[CHECK] Pivot validation: PASSED",
            "[CHECK] UV mapping validation: PASSED", 
            "[CHECK] Scale validation: PASSED",
            "[WARNING] Material 'Material_01' has no diffuse map",
            "[INFO] PBR assignment completed",
            "[SUCCESS] All validations completed",
            "[INFO] Ready for export..."
        ]
        
        self.log_text.setPlainText("\n".join(log_messages))
        layout.addWidget(self.log_text)
        
        # Main container with shadow
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
    
    def slide_in(self, parent_pos, parent_size):
        # Position to the right of parent
        start_x = parent_pos.x() + parent_size.width()
        start_y = parent_pos.y() + 100
        end_x = start_x
        end_y = start_y
        
        # Start from outside the screen
        self.setGeometry(start_x + 350, start_y, 350, 400)
        self.show()
        
        # Animate sliding in
        self.animation.setStartValue(QRect(start_x + 350, start_y, 350, 400))
        self.animation.setEndValue(QRect(end_x, end_y, 350, 400))
        self.animation.start()
    
    def slide_out(self):
        # Get current position
        current_rect = self.geometry()
        end_x = current_rect.x() + 350
        
        # Animate sliding out
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(QRect(end_x, current_rect.y(), 350, 400))
        self.animation.finished.connect(self.hide)
        self.animation.start()

class ImagePlaceholder(QLabel):
    def __init__(self, text="Application\nBanner Image", size=(100, 60)):
        super().__init__()
        self.placeholder_text = text
        self.setFixedSize(*size)
        self.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                color: #888888;
                font-size: 10px;
                padding: 5px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText(self.placeholder_text)

class ToggleSwitch(QWidget):
    def __init__(self, checked=False):
        super().__init__()
        self._checked = checked
        self.setFixedSize(44, 22)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Track
        track_color = QColor("#4CAF50" if self._checked else "#e0e0e0")
        painter.setBrush(track_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 44, 22, 11, 11)
        
        # Handle
        handle_x = 24 if self._checked else 2
        painter.setBrush(QColor("white"))
        painter.setPen(QColor("#d0d0d0"))
        painter.drawEllipse(handle_x, 2, 18, 18)
    
    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.update()
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, checked):
        self._checked = checked
        self.update()

class StyledButton(QPushButton):
    def __init__(self, text, primary=False, small=False):
        super().__init__(text)
        size = "8px 12px" if small else "10px 16px"
        font_size = "11px" if small else "12px"
        
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: {size};
                    border-radius: 4px;
                    font-size: {font_size};
                    font-weight: 500;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                QPushButton:pressed {{
                    background-color: #1565C0;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    padding: {size};
                    border-radius: 4px;
                    font-size: {font_size};
                    font-weight: 500;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }}
                QPushButton:pressed {{
                    background-color: #dee2e6;
                }}
            """)

class TabButton(QPushButton):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.is_active = active
        self.setCheckable(True)
        self.setChecked(active)
        self.setFixedHeight(32)
        self.update_style()
        
    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: #343a40;
                    color: white;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                    min-width: 90px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #6c757d;
                    border: 1px solid #dee2e6;
                    padding: 6px 16px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 500;
                    min-width: 90px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    color: #495057;
                }
            """)

class SectionTitle(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setFont(QFont("Arial", 11, QFont.Bold))
        self.setStyleSheet("color: #495057; margin: 15px 0px 8px 0px;")

class FieldRow(QWidget):
    def __init__(self, label_text, widget, has_toggle=True, toggle_checked=False):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Label
        label = QLabel(label_text)
        label.setFixedWidth(80)
        label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(label)
        
        # Widget
        if isinstance(widget, QLineEdit):
            widget.setStyleSheet("""
                QLineEdit {
                    padding: 6px 10px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 11px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #2196F3;
                }
            """)
        elif isinstance(widget, QComboBox):
            widget.setStyleSheet("""
                QComboBox {
                    padding: 6px 10px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 11px;
                    background-color: white;
                    min-width: 200px;
                }
                QComboBox:focus {
                    border-color: #2196F3;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        
        layout.addWidget(widget)
        
        # Toggle
        if has_toggle:
            toggle = ToggleSwitch(toggle_checked)
            layout.addWidget(toggle)
        
        self.setLayout(layout)

class NamingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Naming Hierarchy section
        naming_title = SectionTitle("Naming Hierarchy")
        layout.addWidget(naming_title)
        
        # Form fields
        prefix_field = FieldRow("Prefix", QLineEdit("Text"), True, True)
        layout.addWidget(prefix_field)
        
        mattype_combo = QComboBox()
        mattype_combo.addItem("⊕ Drop Down List Material Types")
        mattype_field = FieldRow("Mat-Type", mattype_combo, True, True)
        layout.addWidget(mattype_field)
        
        additional1_field = FieldRow("Additional", QLineEdit("Text"), True, True)
        layout.addWidget(additional1_field)
        
        additional2_field = FieldRow("Additional", QLineEdit("Text"), True, False)
        layout.addWidget(additional2_field)
        
        suffix_field = FieldRow("Suffix [Ovr]", QLineEdit("Text"), True, False)
        layout.addWidget(suffix_field)
        
        # Separator
        layout.addWidget(SeparatorLine())
        
        # Apply Rename section
        apply_title = SectionTitle("Apply Rename")
        layout.addWidget(apply_title)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        rename_btn = StyledButton("Rename")
        auto_rename_btn = StyledButton("Auto Rename")
        button_layout.addWidget(rename_btn)
        button_layout.addWidget(auto_rename_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)

class ValidateExportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.log_window = LogWindow()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Scene Validations section
        validation_title = SectionTitle("Scene Validations")
        layout.addWidget(validation_title)
        
        # Toggle options in a grid
        options_layout = QHBoxLayout()
        options_layout.setSpacing(30)
        
        # Pivot
        pivot_layout = QVBoxLayout()
        pivot_layout.setSpacing(5)
        pivot_label = QLabel("Pivot")
        pivot_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        pivot_toggle = ToggleSwitch(True)
        pivot_layout.addWidget(pivot_label)
        pivot_layout.addWidget(pivot_toggle)
        options_layout.addLayout(pivot_layout)
        
        # UV
        uv_layout = QVBoxLayout()
        uv_layout.setSpacing(5)
        uv_label = QLabel("UV")
        uv_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        uv_toggle = ToggleSwitch(True)
        uv_layout.addWidget(uv_label)
        uv_layout.addWidget(uv_toggle)
        options_layout.addLayout(uv_layout)
        
        # Scale
        scale_layout = QVBoxLayout()
        scale_layout.setSpacing(5)
        scale_label = QLabel("Scale")
        scale_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        scale_toggle = ToggleSwitch(True)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(scale_toggle)
        options_layout.addLayout(scale_layout)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Validation buttons
        validation_layout = QHBoxLayout()
        validation_layout.setSpacing(10)
        validate_btn = StyledButton("Validate")
        get_log_btn = StyledButton("Get Log")
        get_log_btn.clicked.connect(self.show_log_window)
        validation_layout.addWidget(validate_btn)
        validation_layout.addWidget(get_log_btn)
        validation_layout.addStretch()
        layout.addLayout(validation_layout)
        
        # Separator
        layout.addWidget(SeparatorLine())
        
        # Export Settings section
        export_title = SectionTitle("Export Settings")
        layout.addWidget(export_title)
        
        # Assign PBR
        pbr_combo = QComboBox()
        pbr_combo.addItem("⊕ Drop Down List for Material List")
        pbr_field = FieldRow("Assign PBR", pbr_combo, True, True)
        layout.addWidget(pbr_field)
        
        # Preset
        preset_combo = QComboBox()
        preset_combo.addItem("⊕ Drop Down List for PBX presets")
        preset_field = FieldRow("Preset", preset_combo, True, False)
        layout.addWidget(preset_field)
        
        # Separator
        layout.addWidget(SeparatorLine())
        
        # Exports section
        exports_title = SectionTitle("Exports")
        layout.addWidget(exports_title)
        
        export_button_layout = QHBoxLayout()
        export_button_layout.setSpacing(10)
        auto_setup_btn = StyledButton("Auto-Setup")
        export_selection_btn = StyledButton("Export Selection")
        export_button_layout.addWidget(auto_setup_btn)
        export_button_layout.addWidget(export_selection_btn)
        export_button_layout.addStretch()
        layout.addLayout(export_button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def show_log_window(self):
        parent_pos = self.window().pos()
        parent_size = self.window().size()
        self.log_window.slide_in(parent_pos, parent_size)

class PublishTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Scene Set-Up section
        setup_title = SectionTitle("Scene Set-Up")
        layout.addWidget(setup_title)
        
        # Material section
        material_layout = QHBoxLayout()
        material_layout.setSpacing(30)
        
        # Material info
        material_info_layout = QVBoxLayout()
        material_info_layout.setSpacing(5)
        material_label = QLabel("Material")
        material_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        matid_label = QLabel("Mat-Id count")
        matid_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        material_info_layout.addWidget(material_label)
        material_info_layout.addWidget(matid_label)
        material_layout.addLayout(material_info_layout)
        
        # Multi-Mat toggle
        multimat_layout = QVBoxLayout()
        multimat_layout.setSpacing(5)
        multimat_label = QLabel("Multi-Mat")
        multimat_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        multimat_toggle = ToggleSwitch(True)
        multimat_layout.addWidget(multimat_label)
        multimat_layout.addWidget(multimat_toggle)
        material_layout.addLayout(multimat_layout)
        
        material_layout.addStretch()
        layout.addLayout(material_layout)
        
        # Assign Maps section
        maps_layout = QHBoxLayout()
        maps_layout.setSpacing(30)
        
        # Assign Maps label
        maps_label = QLabel("Assign Maps")
        maps_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        maps_layout.addWidget(maps_label)
        
        # Simple toggle
        simple_layout = QVBoxLayout()
        simple_layout.setSpacing(5)
        simple_label = QLabel("Simple")
        simple_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        simple_toggle = ToggleSwitch(True)
        simple_layout.addWidget(simple_label)
        simple_layout.addWidget(simple_toggle)
        maps_layout.addLayout(simple_layout)
        
        # Hybrid toggle
        hybrid_layout = QVBoxLayout()
        hybrid_layout.setSpacing(5)
        hybrid_label = QLabel("Hybrid")
        hybrid_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        hybrid_toggle = ToggleSwitch(False)
        hybrid_layout.addWidget(hybrid_label)
        hybrid_layout.addWidget(hybrid_toggle)
        maps_layout.addLayout(hybrid_layout)
        
        maps_layout.addStretch()
        layout.addLayout(maps_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        scene_setup_btn = StyledButton("Scene Set-Up")
        validate_log_btn = StyledButton("Validate & Log")
        action_layout.addWidget(scene_setup_btn)
        action_layout.addWidget(validate_log_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Separator
        layout.addWidget(SeparatorLine())
        
        # Scene Publish section
        publish_title = SectionTitle("Scene Publish")
        layout.addWidget(publish_title)
        
        # Re-Link Maps
        relink_field = FieldRow("Re-Link Maps to Net APP", QWidget(), True, True)
        layout.addWidget(relink_field)
        
        # Separator
        layout.addWidget(SeparatorLine())
        
        # Publish section
        final_publish_title = SectionTitle("Publish")
        layout.addWidget(final_publish_title)
        
        publish_button_layout = QHBoxLayout()
        publish_button_layout.setSpacing(10)
        publish_btn = StyledButton("Publish", primary=True)
        auto_publish_btn = StyledButton("Auto Publish")
        publish_button_layout.addWidget(publish_btn)
        publish_button_layout.addWidget(auto_publish_btn)
        publish_button_layout.addStretch()
        layout.addLayout(publish_button_layout)
        
        layout.addStretch()
        self.setLayout(layout)

class Main3DABTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("3D AB Tool")
        self.setFixedSize(420, 650)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header with banner
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Title : 3D AB")
        title_label.setFont(QFont("Arial", 13, QFont.Bold))
        title_label.setStyleSheet("color: #212529; background: transparent; border: none;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Image placeholder
        image_placeholder = ImagePlaceholder()
        header_layout.addWidget(image_placeholder)
        
        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)
        
        # Select Tab label
        select_tab_label = QLabel("Select Tab")
        select_tab_label.setStyleSheet("color: #2196F3; font-size: 11px; margin-top: 5px; font-weight: 500;")
        main_layout.addWidget(select_tab_label)
        
        # Tab buttons
        tab_button_layout = QHBoxLayout()
        tab_button_layout.setSpacing(8)
        self.naming_btn = TabButton("Naming", active=True)
        self.validate_btn = TabButton("Validate/Export")
        self.publish_btn = TabButton("Publish")
        
        # Connect tab buttons
        self.naming_btn.clicked.connect(lambda: self.switch_tab(0))
        self.validate_btn.clicked.connect(lambda: self.switch_tab(1))
        self.publish_btn.clicked.connect(lambda: self.switch_tab(2))
        
        tab_button_layout.addWidget(self.naming_btn)
        tab_button_layout.addWidget(self.validate_btn)
        tab_button_layout.addWidget(self.publish_btn)
        tab_button_layout.addStretch()
        main_layout.addLayout(tab_button_layout)
        
        # Tab content area
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #ffffff;
                margin-top: 5px;
            }
            QTabBar::tab {
                height: 0px;
                width: 0px;
                border: none;
            }
        """)
        
        # Add tabs
        self.naming_tab = NamingTab()
        self.validate_tab = ValidateExportTab()
        self.publish_tab = PublishTab()
        
        self.tab_widget.addTab(self.naming_tab, "Naming")
        self.tab_widget.addTab(self.validate_tab, "Validate/Export")
        self.tab_widget.addTab(self.publish_tab, "Publish")
        
        # Hide tab bar
        self.tab_widget.tabBar().setVisible(False)
        
        main_layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(main_layout)
    
    def switch_tab(self, index):
        # Update button states
        buttons = [self.naming_btn, self.validate_btn, self.publish_btn]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
            btn.update_style()
        
        # Switch tab
        self.tab_widget.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = Main3DABTool()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()