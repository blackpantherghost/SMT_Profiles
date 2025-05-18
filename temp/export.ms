/*
  Enhanced FBX Export Script with Validation
  This script exports selected objects to FBX format with validation checks
  
  Validates:
  1. If selection contains only EditPoly meshes or groups
  2. If objects have scale of [100,100,100]
  3. If scene units are set to inches
  
  Created: May 18, 2025
*/

-- Function to check if an object is a valid mesh (EditPoly) or group
fn isValidObjectType obj = 
(
    -- Check if object is a group
    if isGroupHead obj then
        return true
    
    -- Check if object is an Editable Poly
    if classOf obj == Editable_Poly then
        return true
    
    -- Check if object has Edit_Poly modifier
    if classOf obj == Editable_mesh then
    (
        hasEditPoly = false
        for m in obj.modifiers do
        (
            if classOf m == Edit_Poly then
            (
                hasEditPoly = true
                exit
            )
        )
        return hasEditPoly
    )
    
    -- Check other mesh objects that might have Edit_Poly applied
    if superClassOf obj == GeometryClass then
    (
        hasEditPoly = false
        for m in obj.modifiers do
        (
            if classOf m == Edit_Poly then
            (
                hasEditPoly = true
                exit
            )
        )
        return hasEditPoly
    )
    
    return false
)

-- Function to validate the scale of an object (should be 100,100,100)
fn hasValidScale obj = 
(
    -- Get object scale
    objScale = obj.scale
    
    -- Compare with [100,100,100]
    -- Using a small tolerance for floating point comparison
    tolerance = 0.001
    
    -- Check if scale values are approximately 100
    xValid = abs(objScale.x - 100.0) < tolerance
    yValid = abs(objScale.y - 100.0) < tolerance
    zValid = abs(objScale.z - 100.0) < tolerance
    
    return (xValid and yValid and zValid)
)

-- Function to validate scale for an object and all of its children (if it's a group)
fn validateScaleRecursive obj results =
(
    -- Check the object itself
    if not hasValidScale obj then
    (
        append results (obj.name + " has incorrect scale: " + obj.scale as string)
    )
    
    -- If it's a group, check all children
    if isGroupHead obj then
    (
        -- Get all children in the group
        children = for child in obj.children collect child
        
        -- Recursively check each child
        for child in children do
        (
            validateScaleRecursive child results
        )
    )
    
    return results
)

-- Function to validate if scene units are set to inches
fn areUnitsInches = 
(
    -- Get current unit settings
    currentUnits = units.systemType
    
    -- Check if units are set to inches
    return currentUnits == #inches
)

-- Main validation function that performs all checks
fn validateSelection =
(
    -- Initialize results
    local results = #()
    local isValid = true
    
    -- Check if scene units are set to inches
    if not areUnitsInches() then
    (
        append results "ERROR: Scene units are not set to inches"
        isValid = false
    )
    
    -- Validate selection
    if selection.count == 0 then
    (
        append results "ERROR: Nothing selected"
        isValid = false
    )
    else
    (
        -- Check each selected object
        for obj in selection do
        (
            -- Check if it's a valid object type (EditPoly or Group)
            if not isValidObjectType obj then
            (
                append results ("ERROR: " + obj.name + " is not an Editable Poly or Group")
                isValid = false
            )
            
            -- Check scales (object and children if it's a group)
            scaleResults = #()
            scaleResults = validateScaleRecursive obj scaleResults
            
            if scaleResults.count > 0 then
            (
                for msg in scaleResults do
                (
                    append results ("ERROR: " + msg)
                )
                isValid = false
            )
        )
    )
    
    return #(isValid, results)
)

-- UI Setup
rollout FBXExportRollout "FBX Export Tool with Validation" width:450 height:400
(
    group "FBX Export Settings"
    (
        edittext txt_exportPath "Export Path:" fieldWidth:330 height:20
        button btn_browsePath "Browse..." width:60 align:#right offset:[0,-24]
        edittext txt_presetPath "FBX Preset File:" fieldWidth:330 height:20
        button btn_browsePreset "Browse..." width:60 align:#right offset:[0,-24]
    )
    
    group "Validation"
    (
        checkbox chk_validateBeforeExport "Validate before export" checked:true
        button btn_validateNow "Validate Now" width:100 height:25
    )
    
    group "Actions"
    (
        button btn_export "Export FBX" width:150 height:30
    )
    
    group "Status"
    (
        edittext txt_status "Ready" fieldWidth:430 height:100 readOnly:true
    )
    
    -- Function to browse for an export path
    fn browseSaveFile =
    (
        filePath = getSaveFileName caption:"Select Export Path" filename:"" types:"FBX File (*.fbx)|*.fbx|All Files (*.*)|*.*"
        if filePath != undefined do txt_exportPath.text = filePath
    )
    
    -- Function to browse for a preset file
    fn browsePresetFile =
    (
        presetPath = getOpenFileName caption:"Select FBX Preset File" filename:"" types:"FBX Preset (*.fbxexportpreset)|*.fbxexportpreset|All Files (*.*)|*.*"
        if presetPath != undefined do txt_presetPath.text = presetPath
    )
    
    -- Function to display validation results
    fn showValidationResults returnResults:false =
    (
        -- Run validation
        validation = validateSelection()
        valid = validation[1]
        messages = validation[2]
        
        -- Format results as a string
        resultStr = ""
        
        if valid then
        (
            resultStr = "✓ All validation checks passed!\n"
            resultStr += "✓ Selection contains only EditPoly meshes or groups\n"
            resultStr += "✓ All objects have scale [100,100,100]\n"
            resultStr += "✓ Scene units are set to inches"
            
            txt_status.text = resultStr
        )
        else
        (
            resultStr = "❌ Validation failed. Please fix the following issues:\n\n"
            
            for msg in messages do
            (
                resultStr += msg + "\n"
            )
            
            txt_status.text = resultStr
        )
        
        if returnResults then
            return valid
        else
            return true
    )
    
    -- Function to export the selected objects as FBX
    fn exportToFBX exportPath presetPath validateFirst:true =
    (
        -- Check if file path is provided
        if exportPath == "" or exportPath == undefined then
        (
            txt_status.text = "Error: Please specify an export path!"
            return false
        )
        
        -- Check if preset path is provided and exists
        if presetPath != "" and presetPath != undefined then
        (
            if not doesFileExist presetPath then
            (
                txt_status.text = "Error: Preset file does not exist!"
                return false
            )
        )
        
        -- Run validation if required
        if validateFirst then
        (
            if not showValidationResults returnResults:true then
            (
                -- Validation already updated the status text
                return false
            )
        )
        
        try
        (
            -- Create a temporary script to run the FBX exporter with preset
            tempScript = ""
            
            -- If preset file is provided, add it to the script
            if presetPath != "" and presetPath != undefined then
            (
                tempScript += "FBXExporterSetParam \"LoadExportPresetFile\" \"" + presetPath + "\"\n"
            )
            
            -- Set export options (these will be overridden if a preset is used)
            tempScript += "FBXExporterSetParam \"Animation\" false\n"
            tempScript += "FBXExporterSetParam \"BakeAnimationLayers\" false\n"
            tempScript += "FBXExporterSetParam \"Cameras\" false\n"
            tempScript += "FBXExporterSetParam \"EmbedTextures\" false\n"
            tempScript += "FBXExporterSetParam \"FilterKeyReducer\" false\n"
            tempScript += "FBXExporterSetParam \"GeomAsBone\" false\n"
            tempScript += "FBXExporterSetParam \"Lights\" false\n"
            tempScript += "FBXExporterSetParam \"NormalsPerPoly\" false\n"
            tempScript += "FBXExporterSetParam \"Preserveinstances\" true\n"
            tempScript += "FBXExporterSetParam \"SmoothingGroups\" true\n"
            tempScript += "FBXExporterSetParam \"TangentSpaceExport\" false\n"
            tempScript += "FBXExporterSetParam \"Triangulate\" false\n"
            tempScript += "FBXExporterSetParam \"Units\" \"Inches\"\n"
            tempScript += "FBXExporterSetParam \"FileVersion\" \"FBX202000\"\n"
            
            -- Build the export command (always export selected objects)
            tempScript += "exportFile \"" + exportPath + "\" #noPrompt selectedOnly:true using:FBXEXP\n"
            
            -- Execute the temporary script
            execute tempScript
            
            txt_status.text = "Success: Exported to " + exportPath
            return true
        )
        catch
        (
            txt_status.text = "Error: " + getCurrentException()
            return false
        )
    )
    
    -- Event handlers
    on btn_browsePath pressed do browseSaveFile()
    on btn_browsePreset pressed do browsePresetFile()
    on btn_validateNow pressed do showValidationResults()
    
    on btn_export pressed do
    (
        exportToFBX txt_exportPath.text txt_presetPath.text validateFirst:chk_validateBeforeExport.checked
    )
)

-- Create and show the rollout
if (FBXExportFloater != undefined) do (closeRolloutFloater FBXExportFloater)
FBXExportFloater = newRolloutFloater "FBX Export Tool with Validation" 470 460
addRollout FBXExportRollout FBXExportFloater

-- Display initial instruction
FBXExportRollout.txt_status.text = "Set paths and click Export FBX to begin"
