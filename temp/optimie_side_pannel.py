
    def create_optimize_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 3D Model Optimization Method
        optimization_box = CollapsibleBox("3D Model Optimization Method")
        
        # 1.1) 3D Model Optimization Method Checkbox
        model_optimization_checkbox = QCheckBox("3D Model Optimization Method")
        model_optimization_checkbox.setChecked(True)  # Default selected
        optimization_box.addWidget(model_optimization_checkbox)
        
        # 1.2) Buttons for selection of optimization type
        optimization_type_widget = QWidget()
        optimization_type_layout = QHBoxLayout(optimization_type_widget)
        optimization_type_layout.setContentsMargins(0, 0, 0, 0)
        
        # Button group for exclusive selection
        optimization_button_group = QButtonGroup(panel)
        optimization_button_group.setExclusive(True)
        
        # 1.2.1) Mesh and Material Optimization button
        mesh_material_btn = QPushButton("Mesh and Material Optimization")
        mesh_material_btn.setCheckable(True)
        mesh_material_btn.setChecked(True)  # Default selected
        optimization_button_group.addButton(mesh_material_btn)
        optimization_type_layout.addWidget(mesh_material_btn)
        
        # 1.2.2) Material Optimization button
        material_btn = QPushButton("Material Optimization")
        material_btn.setCheckable(True)
        optimization_button_group.addButton(material_btn)
        optimization_type_layout.addWidget(material_btn)
        
        optimization_box.addWidget(optimization_type_widget)
        
        # 1.2.1.1.1) Mesh optimization method selection (only visible when Mesh and Material is selected)
        mesh_method_widget = QWidget()
        mesh_method_layout = QHBoxLayout(mesh_method_widget)
        mesh_method_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label for the mesh method selection
        mesh_method_label = QLabel("Mesh Optimization Method:")
        mesh_method_layout.addWidget(mesh_method_label)
        
        # Button group for exclusive selection of mesh method
        mesh_method_button_group = QButtonGroup(panel)
        mesh_method_button_group.setExclusive(True)
        
        # 1.2.1.1.1.1) Decimator button
        decimator_btn = QPushButton("Decimator")
        decimator_btn.setCheckable(True)
        decimator_btn.setChecked(True)  # Default selected
        mesh_method_button_group.addButton(decimator_btn)
        mesh_method_layout.addWidget(decimator_btn)
        
        # 1.2.1.1.1.2) Remesher button
        remesher_btn = QPushButton("Remesher")
        remesher_btn.setCheckable(True)
        mesh_method_button_group.addButton(remesher_btn)
        mesh_method_layout.addWidget(remesher_btn)
        
        optimization_box.addWidget(mesh_method_widget)
        
        # 1.2.1.1.1.1.1) Decimator specific settings (only visible when Decimator is selected)
        decimator_settings_widget = QWidget()
        decimator_settings_layout = QVBoxLayout(decimator_settings_widget)
        decimator_settings_layout.setContentsMargins(10, 10, 10, 10)
        
        # Decimator collapsible box for preservation options
        decimator_box = CollapsibleBox("Decimator")
        
        # Preservation checkboxes
        # 1.2.1.1.1.1.1.1) Preserve Topology
        preserve_topology_cb = QCheckBox("Preserve Topology")
        preserve_topology_cb.setChecked(False)
        decimator_box.addWidget(preserve_topology_cb)
        
        # 1.2.1.1.1.1.1.2) Preserve Normals
        preserve_normals_cb = QCheckBox("Preserve Normals")
        preserve_normals_cb.setChecked(False)
        decimator_box.addWidget(preserve_normals_cb)
        
        # 1.2.1.1.1.1.1.3) Preserve Mesh Borders
        preserve_mesh_borders_cb = QCheckBox("Preserve Mesh Borders")
        preserve_mesh_borders_cb.setChecked(True)  # Default True
        decimator_box.addWidget(preserve_mesh_borders_cb)
        
        # 1.2.1.1.1.1.1.4) Preserve Material Borders
        preserve_material_borders_cb = QCheckBox("Preserve Material Borders")
        preserve_material_borders_cb.setChecked(False)
        decimator_box.addWidget(preserve_material_borders_cb)
        
        # 1.2.1.1.1.1.1.5) Collapse Unconnected Vertices
        collapse_vertices_cb = QCheckBox("Collapse Unconnected Vertices")
        collapse_vertices_cb.setChecked(True)  # Default True
        decimator_box.addWidget(collapse_vertices_cb)
        
        decimator_settings_layout.addWidget(decimator_box)
        
        # 1.2.1.1.1.1.2) Boundary Preservation Factor
        boundary_layout = QHBoxLayout()
        boundary_layout.addWidget(QLabel("Boundary Preservation Factor:"))
        boundary_spin = QDoubleSpinBox()
        boundary_spin.setRange(0.0, 1.0)
        boundary_spin.setSingleStep(0.1)
        boundary_spin.setValue(0.5)  # Default 0.5
        boundary_layout.addWidget(boundary_spin)
        decimator_box.addLayout(boundary_layout)
        
        # 1.2.1.1.1.1.3) Collapse Distance Threshold
        collapse_layout = QHBoxLayout()
        collapse_layout.addWidget(QLabel("Collapse Distance Threshold:"))
        collapse_spin = QDoubleSpinBox()
        collapse_spin.setRange(0.0, 1.0)
        collapse_spin.setSingleStep(0.01)
        collapse_spin.setValue(0.01)  # Default 0.01
        collapse_layout.addWidget(collapse_spin)
        decimator_box.addLayout(collapse_layout)
        
        # 1.2.1.1.1.1.4) Decimation Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Decimation Method:"))
        method_combo = QComboBox()
        method_combo.addItems(["quadric", "polymeric", "sutaric"])
        method_combo.setCurrentText("quadric")  # Default quadric
        method_layout.addWidget(method_combo)
        decimator_box.addLayout(method_layout)
        
        # 1.2.1.1.1.1.5 & 1.2.1.1.1.1.6) Target and Material Optimization
        target_material_layout = QHBoxLayout()
        
        # 1.2.1.1.1.1.5) Target checkbox
        target_cb = QCheckBox("Target")
        target_cb.setChecked(True)  # Default True
        target_material_layout.addWidget(target_cb)
        
        # 1.2.1.1.1.1.6) Material Optimization checkbox
        material_opt_cb = QCheckBox("Material Optimization")
        material_opt_cb.setChecked(True) # Default True
        # target_material_layout.addWidget(material_opt_cb) # TBD
        
        decimator_box.addLayout(target_material_layout)
        
        
        # 1.2.1.1.1.1.6.1) Material Optimization options
        material_opt_widget = QWidget()
        material_opt_layout = QVBoxLayout(material_opt_widget)
        material_opt_layout.setContentsMargins(10, 0, 10, 0)
        
        # 1.2.1.1.1.1.6.2) Material Optimization Combo Box
        material_opt_combo_layout = QHBoxLayout()
        material_opt_combo_layout.addWidget(QLabel("Material Options:"))
        material_opt_combo = QComboBox()
        material_opt_combo.addItems(["Keep Material and UVs", "Material Merger", "Material and UV Aggregator"])
        material_opt_combo.setCurrentText("Material Merger")  # Default Material Merger
        material_opt_combo_layout.addWidget(material_opt_combo)
        material_opt_layout.addLayout(material_opt_combo_layout)
        
        # 1.2.1.1.1.1.6.2.1) Material Merger options (only visible when Material Merger is selected)
        material_merger_widget = QWidget()
        material_merger_layout = QVBoxLayout(material_merger_widget)
        material_merger_layout.setContentsMargins(10, 10, 10, 0)
        
        # 1.2.1.1.1.1.6.2.1.1) Material Regenerator Combo Box
        material_regenerator_layout = QHBoxLayout()
        material_regenerator_layout.addWidget(QLabel("Material Regenerator:"))
        material_regenerator_combo = QComboBox()
        material_regenerator_combo.addItems(["Generate UV Atlas", "Material Replacer"])
        material_regenerator_combo.setCurrentText("Generate UV Atlas")  # Default Generate UV Atlas
        material_regenerator_layout.addWidget(material_regenerator_combo)
        material_merger_layout.addLayout(material_regenerator_layout)
        
        # *** NEW UI ELEMENTS FOR GENERATE UV ATLAS ***
        # 1.2.1.1.1.1.6.2.1.1.1) Generate UV Atlas options
        uv_atlas_options_widget = QWidget()
        uv_atlas_options_layout = QVBoxLayout(uv_atlas_options_widget)
        uv_atlas_options_layout.setContentsMargins(10, 10, 10, 0)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1) Generate UV Atlas - Button layout
        uv_atlas_button_layout = QHBoxLayout()
        
        # Generate UV Atlas button
        uv_atlas_btn = QPushButton("Generate UV Atlas")
        uv_atlas_btn.setCheckable(True)
        uv_atlas_btn.setChecked(True)  # Default checked
        uv_atlas_button_layout.addWidget(uv_atlas_btn)
        
        uv_atlas_options_layout.addLayout(uv_atlas_button_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1) Generate UV Atlas settings
        uv_atlas_settings_widget = QWidget()
        uv_atlas_settings_layout = QVBoxLayout(uv_atlas_settings_widget)
        uv_atlas_settings_layout.setContentsMargins(10, 10, 10, 0)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.1) Unwrapping Method
        unwrapping_method_layout = QHBoxLayout()
        unwrapping_method_layout.addWidget(QLabel("Unwrapping Method:"))
        unwrapping_method_combo = QComboBox()
        unwrapping_method_combo.addItems(["isometric", "forwardBijective", "fixedBoundary", "fastConformal", "conformal"])
        unwrapping_method_combo.setCurrentText("isometric")  # Default isometric
        unwrapping_method_layout.addWidget(unwrapping_method_combo)
        uv_atlas_settings_layout.addLayout(unwrapping_method_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.2) Segmentation Cut Angle
        cut_angle_layout = QVBoxLayout()
        cut_angle_layout.addWidget(QLabel("Segmentation Cut Angle (Degrees):"))
        cut_angle_slider = QSlider(Qt.Horizontal)
        cut_angle_slider.setMinimum(1)
        cut_angle_slider.setMaximum(360)
        cut_angle_slider.setValue(60)  # Default 60
        cut_angle_slider.setTickPosition(QSlider.TicksBelow)
        cut_angle_slider.setTickInterval(30)
        cut_angle_layout.addWidget(cut_angle_slider)
        uv_atlas_settings_layout.addLayout(cut_angle_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.3) Segmentation Chart Angle
        chart_angle_layout = QVBoxLayout()
        chart_angle_layout.addWidget(QLabel("Segmentation Chart Angle (Degrees):"))
        chart_angle_slider = QSlider(Qt.Horizontal)
        chart_angle_slider.setMinimum(1)
        chart_angle_slider.setMaximum(360)
        chart_angle_slider.setValue(180)  # Default 180
        chart_angle_slider.setTickPosition(QSlider.TicksBelow)
        chart_angle_slider.setTickInterval(30)
        chart_angle_layout.addWidget(chart_angle_slider)
        uv_atlas_settings_layout.addLayout(chart_angle_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.4) Maximum Angle Error
        max_angle_error_layout = QVBoxLayout()
        max_angle_error_layout.addWidget(QLabel("Maximum Angle Error (Degrees):"))
        max_angle_error_slider = QSlider(Qt.Horizontal)
        max_angle_error_slider.setMinimum(1)
        max_angle_error_slider.setMaximum(360)
        max_angle_error_slider.setValue(120)  # Default 120
        max_angle_error_slider.setTickPosition(QSlider.TicksBelow)
        max_angle_error_slider.setTickInterval(30)
        max_angle_error_layout.addWidget(max_angle_error_slider)
        uv_atlas_settings_layout.addLayout(max_angle_error_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.5) Maximum Primitives per UV Chart
        max_primitives_layout = QHBoxLayout()
        max_primitives_layout.addWidget(QLabel("Maximum Primitives per UV Chart:"))
        max_primitives_spinner = QSpinBox()
        max_primitives_spinner.setRange(1, 100000)
        max_primitives_spinner.setValue(10000)  # Default 10000
        max_primitives_layout.addWidget(max_primitives_spinner)
        uv_atlas_settings_layout.addLayout(max_primitives_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.6) Cut Overlapping UV Pieces
        cut_overlapping_cb = QCheckBox("Cut Overlapping UV Pieces")
        cut_overlapping_cb.setChecked(False)  # Default unchecked
        uv_atlas_settings_layout.addWidget(cut_overlapping_cb)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.7) UV Atlas Mode
        uv_atlas_mode_layout = QHBoxLayout()
        uv_atlas_mode_layout.addWidget(QLabel("UV Atlas Mode:"))
        uv_atlas_mode_combo = QComboBox()
        uv_atlas_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        uv_atlas_mode_combo.setCurrentText("single")  # Default single
        uv_atlas_mode_layout.addWidget(uv_atlas_mode_combo)
        uv_atlas_settings_layout.addLayout(uv_atlas_mode_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.8) Packing Resolution
        packing_resolution_layout = QHBoxLayout()
        packing_resolution_layout.addWidget(QLabel("Packing Resolution:"))
        packing_resolution_combo = QComboBox()
        packing_resolution_combo.addItems(["512", "1024", "2048", "4096"])
        packing_resolution_combo.setCurrentText("1024")  # Default 1024
        packing_resolution_layout.addWidget(packing_resolution_combo)
        uv_atlas_settings_layout.addLayout(packing_resolution_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.9) Multiple Atlas Factor
        multiple_atlas_factor_layout = QHBoxLayout()
        multiple_atlas_factor_layout.addWidget(QLabel("Multiple Atlas Factor:"))
        multiple_atlas_factor_spinner = QSpinBox()
        multiple_atlas_factor_spinner.setRange(1, 10)
        multiple_atlas_factor_spinner.setValue(1)  # Default 1
        multiple_atlas_factor_layout.addWidget(multiple_atlas_factor_spinner)
        uv_atlas_settings_layout.addLayout(multiple_atlas_factor_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10) Texture Baker Collapsible Box
        texture_baker_box = CollapsibleBox("Texture Baker")
        texture_baker_box.setChecked(True)  # Default enabled
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10.1) Baking Sample Count
        baking_sample_layout = QHBoxLayout()
        baking_sample_layout.addWidget(QLabel("Baking Sample Count:"))
        baking_sample_spinner = QSpinBox()
        baking_sample_spinner.setRange(1, 16)
        baking_sample_spinner.setValue(4)  # Default 4
        baking_sample_layout.addWidget(baking_sample_spinner)
        texture_baker_box.addLayout(baking_sample_layout)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10.2) Texture Map Auto Scaling
        texture_map_auto_scaling_cb = QCheckBox("Texture Map Auto Scaling")
        texture_map_auto_scaling_cb.setChecked(True)  # Default enabled
        texture_baker_box.addWidget(texture_map_auto_scaling_cb)
        
        # Container for auto scaling dependent options
        texture_auto_scaling_widget = QWidget()
        texture_auto_scaling_layout = QVBoxLayout(texture_auto_scaling_widget)
        texture_auto_scaling_layout.setContentsMargins(10, 0, 0, 0)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10.1.1.1) Normal Map Baker
        normal_map_baker_cb = QCheckBox("Normal Map Baker")
        normal_map_baker_cb.setChecked(False)  # Default unchecked
        texture_auto_scaling_layout.addWidget(normal_map_baker_cb)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10.1.1.2) Ambient Occlusion Map Baker
        ambient_occlusion_map_baker_cb = QCheckBox("Ambient Occlusion Map Baker")
        ambient_occlusion_map_baker_cb.setChecked(False)  # Default unchecked
        texture_auto_scaling_layout.addWidget(ambient_occlusion_map_baker_cb)
        
        # 1.2.1.1.1.1.6.2.1.1.1.1.1.10.1.1.3) Texture Baking Resolution
        texture_baking_resolution_cb = QCheckBox("Texture Baking Resolution")
        texture_baking_resolution_cb.setChecked(False)  # Default unchecked
        texture_auto_scaling_layout.addWidget(texture_baking_resolution_cb)
        
        # Add auto scaling dependent options to texture baker
        texture_baker_box.addWidget(texture_auto_scaling_widget)
        
        # Add texture baker to UV Atlas settings
        uv_atlas_settings_layout.addWidget(texture_baker_box)

        # Add the UV Atlas settings to the UV Atlas options
        uv_atlas_options_layout.addWidget(uv_atlas_settings_widget)
        
        # Add UV Atlas options to Material Merger layout
        material_merger_layout.addWidget(uv_atlas_options_widget)
        
        # 1.2.1.1.1.1.6.2.1.2) Material Merging Method Combo Box
        material_merging_method_layout = QHBoxLayout()
        material_merging_method_layout.addWidget(QLabel("Material Merging Method:"))
        material_merging_method_combo = QComboBox()
        material_merging_method_combo.addItems(["Auto", "Nothing"])
        material_merging_method_combo.setCurrentText("Auto")  # Default Auto
        material_merging_method_layout.addWidget(material_merging_method_combo)
        material_merger_layout.addLayout(material_merging_method_layout)
        
        # 1.2.1.1.1.1.6.2.1.3) Keep Tiled UVs Checkbox
        keep_tiled_uvs_cb = QCheckBox("Keep Tiled UVs")
        keep_tiled_uvs_cb.setChecked(True)  # Default True
        material_merger_layout.addWidget(keep_tiled_uvs_cb)
        
        # 1.2.1.1.1.1.6.2.1.4) Tiling Threshold Double Spinner
        tiling_threshold_layout = QHBoxLayout()
        tiling_threshold_layout.addWidget(QLabel("Tiling Threshold:"))
        tiling_threshold_spin = QDoubleSpinBox()
        tiling_threshold_spin.setRange(0.0, 10.0)
        tiling_threshold_spin.setSingleStep(0.1)
        tiling_threshold_spin.setValue(1.5)  # Default 1.5
        tiling_threshold_layout.addWidget(tiling_threshold_spin)
        material_merger_layout.addLayout(tiling_threshold_layout)
        
        # Add Material Merger widget to Material Optimization layout
        material_opt_layout.addWidget(material_merger_widget)
        
        # Add Material Optimization widget to decimator settings - TBD
        # decimator_box.addWidget(material_opt_widget)
        

        # 1.2.1.1.1.1.6.2.2) Elements for "Keep Material and UVs"
        keep_material_widget = QWidget()
        keep_material_layout = QVBoxLayout(keep_material_widget)
        keep_material_layout.setContentsMargins(10, 0, 10, 0)

        force_rebake_cb = QCheckBox("Force Rebaking Normal Maps")
        drop_uniform_cb = QCheckBox("Drop Uniform Texture Maps")
        generate_uv2_cb = QCheckBox("Generate 2nd UV Atlas")

        keep_material_layout.addWidget(force_rebake_cb)
        keep_material_layout.addWidget(drop_uniform_cb)
        keep_material_layout.addWidget(generate_uv2_cb)

        # 1.2.1.1.1.1.6.2.2.3.1) Nested UV options
        uv2_options_widget = QWidget()
        uv2_options_layout = QVBoxLayout(uv2_options_widget)
        uv2_options_layout.setContentsMargins(10, 0, 10, 0)

        unwrap_layout = QHBoxLayout()
        unwrap_layout.addWidget(QLabel("Unwrapping Method:"))
        unwrap_combo = QComboBox()
        unwrap_combo.addItems(["isometric", "forwardBijective", "fixedBoundary", "fastConformal", "conformal"])
        unwrap_combo.setCurrentText("isometric")
        unwrap_layout.addWidget(unwrap_combo)
        uv2_options_layout.addLayout(unwrap_layout)

        atlas_mode_layout = QHBoxLayout()
        atlas_mode_layout.addWidget(QLabel("UV Atlas Mode:"))
        atlas_mode_combo = QComboBox()
        atlas_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        atlas_mode_layout.addWidget(atlas_mode_combo)
        uv2_options_layout.addLayout(atlas_mode_layout)

        packing_res_layout = QHBoxLayout()
        packing_res_layout.addWidget(QLabel("Packing Resolution:"))
        packing_res_combo = QComboBox()
        packing_res_combo.addItems(["512", "1024", "2048", "4096"])
        packing_res_combo.setCurrentText("1024")
        packing_res_layout.addWidget(packing_res_combo)
        uv2_options_layout.addLayout(packing_res_layout)

        keep_material_layout.addWidget(uv2_options_widget)
        material_opt_layout.addWidget(keep_material_widget)

        # Toggle visibility
        keep_material_widget.hide()
        uv2_options_widget.hide()

        # New section - 1.2.1.1.1.1.5.1) Target options
        target_options_widget = QWidget()
        target_options_layout = QVBoxLayout(target_options_widget)
        target_options_layout.setContentsMargins(10, 0, 10, 0)
        
        # 1.2.1.1.1.1.5.1) Target option buttons in horizontal layout
        target_option_buttons_layout = QHBoxLayout()
        
        # Button group for exclusive target options
        target_option_button_group = QButtonGroup(panel)
        target_option_button_group.setExclusive(True)
        
        # 1.2.1.1.1.1.5.1.1) Faces button
        faces_btn = QPushButton("Faces")
        faces_btn.setCheckable(True)
        faces_btn.setChecked(True)  # Default selected
        target_option_button_group.addButton(faces_btn)
        target_option_buttons_layout.addWidget(faces_btn)
        
        # 1.2.1.1.1.1.5.1.2) Vertices button
        vertices_btn = QPushButton("Vertices")
        vertices_btn.setCheckable(True)
        target_option_button_group.addButton(vertices_btn)
        target_option_buttons_layout.addWidget(vertices_btn)
        
        # 1.2.1.1.1.1.5.1.3) Deviation button
        deviation_btn = QPushButton("Deviation")
        deviation_btn.setCheckable(True)
        target_option_button_group.addButton(deviation_btn)
        target_option_buttons_layout.addWidget(deviation_btn)
        
        target_options_layout.addLayout(target_option_buttons_layout)
        
        # 1.2.1.1.1.1.5.1.1) Faces options widget
        faces_options_widget = QWidget()
        faces_options_layout = QVBoxLayout(faces_options_widget)
        faces_options_layout.setContentsMargins(0, 10, 0, 0)
        
        # Faces option buttons layout
        faces_option_buttons_layout = QHBoxLayout()
        
        # Button group for exclusive faces options
        faces_option_button_group = QButtonGroup(panel)
        faces_option_button_group.setExclusive(True)
        
        # 1.2.1.1.1.1.5.1.1.1) Faces Percentage button
        faces_percentage_btn = QPushButton("Faces Percentage")
        faces_percentage_btn.setCheckable(True)
        faces_option_button_group.addButton(faces_percentage_btn)
        faces_option_buttons_layout.addWidget(faces_percentage_btn)
        
        # 1.2.1.1.1.1.5.1.1.2) Faces Value button
        faces_value_btn = QPushButton("Faces Value")
        faces_value_btn.setCheckable(True)
        faces_value_btn.setChecked(True)  # Default selected
        faces_option_button_group.addButton(faces_value_btn)
        faces_option_buttons_layout.addWidget(faces_value_btn)
        
        faces_options_layout.addLayout(faces_option_buttons_layout)
        
        # 1.2.1.1.1.1.5.1.1.1.1) Faces Percentage slider
        faces_percentage_widget = QWidget()
        faces_percentage_layout = QVBoxLayout(faces_percentage_widget)
        faces_percentage_layout.setContentsMargins(10, 10, 10, 0)
        
        faces_percentage_label = QLabel("Faces Percentage:")
        faces_percentage_layout.addWidget(faces_percentage_label)
        
        faces_percentage_slider = QSlider(Qt.Horizontal)
        faces_percentage_slider.setMinimum(1)
        faces_percentage_slider.setMaximum(100)
        faces_percentage_slider.setValue(100)  # Default 100
        faces_percentage_slider.setTickPosition(QSlider.TicksBelow)
        faces_percentage_slider.setTickInterval(10)
        faces_percentage_layout.addWidget(faces_percentage_slider)
        
        faces_options_layout.addWidget(faces_percentage_widget)
        
        # 1.2.1.1.1.1.5.1.1.2.1) Faces Value spinner
        faces_value_widget = QWidget()
        faces_value_layout = QVBoxLayout(faces_value_widget)
        faces_value_layout.setContentsMargins(10, 10, 10, 0)
        
        faces_value_label = QLabel("Faces Value:")
        faces_value_layout.addWidget(faces_value_label)
        
        faces_value_spinner = QSpinBox()
        faces_value_spinner.setRange(1, 1000000)
        faces_value_spinner.setValue(20000)  # Default 20000
        faces_value_layout.addWidget(faces_value_spinner)
        
        faces_options_layout.addWidget(faces_value_widget)
        
        # Add faces options to target options
        target_options_layout.addWidget(faces_options_widget)
        
        # Add target options to decimator settings
        decimator_box.addWidget(target_options_widget)
        # Add Material Optimization widget to decimator settings - TBD/New
        decimator_box.addWidget(material_opt_cb) # TBD
        decimator_box.addWidget(material_opt_widget)
        decimator_box.addLayout(material_opt_layout)
        
        # Remesher Settings
        remesher_settings_widget = QWidget()
        remesher_settings_layout = QVBoxLayout(remesher_settings_widget)
        remesher_settings_layout.setContentsMargins(10, 10, 10, 10)

        remesher_box = CollapsibleBox("Remesher")

        remeshing_method_layout = QHBoxLayout()
        remeshing_method_layout.addWidget(QLabel("Remeshing Method:"))
        remeshing_method_combo = QComboBox()
        remeshing_method_combo.addItems(["voxelization", "shrinkwrap"])
        remeshing_method_combo.setCurrentText("voxelization")
        remeshing_method_layout.addWidget(remeshing_method_combo)
        remesher_box.addLayout(remeshing_method_layout)

        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        resolution_spinner = QSpinBox()
        resolution_spinner.setRange(0, 10000)
        resolution_spinner.setValue(0)
        resolution_layout.addWidget(resolution_spinner)
        remesher_box.addLayout(resolution_layout)

        # Target and Material Merger Checkboxes
        remesh_target_cb = QCheckBox("Target")
        remesh_target_cb.setChecked(True)  # Default True
        remesh_material_merger_cb = QCheckBox("Material Merger")
        target_mat_layout = QHBoxLayout()
        target_mat_layout.addWidget(remesh_target_cb)
        target_mat_layout.addWidget(remesh_material_merger_cb)
        remesher_box.addLayout(target_mat_layout)

        # Target buttons: Faces / Vertices
        target_buttons_widget = QWidget()
        target_buttons_layout = QHBoxLayout(target_buttons_widget)
        remesh_faces_btn = QPushButton("Faces")
        remesh_faces_btn.setCheckable(True)
        remesh_faces_btn.setChecked(True)
        remesh_vertices_btn = QPushButton("Vertices")
        remesh_vertices_btn.setCheckable(True)

        target_buttons_group = QButtonGroup(target_buttons_widget)
        target_buttons_group.setExclusive(True)

        target_buttons_group.addButton(remesh_faces_btn)
        target_buttons_group.addButton(remesh_vertices_btn)
        target_buttons_layout.addWidget(remesh_faces_btn)
        target_buttons_layout.addWidget(remesh_vertices_btn)

        # Faces options: Percentage / Value
        faces_options_widget = QWidget()
        faces_options_layout = QVBoxLayout(faces_options_widget)

        faces_option_buttons_layout = QHBoxLayout()       

        # Faces Percentage button
        remesh_faces_pct_btn = QPushButton("Faces Percentage")
        remesh_faces_pct_btn.setCheckable(True)
        faces_option_buttons_layout.addWidget(remesh_faces_pct_btn)

        # Faces Value button
        remesh_faces_val_btn = QPushButton("Faces Value")
        remesh_faces_val_btn.setCheckable(True)
        remesh_faces_val_btn.setChecked(True)           
        faces_option_buttons_layout.addWidget(remesh_faces_val_btn)

        # Button group for exclusive faces options
        faces_option_group = QButtonGroup(faces_options_widget)
        faces_option_group.setExclusive(True)
        
        faces_option_group.addButton(remesh_faces_pct_btn)
        faces_option_group.addButton(remesh_faces_val_btn)

        faces_options_layout.addLayout(faces_option_buttons_layout)
        target_buttons_layout.addWidget(target_buttons_widget)

        # Percentage slider
        faces_pct_widget = QWidget()
        faces_pct_layout = QVBoxLayout(faces_pct_widget)
        faces_pct_slider = QSlider(Qt.Horizontal)
        faces_pct_slider.setRange(1, 100)
        faces_pct_slider.setValue(100)
        faces_pct_slider.setTickInterval(10)
        faces_pct_slider.setTickPosition(QSlider.TicksBelow)
        faces_pct_layout.addWidget(QLabel("Faces Percentage:"))
        faces_pct_layout.addWidget(faces_pct_slider)

        faces_options_layout.addWidget(faces_pct_widget)

        # Value spinner
        faces_val_widget = QWidget()
        faces_val_layout = QVBoxLayout(faces_val_widget)
        faces_val_spinner = QSpinBox()
        faces_val_spinner.setRange(0, 1000000)
        faces_val_spinner.setValue(20000)
        faces_val_layout.addWidget(QLabel("Faces Value:"))
        faces_val_layout.addWidget(faces_val_spinner)

        faces_options_layout.addWidget(faces_val_widget)

        #TBD
        remesher_box.addWidget(target_buttons_widget)
        remesher_box.addWidget(faces_options_widget)

        # Visibility logic
        target_buttons_widget.hide()
        faces_options_widget.hide()
        faces_pct_widget.hide()
        faces_val_widget.hide()
        
        # Remesher Settings Ends

        # Add decimator settings to main layout
        optimization_box.addWidget(decimator_settings_widget)
        
        # Add the main optimization box to panel layout
        layout.addWidget(optimization_box)
        
        # ---------- NEW: Material Optimization Section for material_btn ----------

        # Container for material-only optimization mode (shown when material_btn is selected)
        material_only_widget = QWidget()
        material_only_layout = QVBoxLayout(material_only_widget)
        material_only_layout.setContentsMargins(10, 0, 10, 0)

        # Material Optimization checkbox
        material_only_checkbox = QCheckBox("Enable Material Optimization")
        material_only_checkbox.setChecked(True)
        material_only_layout.addWidget(material_only_checkbox)

        # Optimization mode selection
        material_mode_layout = QHBoxLayout()
        material_mode_layout.addWidget(QLabel("Material Optimization Mode:"))
        material_mode_combo = QComboBox()
        material_mode_combo.addItems(["Material Merger", "Keep Material and UVs"])
        material_mode_combo.setCurrentText("Material Merger")
        material_mode_layout.addWidget(material_mode_combo)
        material_only_layout.addLayout(material_mode_layout)

        # --- Material Merger Section ---
        material_merger_only_widget = QWidget()
        material_merger_only_layout = QVBoxLayout(material_merger_only_widget)
        material_merger_only_layout.setContentsMargins(10, 0, 10, 0)

        # Material Merging Method
        merging_method_layout = QHBoxLayout()
        merging_method_layout.addWidget(QLabel("Material Merging Method:"))
        merging_method_combo = QComboBox()
        merging_method_combo.addItems(["Auto", "Nothing"])
        merging_method_combo.setCurrentText("Auto")
        merging_method_layout.addWidget(merging_method_combo)
        material_merger_only_layout.addLayout(merging_method_layout)

        # Keep Tiled UVs
        keep_tiled_uvs_btn = QCheckBox("Keep Tiled UVs")
        keep_tiled_uvs_btn.setChecked(True)
        material_merger_only_layout.addWidget(keep_tiled_uvs_btn)

        # Tiling Threshold
        tiling_threshold_layout = QHBoxLayout()
        tiling_threshold_layout.addWidget(QLabel("Tiling Threshold:"))
        tiling_threshold_spin = QSpinBox()
        tiling_threshold_spin.setRange(0, 100)
        tiling_threshold_spin.setValue(10)
        tiling_threshold_layout.addWidget(tiling_threshold_spin)
        material_merger_only_layout.addLayout(tiling_threshold_layout)

        # --- Keep Material and UVs Section ---
        keep_mat_uvs_widget = QWidget()
        keep_mat_uvs_layout = QVBoxLayout(keep_mat_uvs_widget)
        keep_mat_uvs_layout.setContentsMargins(10, 0, 10, 0)

        force_rebake_btn = QCheckBox("Force Rebaking Normal Maps")
        drop_uniform_btn = QCheckBox("Drop Uniform Texture Maps")
        generate_uv2_btn = QCheckBox("Generate 2nd UV Atlas")

        keep_mat_uvs_layout.addWidget(force_rebake_btn)

        # Add horizontal layout for exclusive buttons
        exclusive_btn_layout = QHBoxLayout()
        exclusive_btn_group = QButtonGroup(panel)
        exclusive_btn_group.setExclusive(True)
        exclusive_btn_group.addButton(drop_uniform_btn)
        exclusive_btn_group.addButton(generate_uv2_btn)
        exclusive_btn_layout.addWidget(drop_uniform_btn)
        exclusive_btn_layout.addWidget(generate_uv2_btn)
        keep_mat_uvs_layout.addLayout(exclusive_btn_layout)

        # UV Atlas Mode and Packing Resolution (Only for "Generate 2nd UV Atlas")
        uv2_options_widget = QWidget()
        uv2_options_layout = QVBoxLayout(uv2_options_widget)
        uv2_options_layout.setContentsMargins(10, 0, 10, 0)

        uv_atlas_mode_layout = QHBoxLayout()
        uv_atlas_mode_layout.addWidget(QLabel("UV Atlas Mode:"))
        uv_atlas_mode_combo = QComboBox()
        uv_atlas_mode_combo.addItems(["single", "separateAlpha", "separateNormals"])
        uv_atlas_mode_layout.addWidget(uv_atlas_mode_combo)
        uv2_options_layout.addLayout(uv_atlas_mode_layout)

        packing_res_layout = QHBoxLayout()
        packing_res_layout.addWidget(QLabel("Packing Resolution:"))
        packing_res_combo = QComboBox()
        packing_res_combo.addItems(["512", "1024", "2048", "4096"])
        packing_res_combo.setCurrentText("1024")
        packing_res_layout.addWidget(packing_res_combo)
        uv2_options_layout.addLayout(packing_res_layout)

        keep_mat_uvs_layout.addWidget(uv2_options_widget)

        # Initially hidden
        material_only_widget.hide()
        material_merger_only_widget.hide()
        keep_mat_uvs_widget.hide()
        uv2_options_widget.hide()

        material_only_layout.addWidget(material_merger_only_widget)
        material_only_layout.addWidget(keep_mat_uvs_widget)
        optimization_box.addWidget(material_only_widget)

        # Logic to show/hide the mesh method based on the optimization type selection
        def toggle_mesh_method_visibility():
            mesh_method_widget.setVisible(mesh_material_btn.isChecked())
            # Also update the decimator settings visibility
            if mesh_material_btn.isChecked():
                update_decimator_settings_visibility()
                update_remesher_visibility()
            else:
                decimator_settings_widget.setVisible(False)
                remesher_settings_widget.setVisible(False)
        
        # Logic to show/hide decimator settings based on decimator button selection
        def update_decimator_settings_visibility():
            decimator_settings_widget.setVisible(decimator_btn.isChecked())
        
        # Logic to show/hide target options based on target checkbox selection
        def toggle_target_options_visibility():
            target_options_widget.setVisible(target_cb.isChecked())
        
        # Logic to show/hide faces options based on faces button selection
        def toggle_faces_options_visibility():
            faces_options_widget.setVisible(faces_btn.isChecked())
        
        # Logic to show/hide faces percentage/value widgets based on selection
        def toggle_faces_percentage_value_visibility():
            faces_percentage_widget.setVisible(faces_percentage_btn.isChecked())
            faces_value_widget.setVisible(faces_value_btn.isChecked())
        
        # Logic to show/hide material optimization options based on checkbox
        def toggle_material_opt_visibility():
            material_opt_widget.setVisible(material_opt_cb.isChecked())
        
        # Logic to show/hide material merger options based on combo selection
        def toggle_material_merger_visibility():
            material_merger_widget.setVisible(material_opt_combo.currentText() == "Material Merger")
        
        # Logic to show/hide UV Atlas options based on Material Regenerator combo selection
        def toggle_uv_atlas_options_visibility():
            uv_atlas_options_widget.setVisible(material_regenerator_combo.currentText() == "Generate UV Atlas")
        
        # Logic to show/hide UV Atlas settings based on UV Atlas button state
        def toggle_uv_atlas_settings_visibility():
            uv_atlas_settings_widget.setVisible(uv_atlas_btn.isChecked())
        
        def toggle_keep_material_visibility():
            keep_material_widget.setVisible(material_opt_combo.currentText() == "Keep Material and UVs")
            uv2_options_widget.setVisible(material_opt_combo.currentText() == "Keep Material and UVs" and generate_uv2_cb.isChecked())

        #Remesher Methods
        def update_remesher_visibility():
            remesher_settings_widget.setVisible(remesher_btn.isChecked())

        def toggle_target_block():
            target_buttons_widget.setVisible(remesh_target_cb.isChecked())
            faces_options_widget.setVisible(remesh_target_cb.isChecked() and remesh_faces_btn.isChecked())

        def toggle_faces_options():
            faces_options_widget.setVisible(remesh_faces_btn.isChecked())

        # Logic to show/hide faces percentage/value widgets based on selection
        def toggle_remesh_faces_percentage_value_visibility():
            faces_pct_widget.setVisible(remesh_faces_pct_btn.isChecked())
            faces_val_widget.setVisible(remesh_faces_val_btn.isChecked())
        #Remesher Methods Ends

        #Material only Btn
        # ---------- Logic for visibility ----------

        def toggle_material_only_visibility():
            show = material_btn.isChecked()
            material_only_widget.setVisible(show)
            material_merger_only_widget.setVisible(show and material_mode_combo.currentText() == "Material Merger")
            keep_mat_uvs_widget.setVisible(show and material_mode_combo.currentText() == "Keep Material and UVs")
            uv2_options_widget.setVisible(generate_uv2_btn.isChecked() and keep_mat_uvs_widget.isVisible())

        def toggle_mode():
            material_merger_only_widget.setVisible(material_mode_combo.currentText() == "Material Merger")
            keep_mat_uvs_widget.setVisible(material_mode_combo.currentText() == "Keep Material and UVs")
            uv2_options_widget.setVisible(generate_uv2_btn.isChecked() and material_mode_combo.currentText() == "Keep Material and UVs")
        #Material only Btn ends

        # Enable/disable optimization type and mesh method based on checkbox state
        def toggle_optimization_enabled(checked):
            optimization_type_widget.setEnabled(checked)
            mesh_method_widget.setEnabled(checked and mesh_material_btn.isChecked())
            decimator_settings_widget.setEnabled(checked and mesh_material_btn.isChecked() and decimator_btn.isChecked())
        
        

        # Connect button signals to toggle visibility
        mesh_material_btn.toggled.connect(toggle_mesh_method_visibility)
        material_btn.toggled.connect(toggle_mesh_method_visibility)
        decimator_btn.toggled.connect(update_decimator_settings_visibility)
        remesher_btn.toggled.connect(update_decimator_settings_visibility)
        target_cb.toggled.connect(toggle_target_options_visibility)
        faces_btn.toggled.connect(toggle_faces_options_visibility)
        faces_percentage_btn.toggled.connect(toggle_faces_percentage_value_visibility)
        faces_value_btn.toggled.connect(toggle_faces_percentage_value_visibility)
        material_opt_cb.toggled.connect(toggle_material_opt_visibility)
        material_opt_combo.currentTextChanged.connect(toggle_material_merger_visibility)
        material_regenerator_combo.currentTextChanged.connect(toggle_uv_atlas_options_visibility)
        uv_atlas_btn.toggled.connect(toggle_uv_atlas_settings_visibility)

        model_optimization_checkbox.toggled.connect(toggle_optimization_enabled)

        material_opt_combo.currentTextChanged.connect(toggle_keep_material_visibility)
        generate_uv2_cb.toggled.connect(lambda checked: uv2_options_widget.setVisible(checked and material_opt_combo.currentText() == "Keep Material and UVs"))

        #Remesher Methods Connects
        remesher_btn.toggled.connect(update_remesher_visibility)
        remesh_target_cb.toggled.connect(toggle_target_block)
        remesh_faces_btn.toggled.connect(toggle_faces_options)
        remesh_faces_pct_btn.toggled.connect(toggle_remesh_faces_percentage_value_visibility)
        remesh_faces_val_btn.toggled.connect(toggle_remesh_faces_percentage_value_visibility)
        #Remesher Methods Connects Ends
        
        #Material Only
        material_btn.toggled.connect(toggle_material_only_visibility)
        material_mode_combo.currentTextChanged.connect(toggle_mode)
        generate_uv2_btn.toggled.connect(lambda: uv2_options_widget.setVisible(
            generate_uv2_btn.isChecked() and material_mode_combo.currentText() == "Keep Material and UVs"))
        #Material Only ends   
        
        # Set initial visibility states
        toggle_mesh_method_visibility()
        update_decimator_settings_visibility()
        toggle_target_options_visibility()
        toggle_faces_options_visibility()
        toggle_faces_percentage_value_visibility()
        toggle_material_opt_visibility()
        toggle_material_merger_visibility()
        toggle_uv_atlas_options_visibility()
        toggle_uv_atlas_settings_visibility()    

        #Remesher initial Stets
        update_remesher_visibility()
        toggle_target_block()
        toggle_faces_options()
        toggle_remesh_faces_percentage_value_visibility()
        
        #Remesher initial Stets Ends

        # Materials only : Set initial state
        toggle_material_only_visibility()

        #Remesher Layout
        remesher_settings_layout.addWidget(remesher_box)
        optimization_box.addWidget(remesher_settings_widget)
        #Remesher Layout Ends

        # Set initial enabled states
        toggle_optimization_enabled(model_optimization_checkbox.isChecked())
        layout.addStretch()
        return panel
