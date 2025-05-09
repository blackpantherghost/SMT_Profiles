import os
import subprocess
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QCheckBox, QComboBox, QSlider, QSpinBox, QDoubleSpinBox, 
                               QPushButton, QSplitter, QGroupBox, QRadioButton, QButtonGroup,
                               QTabWidget, QScrollArea, QMenu, QToolBar, QMenuBar, QSizePolicy,
                               QTableWidget, QTableWidgetItem, QTextEdit, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QAction, QPixmap, QFont, QPalette, QColor







class CollapsibleBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.setFlat(True)
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 0.5em;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QGroupBox::indicator {
                width: 13px;
                height: 13px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 15, 10, 10)
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.contentWidget)
        
        self.toggled.connect(self.on_toggled)
        
    def on_toggled(self, checked):
        self.contentWidget.setVisible(checked)
        
    def addWidget(self, widget):
        self.contentLayout.addWidget(widget)
        
    def addLayout(self, layout):
        self.contentLayout.addLayout(layout)


class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245, 25))  # Light gray with 10% opacity
        self.setPalette(palette)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)
        
        self.title = QLabel("Modifiers")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.title)
        
        self.buttons = []
        
        # Create buttons
        button_names = ["Import", "Scene Graph Flattening", "3D Edit", 
                      "Mesh Culling", "Optimize", "Modifier", "Export"]
        
        # Using QButtonGroup to handle exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        for i, name in enumerate(button_names):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 10px;
                    border: none;
                    border-radius: 0;
                    background-color: transparent;
                }
                QPushButton:checked {
                    background-color: #d0d0d0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            
            # In a real app, you would add an icon using:
            # btn.setIcon(QIcon("path/to/icon.png"))
            # Using placeholders for now
            # Create a placeholder icon with the first letter of the button name
            placeholder_icon = QLabel(name[0])
            placeholder_icon.setMinimumSize(QSize(24, 24))
            placeholder_icon.setMaximumSize(QSize(24, 24))
            placeholder_icon.setAlignment(Qt.AlignCenter)
            placeholder_icon.setStyleSheet("background-color: #808080; color: white; border-radius: 12px;")
            
            # Create a horizontal layout for the button content
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            btn_layout.addWidget(placeholder_icon)
            btn_layout.addSpacing(5)
            
            self.buttons.append(btn)
            self.layout.addWidget(btn)
            self.button_group.addButton(btn, i)
        
        # Set the first button as checked initially
        self.buttons[0].setChecked(True)
        
        # Add spacer at the bottom
        self.layout.addStretch()

class DropArea(QFrame):
    files_dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedSize(200, 200)
        # self.setReadOnly(True)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #aaa;
                \\\\background-color: #f0f0f0;
            }
        """)
        layout = QVBoxLayout(self)
        label = QLabel("Drag and drop files here")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("border: none;")
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):  # ADD THIS METHOD
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            valid_extensions = {'.obj', '.fbx', '.glb', '.usdz', '.gltf', '.png'}
            files = []
            invalid_files = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if any(path.lower().endswith(ext) for ext in valid_extensions):
                    files.append(path)
                else:
                    invalid_files.append(path)
            if files:
                self.files_dropped.emit(files)
            if invalid_files:
                QMessageBox.warning (self, "Unsupported File(s)",
                                    "Some files were ignored because they are not supported types:\
                                    " + "\
                                    ".join(invalid_files))
            event.acceptProposedAction()

class MainPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Title for the main panel
        self.title = QLabel("Adjust Settings")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.title)
        
        # Scroll area for parameter panels
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)
        
        # Create parameter panels but hide them initially
        self.import_panel = self.create_import_panel()
        self.scene_graph_panel = self.create_scene_graph_panel()
        self.edit_3d_panel = self.create_3d_edit_panel()
        self.mesh_culling_panel = self.create_mesh_culling_panel()
        
        # Create placeholder panels for the rest
        self.optimize_panel = self.create_optimize_panel()
        # self.optimize_layout = QVBoxLayout(self.optimize_panel)
        # self.optimize_layout.addWidget(QLabel("Optimize parameters will be shown here"))
        
        self.modifier_panel = self.create_modifier_panel() # QWidget()
        # self.modifier_layout = QVBoxLayout(self.modifier_panel)
        # self.modifier_layout.addWidget(QLabel("Modifier parameters will be shown here"))
        
        self.export_panel = self.create_export_panel() #QWidget()
        # self.export_layout = QVBoxLayout(self.export_panel)
        # self.export_layout.addWidget(QLabel("Export parameters will be shown here"))
        
        # Add panels to scroll area
        self.parameter_panels = [
            self.import_panel,
            self.scene_graph_panel,
            self.edit_3d_panel,
            self.mesh_culling_panel,
            self.optimize_panel,
            self.modifier_panel,
            self.export_panel
        ]
        
        for panel in self.parameter_panels:
            self.scroll_layout.addWidget(panel)
            panel.hide()
        
        # Show the first panel initially
        self.parameter_panels[0].show()
        
        # Add bottom buttons
        self.create_bottom_buttons()
      

    def create_import_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)


        # -------- Input Drag and Drop Settings --------
        input_box = CollapsibleBox("Input Drag and Drop Settings")

        # Table for File List
        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["S.No", "File Name", "File Path"])
        self.file_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Drag and Drop Area
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.update_file_table)
        # Drag & Drop Logic
        # self.drop_area.dragEnterEvent = lambda e: e.accept() if e.mimeData().hasUrls() else e.ignore()
        # self.drop_area.dropEvent = self.handle_drop_event
        # Horizontal Layout for Table and Drop Area
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.file_table)
        input_layout.addWidget(self.drop_area)

        # Refresh/Reload Button (Vertical under Table)
        refresh_button = QPushButton("Refresh / Reload")
        refresh_button.clicked.connect(self.clear_file_table_and_drop_area)
        refresh_layout = QVBoxLayout()
        refresh_layout.addWidget(refresh_button)
        refresh_layout.addStretch()
        input_layout.addLayout(refresh_layout)

        input_box.addLayout(input_layout)     

        # Horizontal layout to hold 4 frames
        quick_frame = QFrame()
        quick_frame.setFrameShape(QFrame.StyledPanel)
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.addWidget(QLabel("Quick Preset Settings"))
        h_layout = QHBoxLayout()

        # -------- Frame 1: Poly Count --------
        frame1 = QVBoxLayout()
        frame1.addWidget(QLabel("Poly Count"))
        self.poly_spinner = QSpinBox()
        self.poly_spinner.setMinimum(0)
        self.poly_spinner.setMaximum(400000)
        self.poly_spinner.setValue(20000)
        self.poly_spinner.setFixedHeight(55)
        frame1.addWidget(self.poly_spinner)
        h_layout.addLayout(frame1)

        # -------- Frame 2: Surface Type --------
        frame2 = QVBoxLayout()
        frame2.addWidget(QLabel("Surface Type"))
        self.surface_button_group = QButtonGroup(self)
        self.hard_button = QPushButton("Hard Surface")
        self.soft_button = QPushButton("Soft Surface")
        for b in (self.hard_button, self.soft_button):
            b.setCheckable(True)
            frame2.addWidget(b)
        self.surface_button_group.addButton(self.hard_button)
        self.surface_button_group.addButton(self.soft_button)
        self.surface_button_group.setExclusive(True)
        self.soft_button.setChecked(True)
        h_layout.addLayout(frame2)

        # -------- Frame 3: UVs Type --------
        frame3 = QVBoxLayout()
        frame3.addWidget(QLabel("UVs Type"))
        self.uv_button_group = QButtonGroup(self)
        self.preserve_uv_button = QPushButton("Preserve UVs")
        self.auto_uv_button = QPushButton("Auto UVs")
        for b in (self.preserve_uv_button, self.auto_uv_button):
            b.setCheckable(True)
            frame3.addWidget(b)
        self.uv_button_group.addButton(self.preserve_uv_button)
        self.uv_button_group.addButton(self.auto_uv_button)
        self.uv_button_group.setExclusive(True)
        self.auto_uv_button.setChecked(True)
        h_layout.addLayout(frame3)

        # -------- Frame 4: Processor Button --------
        frame4 = QVBoxLayout()
        frame4.addWidget(QLabel("Quick Processor"))
        frame4_processorTypes = QHBoxLayout()
        self.processorDecimator_button = QPushButton("Decimate")
        self.processorDecimator_button.setFixedHeight(55)
        self.processorDecimator_button.clicked.connect(self.handle_processor_click)
        self.processorRemesh_button = QPushButton("Remesh")
        self.processorRemesh_button.clicked.connect(self.process_files_with_rpdx)
        self.processorRemesh_button.setFixedHeight(55)
        frame4_processorTypes.addWidget(self.processorDecimator_button)
        frame4_processorTypes.addWidget(self.processorRemesh_button)
        frame4.addLayout(frame4_processorTypes)
        h_layout.addLayout(frame4)

        quick_layout.addLayout(h_layout)
        input_box.addWidget(quick_frame)        

        layout.addWidget(input_box)

        # General Import Settings
        general_box = CollapsibleBox("General Import Settings")
        general_box.addWidget(QCheckBox("Convert Z-Up to Y-Up"))
        general_box.addWidget(QCheckBox("Clean Up Animation Data"))
        general_box.addWidget(QCheckBox("Normal Map Y Flip"))
        layout.addWidget(general_box)
        
        # USD Import Settings
        usd_box = CollapsibleBox("USD Import Settings")
        usd_profile_layout = QHBoxLayout()
        usd_profile_layout.addWidget(QLabel("USD Import Profile:"))
        usd_profile_combo = QComboBox()
        usd_profile_combo.addItems(["auto", "arkit"])
        usd_profile_combo.setCurrentText("arkit")
        usd_profile_layout.addWidget(usd_profile_combo)
        usd_box.addLayout(usd_profile_layout)
        
        usd_purpose_layout = QHBoxLayout()
        usd_purpose_layout.addWidget(QLabel("USD Purpose:"))
        usd_purpose_combo = QComboBox()
        usd_purpose_combo.addItems(["auto", "render"])
        usd_purpose_combo.setCurrentText("render")
        usd_purpose_layout.addWidget(usd_purpose_combo)
        usd_box.addLayout(usd_purpose_layout)
        layout.addWidget(usd_box)
        
        # CAD Import Settings
        cad_box = CollapsibleBox("CAD Import Settings")
        cad_layout = QHBoxLayout()
        cad_layout.addWidget(QLabel("Tessellation Resolution:"))
        cad_combo = QComboBox()
        cad_combo.addItems(["auto", "fine"])
        cad_combo.setCurrentText("fine")
        cad_layout.addWidget(cad_combo)
        cad_box.addLayout(cad_layout)
        layout.addWidget(cad_box)
        
        # Discard Properties on Import
        discard_box = CollapsibleBox("Discard Properties on Import")
        discard_box.addWidget(QCheckBox("Discard Cameras"))
        discard_box.addWidget(QCheckBox("Discard Lights"))
        discard_box.addWidget(QCheckBox("Discard Animations"))
        discard_box.addWidget(QCheckBox("Discard Morph Targets"))
        discard_box.addWidget(QCheckBox("Discard Unused UV sets"))
        layout.addWidget(discard_box)
        
        return panel
    
    # def handle_drop_event(self, event):
    #     event.accept()
    #     for url in event.mimeData().urls():
    #         file_path = url.toLocalFile()
    #         row_position = self.file_table.rowCount()
    #         self.file_table.insertRow(row_position)
    #         self.file_table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
    #         self.file_table.setItem(row_position, 1, QTableWidgetItem(file_path.split("/")[-1]))
    #         self.file_table.setItem(row_position, 2, QTableWidgetItem(file_path))

    def handle_processor_click(self):
        if self.hard_button.isChecked():
            print("Hard")
        elif self.soft_button.isChecked():
            print("Soft")

        if self.preserve_uv_button.isChecked():
            print("PUv")
        elif self.auto_uv_button.isChecked():
            print("AUv")

    def process_files_with_rpdx(self):
        for row in range(self.file_table.rowCount()):
            inputFilePath = self.file_table.item(row, 2).text().strip()
            fileName = self.file_table.item(row, 1).text().strip()
            baseName = os.path.splitext(fileName)[0]

            if not os.path.isfile(inputFilePath):
                print(f"Invalid file path: {inputFilePath}")
                continue

            # Step 1: Create "dirlod/<basename>" directory
            parent_dir = os.path.dirname(inputFilePath)
            outputFilePath = os.path.join(parent_dir, "dirlod", baseName)
            os.makedirs(outputFilePath, exist_ok=True)

            # Step 2: Create format subdirectories
            formats = ["glb", "gltf", "obj", "fbx", "usdz"]
            for fmt in formats:
                os.makedirs(os.path.join(outputFilePath, fmt), exist_ok=True)

            # Step 3: Output format paths
            outputFilePathGlb = os.path.join(outputFilePath, "glb")
            outputFilePathGltf = os.path.join(outputFilePath, "gltf")
            outputFilePathObj = os.path.join(outputFilePath, "obj")
            outputFilePathFbx = os.path.join(outputFilePath, "fbx")
            outputFilePathUsdz = os.path.join(outputFilePath, "usdz")

            # Step 4–8: Config paths
            InputUserCustomConfigRPDXJsonPath      = os.path.join(outputFilePath, "UserCustomConfigRPDX.Json")
            InputUserCustomConfigRPDXJsonGLTFPath  = os.path.join(outputFilePath, "UserCustomConfigRPDX_gltf.Json")
            InputUserCustomConfigRPDXJsonOBJPath   = os.path.join(outputFilePath, "UserCustomConfigRPDX_obj.Json")
            InputUserCustomConfigRPDXJsonFBXPath   = os.path.join(outputFilePath, "UserCustomConfigRPDX_fbx.Json")
            InputUserCustomConfigRPDXJsonUSDZPath  = os.path.join(outputFilePath, "UserCustomConfigRPDX_usdz.Json")

            # Step 9: Build CLI command
            cmd = [
                "rpdx", "-i", inputFilePath,
                "--read_config", InputUserCustomConfigRPDXJsonPath,
                "-e", outputFilePathGlb,
                "--read_config", InputUserCustomConfigRPDXJsonGLTFPath,
                "-e", outputFilePathGltf,
                "--read_config", InputUserCustomConfigRPDXJsonOBJPath,
                "-e", outputFilePathObj,
                "--read_config", InputUserCustomConfigRPDXJsonFBXPath,
                "-e", outputFilePathFbx,
                "-r"
            ]

            # Step 10: Print and run the command
            print("Executing:", " ".join(cmd))
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error while executing rpdx: {e}")

    def update_file_table(self, file_paths):
        for file_path in file_paths:
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            self.file_table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
            self.file_table.setItem(row_position, 1, QTableWidgetItem(file_path.split("/")[-1]))
            self.file_table.setItem(row_position, 2, QTableWidgetItem(file_path))

    def clear_file_table_and_drop_area(self):
        self.file_table.setRowCount(0)
        # self.drop_area.clear()

    def create_scene_graph_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scene Graph Flattening
        scene_box = CollapsibleBox("Scene Graph Flattening")
        
        flattening_layout = QHBoxLayout()
        flattening_layout.addWidget(QLabel("Flattening Method:"))
        flattening_combo = QComboBox()
        flattening_combo.addItems(["auto", "byOpacity"])
        flattening_combo.setCurrentText("byOpacity")
        flattening_layout.addWidget(flattening_combo)
        scene_box.addLayout(flattening_layout)
        
        split_layout = QHBoxLayout()
        split_layout.addWidget(QLabel("Split Mode:"))
        split_combo = QComboBox()
        split_combo.addItems(["auto", "byOpacity"])
        split_combo.setCurrentText("byOpacity")
        split_layout.addWidget(split_combo)
        scene_box.addLayout(split_layout)
        
        depth_layout = QVBoxLayout()
        depth_layout.addWidget(QLabel("Preserve Scene Depth Level:"))
        depth_slider = QSlider(Qt.Horizontal)
        depth_slider.setMinimum(1)
        depth_slider.setMaximum(20)
        depth_slider.setValue(1)
        depth_slider.setTickPosition(QSlider.TicksBelow)
        depth_slider.setTickInterval(2)
        depth_layout.addWidget(depth_slider)
        scene_box.addLayout(depth_layout)
        
        layout.addWidget(scene_box)
        
        return panel
    
    def create_3d_edit_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Mesh Normals
        normals_box = CollapsibleBox("Mesh Normals")
        normals_box.addWidget(QCheckBox("Recompute input Normals"))
        
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Normal Hard Angle Threshold (Degrees):"))
        angle_spin = QDoubleSpinBox()
        angle_spin.setRange(0, 180)
        angle_spin.setValue(60.0)
        angle_layout.addWidget(angle_spin)
        normals_box.addLayout(angle_layout)
        
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Normal Compute Method:"))
        method_combo = QComboBox()
        method_combo.addItems(["area", "full"])
        method_layout.addWidget(method_combo)
        normals_box.addLayout(method_layout)
        
        layout.addWidget(normals_box)
        
        # Model Edit
        model_box = CollapsibleBox("Model Edit")
        model_box.addWidget(QCheckBox("Model Edit"))
        
        scaling_layout = QHBoxLayout()
        scaling_layout.addWidget(QLabel("Scaling Factor:"))
        scaling_combo = QComboBox()
        scaling_combo.addItems(["inches 39.37", "cm 100", "mm 100"])
        scaling_layout.addWidget(scaling_combo)
        model_box.addLayout(scaling_layout)
        
        model_box.addWidget(QCheckBox("Center Model"))
        layout.addWidget(model_box)
        
        # Material Edit
        material_box = CollapsibleBox("Material Edit")
        material_box.addWidget(QCheckBox("Material Edit"))
        material_box.addWidget(QCheckBox("Material Edit Replacer"))
        layout.addWidget(material_box)
        
        return panel
    
    def create_mesh_culling_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Occlusion Culling
        occlusion_box = CollapsibleBox("Occlusion Culling")
        occlusion_box.addWidget(QCheckBox("Occlusion Culling"))
        occlusion_box.addWidget(QCheckBox("Per Mesh"))
        layout.addWidget(occlusion_box)
        
        # Small Feature Culling
        feature_box = CollapsibleBox("Small Feature Culling")
        feature_box.addWidget(QCheckBox("Small Feature Culling"))
        layout.addWidget(feature_box)
        
        # Size Threshold
        threshold_box = CollapsibleBox("Size Threshold")
        
        # Radio buttons for threshold options
        threshold_radio_layout = QHBoxLayout()
        
        radio_group = QButtonGroup(panel)
        relative_radio = QRadioButton("Relative Percentage bbox")
        value_radio = QRadioButton("Value")
        radio_group.addButton(relative_radio)
        radio_group.addButton(value_radio)
        threshold_radio_layout.addWidget(relative_radio)
        threshold_radio_layout.addWidget(value_radio)
        threshold_box.addLayout(threshold_radio_layout)
        
        # Relative percentage widget
        relative_widget = QWidget()
        relative_layout = QVBoxLayout(relative_widget)
        relative_layout.setContentsMargins(0, 0, 0, 0)
        
        relative_slider = QSlider(Qt.Horizontal)
        relative_slider.setMinimum(1)
        relative_slider.setMaximum(100)
        relative_slider.setValue(10)
        relative_slider.setTickPosition(QSlider.TicksBelow)
        relative_slider.setTickInterval(10)
        relative_layout.addWidget(QLabel("Relative Percentage:"))
        relative_layout.addWidget(relative_slider)
        
        # Value widget
        value_widget = QWidget()
        value_layout = QVBoxLayout(value_widget)
        value_layout.setContentsMargins(0, 0, 0, 0)
        
        value_spin = QSpinBox()
        value_spin.setRange(0, 1000)
        value_layout.addWidget(QLabel("Value:"))
        value_layout.addWidget(value_spin)
        
        threshold_box.addWidget(relative_widget)
        threshold_box.addWidget(value_widget)
        
        # Set up initial state
        relative_radio.setChecked(True)
        value_widget.hide()
        
        # Connect radio buttons to show/hide corresponding widgets
        def toggle_threshold_widgets():
            relative_widget.setVisible(relative_radio.isChecked())
            value_widget.setVisible(value_radio.isChecked())
        
        relative_radio.toggled.connect(toggle_threshold_widgets)
        value_radio.toggled.connect(toggle_threshold_widgets)
        
        layout.addWidget(threshold_box)
        
        return panel
    
    def create_optimize_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1) 3D Model Optimization Method
        model_opt_box = CollapsibleBox("3D Model Optimization Method")
        model_opt_box.setCheckable(True)
        model_opt_box.setChecked(False)
        
        # 1.1) 3D Model Optimization Method checkbox
        model_opt_check = QCheckBox("3D Model Optimization Method")
        model_opt_box.addWidget(model_opt_check)
        
        # 1.2) Optimization type radio buttons
        opt_type_group = QButtonGroup()
        mesh_material_radio = QRadioButton("Mesh and Material Optimization")
        material_radio = QRadioButton("Material Optimization")
        opt_type_group.addButton(mesh_material_radio)
        opt_type_group.addButton(material_radio)
        
        opt_type_layout = QHBoxLayout()
        opt_type_layout.addWidget(mesh_material_radio)
        opt_type_layout.addWidget(material_radio)
        model_opt_box.addLayout(opt_type_layout)
        
        # Container for material optimization options
        material_opt_container = QWidget()
        material_opt_layout = QVBoxLayout(material_opt_container)
        material_opt_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1) Material Optimization options
        material_opt_combo = QComboBox()
        material_opt_combo.addItems(["Material Merger", "Keep Material and UVs"])
        material_opt_layout.addWidget(material_opt_combo)
        
        # Material Merger options container
        material_merger_container = QWidget()
        material_merger_layout = QVBoxLayout(material_merger_container)
        material_merger_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1.1.1) Material Merging Method
        merge_method_combo = QComboBox()
        merge_method_combo.addItems(["Auto", "Nothing"])
        material_merger_layout.addWidget(QLabel("Material Merging Method:"))
        material_merger_layout.addWidget(merge_method_combo)
        
        # 1.2.2.1.1.2) Keep Tiled UVs
        keep_tiled_check = QCheckBox("Keep Tiled UVs")
        material_merger_layout.addWidget(keep_tiled_check)
        
        # 1.2.2.1.1.3) Tiling Threshold
        tiling_threshold_spin = QSpinBox()
        tiling_threshold_spin.setRange(0, 100)
        material_merger_layout.addWidget(QLabel("Tiling Threshold:"))
        material_merger_layout.addWidget(tiling_threshold_spin)
        
        material_merger_container.hide()
        material_opt_layout.addWidget(material_merger_container)
        
        # Keep Material and UVs options container
        keep_material_container = QWidget()
        keep_material_layout = QVBoxLayout(keep_material_container)
        keep_material_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1.1.2.1) Force Rebaking Normal Maps
        rebake_check = QCheckBox("Force Rebaking Normal Maps")
        keep_material_layout.addWidget(rebake_check)
        
        # 1.2.2.1.1.2.1) Texture map options
        texture_group = QButtonGroup()
        drop_uniform_radio = QRadioButton("Drop Uniform Texture Maps")
        gen_uv_radio = QRadioButton("Generate 2nd UV Atlas")
        texture_group.addButton(drop_uniform_radio)
        texture_group.addButton(gen_uv_radio)
        
        texture_layout = QHBoxLayout()
        texture_layout.addWidget(drop_uniform_radio)
        texture_layout.addWidget(gen_uv_radio)
        keep_material_layout.addLayout(texture_layout)
        
        # Generate UV Atlas options container
        gen_uv_container = QWidget()
        gen_uv_layout = QVBoxLayout(gen_uv_container)
        gen_uv_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1.1.2.1.1) UV Atlas Mode
        uv_mode_combo = QComboBox()
        uv_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        gen_uv_layout.addWidget(QLabel("UV Atlas Mode:"))
        gen_uv_layout.addWidget(uv_mode_combo)
        
        # 1.2.2.1.1.2.1.2) Packing Resolution
        packing_res_combo = QComboBox()
        packing_res_combo.addItems(["512", "1024", "2048", "4096"])
        gen_uv_layout.addWidget(QLabel("Packing Resolution:"))
        gen_uv_layout.addWidget(packing_res_combo)
        
        gen_uv_container.hide()
        keep_material_layout.addWidget(gen_uv_container)
        
        keep_material_container.hide()
        material_opt_layout.addWidget(keep_material_container)
        
        # Show/hide based on material optimization combo selection
        def update_material_opt_ui():
            material_merger_container.setVisible(material_opt_combo.currentText() == "Material Merger")
            keep_material_container.setVisible(material_opt_combo.currentText() == "Keep Material and UVs")
        
        material_opt_combo.currentTextChanged.connect(update_material_opt_ui)
        
        # Show/hide UV atlas options based on radio selection
        def update_texture_ui():
            gen_uv_container.setVisible(gen_uv_radio.isChecked())
        
        gen_uv_radio.toggled.connect(update_texture_ui)
        
        # 1.2.2.1.2) Material Regenerator
        material_regen_box = CollapsibleBox("Material Regenerator")
        material_regen_box.setCheckable(True)
        material_regen_box.setChecked(False)
        
        regen_group = QButtonGroup()
        gen_atlas_radio = QRadioButton("Generate UV Atlas")
        material_replacer_radio = QRadioButton("Material Replacer")
        regen_group.addButton(gen_atlas_radio)
        regen_group.addButton(material_replacer_radio)
        
        regen_layout = QHBoxLayout()
        regen_layout.addWidget(gen_atlas_radio)
        regen_layout.addWidget(material_replacer_radio)
        material_regen_box.addLayout(regen_layout)
        
        # Generate UV Atlas options container
        gen_atlas_container = QWidget()
        gen_atlas_layout = QVBoxLayout(gen_atlas_container)
        gen_atlas_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1.2.1.1) UV Atlas Mode
        gen_atlas_mode_combo = QComboBox()
        gen_atlas_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        gen_atlas_layout.addWidget(QLabel("UV Atlas Mode:"))
        gen_atlas_layout.addWidget(gen_atlas_mode_combo)
        
        # 1.2.2.1.2.1.2) Packing Resolution
        gen_atlas_res_combo = QComboBox()
        gen_atlas_res_combo.addItems(["512", "1024", "2048", "4096"])
        gen_atlas_layout.addWidget(QLabel("Packing Resolution:"))
        gen_atlas_layout.addWidget(gen_atlas_res_combo)
        
        # 1.2.2.1.2.1.3) Multiple Atlas Factor
        atlas_factor_spin = QSpinBox()
        atlas_factor_spin.setRange(1, 10)
        gen_atlas_layout.addWidget(QLabel("Multiple Atlas Factor:"))
        gen_atlas_layout.addWidget(atlas_factor_spin)
        
        # 1.2.2.1.2.1.4) Texture Baker
        texture_baker_box = CollapsibleBox("Texture Baker")
        texture_baker_box.setCheckable(True)
        texture_baker_box.setChecked(False)
        
        # 1.2.2.1.2.1.4.1) Baking Sample Count
        sample_count_spin = QSpinBox()
        sample_count_spin.setRange(1, 100)
        sample_count_spin.setValue(4)
        texture_baker_box.addWidget(QLabel("Baking Sample Count:"))
        texture_baker_box.addWidget(sample_count_spin)
        
        # 1.2.2.1.2.1.4.2) Texture Map Auto Scaling
        auto_scaling_check = QCheckBox("Texture Map Auto Scaling")
        auto_scaling_check.setChecked(True)
        texture_baker_box.addWidget(auto_scaling_check)
        
        # Auto scaling options container
        auto_scaling_container = QWidget()
        auto_scaling_layout = QVBoxLayout(auto_scaling_container)
        auto_scaling_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.1.2.1.4.1.1) Auto scaling options
        normal_baker_check = QCheckBox("Normal Map Baker")
        ao_baker_check = QCheckBox("Ambient Occlusion Map Baker")
        res_baker_check = QCheckBox("Texture Baking Resolution")
        
        auto_scaling_layout.addWidget(normal_baker_check)
        auto_scaling_layout.addWidget(ao_baker_check)
        auto_scaling_layout.addWidget(res_baker_check)
        
        auto_scaling_check.toggled.connect(auto_scaling_container.setVisible)
        auto_scaling_container.setVisible(auto_scaling_check.isChecked())
        
        texture_baker_box.addWidget(auto_scaling_container)
        gen_atlas_layout.addWidget(texture_baker_box)
        
        gen_atlas_container.hide()
        material_regen_box.addWidget(gen_atlas_container)
        
        # Show/hide based on radio selection
        def update_regen_ui():
            gen_atlas_container.setVisible(gen_atlas_radio.isChecked())
        
        gen_atlas_radio.toggled.connect(update_regen_ui)
        
        material_opt_layout.addWidget(material_regen_box)
        material_opt_container.hide()
        model_opt_box.addWidget(material_opt_container)
        
        # Mesh and Material Optimization container
        mesh_material_container = QWidget()
        mesh_material_layout = QVBoxLayout(mesh_material_container)
        mesh_material_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1) Decimator/Remesher options
        decimator_remesher_group = QButtonGroup()
        decimator_radio = QRadioButton("Decimator")
        remesher_radio = QRadioButton("Remesher")
        decimator_remesher_group.addButton(decimator_radio)
        decimator_remesher_group.addButton(remesher_radio)
        
        decimator_remesher_layout = QHBoxLayout()
        decimator_remesher_layout.addWidget(decimator_radio)
        decimator_remesher_layout.addWidget(remesher_radio)
        mesh_material_layout.addLayout(decimator_remesher_layout)
        
        # Decimator options container
        decimator_container = QWidget()
        decimator_layout = QVBoxLayout(decimator_container)
        decimator_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.1) Decimator options
        decimator_box = CollapsibleBox("Decimator")
        decimator_box.setCheckable(True)
        decimator_box.setChecked(True)
        
        # 1.2.2.2.1.1.1) Decimator checkboxes
        decimator_box.addWidget(QCheckBox("Preserve Topology"))
        decimator_box.addWidget(QCheckBox("Preserve Normals"))
        decimator_box.addWidget(QCheckBox("Preserve Mesh Borders"))
        decimator_box.addWidget(QCheckBox("Preserve Material Borders"))
        decimator_box.addWidget(QCheckBox("Collapse Unconnected Vertices"))
        
        # 1.2.2.2.1.1.2) Boundary Preservation Factor
        boundary_spin = QDoubleSpinBox()
        boundary_spin.setRange(0, 1)
        boundary_spin.setValue(0.5)
        boundary_spin.setSingleStep(0.1)
        decimator_box.addWidget(QLabel("Boundary Preservation Factor:"))
        decimator_box.addWidget(boundary_spin)
        
        # 1.2.2.2.1.1.3) Collapse Distance Threshold
        collapse_spin = QDoubleSpinBox()
        collapse_spin.setRange(0, 1)
        collapse_spin.setValue(0.01)
        collapse_spin.setSingleStep(0.01)
        decimator_box.addWidget(QLabel("Collapse Distance Threshold:"))
        decimator_box.addWidget(collapse_spin)
        
        # 1.2.2.2.1.1.4) Decimation Method
        decimation_combo = QComboBox()
        decimation_combo.addItems(["quadric", "polymeric", "sutaric"])
        decimator_box.addWidget(QLabel("Decimation Method:"))
        decimator_box.addWidget(decimation_combo)
        
        # 1.2.2.2.1.1.5) Target and Material Optimization checkboxes
        target_check = QCheckBox("Target")
        material_opt_check = QCheckBox("Material Optimization")
        
        target_material_layout = QHBoxLayout()
        target_material_layout.addWidget(target_check)
        target_material_layout.addWidget(material_opt_check)
        decimator_box.addLayout(target_material_layout)
        
        # Target options container
        target_container = QWidget()
        target_layout = QVBoxLayout(target_container)
        target_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.1.5.1) Target options
        target_type_group = QButtonGroup()
        faces_radio = QRadioButton("Faces")
        vertices_radio = QRadioButton("Vertices")
        deviation_radio = QRadioButton("Deviation")
        target_type_group.addButton(faces_radio)
        target_type_group.addButton(vertices_radio)
        target_type_group.addButton(deviation_radio)
        
        target_type_layout = QHBoxLayout()
        target_type_layout.addWidget(faces_radio)
        target_type_layout.addWidget(vertices_radio)
        target_type_layout.addWidget(deviation_radio)
        target_layout.addLayout(target_type_layout)
        
        # Faces options container
        faces_container = QWidget()
        faces_layout = QVBoxLayout(faces_container)
        faces_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.1.5.1.1) Faces options
        faces_type_group = QButtonGroup()
        faces_percent_radio = QRadioButton("Faces Percentage")
        faces_value_radio = QRadioButton("Faces Value")
        faces_type_group.addButton(faces_percent_radio)
        faces_type_group.addButton(faces_value_radio)
        
        faces_type_layout = QHBoxLayout()
        faces_type_layout.addWidget(faces_percent_radio)
        faces_type_layout.addWidget(faces_value_radio)
        faces_layout.addLayout(faces_type_layout)
        
        # 1.2.2.2.1.1.5.1.1.1) Faces Percentage slider
        faces_percent_slider = QSlider(Qt.Horizontal)
        faces_percent_slider.setRange(1, 100)
        faces_percent_slider.setValue(100)
        faces_percent_slider.setTickPosition(QSlider.TicksBelow)
        faces_percent_slider.setTickInterval(10)
        faces_layout.addWidget(QLabel("Faces Percentage:"))
        faces_layout.addWidget(faces_percent_slider)
        
        # 1.2.2.2.1.1.5.1.1.2) Faces Value spinner
        faces_value_spin = QSpinBox()
        faces_value_spin.setRange(0, 1000000)
        faces_value_spin.setValue(20000)
        faces_layout.addWidget(QLabel("Faces Value:"))
        faces_layout.addWidget(faces_value_spin)
        
        faces_value_container = QWidget()
        faces_value_layout = QVBoxLayout(faces_value_container)
        faces_value_layout.setContentsMargins(15, 5, 5, 5)
        faces_value_layout.addWidget(faces_value_spin)
        
        faces_percent_container = QWidget()
        faces_percent_layout = QVBoxLayout(faces_percent_container)
        faces_percent_layout.setContentsMargins(15, 5, 5, 5)
        faces_percent_layout.addWidget(faces_percent_slider)
        
        faces_value_container.hide()
        faces_percent_container.hide()
        
        def update_faces_ui():
            faces_percent_container.setVisible(faces_percent_radio.isChecked())
            faces_value_container.setVisible(faces_value_radio.isChecked())
        
        faces_percent_radio.toggled.connect(update_faces_ui)
        faces_value_radio.toggled.connect(update_faces_ui)
        
        faces_layout.addWidget(faces_percent_container)
        faces_layout.addWidget(faces_value_container)
        faces_container.hide()
        target_layout.addWidget(faces_container)
        
        # Show/hide based on target type selection
        def update_target_ui():
            faces_container.setVisible(faces_radio.isChecked())
        
        faces_radio.toggled.connect(update_target_ui)
        target_container.hide()
        decimator_box.addWidget(target_container)
        
        # Show/hide based on target checkbox
        def update_decimator_ui():
            target_container.setVisible(target_check.isChecked())
        
        target_check.toggled.connect(update_decimator_ui)
        
        decimator_layout.addWidget(decimator_box)
        decimator_container.hide()
        mesh_material_layout.addWidget(decimator_container)
        
        # Remesher options container
        remesher_container = QWidget()
        remesher_layout = QVBoxLayout(remesher_container)
        remesher_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.2) Remesher options
        remesher_box = CollapsibleBox("Remesher")
        remesher_box.setCheckable(True)
        remesher_box.setChecked(True)
        
        # 1.2.2.2.1.2.1) Remeshing Method
        remesh_combo = QComboBox()
        remesh_combo.addItems(["voxelization", "shrinkwrap"])
        remesh_combo.setCurrentText("voxelization")
        remesher_box.addWidget(QLabel("Remeshing Method:"))
        remesher_box.addWidget(remesh_combo)
        
        # 1.2.2.2.1.2.2) Resolution
        resolution_spin = QSpinBox()
        resolution_spin.setRange(0, 10000)
        resolution_spin.setValue(0)
        remesher_box.addWidget(QLabel("Resolution:"))
        remesher_box.addWidget(resolution_spin)
        
        # 1.2.2.2.1.2.3) Target and Material Merger checkboxes
        remesh_target_check = QCheckBox("Target")
        remesh_material_check = QCheckBox("Material Merger")
        
        remesh_target_layout = QHBoxLayout()
        remesh_target_layout.addWidget(remesh_target_check)
        remesh_target_layout.addWidget(remesh_material_check)
        remesher_box.addLayout(remesh_target_layout)
        
        # Remesher Target options container
        remesh_target_container = QWidget()
        remesh_target_layout = QVBoxLayout(remesh_target_container)
        remesh_target_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.2.3.1) Target options
        remesh_target_type_group = QButtonGroup()
        remesh_faces_radio = QRadioButton("Faces")
        remesh_vertices_radio = QRadioButton("Vertices")
        remesh_target_type_group.addButton(remesh_faces_radio)
        remesh_target_type_group.addButton(remesh_vertices_radio)
        
        remesh_target_type_layout = QHBoxLayout()
        remesh_target_type_layout.addWidget(remesh_faces_radio)
        remesh_target_type_layout.addWidget(remesh_vertices_radio)
        remesh_target_layout.addLayout(remesh_target_type_layout)
        
        # Remesher Faces options container
        remesh_faces_container = QWidget()
        remesh_faces_layout = QVBoxLayout(remesh_faces_container)
        remesh_faces_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.1.2.3.1.1) Faces options
        remesh_faces_type_group = QButtonGroup()
        remesh_faces_percent_radio = QRadioButton("Faces Percentage")
        remesh_faces_value_radio = QRadioButton("Faces Value")
        remesh_faces_type_group.addButton(remesh_faces_percent_radio)
        remesh_faces_type_group.addButton(remesh_faces_value_radio)
        
        remesh_faces_type_layout = QHBoxLayout()
        remesh_faces_type_layout.addWidget(remesh_faces_percent_radio)
        remesh_faces_type_layout.addWidget(remesh_faces_value_radio)
        remesh_faces_layout.addLayout(remesh_faces_type_layout)
        
        # 1.2.2.2.1.2.3.1.1.1) Faces Percentage slider
        remesh_faces_percent_slider = QSlider(Qt.Horizontal)
        remesh_faces_percent_slider.setRange(1, 100)
        remesh_faces_percent_slider.setValue(100)
        remesh_faces_percent_slider.setTickPosition(QSlider.TicksBelow)
        remesh_faces_percent_slider.setTickInterval(10)
        remesh_faces_layout.addWidget(QLabel("Faces Percentage:"))
        remesh_faces_layout.addWidget(remesh_faces_percent_slider)
        
        # 1.2.2.2.1.2.3.1.1.2) Faces Value spinner
        remesh_faces_value_spin = QSpinBox()
        remesh_faces_value_spin.setRange(0, 1000000)
        remesh_faces_value_spin.setValue(20000)
        remesh_faces_layout.addWidget(QLabel("Faces Value:"))
        remesh_faces_layout.addWidget(remesh_faces_value_spin)
        
        remesh_faces_value_container = QWidget()
        remesh_faces_value_layout = QVBoxLayout(remesh_faces_value_container)
        remesh_faces_value_layout.setContentsMargins(15, 5, 5, 5)
        remesh_faces_value_layout.addWidget(remesh_faces_value_spin)
        
        remesh_faces_percent_container = QWidget()
        remesh_faces_percent_layout = QVBoxLayout(remesh_faces_percent_container)
        remesh_faces_percent_layout.setContentsMargins(15, 5, 5, 5)
        remesh_faces_percent_layout.addWidget(remesh_faces_percent_slider)
        
        remesh_faces_value_container.hide()
        remesh_faces_percent_container.hide()
        
        def update_remesh_faces_ui():
            remesh_faces_percent_container.setVisible(remesh_faces_percent_radio.isChecked())
            remesh_faces_value_container.setVisible(remesh_faces_value_radio.isChecked())
        
        remesh_faces_percent_radio.toggled.connect(update_remesh_faces_ui)
        remesh_faces_value_radio.toggled.connect(update_remesh_faces_ui)
        
        remesh_faces_layout.addWidget(remesh_faces_percent_container)
        remesh_faces_layout.addWidget(remesh_faces_value_container)
        remesh_faces_container.hide()
        remesh_target_layout.addWidget(remesh_faces_container)
        
        # Show/hide based on remesher target type selection
        def update_remesh_target_ui():
            remesh_faces_container.setVisible(remesh_faces_radio.isChecked())
        
        remesh_faces_radio.toggled.connect(update_remesh_target_ui)
        remesh_target_container.hide()
        remesher_box.addWidget(remesh_target_container)
        
        # Show/hide based on remesher target checkbox
        def update_remesher_ui():
            remesh_target_container.setVisible(remesh_target_check.isChecked())
        
        remesh_target_check.toggled.connect(update_remesher_ui)
        
        remesher_layout.addWidget(remesher_box)
        remesher_container.hide()
        mesh_material_layout.addWidget(remesher_container)
        
        # Show/hide based on decimator/remesher selection
        def update_mesh_material_ui():
            decimator_container.setVisible(decimator_radio.isChecked())
            remesher_container.setVisible(remesher_radio.isChecked())
        
        decimator_radio.toggled.connect(update_mesh_material_ui)
        remesher_radio.toggled.connect(update_mesh_material_ui)
        
        # 1.2.2.2.2) Material Regenerator
        mesh_material_regen_box = CollapsibleBox("Material Regenerator")
        mesh_material_regen_box.setCheckable(True)
        mesh_material_regen_box.setChecked(False)
        
        mesh_regen_group = QButtonGroup()
        mesh_gen_atlas_radio = QRadioButton("Generate UV Atlas")
        mesh_material_replacer_radio = QRadioButton("Material Replacer")
        mesh_regen_group.addButton(mesh_gen_atlas_radio)
        mesh_regen_group.addButton(mesh_material_replacer_radio)
        
        mesh_regen_layout = QHBoxLayout()
        mesh_regen_layout.addWidget(mesh_gen_atlas_radio)
        mesh_regen_layout.addWidget(mesh_material_replacer_radio)
        mesh_material_regen_box.addLayout(mesh_regen_layout)
        
        # Generate UV Atlas options container
        mesh_gen_atlas_container = QWidget()
        mesh_gen_atlas_layout = QVBoxLayout(mesh_gen_atlas_container)
        mesh_gen_atlas_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.2.1.1) Unwrapping Method
        unwrap_combo = QComboBox()
        unwrap_combo.addItems(["isometric", "forwardBijective", "fixedBoundary", "fastConformal", "conformal"])
        unwrap_combo.setCurrentText("isometric")
        mesh_gen_atlas_layout.addWidget(QLabel("Unwrapping Method:"))
        mesh_gen_atlas_layout.addWidget(unwrap_combo)
        
        # 1.2.2.2.2.1.2) Segmentation Cut Angle
        cut_angle_slider = QSlider(Qt.Horizontal)
        cut_angle_slider.setRange(1, 360)
        cut_angle_slider.setValue(60)
        cut_angle_slider.setTickPosition(QSlider.TicksBelow)
        cut_angle_slider.setTickInterval(30)
        mesh_gen_atlas_layout.addWidget(QLabel("Segmentation Cut Angle (Degrees):"))
        mesh_gen_atlas_layout.addWidget(cut_angle_slider)
        
        # 1.2.2.2.2.1.3) Segmentation Chart Angle
        chart_angle_slider = QSlider(Qt.Horizontal)
        chart_angle_slider.setRange(1, 360)
        chart_angle_slider.setValue(180)
        chart_angle_slider.setTickPosition(QSlider.TicksBelow)
        chart_angle_slider.setTickInterval(30)
        mesh_gen_atlas_layout.addWidget(QLabel("Segmentation Chart Angle (Degrees):"))
        mesh_gen_atlas_layout.addWidget(chart_angle_slider)
        
        # 1.2.2.2.2.1.4) Maximum Angle error
        max_angle_slider = QSlider(Qt.Horizontal)
        max_angle_slider.setRange(1, 360)
        max_angle_slider.setValue(120)
        max_angle_slider.setTickPosition(QSlider.TicksBelow)
        max_angle_slider.setTickInterval(30)
        mesh_gen_atlas_layout.addWidget(QLabel("Maximum Angle error (Degrees):"))
        mesh_gen_atlas_layout.addWidget(max_angle_slider)
        
        # 1.2.2.2.2.1.5) Maximum Primitives per UV Chart
        max_primitives_spin = QSpinBox()
        max_primitives_spin.setRange(1, 100000)
        max_primitives_spin.setValue(10000)
        mesh_gen_atlas_layout.addWidget(QLabel("Maximum Primitives per UV Chart:"))
        mesh_gen_atlas_layout.addWidget(max_primitives_spin)
        
        # 1.2.2.2.2.1.6) Cut Overlapping UV Pieces
        cut_overlap_check = QCheckBox("Cut Overlapping UV Pieces")
        mesh_gen_atlas_layout.addWidget(cut_overlap_check)
        
        # 1.2.2.2.2.1.7) UV Atlas Mode
        mesh_uv_mode_combo = QComboBox()
        mesh_uv_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        mesh_gen_atlas_layout.addWidget(QLabel("UV Atlas Mode:"))
        mesh_gen_atlas_layout.addWidget(mesh_uv_mode_combo)
        
        # 1.2.2.2.2.1.8) Packing Resolution
        mesh_packing_res_combo = QComboBox()
        mesh_packing_res_combo.addItems(["512", "1024", "2048", "4096"])
        mesh_gen_atlas_layout.addWidget(QLabel("Packing Resolution:"))
        mesh_gen_atlas_layout.addWidget(mesh_packing_res_combo)
        
        # 1.2.2.2.2.1.9) Multiple Atlas Factor
        mesh_atlas_factor_spin = QSpinBox()
        mesh_atlas_factor_spin.setRange(1, 10)
        mesh_gen_atlas_layout.addWidget(QLabel("Multiple Atlas Factor:"))
        mesh_gen_atlas_layout.addWidget(mesh_atlas_factor_spin)
        
        # 1.2.2.2.2.1.10) Texture Baker
        mesh_texture_baker_box = CollapsibleBox("Texture Baker")
        mesh_texture_baker_box.setCheckable(True)
        mesh_texture_baker_box.setChecked(False)
        
        # 1.2.2.2.2.1.10.1) Baking Sample Count
        mesh_sample_count_spin = QSpinBox()
        mesh_sample_count_spin.setRange(1, 100)
        mesh_sample_count_spin.setValue(4)
        mesh_texture_baker_box.addWidget(QLabel("Baking Sample Count:"))
        mesh_texture_baker_box.addWidget(mesh_sample_count_spin)
        
        # 1.2.2.2.2.1.10.2) Texture Map Auto Scaling
        mesh_auto_scaling_check = QCheckBox("Texture Map Auto Scaling")
        mesh_auto_scaling_check.setChecked(True)
        mesh_texture_baker_box.addWidget(mesh_auto_scaling_check)
        
        # Auto scaling options container
        mesh_auto_scaling_container = QWidget()
        mesh_auto_scaling_layout = QVBoxLayout(mesh_auto_scaling_container)
        mesh_auto_scaling_layout.setContentsMargins(15, 5, 5, 5)
        
        # 1.2.2.2.2.1.10.1.1) Auto scaling options
        mesh_normal_baker_check = QCheckBox("Normal Map Baker")
        mesh_ao_baker_check = QCheckBox("Ambient Occlusion Map Baker")
        mesh_res_baker_check = QCheckBox("Texture Baking Resolution")
        
        mesh_auto_scaling_layout.addWidget(mesh_normal_baker_check)
        mesh_auto_scaling_layout.addWidget(mesh_ao_baker_check)
        mesh_auto_scaling_layout.addWidget(mesh_res_baker_check)
        
        mesh_auto_scaling_check.toggled.connect(mesh_auto_scaling_container.setVisible)
        mesh_auto_scaling_container.setVisible(mesh_auto_scaling_check.isChecked())
        
        mesh_texture_baker_box.addWidget(mesh_auto_scaling_container)
        mesh_gen_atlas_layout.addWidget(mesh_texture_baker_box)
        
        mesh_gen_atlas_container.hide()
        mesh_material_regen_box.addWidget(mesh_gen_atlas_container)
        
        # Show/hide based on radio selection
        def update_mesh_regen_ui():
            mesh_gen_atlas_container.setVisible(mesh_gen_atlas_radio.isChecked())
        
        mesh_gen_atlas_radio.toggled.connect(update_mesh_regen_ui)
        
        mesh_material_layout.addWidget(mesh_material_regen_box)
        mesh_material_container.hide()
        model_opt_box.addWidget(mesh_material_container)
        
        # Show/hide based on optimization type selection
        def update_opt_type_ui():
            material_opt_container.setVisible(material_radio.isChecked())
            mesh_material_container.setVisible(mesh_material_radio.isChecked())
        
        material_radio.toggled.connect(update_opt_type_ui)
        mesh_material_radio.toggled.connect(update_opt_type_ui)
        
        # Show/hide based on model optimization checkbox
        def update_model_opt_ui():
            checked = model_opt_check.isChecked()            
            # TBD
            # opt_type_layout.parent().setVisible(checked) # Have Error due to layout as CollapsibleBox
            #
            for i in range(opt_type_layout.parent().count()):
                item = opt_type_layout.parent().itemAt(i)
                widget = item.widget()
                if widget:
                    widget.setVisible(checked)

            material_opt_container.setVisible(checked and material_radio.isChecked())
            mesh_material_container.setVisible(checked and mesh_material_radio.isChecked())
        
        model_opt_check.toggled.connect(update_model_opt_ui)
        
        # Set initial visibility
        update_model_opt_ui()
        update_opt_type_ui()
        
        layout.addWidget(model_opt_box)
        
        # 2) Animation Optimization
        anim_opt_box = CollapsibleBox("Animation Optimization")
        anim_opt_box.setCheckable(True)
        anim_opt_box.setChecked(False)
        
        # Add animation optimization content here if needed
        anim_opt_box.addWidget(QLabel("Animation optimization parameters will be shown here"))
        
        layout.addWidget(anim_opt_box)
        layout.addStretch()
    
        return panel
    
    def create_modifier_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Modifier Settings Collapsible Box
        modifier_box = CollapsibleBox("Modifier Settings")

        # 1.1 Modifier checkbox
        modifier_checkbox = QCheckBox("Modifier")
        modifier_box.addWidget(modifier_checkbox)

        # 1.2 Modifier type dropdown
        modifier_type_layout = QHBoxLayout()
        modifier_type_label = QLabel("Modifier Type:")
        modifier_type_combo = QComboBox()
        modifier_type_combo.addItems(["Size on Screen", "None"])
        modifier_type_combo.setCurrentText("Size on Screen")
        modifier_type_layout.addWidget(modifier_type_label)
        modifier_type_layout.addWidget(modifier_type_combo)
        modifier_box.addLayout(modifier_type_layout)

        # 1.2.1 Size on Screen Collapsible Box
        size_on_screen_box = CollapsibleBox("Size on Screen")

        # 1.2.1.1 Pixel Target
        pixel_target_layout = QHBoxLayout()
        pixel_target_label = QLabel("Pixel Target:")
        pixel_target_spin = QDoubleSpinBox()
        pixel_target_spin.setRange(1.0, 100000.0)
        pixel_target_spin.setValue(1024.00)
        pixel_target_layout.addWidget(pixel_target_label)
        pixel_target_layout.addWidget(pixel_target_spin)
        size_on_screen_box.addLayout(pixel_target_layout)

        # 1.2.1.2 Power of Two Resolution dropdown
        power_res_layout = QHBoxLayout()
        power_res_label = QLabel("Power of Two Resolution:")
        power_res_combo = QComboBox()
        power_res_combo.addItems(["auto", "none"])
        power_res_combo.setCurrentText("none")
        power_res_layout.addWidget(power_res_label)
        power_res_layout.addWidget(power_res_combo)
        size_on_screen_box.addLayout(power_res_layout)

        # Add Size on Screen panel to Modifier
        modifier_box.addWidget(size_on_screen_box)

        # Show/hide Size on Screen panel based on combo selection
        def on_modifier_type_changed(value):
            size_on_screen_box.setVisible(value == "Size on Screen")

        modifier_type_combo.currentTextChanged.connect(on_modifier_type_changed)
        on_modifier_type_changed(modifier_type_combo.currentText())

        layout.addWidget(modifier_box)
        layout.addStretch()
        return panel

    def create_export_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1) Export Format Panel
        export_format_box = CollapsibleBox("Export Format")
        
        # 1.1) Glb/Gltf Format
        gltf_box = CollapsibleBox("Glb/Gltf Format")
        gltf_check = QCheckBox("Glb/Gltf Format")
        gltf_check.setChecked(True)
        gltf_box.addWidget(gltf_check)
        
        # 1.1.1.2) Geometry Compression
        geo_compression_layout = QHBoxLayout()
        geo_compression_layout.addWidget(QLabel("Geometry Compression:"))
        geo_compression_combo = QComboBox()
        geo_compression_combo.addItems(["none", "draco", "dracoLossy", "meshQuantization"])
        geo_compression_layout.addWidget(geo_compression_combo)
        gltf_box.addLayout(geo_compression_layout)
        
        # 1.1.1.3) Exclude Tangents
        exclude_tangents_check = QCheckBox("Exclude Tangents")
        exclude_tangents_check.setChecked(True)
        gltf_box.addWidget(exclude_tangents_check)
        
        # 1.1.1.4) glb PBR Material
        pbr_box = CollapsibleBox("glb PBR Material")
        
        # 1.1.1.4.1-5) PBR Material Checkboxes
        pbr_box.addWidget(QCheckBox("Separate Occlusion Map"))
        pbr_box.addWidget(QCheckBox("Exclude Material Extensions on Export"))
        pbr_box.addWidget(QCheckBox("Force Double Sided Materials"))
        pbr_box.addWidget(QCheckBox("Force Unlit Materials"))
        pbr_box.addWidget(QCheckBox("Convert to MetalRoughness"))
        
        # 1.1.1.4.6) Enable Maximum Texture Map Resolution
        max_texture_check = QCheckBox("Enable Maximum Texture Map Resolution")
        max_texture_check.setChecked(True)
        pbr_box.addWidget(max_texture_check)
        
        # 1.1.1.4.6.1) Maximum Texture Map Resolution
        max_texture_box = CollapsibleBox("Maximum Texture Map Resolution")
        max_texture_layout = QHBoxLayout()
        max_texture_layout.addWidget(QLabel("Default:"))
        max_texture_spin = QSpinBox()
        max_texture_spin.setRange(1, 16384)
        max_texture_spin.setValue(16384)
        max_texture_layout.addWidget(max_texture_spin)
        max_texture_box.addLayout(max_texture_layout)
        pbr_box.addWidget(max_texture_box)
        
        # 1.1.1.4.7) Enable Texture Map Format
        texture_format_check = QCheckBox("Enable Texture Map Format")
        pbr_box.addWidget(texture_format_check)
        
        # 1.1.1.4.7.1) Texture Map Format
        texture_format_box = CollapsibleBox("Enable Texture Map Format")
        texture_format_layout = QHBoxLayout()
        texture_format_layout.addWidget(QLabel("Default:"))
        texture_format_combo = QComboBox()
        texture_format_combo.addItems(["auto", "jpg", "png", "png8", "webp"])
        texture_format_combo.setCurrentText("png")
        texture_format_layout.addWidget(texture_format_combo)
        texture_format_box.addLayout(texture_format_layout)
        pbr_box.addWidget(texture_format_box)
        
        # 1.1.1.4.8) Enable Texture Compression Settings
        texture_compression_check = QCheckBox("Enable Texture Compression Settings")
        pbr_box.addWidget(texture_compression_check)
        
        # 1.1.1.4.8.1) Texture Compression Settings
        texture_compression_box = CollapsibleBox("Texture Compression Settings")
        
        # 1.1.1.4.8.1.1) JPEG
        jpeg_box = CollapsibleBox("JPEG")
        jpeg_quality_layout = QHBoxLayout()
        jpeg_quality_layout.addWidget(QLabel("Quality:"))
        jpeg_quality_spin = QSpinBox()
        jpeg_quality_spin.setRange(1, 100)
        jpeg_quality_spin.setValue(90)
        jpeg_quality_layout.addWidget(jpeg_quality_spin)
        jpeg_box.addLayout(jpeg_quality_layout)
        
        jpeg_normals_layout = QHBoxLayout()
        jpeg_normals_layout.addWidget(QLabel("Quality Normals:"))
        jpeg_normals_spin = QSpinBox()
        jpeg_normals_spin.setRange(1, 100)
        jpeg_normals_spin.setValue(95)
        jpeg_normals_layout.addWidget(jpeg_normals_spin)
        jpeg_box.addLayout(jpeg_normals_layout)
        texture_compression_box.addWidget(jpeg_box)
        
        # 1.1.1.4.8.1.2) WEBP
        webp_box = CollapsibleBox("WEBP")
        webp_quality_layout = QHBoxLayout()
        webp_quality_layout.addWidget(QLabel("Quality:"))
        webp_quality_spin = QSpinBox()
        webp_quality_spin.setRange(1, 100)
        webp_quality_spin.setValue(90)
        webp_quality_layout.addWidget(webp_quality_spin)
        webp_box.addLayout(webp_quality_layout)
        
        webp_normals_layout = QHBoxLayout()
        webp_normals_layout.addWidget(QLabel("Quality Normals:"))
        webp_normals_spin = QSpinBox()
        webp_normals_spin.setRange(1, 100)
        webp_normals_spin.setValue(95)
        webp_normals_layout.addWidget(webp_normals_spin)
        webp_box.addLayout(webp_normals_layout)
        texture_compression_box.addWidget(webp_box)
        
        # 1.1.1.4.8.1.3) KTX
        ktx_box = CollapsibleBox("KTX")
        ktx_speed_layout = QHBoxLayout()
        ktx_speed_layout.addWidget(QLabel("Compression Speed:"))
        ktx_speed_spin = QSpinBox()
        ktx_speed_spin.setRange(1, 10)
        ktx_speed_spin.setValue(2)
        ktx_speed_layout.addWidget(ktx_speed_spin)
        ktx_box.addLayout(ktx_speed_layout)
        
        ktx_quality_layout = QHBoxLayout()
        ktx_quality_layout.addWidget(QLabel("Quality:"))
        ktx_quality_spin = QSpinBox()
        ktx_quality_spin.setRange(1, 256)
        ktx_quality_spin.setValue(128)
        ktx_quality_layout.addWidget(ktx_quality_spin)
        ktx_box.addLayout(ktx_quality_layout)
        texture_compression_box.addWidget(ktx_box)
        
        pbr_box.addWidget(texture_compression_box)
        
        # 1.1.1.4.9) Draco Compression Settings (conditionally shown)
        draco_box = CollapsibleBox("Draco Compression Settings")
        
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position Quantization:"))
        position_spin = QSpinBox()
        position_spin.setRange(1, 20)
        position_spin.setValue(14)
        position_layout.addWidget(position_spin)
        draco_box.addLayout(position_layout)
        
        normal_layout = QHBoxLayout()
        normal_layout.addWidget(QLabel("Normal Quantization:"))
        normal_spin = QSpinBox()
        normal_spin.setRange(1, 20)
        normal_spin.setValue(10)
        normal_layout.addWidget(normal_spin)
        draco_box.addLayout(normal_layout)
        
        uv_layout = QHBoxLayout()
        uv_layout.addWidget(QLabel("UV Quantization:"))
        uv_spin = QSpinBox()
        uv_spin.setRange(1, 20)
        uv_spin.setValue(12)
        uv_layout.addWidget(uv_spin)
        draco_box.addLayout(uv_layout)
        
        bone_layout = QHBoxLayout()
        bone_layout.addWidget(QLabel("Bone Weight Quantization:"))
        bone_spin = QSpinBox()
        bone_spin.setRange(1, 20)
        bone_spin.setValue(12)
        bone_layout.addWidget(bone_spin)
        draco_box.addLayout(bone_layout)
        
        # Add Draco box to main container but hide initially
        pbr_box.addWidget(draco_box)
        draco_box.hide()
        
        # Connect Draco visibility to combo box selection
        def toggle_draco_visibility():
            draco_box.setVisible(geo_compression_combo.currentText() == "draco")
        
        geo_compression_combo.currentTextChanged.connect(toggle_draco_visibility)
        
        # Add PBR box to GLTF box
        gltf_box.addWidget(pbr_box)
        
        # Add GLTF box to Export Format box
        export_format_box.addWidget(gltf_box)
        
        # 1.2) Obj Format
        obj_box = CollapsibleBox("Obj Format")
        obj_check = QCheckBox("Obj Format")
        obj_check.setChecked(True)
        obj_box.addWidget(obj_check)
        
        # 1.2.1.1) Preferred UV Channel
        uv_channel_layout = QHBoxLayout()
        uv_channel_layout.addWidget(QLabel("Preferred UV Channel:"))
        uv_channel_spin = QSpinBox()
        uv_channel_spin.setRange(0, 10)
        uv_channel_spin.setValue(0)
        uv_channel_layout.addWidget(uv_channel_spin)
        obj_box.addLayout(uv_channel_layout)
        
        # 1.2.1.2) mtl Material
        mtl_box = CollapsibleBox("mtl Material")
        
        # 1.2.1.2.1) Displacement To NormalMap Alpha
        displacement_check = QCheckBox("Displacement To NormalMap Alpha")
        mtl_box.addWidget(displacement_check)
        
        # 1.2.1.2.2) Enable Maximum Texture Map Resolution
        obj_max_texture_check = QCheckBox("Enable Maximum Texture Map Resolution")
        obj_max_texture_check.setChecked(True)
        mtl_box.addWidget(obj_max_texture_check)
        
        # 1.2.1.2.2.1) Maximum Texture Map Resolution
        obj_max_texture_box = CollapsibleBox("Maximum Texture Map Resolution")
        obj_max_texture_layout = QHBoxLayout()
        obj_max_texture_layout.addWidget(QLabel("Default:"))
        obj_max_texture_spin = QSpinBox()
        obj_max_texture_spin.setRange(1, 16384)
        obj_max_texture_spin.setValue(16384)
        obj_max_texture_layout.addWidget(obj_max_texture_spin)
        obj_max_texture_box.addLayout(obj_max_texture_layout)
        mtl_box.addWidget(obj_max_texture_box)
        
        # Similar pattern for other texture settings in OBJ format
        # Adding the essential ones for brevity
        
        obj_box.addWidget(mtl_box)
        export_format_box.addWidget(obj_box)
        
        # 1.3) Fbx Format
        fbx_box = CollapsibleBox("Fbx Format")
        fbx_check = QCheckBox("Fbx Format")
        fbx_check.setChecked(True)
        fbx_box.addWidget(fbx_check)
        
        # 1.3.1.1) Unit Conversion
        unit_conversion_check = QCheckBox("Unit Conversion")
        unit_conversion_check.setChecked(True)
        fbx_box.addWidget(unit_conversion_check)
        
        # 1.3.1.2) Exclude Tangents
        fbx_exclude_tangents_check = QCheckBox("Exclude Tangents")
        fbx_exclude_tangents_check.setChecked(True)
        fbx_box.addWidget(fbx_exclude_tangents_check)
        
        # 1.3.1.3) Flip Normal Map Y
        flip_normal_y_check = QCheckBox("Flip Normal Map Y")
        fbx_box.addWidget(flip_normal_y_check)
        
        # 1.3.1.4) Preferred Binary Format
        binary_format_check = QCheckBox("Preferred Binary Format")
        binary_format_check.setChecked(True)
        fbx_box.addWidget(binary_format_check)
        
        # 1.3.1.4) 3dsMax Physical Material
        max_material_box = CollapsibleBox("3dsMax Physical Material")
        
        # Adding texture settings similar to previous formats
        fbx_max_texture_check = QCheckBox("Enable Maximum Texture Map Resolution")
        fbx_max_texture_check.setChecked(True)
        max_material_box.addWidget(fbx_max_texture_check)
        
        fbx_box.addWidget(max_material_box)
        export_format_box.addWidget(fbx_box)
        
        # 1.4) Usdz Format
        usdz_box = CollapsibleBox("Usdz Format")
        usdz_check = QCheckBox("Usdz Format")
        usdz_check.setChecked(True)
        usdz_box.addWidget(usdz_check)
        
        # 1.4.1.1) Force Double Sided Meshes
        double_sided_meshes_check = QCheckBox("Force Double Sided Meshes")
        usdz_box.addWidget(double_sided_meshes_check)
        
        # 1.4.1.2) Usd Preview Surface
        usd_preview_box = CollapsibleBox("Usd Preview Surface")
        
        # Adding texture settings similar to previous formats
        usdz_max_texture_check = QCheckBox("Enable Maximum Texture Map Resolution")
        usdz_max_texture_check.setChecked(True)
        usd_preview_box.addWidget(usdz_max_texture_check)
        
        usdz_box.addWidget(usd_preview_box)
        export_format_box.addWidget(usdz_box)
        
        # Add all to main layout
        layout.addWidget(export_format_box)
        
        # TBD
        # Connect visibility toggles for all conditional elements
        def setup_conditional_visibility(parent_check, child_widget):
            child_widget.setVisible(parent_check.isChecked())             
            parent_check.toggled.connect(child_widget.setVisible)

            # for i in range(opt_type_layout.parent().count()):
            #     item = opt_type_layout.parent().itemAt(i)
            #     widget = item.widget()
            #     if widget:
            #         widget.setVisible(checked)

        
        # Setup visibility for GLTF format elements
        # setup_conditional_visibility(gltf_check, geo_compression_layout.parent()) # TBD
        setup_conditional_visibility(max_texture_check, max_texture_box)
        setup_conditional_visibility(texture_format_check, texture_format_box)
        setup_conditional_visibility(texture_compression_check, texture_compression_box)
        
        # Setup visibility for OBJ format elements
        # setup_conditional_visibility(obj_check, uv_channel_layout.parent()) # TBD
        setup_conditional_visibility(obj_max_texture_check, obj_max_texture_box)
        
        # Setup initial visibility based on checkbox state
        toggle_draco_visibility()
        
        return panel
    
    def create_bottom_buttons(self):
        # Bottom buttons layout
        bottom_layout = QHBoxLayout()
        
        # Group 1 - Left side
        group1_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        export_fbx_btn = QPushButton("Export FBX")
        group1_layout.addWidget(reset_btn)
        group1_layout.addWidget(export_fbx_btn)
        
        # Group 2 - Right side
        group2_layout = QHBoxLayout()
        export_json_btn = QPushButton("Export as Json Only")
        export_run_btn = QPushButton("Export and Run Processor")
        group2_layout.addWidget(export_json_btn)
        group2_layout.addWidget(export_run_btn)
        
        # Add spacer between groups
        bottom_layout.addLayout(group1_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(group2_layout)
        
        self.layout.addLayout(bottom_layout)
    
    def show_panel(self, index):
        # Hide all panels
        for panel in self.parameter_panels:
            panel.hide()
        
        # Show the selected panel
        if 0 <= index < len(self.parameter_panels):
            self.parameter_panels[index].show()


class ModelProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model Processor")
        self.resize(1000, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create banner
        self.create_banner()
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add banner to main layout
        self.main_layout.addWidget(self.banner)
        
        # Create horizontal splitter for panels
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create side panel
        self.side_panel = SidePanel()
        self.splitter.addWidget(self.side_panel)
        
        # Create main panel
        self.main_panel = MainPanel()
        self.splitter.addWidget(self.main_panel)
        
        # Set initial sizes
        self.splitter.setSizes([200, 800])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Connect side panel buttons to show corresponding panels
        for i, btn in enumerate(self.side_panel.buttons):
            btn.clicked.connect(lambda checked, idx=i: self.main_panel.show_panel(idx))
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
    
    def create_banner(self):
        self.banner = QWidget()
        self.banner.setMinimumHeight(80)
        self.banner.setMaximumHeight(80)
        self.banner.setStyleSheet("background-color: #2c3e50; color: white;")
        
        banner_layout = QHBoxLayout(self.banner)
        
        # App logo/title
        app_title = QLabel("Model Processor")
        app_title.setFont(QFont("Arial", 16, QFont.Bold))
        app_title.setStyleSheet("color: white;")
        
        banner_layout.addWidget(app_title)
        banner_layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelProcessorApp()
    window.show()
    sys.exit(app.exec())
