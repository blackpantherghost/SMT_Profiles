/*
  FBX Export Script
  This script exports selected objects to FBX format using a specified preset file
  
  Created: May 18, 2025
*/

-- UI Setup
rollout FBXExportRollout "FBX Export Tool" width:400 height:300
(
    group "FBX Export Settings"
    (
        edittext txt_exportPath "Export Path:" fieldWidth:300 height:20
        button btn_browsePath "Browse..." width:60 align:#right offset:[0,-24]
        edittext txt_presetPath "FBX Preset File:" fieldWidth:300 height:20
        button btn_browsePreset "Browse..." width:60 align:#right offset:[0,-24]
        checkbox chk_useSelected "Export Selected Objects Only" checked:true
        button btn_export "Export FBX" width:150 height:30
    )
    
    group "Status"
    (
        edittext txt_status "Ready" fieldWidth:380 height:40 readOnly:true
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
    
    -- Function to export the selected objects as FBX
    fn exportToFBX exportPath presetPath useSelected =
    (
        -- Check if file path is provided
        if exportPath == "" or exportPath == undefined then
        (
            txt_status.text = "Error: Please specify an export path!"
            return false
        )
        
        -- Check if preset path is provided
        if presetPath == "" or presetPath == undefined then
        (
            txt_status.text = "Error: Please specify a preset file!"
            return false
        )
        
        -- Check if preset file exists
        if not doesFileExist presetPath then
        (
            txt_status.text = "Error: Preset file does not exist!"
            return false
        )
        
        -- Check if there are selected objects (if using selection)
        if useSelected and selection.count == 0 then
        (
            txt_status.text = "Error: No objects selected!"
            return false
        )
        
        try
        (
            -- Create a collection of nodes to export
            nodesToExport = #()
            
            if useSelected then
            (
                -- Get selected objects
                for obj in selection do
                (
                    append nodesToExport obj
                )
            )
            else
            (
                -- Get all objects
                for obj in objects do
                (
                    append nodesToExport obj
                )
            )
            
            -- Setup export options
            exporterPlugin = exporterInterface.GetExporter #("Autodesk","FBX")
            if exporterPlugin == undefined then
            (
                txt_status.text = "Error: FBX exporter not found!"
                return false
            )
            
            -- Apply preset
            exporterPlugin.LoadPreset presetPath
            
            -- Export the file
            exportFile exportPath #noPrompt selectedOnly:useSelected using:exporterPlugin
            
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
    on btn_export pressed do
    (
        exportToFBX txt_exportPath.text txt_presetPath.text chk_useSelected.checked
    )
)

-- Create and show the rollout
if (FBXExportFloater != undefined) do (closeRolloutFloater FBXExportFloater)
FBXExportFloater = newRolloutFloater "FBX Export Tool" 420 340
addRollout FBXExportRollout FBXExportFloater

-- Display initial instruction
FBXExportRollout.txt_status.text = "Set paths and click Export FBX to begin"
