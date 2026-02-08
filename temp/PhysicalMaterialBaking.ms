-- ========================================
-- Physical Material Map Baking Script
-- Renderer: Scanline
-- ========================================

global cancelled = false

-- ========================================
-- MATERIAL CONVERSION FUNCTIONS
-- ========================================

-- Convert Physical Material to bake Base Color/Diffuse
fn Convert_Bake_BaseColor_Material material = (
    if (material != undefined) do (
        -- Handle multi-sub materials recursively
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_BaseColor_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Disable all maps except base color (with property existence checks)
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
            
            -- Keep only base color active
            try (material.base_color_map_on = true) catch()
        )
    )
)

fn Convert_Bake_BaseColor_Node node = (
    if isValidNode node then (
        Convert_Bake_BaseColor_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_BaseColor_Node node.children[i]
        )
    )
)

-- Convert Physical Material to bake Roughness
fn Convert_Bake_Roughness_Material material = (
    if (material != undefined) do (
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_Roughness_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Transfer roughness to base color for baking
            local hasRoughnessMap = false
            try (hasRoughnessMap = (material.roughness_map != undefined)) catch()
            
            if hasRoughnessMap then (
                try (material.base_color_map = material.roughness_map) catch()
                try (material.base_color_map_on = true) catch()
            ) else (
                -- If no map, create a solid color based on roughness value
                try (
                    local roughVal = material.roughness * 255
                    material.base_color = color roughVal roughVal roughVal
                ) catch()
            )
            
            -- Disable all other maps
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
        )
    )
)

fn Convert_Bake_Roughness_Node node = (
    if isValidNode node then (
        Convert_Bake_Roughness_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_Roughness_Node node.children[i]
        )
    )
)

-- Convert Physical Material to bake Metalness
fn Convert_Bake_Metalness_Material material = (
    if (material != undefined) do (
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_Metalness_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Transfer metalness to base color for baking
            local hasMetalnessMap = false
            try (hasMetalnessMap = (material.metalness_map != undefined)) catch()
            
            if hasMetalnessMap then (
                try (material.base_color_map = material.metalness_map) catch()
                try (material.base_color_map_on = true) catch()
            ) else (
                -- If no map, create a solid color based on metalness value
                try (
                    local metalVal = material.metalness * 255
                    material.base_color = color metalVal metalVal metalVal
                ) catch()
            )
            
            -- Disable all other maps
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
        )
    )
)

fn Convert_Bake_Metalness_Node node = (
    if isValidNode node then (
        Convert_Bake_Metalness_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_Metalness_Node node.children[i]
        )
    )
)

-- Convert Physical Material to bake Opacity
fn Convert_Bake_Opacity_Material material = (
    if (material != undefined) do (
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_Opacity_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Transfer transparency/opacity to base color
            local hasTransparencyMap = false
            try (hasTransparencyMap = (material.transparency_map != undefined)) catch()
            
            if hasTransparencyMap then (
                try (material.base_color_map = material.transparency_map) catch()
                try (material.base_color_map_on = true) catch()
            ) else (
                -- Create solid color based on transparency value
                try (
                    local opacVal = (1.0 - material.transparency) * 255
                    material.base_color = color opacVal opacVal opacVal
                ) catch()
            )
            
            -- Disable all other maps
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
        )
    )
)

fn Convert_Bake_Opacity_Node node = (
    if isValidNode node then (
        Convert_Bake_Opacity_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_Opacity_Node node.children[i]
        )
    )
)

-- Convert Physical Material to bake Emission/Self-Illumination
fn Convert_Bake_Emission_Material material = (
    if (material != undefined) do (
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_Emission_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Transfer emission to base color
            local hasEmissionMap = false
            try (hasEmissionMap = (material.emission_map != undefined)) catch()
            
            if hasEmissionMap then (
                try (material.base_color_map = material.emission_map) catch()
                try (material.base_color_map_on = true) catch()
            ) else (
                try (material.base_color = material.emit_color) catch()
            )
            
            -- Disable all other maps
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
        )
    )
)

fn Convert_Bake_Emission_Node node = (
    if isValidNode node then (
        Convert_Bake_Emission_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_Emission_Node node.children[i]
        )
    )
)

-- Convert Physical Material to bake Coating
fn Convert_Bake_Coating_Material material = (
    if (material != undefined) do (
        for i = 1 to (getNumSubMtls material) do (
            Convert_Bake_Coating_Material (getSubMtl material i)
        )
        
        if ((classof material) == PhysicalMaterial) do (
            -- Transfer coating to base color
            local hasCoatingMap = false
            try (hasCoatingMap = (material.coating_map != undefined)) catch()
            
            if hasCoatingMap then (
                try (material.base_color_map = material.coating_map) catch()
                try (material.base_color_map_on = true) catch()
            ) else (
                try (
                    local coatVal = material.coating * 255
                    material.base_color = color coatVal coatVal coatVal
                ) catch()
            )
            
            -- Disable all other maps
            try (material.roughness_map_on = false) catch()
            try (material.metalness_map_on = false) catch()
            try (material.bump_map_on = false) catch()
            try (material.displacement_map_on = false) catch()
            try (material.emission_map_on = false) catch()
            try (material.anisotropy_map_on = false) catch()
            try (material.aniso_angle_map_on = false) catch()
            try (material.transparency_map_on = false) catch()
            try (material.trans_roughness_map_on = false) catch()
            try (material.scattering_map_on = false) catch()
            try (material.coating_map_on = false) catch()
            try (material.coat_roughness_map_on = false) catch()
            try (material.coat_bump_map_on = false) catch()
            try (material.coat_color_map_on = false) catch()
        )
    )
)

fn Convert_Bake_Coating_Node node = (
    if isValidNode node then (
        Convert_Bake_Coating_Material node.material
    ) else (
        for i = 1 to node.children.count do (
            Convert_Bake_Coating_Node node.children[i]
        )
    )
)

-- ========================================
-- CANCEL DIALOG
-- ========================================

rollout Cancel_Rollout "Baking in Progress" width:200 height:80
(
    label lbl_status "Baking textures..." pos:[10,10]
    button btn_cancel "Cancel Baking" pos:[40,40] width:120
    
    on btn_cancel pressed do
    (
        cancelled = true
        destroyDialog Cancel_Rollout
    )
    
    timer close_timer interval:100 active:true
    on close_timer tick do
    (
        close_timer.active = false
        destroyDialog Cancel_Rollout
    )
)

-- ========================================
-- MAIN BAKING DIALOG
-- ========================================

rollout Bake_Physical_Material_Rollout "Physical Material Baker - Scanline" width:400 height:750
(
    -- Output Settings
    group "Output Settings"
    (
        edittext txt_bake_path "Output Path:" text:"C:\\Temp\\" fieldwidth:280
        button btn_browse_path "Browse..." width:80 align:#right offset:[0,-26]
        
        dropdownlist ddl_resolution "Resolution:" items:#("512", "1024", "2048", "4096", "8192") selection:3
        dropdownlist ddl_format "Format:" items:#("png", "tga", "jpg", "tif", "bmp", "exr") selection:1
        
        spinner spn_bake_channel "Bake Channel:" range:[1,99,1] type:#integer fieldwidth:50
        spinner spn_padding "Padding:" range:[0,32,4] type:#integer fieldwidth:50
    )
    
    -- Map Selection
    group "Maps to Bake"
    (
        checkbox chk_base_color "Base Color (Diffuse)" checked:true
        checkbox chk_roughness "Roughness" checked:false
        checkbox chk_metalness "Metalness" checked:false
        checkbox chk_normal "Normal Map" checked:false
        checkbox chk_opacity "Opacity" checked:false
        checkbox chk_emission "Emission (Self-Illumination)" checked:false
        checkbox chk_coating "Coating" checked:false
        checkbox chk_ambient_occlusion "Ambient Occlusion" checked:false
    )
    
    -- Bake Options
    group "Bake Options"
    (
        checkbox chk_create_material "Create Baked Material" checked:true
        checkbox chk_suffix_name "Add '_baked' suffix to object" checked:true
    )
    
    -- Action Buttons
    button btn_bake "BAKE SELECTED" width:380 height:40
    button btn_check_renderer "Check Current Renderer" width:380 height:25
    
    -- Status
    label lbl_status "" height:30
    
    -- Browse for output path
    on btn_browse_path pressed do
    (
        local bake_folder = getSavePath caption:"Select Bake Output Folder"
        if bake_folder != undefined do
        (
            txt_bake_path.text = bake_folder + "\\"
        )
    )
    
    -- Check renderer
    on btn_check_renderer pressed do
    (
        local current_renderer = renderers.current
        if (classof current_renderer == Default_Scanline_Renderer) then (
            messageBox "Current renderer is Scanline - Ready to bake!" title:"Renderer Check"
        ) else (
            if (queryBox ("Current renderer is: " + (classof current_renderer as string) + "\n\nSwitch to Scanline renderer?") title:"Renderer Check") then (
                renderers.current = Default_Scanline_Renderer()
                messageBox "Renderer switched to Scanline" title:"Success"
            )
        )
    )
    
    -- Main bake function
    on btn_bake pressed do
    (
        -- Validation
        if selection.count == 0 do (
            messageBox "Please select at least one object to bake!" title:"No Selection"
            return false
        )
        
        -- Check if any map is selected
        if (not chk_base_color.checked and not chk_roughness.checked and not chk_metalness.checked and 
            not chk_normal.checked and not chk_opacity.checked and not chk_emission.checked and 
            not chk_coating.checked and not chk_ambient_occlusion.checked) do (
            messageBox "Please select at least one map type to bake!" title:"No Maps Selected"
            return false
        )
        
        -- Verify Scanline renderer
        if (classof renderers.current != Default_Scanline_Renderer) do (
            messageBox "Please set the renderer to Scanline before baking!" title:"Wrong Renderer"
            return false
        )
        
        -- Get settings
        local file_resolution = (ddl_resolution.selected as integer)
        local file_format = ddl_format.selected
        local bake_path = txt_bake_path.text
        
        -- Ensure path ends with backslash
        if (bake_path[bake_path.count] != "\\") do bake_path += "\\"
        
        -- Create directory if it doesn't exist
        makeDir bake_path all:true
        
        lbl_status.text = "Starting baking process..."
        
        -- Process each selected object
        for obj in selection do (
            
            if obj.material == undefined do (
                messageBox ("Object '" + obj.name + "' has no material assigned!") title:"Warning"
                continue
            )
            
            if (classof obj.material != PhysicalMaterial) and (getNumSubMtls obj.material == 0) do (
                messageBox ("Object '" + obj.name + "' does not have a Physical Material!") title:"Warning"
                continue
            )
            
            lbl_status.text = ("Baking: " + obj.name)
            
            cancelled = false
            
            -- BAKE BASE COLOR
            if (chk_base_color.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_BaseColor_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_diffuse = DiffuseMap()
                be_diffuse.outputSzX = be_diffuse.outputSzY = file_resolution
                be_diffuse.fileType = (bake_path + obj.name + "_BaseColor." + file_format)
                be_diffuse.fileName = filenameFromPath be_diffuse.fileType
                be_diffuse.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_diffuse
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE ROUGHNESS
            if (chk_roughness.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_Roughness_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_roughness = DiffuseMap()
                be_roughness.outputSzX = be_roughness.outputSzY = file_resolution
                be_roughness.fileType = (bake_path + obj.name + "_Roughness." + file_format)
                be_roughness.fileName = filenameFromPath be_roughness.fileType
                be_roughness.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_roughness
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE METALNESS
            if (chk_metalness.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_Metalness_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_metalness = DiffuseMap()
                be_metalness.outputSzX = be_metalness.outputSzY = file_resolution
                be_metalness.fileType = (bake_path + obj.name + "_Metalness." + file_format)
                be_metalness.fileName = filenameFromPath be_metalness.fileType
                be_metalness.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_metalness
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE NORMAL MAP
            if (chk_normal.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_normal = NormalsMap()
                be_normal.outputSzX = be_normal.outputSzY = file_resolution
                be_normal.fileType = (bake_path + obj.name + "_Normal." + file_format)
                be_normal.fileName = filenameFromPath be_normal.fileType
                be_normal.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_normal
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE OPACITY
            if (chk_opacity.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_Opacity_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_opacity = DiffuseMap()
                be_opacity.outputSzX = be_opacity.outputSzY = file_resolution
                be_opacity.fileType = (bake_path + obj.name + "_Opacity." + file_format)
                be_opacity.fileName = filenameFromPath be_opacity.fileType
                be_opacity.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_opacity
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE EMISSION
            if (chk_emission.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_Emission_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_emission = DiffuseMap()
                be_emission.outputSzX = be_emission.outputSzY = file_resolution
                be_emission.fileType = (bake_path + obj.name + "_Emission." + file_format)
                be_emission.fileName = filenameFromPath be_emission.fileType
                be_emission.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_emission
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE COATING
            if (chk_coating.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                obj2.material = copy obj.material
                Convert_Bake_Coating_Node obj2
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_coating = DiffuseMap()
                be_coating.outputSzX = be_coating.outputSzY = file_resolution
                be_coating.fileType = (bake_path + obj.name + "_Coating." + file_format)
                be_coating.fileName = filenameFromPath be_coating.fileType
                be_coating.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_coating
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- BAKE AMBIENT OCCLUSION
            if (chk_ambient_occlusion.checked == true) and (not cancelled) do (
                if (NOT cancelled) do CreateDialog Cancel_Rollout modal:true
                
                obj2 = copy obj
                select obj2
                
                obj2.INodeBakeProperties.removeAllBakeElements()
                be_ao = LightingMap()
                be_ao.outputSzX = be_ao.outputSzY = file_resolution
                be_ao.fileType = (bake_path + obj.name + "_AO." + file_format)
                be_ao.fileName = filenameFromPath be_ao.fileType
                be_ao.enabled = true
                
                obj2.INodeBakeProperties.addBakeElement be_ao
                obj2.INodeBakeProperties.bakeEnabled = true
                obj2.INodeBakeProperties.bakeChannel = spn_bake_channel.value as integer
                obj2.INodeBakeProperties.nDilations = spn_padding.value as integer
                
                render rendertype:#bakeSelected vfb:off progressBar:false outputSize:[file_resolution, file_resolution]
                delete obj2
                select obj
            )
            
            -- CREATE BAKED MATERIAL
            if (chk_create_material.checked == true) and (not cancelled) do (
                -- Create a new object with baked material
                obj2 = copy obj
                
                if chk_suffix_name.checked then (
                    obj2.name = obj.name + "_baked"
                ) else (
                    obj2.name = obj.name + "_new"
                )
                
                -- Rename original material
                obj.material.name = obj.material.name + "_original"
                
                -- Create new Physical Material with baked textures
                new_baked_material = PhysicalMaterial()
                new_baked_material.name = obj.name + "_baked"
                
                -- Assign baked textures
                if chk_base_color.checked == true do (
                    new_baked_material.base_color_map = Bitmaptexture fileName:(bake_path + obj.name + "_BaseColor." + file_format)
                    new_baked_material.base_color_map_on = true
                )
                
                if chk_roughness.checked == true do (
                    new_baked_material.roughness_map = Bitmaptexture fileName:(bake_path + obj.name + "_Roughness." + file_format)
                    new_baked_material.roughness_map_on = true
                )
                
                if chk_metalness.checked == true do (
                    new_baked_material.metalness_map = Bitmaptexture fileName:(bake_path + obj.name + "_Metalness." + file_format)
                    new_baked_material.metalness_map_on = true
                )
                
                if chk_normal.checked == true do (
                    new_baked_material.bump_map = Normal_Bump()
                    new_baked_material.bump_map.normal_map = Bitmaptexture fileName:(bake_path + obj.name + "_Normal." + file_format)
                    new_baked_material.bump_map_on = true
                )
                
                if chk_opacity.checked == true do (
                    new_baked_material.transparency_map = Bitmaptexture fileName:(bake_path + obj.name + "_Opacity." + file_format)
                    new_baked_material.transparency_map_on = true
                )
                
                if chk_emission.checked == true do (
                    new_baked_material.emission_map = Bitmaptexture fileName:(bake_path + obj.name + "_Emission." + file_format)
                    new_baked_material.emission_map_on = true
                )
                
                if chk_coating.checked == true do (
                    try (
                        new_baked_material.coating_map = Bitmaptexture fileName:(bake_path + obj.name + "_Coating." + file_format)
                        new_baked_material.coating_map_on = true
                    ) catch (
                        format "Warning: Coating properties not available in this Physical Material mode\n"
                    )
                )
                
                obj2.material = new_baked_material
            )
            
            cancelled = false
        )
        
        lbl_status.text = "Baking Complete!"
        messageBox ("Baking completed successfully!\n\nTextures saved to:\n" + bake_path) title:"Baking Complete"
    )
)

-- Create and show the dialog
CreateDialog Bake_Physical_Material_Rollout
