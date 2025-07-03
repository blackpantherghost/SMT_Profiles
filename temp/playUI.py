import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QCheckBox, QComboBox, QFrame, QTabWidget, 
                               QGridLayout, QSizePolicy, QSpacerItem, QTextEdit,
                               QScrollArea, QGraphicsOpacityEffect, QSplitter)
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

class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(50)  # Minimum width when collapsed
        self.setMaximumWidth(400)  # Maximum width when expanded
        self.is_expanded = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with toggle button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toggle button (always visible)
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_panel)
        header_layout.addWidget(self.toggle_btn)
        
        # Title (hidden when collapsed)
        self.title_label = QLabel("Validation Log")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #2196F3; margin-left: 10px;")
        self.title_label.setVisible(False)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Close button (hidden when collapsed)
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.setStyleSheet("""
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
        self.close_btn.clicked.connect(self.collapse_panel)
        self.close_btn.setVisible(False)
        header_layout.addWidget(self.close_btn)
        
        layout.addLayout(header_layout)
        
        # Log content (hidden when collapsed)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d3748;          # CHANGED: Dark background
                color: #e2e8f0;                     # CHANGED: Light text color
                border: 1px solid #4a5568;          # CHANGED: Dark border
                border-radius: 6px;
                padding: 12px;                      # CHANGED: Increased padding
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;  # CHANGED: Better fonts
                font-size: 11px;
                line-height: 1.4;                   # CHANGED: Better line spacing
            }
            QTextEdit:focus {
                border-color: #2196F3;
                outline: none;
            }
            QScrollBar:vertical {                   # CHANGED: Added custom scrollbar
                background-color: #4a5568;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #718096;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0aec0;
            }
        """)
        self.log_text.setVisible(False)
        
        # Sample log messages
        log_messages = [
            "<span style='color: #63b3ed;'>[INFO]</span> <span style='color: #e2e8f0;'>Starting validation process...</span>",
            "<span style='color: #68d391;'>[CHECK]</span> <span style='color: #e2e8f0;'>Pivot validation:</span> <span style='color: #68d391;'>PASSED</span>",
            "<span style='color: #68d391;'>[CHECK]</span> <span style='color: #e2e8f0;'>UV mapping validation:</span> <span style='color: #68d391;'>PASSED</span>", 
            "<span style='color: #68d391;'>[CHECK]</span> <span style='color: #e2e8f0;'>Scale validation:</span> <span style='color: #68d391;'>PASSED</span>",
            "<span style='color: #fbb040;'>[WARNING]</span> <span style='color: #e2e8f0;'>Material 'Material_01' has no diffuse map</span>",
            "<span style='color: #63b3ed;'>[INFO]</span> <span style='color: #e2e8f0;'>PBR assignment completed</span>",
            "<span style='color: #68d391;'>[SUCCESS]</span> <span style='color: #e2e8f0;'>All validations completed</span>",
            "<span style='color: #63b3ed;'>[INFO]</span> <span style='color: #e2e8f0;'>Ready for export...</span>"
        ]
        
        # self.log_text.setPlainText("\n".join(log_messages))
        self.log_text.setHtml("<br>".join(log_messages))
        layout.addWidget(self.log_text)
        
        # Set panel style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-left: 1px solid #e0e0e0;
            }
        """)
        
        self.setLayout(layout)
        
        # Set initial collapsed state
        self.setFixedWidth(50)

        # Set initial collapsed state
        self.setVisible(False)  # CHANGED: Start completely hidden instead of setFixedWidth(50)
    
    def toggle_panel(self):
        if self.is_expanded:
            self.collapse_panel()
        else:
            self.expand_panel()
    
    def expand_panel(self):
        self.is_expanded = True
        self.setVisible(True)
        self.setFixedWidth(300)
        self.toggle_btn.setText("▶")
        self.title_label.setVisible(True)
        self.close_btn.setVisible(True)
        self.log_text.setVisible(True)
        
        # Update log content when expanded
        self.update_log()
    
    def collapse_panel(self):
        self.is_expanded = False
        # self.setFixedWidth(50)
        self.setVisible(False)
        self.toggle_btn.setText("◀")
        self.title_label.setVisible(False)
        self.close_btn.setVisible(False)
        self.log_text.setVisible(False)
    
    def update_log(self):
        # # Add new log entry to simulate activity
        # import datetime
        # timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        # new_entry = f"[{timestamp}] Log panel opened by user"
        
        # current_text = self.log_text.toPlainText()
        # updated_text = current_text + "\n" + new_entry
        # self.log_text.setPlainText(updated_text)
        
        # # Scroll to bottom
        # scrollbar = self.log_text.verticalScrollBar()
        # scrollbar.setValue(scrollbar.maximum())

        # Add new log entry to simulate activity
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        new_entry = f"<span style='color: #63b3ed;'>[{timestamp}]</span> <span style='color: #e2e8f0;'>Log panel accessed by user</span>"
        
        current_text = self.log_text.toHtml()  # CHANGED: Using toHtml() instead of toPlainText()
        updated_text = current_text + "<br>" + new_entry  # CHANGED: Using <br> instead of \n
        self.log_text.setHtml(updated_text)  # CHANGED: Using setHtml() instead of setPlainText()
        
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

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
        # We'll connect this in the main window
        validation_layout.addWidget(validate_btn)
        validation_layout.addWidget(get_log_btn)
        validation_layout.addStretch()
        layout.addLayout(validation_layout)
        
        # Store reference to get_log_btn for connection in main window
        self.get_log_btn = get_log_btn
        
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
        self.setMinimumSize(500, 650)
        self.resize(750, 650)  # Start with expanded size to accommodate log panel
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
            }
        """)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # Main content widget
        main_content = QWidget()
        main_content.setMinimumWidth(420)
        
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
        main_content.setLayout(main_layout)
        
        # Create log panel
        self.log_panel = LogPanel()
        
        # Add widgets to splitter
        self.main_splitter.addWidget(main_content)
        self.main_splitter.addWidget(self.log_panel)
        
        # Set splitter properties
        # self.main_splitter.setSizes([420, 50])  # Start with log panel collapsed
        self.main_splitter.setSizes([500, 0])  # CHANGED: Start with log panel completely hidden
        self.main_splitter.setStretchFactor(0, 1)  # Main content can stretch
        self.main_splitter.setStretchFactor(1, 0)  # Log panel fixed size
        
        # Connect get log button
        self.validate_tab.get_log_btn.clicked.connect(self.show_log_panel)
        
        # Style the splitter
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
        """)

    def switch_tab(self, index):
        # Update button states
        buttons = [self.naming_btn, self.validate_btn, self.publish_btn]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
            btn.update_style()
        
        # Switch tab
        self.tab_widget.setCurrentIndex(index)
    
    def show_log_panel(self):
        """Toggle the log panel when Get Log button is clicked"""
        if not self.log_panel.is_expanded:
            # Panel is collapsed, so expand it
            self.log_panel.expand_panel()
            
            # If window is too narrow, expand it to accommodate the log panel
            if self.width() < 720:  # 420 (min main content) + 300 (log panel)
                self.resize(720, self.height())
            
            # Set splitter sizes to show the log panel
            main_content_width = self.width() - 300 - 10  # Leave space for log panel + splitter
            self.main_splitter.setSizes([main_content_width, 300])
        
        else:
            # Panel is expanded, so collapse it
            self.log_panel.collapse_panel()
            
            # Adjust splitter to hide the log panel completely
            self.main_splitter.setSizes([self.width(), 0])


def main():
    """Main function to launch the application"""
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("3D AB Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("3D Tools")
    
    # Create and show the main window
    window = Main3DABTool()
    window.show()
    
    # Center the window on screen
    screen = app.primaryScreen()
    if screen:
        screen_geometry = screen.geometry()
        window_geometry = window.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        window.move(x, y)
    
    # Start the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
