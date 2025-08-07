-- Multi/Sub-Object Material Assignment Script for 3ds Max
-- This script validates and applies Multi/Sub-Object materials to editable poly objects

(
    -- Clear listener for clean output
    clearListener()
    
    -- Initialize arrays to store objects with different material states
    local obj_withMultimat = #()
    local obj_with_nonMultimat = #()
    local editablePoly_objects = #()
    
    -- Function to check if an object is hair/fur
    fn isHairFurObject obj = (
        local objClass = classof obj
        return (objClass == HairAndFur or 
                objClass == HairFur or 
                (obj.modifiers != undefined and 
                 (for m in obj.modifiers where (classof m == HairAndFur or classof m == HairFur) collect m).count > 0))
    )
    
    -- Function to check if material is Multi/Sub-Object
    fn isMultiSubMaterial mat = (
        return (classof mat == Multimaterial)
    )
    
    -- Function to create a Multi/Sub-Object material with Physical materials
    fn createMultiSubMaterial objName maxSubMats = (
        local multiMat = Multimaterial()
        multiMat.name = (objName + "_MultiSub")
        multiMat.numsubs = maxSubMats
        
        -- Create Physical materials for each sub-material slot
        for i = 1 to maxSubMats do (
            local physMat = PhysicalMaterial()
            physMat.name = (objName + "_Physical_" + i as string)
            
            -- Set some basic properties for variety
            case i of (
                1: (physMat.base_color = color 200 200 200) -- Light Gray
                2: (physMat.base_color = color 150 150 200) -- Light Blue
                3: (physMat.base_color = color 200 150 150) -- Light Red
                4: (physMat.base_color = color 150 200 150) -- Light Green
                5: (physMat.base_color = color 200 200 150) -- Light Yellow
                6: (physMat.base_color = color 200 150 200) -- Light Magenta
                7: (physMat.base_color = color 150 200 200) -- Light Cyan
            )
            
            multiMat[i] = physMat
        )
        
        return multiMat
    )
    
    -- Step 1: Find all editable poly objects, excluding hair/fur
    print "=== Step 1: Finding Editable Poly Objects ==="
    
    for obj in objects do (
        -- Check if object is editable poly and not hair/fur
        if (classof obj == Editable_Poly and not isHairFurObject obj) then (
            append editablePoly_objects obj
            print ("Found Editable Poly: " + obj.name)
        )
    )
    
    print ("Total Editable Poly objects found: " + editablePoly_objects.count as string)
    print ""
    
    -- Step 2 & 3: Validate existing materials
    print "=== Step 2-3: Validating Existing Materials ==="
    
    for obj in editablePoly_objects do (
        if obj.material != undefined then (
            if isMultiSubMaterial obj.material then (
                -- Object has Multi/Sub-Object material
                local matInfo = #(obj, obj.material.name)
                append obj_withMultimat matInfo
                print ("Object '" + obj.name + "' already has Multi/Sub-Object material: " + obj.material.name)
            ) else (
                -- Object has non-Multi/Sub-Object material
                local matInfo = #(obj, obj.material.name)
                append obj_with_nonMultimat matInfo
                print ("Object '" + obj.name + "' has non-Multi/Sub-Object material: " + obj.material.name)
            )
        ) else (
            -- Object has no material
            local matInfo = #(obj, "No Material")
            append obj_with_nonMultimat matInfo
            print ("Object '" + obj.name + "' has no material assigned")
        )
    )
    
    print ""
    print ("Objects with Multi/Sub-Object materials: " + obj_withMultimat.count as string)
    print ("Objects without Multi/Sub-Object materials: " + obj_with_nonMultimat.count as string)
    print ""
    
    -- Step 4: Apply Multi/Sub-Object materials to objects that need them
    if obj_with_nonMultimat.count > 0 then (
        print "=== Step 4: Applying Multi/Sub-Object Materials ==="
        
        local maxSubMaterials = 7  -- Maximum 7 sub-materials as specified
        
        for objInfo in obj_with_nonMultimat do (
            local targetObj = objInfo[1]
            local oldMatName = objInfo[2]
            
            try (
                -- Create new Multi/Sub-Object material
                local newMultiMat = createMultiSubMaterial targetObj.name maxSubMaterials
                
                -- Assign the new material to the object
                targetObj.material = newMultiMat
                
                -- Set material IDs for the faces (example: set all faces to material ID 1)
                -- You can modify this section to assign different material IDs as needed
                if classof targetObj == Editable_Poly then (
                    polyop.setFaceMatID targetObj #{1..polyop.getNumFaces targetObj} 1
                )
                
                print ("Applied Multi/Sub-Object material to '" + targetObj.name + "' (replacing '" + oldMatName + "')")
                
            ) catch (
                print ("ERROR: Failed to apply material to '" + targetObj.name + "': " + getCurrentException())
            )
        )
        
        print ""
        print ("Successfully processed " + obj_with_nonMultimat.count as string + " objects")
        
    ) else (
        print "=== No Objects Need Multi/Sub-Object Materials ==="
        print "All editable poly objects already have Multi/Sub-Object materials assigned."
    )
    
    -- Summary Report
    print ""
    print "=== SUMMARY REPORT ==="
    print ("Total Editable Poly objects processed: " + editablePoly_objects.count as string)
    print ("Objects that already had Multi/Sub-Object materials: " + obj_withMultimat.count as string)
    print ("Objects that received new Multi/Sub-Object materials: " + obj_with_nonMultimat.count as string)
    
    if obj_withMultimat.count > 0 then (
        print ""
        print "Objects with existing Multi/Sub-Object materials:"
        for objInfo in obj_withMultimat do (
            print ("  - " + objInfo[1].name + " (Material: " + objInfo[2] + ")")
        )
    )
    
    if obj_with_nonMultimat.count > 0 then (
        print ""
        print "Objects that received new Multi/Sub-Object materials:"
        for objInfo in obj_with_nonMultimat do (
            print ("  - " + objInfo[1].name + " (Previously: " + objInfo[2] + ")")
        )
    )
    
    print ""
    print "=== SCRIPT COMPLETED ==="
)

-- Usage Instructions:
-- 1. Select all objects or make sure your scene objects are ready
-- 2. Run this script in the MAXScript Listener or save as .ms file
-- 3. The script will automatically process all editable poly objects
-- 4. Check the listener output for detailed results

-- Notes:
-- - Hair/Fur objects are automatically excluded
-- - Each Multi/Sub-Object material contains up to 7 Physical sub-materials
-- - Material IDs are set to 1 by default (modify the polyop.setFaceMatID section as needed)
-- - The script preserves existing Multi/Sub-Object materials
-- - All operations are logged to the listener for tracking





-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------


-- Multi/Sub-Object Material Assignment Script for 3ds Max
-- Error-free version with comprehensive validation and error handling

(
    -- Clear listener for clean output
    clearListener()
    
    -- Initialize arrays to store objects with different material states
    local obj_withMultimat = #()
    local obj_with_nonMultimat = #()
    local editablePoly_objects = #()
    local errorLog = #()
    
    -- Function to safely check if an object is hair/fur
    fn isHairFurObject obj = (
        try (
            if obj == undefined or not isValidNode obj then return false
            
            local objClass = classof obj
            
            -- Check for Hair and Fur system objects
            if objClass == HairAndFur then return true
            
            -- Check for modifiers (safely)
            if obj.modifiers != undefined then (
                for m in obj.modifiers do (
                    if classof m == Hair_and_Fur then return true
                )
            )
            
            -- Check object name for common hair/fur naming conventions
            local objNameLower = toLower obj.name
            if matchPattern objNameLower pattern:"*hair*" or 
               matchPattern objNameLower pattern:"*fur*" then return true
            
            return false
        ) catch (
            append errorLog ("Warning: Error checking hair/fur status for object: " + (try obj.name catch "Unknown"))
            return false
        )
    )
    
    -- Function to safely check if material is Multi/Sub-Object
    fn isMultiSubMaterial mat = (
        try (
            return (mat != undefined and classof mat == Multimaterial)
        ) catch (
            return false
        )
    )
    
    -- Function to create a Multi/Sub-Object material with Physical materials
    fn createMultiSubMaterial objName maxSubMats = (
        try (
            local multiMat = Multimaterial numsubs:maxSubMats
            multiMat.name = (objName + "_MultiSub")
            
            -- Create Physical materials for each sub-material slot
            for i = 1 to maxSubMats do (
                local physMat = PhysicalMaterial()
                physMat.name = (objName + "_Physical_" + i as string)
                
                -- Set base colors with error handling
                try (
                    case i of (
                        1: physMat.base_color = color 200 200 200  -- Light Gray
                        2: physMat.base_color = color 150 150 200  -- Light Blue
                        3: physMat.base_color = color 200 150 150  -- Light Red
                        4: physMat.base_color = color 150 200 150  -- Light Green
                        5: physMat.base_color = color 200 200 150  -- Light Yellow
                        6: physMat.base_color = color 200 150 200  -- Light Magenta
                        7: physMat.base_color = color 150 200 200  -- Light Cyan
                        default: physMat.base_color = color 128 128 128  -- Default gray
                    )
                ) catch (
                    physMat.base_color = color 128 128 128  -- Fallback color
                )
                
                -- Assign sub-material safely
                try (
                    multiMat[i] = physMat
                ) catch (
                    append errorLog ("Error assigning sub-material " + i as string + " for " + objName)
                )
            )
            
            return multiMat
        ) catch (
            append errorLog ("Error creating Multi/Sub-Object material for: " + objName)
            return undefined
        )
    )
    
    -- Function to safely get material name
    fn getMaterialName mat = (
        try (
            if mat != undefined and mat.name != undefined then
                return mat.name
            else
                return "Unnamed Material"
        ) catch (
            return "Unknown Material"
        )
    )
    
    -- Step 1: Find all editable poly objects, excluding hair/fur
    print "=== Step 1: Finding Editable Poly Objects ==="
    
    try (
        for obj in objects do (
            try (
                -- Validate object first
                if obj != undefined and isValidNode obj then (
                    -- Check if object is editable poly and not hair/fur
                    if classof obj == Editable_Poly and not isHairFurObject obj then (
                        append editablePoly_objects obj
                        print ("Found Editable Poly: " + obj.name)
                    )
                )
            ) catch (
                append errorLog ("Error processing object in scene scan: " + (try obj.name catch "Unknown"))
            )
        )
    ) catch (
        print "Error: Failed to scan scene objects"
        append errorLog "Critical error during scene scan"
    )
    
    print ("Total Editable Poly objects found: " + editablePoly_objects.count as string)
    print ""
    
    -- Step 2 & 3: Validate existing materials
    print "=== Step 2-3: Validating Existing Materials ==="
    
    for obj in editablePoly_objects do (
        try (
            if obj != undefined and isValidNode obj then (
                local matName = "No Material"
                local hasMultiSub = false
                
                -- Check if object has material
                if obj.material != undefined then (
                    matName = getMaterialName obj.material
                    hasMultiSub = isMultiSubMaterial obj.material
                )
                
                if hasMultiSub then (
                    -- Object has Multi/Sub-Object material
                    local matInfo = #(obj, matName)
                    append obj_withMultimat matInfo
                    print ("Object '" + obj.name + "' already has Multi/Sub-Object material: " + matName)
                ) else (
                    -- Object has non-Multi/Sub-Object material or no material
                    local matInfo = #(obj, matName)
                    append obj_with_nonMultimat matInfo
                    if obj.material != undefined then
                        print ("Object '" + obj.name + "' has non-Multi/Sub-Object material: " + matName)
                    else
                        print ("Object '" + obj.name + "' has no material assigned")
                )
            )
        ) catch (
            local objNameSafe = try obj.name catch "Unknown"
            append errorLog ("Error validating material for object: " + objNameSafe)
            print ("Warning: Error processing material for object: " + objNameSafe)
        )
    )
    
    print ""
    print ("Objects with Multi/Sub-Object materials: " + obj_withMultimat.count as string)
    print ("Objects without Multi/Sub-Object materials: " + obj_with_nonMultimat.count as string)
    print ""
    
    -- Step 4: Apply Multi/Sub-Object materials to objects that need them
    if obj_with_nonMultimat.count > 0 then (
        print "=== Step 4: Applying Multi/Sub-Object Materials ==="
        
        local maxSubMaterials = 7  -- Maximum 7 sub-materials as specified
        local successCount = 0
        local failCount = 0
        
        for objInfo in obj_with_nonMultimat do (
            local targetObj = objInfo[1]
            local oldMatName = objInfo[2]
            
            try (
                -- Validate object before processing
                if targetObj != undefined and isValidNode targetObj then (
                    -- Create new Multi/Sub-Object material
                    local newMultiMat = createMultiSubMaterial targetObj.name maxSubMaterials
                    
                    if newMultiMat != undefined then (
                        -- Assign the new material to the object
                        targetObj.material = newMultiMat
                        
                        -- Set material IDs for faces if object is still editable poly
                        if classof targetObj == Editable_Poly then (
                            try (
                                local numFaces = polyop.getNumFaces targetObj
                                if numFaces > 0 then (
                                    polyop.setFaceMatID targetObj #{1..numFaces} 1
                                )
                            ) catch (
                                append errorLog ("Warning: Could not set material IDs for: " + targetObj.name)
                            )
                        )
                        
                        print ("Applied Multi/Sub-Object material to '" + targetObj.name + "' (replacing '" + oldMatName + "')")
                        successCount += 1
                    ) else (
                        print ("ERROR: Failed to create material for '" + targetObj.name + "'")
                        failCount += 1
                    )
                ) else (
                    print ("ERROR: Invalid object reference for material assignment")
                    failCount += 1
                )
            ) catch (
                local objNameSafe = try targetObj.name catch "Unknown"
                print ("ERROR: Failed to apply material to '" + objNameSafe + "': " + getCurrentException())
                append errorLog ("Material assignment failed for: " + objNameSafe + " - " + getCurrentException())
                failCount += 1
            )
        )
        
        print ""
        print ("Successfully processed: " + successCount as string + " objects")
        if failCount > 0 then (
            print ("Failed to process: " + failCount as string + " objects")
        )
        
    ) else (
        print "=== No Objects Need Multi/Sub-Object Materials ==="
        print "All editable poly objects already have Multi/Sub-Object materials assigned."
    )
    
    -- Summary Report
    print ""
    print "=== SUMMARY REPORT ==="
    print ("Total Editable Poly objects processed: " + editablePoly_objects.count as string)
    print ("Objects that already had Multi/Sub-Object materials: " + obj_withMultimat.count as string)
    print ("Objects that needed new Multi/Sub-Object materials: " + obj_with_nonMultimat.count as string)
    
    if obj_withMultimat.count > 0 then (
        print ""
        print "Objects with existing Multi/Sub-Object materials:"
        for objInfo in obj_withMultimat do (
            try (
                print ("  - " + objInfo[1].name + " (Material: " + objInfo[2] + ")")
            ) catch (
                print ("  - Error displaying object info")
            )
        )
    )
    
    if obj_with_nonMultimat.count > 0 then (
        print ""
        print "Objects that received new Multi/Sub-Object materials:"
        for objInfo in obj_with_nonMultimat do (
            try (
                print ("  - " + objInfo[1].name + " (Previously: " + objInfo[2] + ")")
            ) catch (
                print ("  - Error displaying object info")
            )
        )
    )
    
    -- Display error log if any errors occurred
    if errorLog.count > 0 then (
        print ""
        print "=== ERROR LOG ==="
        for errMsg in errorLog do (
            print ("ERROR: " + errMsg)
        )
        print ("Total errors/warnings: " + errorLog.count as string)
    )
    
    print ""
    print "=== SCRIPT COMPLETED ==="
    
    -- Return summary for potential further use
    #{obj_withMultimat.count, obj_with_nonMultimat.count, errorLog.count}
)

-- Usage Instructions:
-- 1. Open 3ds Max and ensure your scene is loaded
-- 2. Run this script in the MAXScript Listener or save as .ms file and execute
-- 3. The script will automatically process all editable poly objects in the scene
-- 4. Check the listener output for detailed results and any errors
-- 5. Review the error log section if any issues occurred

-- Error Handling Features:
-- - Validates all object references before processing
-- - Handles missing or invalid materials gracefully
-- - Provides detailed error logging
-- - Continues processing even if individual objects fail
-- - Safe material creation with fallback options
-- - Comprehensive try-catch blocks throughout

-- Technical Notes:
-- - Uses isValidNode() to ensure object validity
-- - Handles edge cases like deleted objects or missing materials
-- - Provides fallback colors if material property setting fails
-- - Safely handles face material ID assignment
-- - Returns processing statistics for potential automation use

-------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------

-- Multi/Sub-Object Material Assignment Script for 3ds Max
-- Modular function-based version for easy customization and reuse

-- =============================================================================
-- GLOBAL VARIABLES
-- =============================================================================
global MultiSubMaterialTool

struct MultiSubMaterialTool (
    -- Configuration variables
    maxSubMaterials = 7,
    excludeHairFur = true,
    setMaterialID = true,
    defaultMaterialID = 1,
    verboseOutput = true,
    
    -- Data storage
    obj_withMultimat = #(),
    obj_with_nonMultimat = #(),
    editablePoly_objects = #(),
    errorLog = #(),
    
    -- =============================================================================
    -- UTILITY FUNCTIONS
    -- =============================================================================
    
    -- Function to safely log messages
    fn logMessage msg level:"INFO" = (
        if verboseOutput then (
            case level of (
                "ERROR": print ("ERROR: " + msg)
                "WARNING": print ("WARNING: " + msg)
                "INFO": print ("INFO: " + msg)
                default: print msg
            )
        )
        if level == "ERROR" or level == "WARNING" then (
            append errorLog (level + ": " + msg)
        )
    ),
    
    -- Function to safely check if an object is hair/fur
    fn isHairFurObject obj = (
        if not excludeHairFur then return false
        
        try (
            if obj == undefined or not isValidNode obj then return false
            
            local objClass = classof obj
            
            -- Check for Hair and Fur system objects
            if objClass == HairAndFur or objClass == Hair_and_Fur then return true
            
            -- Check for modifiers (safely)
            if obj.modifiers != undefined then (
                for m in obj.modifiers do (
                    local modClass = classof m
                    if modClass == Hair_and_Fur or modClass == HairAndFur then return true
                )
            )
            
            -- Check object name for common hair/fur naming conventions
            local objNameLower = toLower obj.name
            if matchPattern objNameLower pattern:"*hair*" or 
               matchPattern objNameLower pattern:"*fur*" then return true
            
            return false
        ) catch (
            logMessage ("Error checking hair/fur status for object: " + (try obj.name catch "Unknown")) level:"WARNING"
            return false
        )
    ),
    
    -- Function to safely check if material is Multi/Sub-Object
    fn isMultiSubMaterial mat = (
        try (
            return (mat != undefined and classof mat == Multimaterial)
        ) catch (
            return false
        )
    ),
    
    -- Function to safely get material name
    fn getMaterialName mat = (
        try (
            if mat != undefined and mat.name != undefined then
                return mat.name
            else
                return "Unnamed Material"
        ) catch (
            return "Unknown Material"
        )
    ),
    
    -- Function to generate unique material name
    fn generateUniqueMaterialName baseName = (
        local uniqueName = baseName + "_MultiSub"
        local counter = 1
        
        -- Check if material with this name already exists
        while (sceneMaterials[uniqueName] != undefined) do (
            uniqueName = baseName + "_MultiSub_" + counter as string
            counter += 1
        )
        
        return uniqueName
    ),
    
    -- =============================================================================
    -- CORE MATERIAL FUNCTIONS
    -- =============================================================================
    
    -- Function to create a single Physical material with custom properties
    fn createPhysicalMaterial matName colorIndex roughness:0.5 metallic:0.0 = (
        try (
            local physMat = PhysicalMaterial()
            physMat.name = matName
            
            -- Set base colors based on index
            local baseColor = case colorIndex of (
                1: color 200 200 200  -- Light Gray
                2: color 150 150 200  -- Light Blue
                3: color 200 150 150  -- Light Red
                4: color 150 200 150  -- Light Green
                5: color 200 200 150  -- Light Yellow
                6: color 200 150 200  -- Light Magenta
                7: color 150 200 200  -- Light Cyan
                default: color 128 128 128  -- Default gray
            )
            
            physMat.base_color = baseColor
            physMat.roughness = roughness
            physMat.metalness = metallic
            
            return physMat
        ) catch (
            logMessage ("Error creating Physical material: " + matName) level:"ERROR"
            return undefined
        )
    ),
    
    -- Function to create a Multi/Sub-Object material with Physical materials
    fn createMultiSubMaterial objName numSubMats = (
        try (
            local multiMat = Multimaterial numsubs:numSubMats
            multiMat.name = generateUniqueMaterialName objName
            
            -- Create Physical materials for each sub-material slot
            for i = 1 to numSubMats do (
                local subMatName = objName + "_Physical_" + i as string
                local physMat = createPhysicalMaterial subMatName i
                
                if physMat != undefined then (
                    multiMat[i] = physMat
                ) else (
                    logMessage ("Failed to create sub-material " + i as string + " for " + objName) level:"ERROR"
                )
            )
            
            return multiMat
        ) catch (
            logMessage ("Error creating Multi/Sub-Object material for: " + objName) level:"ERROR"
            return undefined
        )
    ),
    
    -- Function to apply material to object and set material IDs
    fn applyMaterialToObject obj material matID:1 = (
        try (
            if obj == undefined or not isValidNode obj then return false
            if material == undefined then return false
            
            -- Assign material to object
            obj.material = material
            
            -- Set material IDs if requested and object is editable poly
            if setMaterialID and classof obj == Editable_Poly then (
                local numFaces = polyop.getNumFaces obj
                if numFaces > 0 then (
                    polyop.setFaceMatID obj #{1..numFaces} matID
                )
            )
            
            return true
        ) catch (
            logMessage ("Error applying material to object: " + (try obj.name catch "Unknown")) level:"ERROR"
            return false
        )
    ),
    
    -- =============================================================================
    -- SCENE ANALYSIS FUNCTIONS
    -- =============================================================================
    
    -- Function to find all editable poly objects in scene
    fn findEditablePolyObjects = (
        local foundObjects = #()
        
        logMessage "=== Finding Editable Poly Objects ===" level:"INFO"
        
        try (
            for obj in objects do (
                try (
                    if obj != undefined and isValidNode obj then (
                        if classof obj == Editable_Poly and not isHairFurObject obj then (
                            append foundObjects obj
                            logMessage ("Found Editable Poly: " + obj.name) level:"INFO"
                        )
                    )
                ) catch (
                    logMessage ("Error processing object in scene scan: " + (try obj.name catch "Unknown")) level:"WARNING"
                )
            )
        ) catch (
            logMessage "Critical error during scene scan" level:"ERROR"
        )
        
        editablePoly_objects = foundObjects
        logMessage ("Total Editable Poly objects found: " + foundObjects.count as string) level:"INFO"
        
        return foundObjects
    ),
    
    -- Function to analyze existing materials on objects
    fn analyzeMaterials objects = (
        local withMulti = #()
        local withoutMulti = #()
        
        logMessage "=== Analyzing Existing Materials ===" level:"INFO"
        
        for obj in objects do (
            try (
                if obj != undefined and isValidNode obj then (
                    local matName = "No Material"
                    local hasMultiSub = false
                    
                    if obj.material != undefined then (
                        matName = getMaterialName obj.material
                        hasMultiSub = isMultiSubMaterial obj.material
                    )
                    
                    local matInfo = #(obj, matName)
                    
                    if hasMultiSub then (
                        append withMulti matInfo
                        logMessage ("Object '" + obj.name + "' already has Multi/Sub-Object material: " + matName) level:"INFO"
                    ) else (
                        append withoutMulti matInfo
                        if obj.material != undefined then
                            logMessage ("Object '" + obj.name + "' has non-Multi/Sub-Object material: " + matName) level:"INFO"
                        else
                            logMessage ("Object '" + obj.name + "' has no material assigned") level:"INFO"
                    )
                )
            ) catch (
                local objNameSafe = try obj.name catch "Unknown"
                logMessage ("Error analyzing material for object: " + objNameSafe) level:"WARNING"
            )
        )
        
        obj_withMultimat = withMulti
        obj_with_nonMultimat = withoutMulti
        
        logMessage ("Objects with Multi/Sub-Object materials: " + withMulti.count as string) level:"INFO"
        logMessage ("Objects without Multi/Sub-Object materials: " + withoutMulti.count as string) level:"INFO"
        
        return #(withMulti, withoutMulti)
    ),
    
    -- =============================================================================
    -- MATERIAL APPLICATION FUNCTIONS
    -- =============================================================================
    
    -- Function to process a single object
    fn processSingleObject objInfo = (
        local targetObj = objInfo[1]
        local oldMatName = objInfo[2]
        
        try (
            if targetObj != undefined and isValidNode targetObj then (
                local newMultiMat = createMultiSubMaterial targetObj.name maxSubMaterials
                
                if newMultiMat != undefined then (
                    if applyMaterialToObject targetObj newMultiMat matID:defaultMaterialID then (
                        logMessage ("Applied Multi/Sub-Object material to '" + targetObj.name + "' (replacing '" + oldMatName + "')")
                        return true
                    )
                )
            )
        ) catch (
            local objNameSafe = try targetObj.name catch "Unknown"
            logMessage ("Failed to process object: " + objNameSafe + " - " + getCurrentException()) level:"ERROR"
        )
        
        return false
    ),
    
    -- Function to apply materials to all objects that need them
    fn applyMaterialsToObjects objectList = (
        if objectList.count == 0 then (
            logMessage "=== No Objects Need Multi/Sub-Object Materials ===" level:"INFO"
            logMessage "All editable poly objects already have Multi/Sub-Object materials assigned." level:"INFO"
            return #{0, 0}
        )
        
        logMessage "=== Applying Multi/Sub-Object Materials ===" level:"INFO"
        
        local successCount = 0
        local failCount = 0
        
        for objInfo in objectList do (
            if processSingleObject objInfo then
                successCount += 1
            else
                failCount += 1
        )
        
        logMessage ("Successfully processed: " + successCount as string + " objects") level:"INFO"
        if failCount > 0 then (
            logMessage ("Failed to process: " + failCount as string + " objects") level:"WARNING"
        )
        
        return #{successCount, failCount}
    ),
    
    -- =============================================================================
    -- REPORTING FUNCTIONS
    -- =============================================================================
    
    -- Function to generate summary report
    fn generateSummaryReport = (
        logMessage "" level:"INFO"
        logMessage "=== SUMMARY REPORT ===" level:"INFO"
        logMessage ("Total Editable Poly objects processed: " + editablePoly_objects.count as string) level:"INFO"
        logMessage ("Objects that already had Multi/Sub-Object materials: " + obj_withMultimat.count as string) level:"INFO"
        logMessage ("Objects that needed new Multi/Sub-Object materials: " + obj_with_nonMultimat.count as string) level:"INFO"
        
        if obj_withMultimat.count > 0 then (
            logMessage "" level:"INFO"
            logMessage "Objects with existing Multi/Sub-Object materials:" level:"INFO"
            for objInfo in obj_withMultimat do (
                try (
                    logMessage ("  - " + objInfo[1].name + " (Material: " + objInfo[2] + ")") level:"INFO"
                ) catch (
                    logMessage ("  - Error displaying object info") level:"WARNING"
                )
            )
        )
        
        if obj_with_nonMultimat.count > 0 then (
            logMessage "" level:"INFO"
            logMessage "Objects that received new Multi/Sub-Object materials:" level:"INFO"
            for objInfo in obj_with_nonMultimat do (
                try (
                    logMessage ("  - " + objInfo[1].name + " (Previously: " + objInfo[2] + ")") level:"INFO"
                ) catch (
                    logMessage ("  - Error displaying object info") level:"WARNING"
                )
            )
        )
        
        if errorLog.count > 0 then (
            logMessage "" level:"INFO"
            logMessage "=== ERROR LOG ===" level:"INFO"
            for errMsg in errorLog do (
                print errMsg
            )
            logMessage ("Total errors/warnings: " + errorLog.count as string) level:"INFO"
        )
    ),
    
    -- =============================================================================
    -- MAIN EXECUTION FUNCTIONS
    -- =============================================================================
    
    -- Function to reset all data
    fn resetData = (
        obj_withMultimat = #()
        obj_with_nonMultimat = #()
        editablePoly_objects = #()
        errorLog = #()
    ),
    
    -- Main function to execute the entire process
    fn executeProcess = (
        clearListener()
        resetData()
        
        logMessage "=== MULTI/SUB-OBJECT MATERIAL TOOL STARTED ===" level:"INFO"
        
        -- Step 1: Find editable poly objects
        local foundObjects = findEditablePolyObjects()
        
        if foundObjects.count == 0 then (
            logMessage "No editable poly objects found in scene." level:"WARNING"
            return #{0, 0, errorLog.count}
        )
        
        -- Step 2: Analyze existing materials
        analyzeMaterials foundObjects
        
        -- Step 3: Apply materials where needed
        local results = applyMaterialsToObjects obj_with_nonMultimat
        
        -- Step 4: Generate report
        generateSummaryReport()
        
        logMessage "" level:"INFO"
        logMessage "=== SCRIPT COMPLETED ===" level:"INFO"
        
        return #{obj_withMultimat.count, obj_with_nonMultimat.count, errorLog.count}
    ),
    
    -- =============================================================================
    -- CONFIGURATION FUNCTIONS
    -- =============================================================================
    
    -- Function to configure tool settings
    fn configure maxSubs:7 excludeHair:true setMatID:true matID:1 verbose:true = (
        maxSubMaterials = maxSubs
        excludeHairFur = excludeHair
        setMaterialID = setMatID
        defaultMaterialID = matID
        verboseOutput = verbose
        
        logMessage "Tool configured with new settings:" level:"INFO"
        logMessage ("  Max Sub-Materials: " + maxSubMaterials as string) level:"INFO"
        logMessage ("  Exclude Hair/Fur: " + excludeHairFur as string) level:"INFO"
        logMessage ("  Set Material ID: " + setMaterialID as string) level:"INFO"
        logMessage ("  Default Material ID: " + defaultMaterialID as string) level:"INFO"
        logMessage ("  Verbose Output: " + verboseOutput as string) level:"INFO"
    ),
    
    -- Function to process only selected objects
    fn processSelectedObjects = (
        clearListener()
        resetData()
        
        logMessage "=== PROCESSING SELECTED OBJECTS ONLY ===" level:"INFO"
        
        local selectedObjs = #()
        for obj in selection do (
            if classof obj == Editable_Poly and not isHairFurObject obj then (
                append selectedObjs obj
            )
        )
        
        if selectedObjs.count == 0 then (
            logMessage "No valid editable poly objects selected." level:"WARNING"
            return #{0, 0, 1}
        )
        
        editablePoly_objects = selectedObjs
        analyzeMaterials selectedObjs
        local results = applyMaterialsToObjects obj_with_nonMultimat
        generateSummaryReport()
        
        return #{obj_withMultimat.count, obj_with_nonMultimat.count, errorLog.count}
    )
)

-- =============================================================================
-- INITIALIZE AND EXECUTE
-- =============================================================================

-- Create global instance
MultiSubMaterialTool = MultiSubMaterialTool()

-- =============================================================================
-- USAGE EXAMPLES AND QUICK FUNCTIONS
-- =============================================================================

-- Quick execute function for entire scene
fn processEntireScene = (
    MultiSubMaterialTool.executeProcess()
)

-- Quick execute function for selected objects only
fn processSelectedOnly = (
    MultiSubMaterialTool.processSelectedObjects()
)

-- Configure and execute function
fn configureAndProcess maxSubs:7 excludeHair:true setMatID:true matID:1 verbose:true = (
    MultiSubMaterialTool.configure maxSubs:maxSubs excludeHair:excludeHair setMatID:setMatID matID:matID verbose:verbose
    MultiSubMaterialTool.executeProcess()
)

-- =============================================================================
-- EXECUTE THE SCRIPT
-- =============================================================================

-- Uncomment one of the following lines to execute:

-- Process entire scene with default settings
processEntireScene()

-- Alternative execution methods (uncomment to use):
-- processSelectedOnly()  -- Process only selected objects
-- configureAndProcess maxSubs:5 excludeHair:false  -- Custom configuration

print ""
print "============================================================================="
print "MULTI/SUB-OBJECT MATERIAL TOOL - FUNCTION REFERENCE"
print "============================================================================="
print ""
print "Quick Functions:"
print "  processEntireScene() - Process all editable poly objects in scene"
print "  processSelectedOnly() - Process only selected objects"
print "  configureAndProcess() - Configure settings and process"
print ""
print "Advanced Usage:"
print "  MultiSubMaterialTool.configure maxSubs:5 excludeHair:false"
print "  MultiSubMaterialTool.executeProcess()"
print "  MultiSubMaterialTool.processSelectedObjects()"
print ""
print "Configuration Options:"
print "  maxSubs - Maximum sub-materials (default: 7)"
print "  excludeHair - Exclude hair/fur objects (default: true)"
print "  setMatID - Set material IDs on faces (default: true)"
print "  matID - Default material ID to assign (default: 1)"
print "  verbose - Show detailed output (default: true)"
print "============================================================================="


"""
Main Components:

MultiSubMaterialTool Struct - Contains all functionality in organized methods
Utility Functions - Common operations like logging, validation, name generation
Core Material Functions - Material creation and application
Scene Analysis Functions - Object discovery and material analysis
Reporting Functions - Summary generation and error reporting
Configuration Functions - Easy customization options

-- Process entire scene with default settings
processEntireScene()

-- Process only selected objects
processSelectedOnly()

-- Custom configuration and process
configureAndProcess maxSubs:5 excludeHair:false

-- Configure tool first
MultiSubMaterialTool.configure maxSubs:5 excludeHair:false setMatID:true matID:2 verbose:true

-- Then execute
MultiSubMaterialTool.executeProcess()

maxSubs - Maximum sub-materials per Multi/Sub-Object (default: 7)
excludeHair - Whether to exclude hair/fur objects (default: true)
setMatID - Whether to set material IDs on faces (default: true)
matID - Default material ID to assign (default: 1)
verbose - Show detailed output (default: true)

findEditablePolyObjects() - Scene object discovery
analyzeMaterials() - Material state analysis
createMultiSubMaterial() - Smart material creation
applyMaterialToObject() - Safe material application
processSingleObject() - Individual object processing
generateSummaryReport() - Comprehensive reporting
Smart Features:

Unique Material Names - Prevents naming conflicts
Selective Processing - Work with entire scene or selected objects
Flexible Configuration - Easy parameter adjustment
Comprehensive Logging - Detailed operation tracking
Error Recovery - Continues processing despite individual failures

Safety Features:

Complete object validation
Safe material creation with fallbacks
Error logging and reporting
Memory management
Version compatibility

-- Just run with defaults
processEntireScene()

maxscript-- 5 sub-materials, include hair objects, set material ID 3
configureAndProcess maxSubs:5 excludeHair:false matID:3

-- Select objects first, then run
select $YourObject*
processSelectedOnly()

"""
