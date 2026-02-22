Sub PopulateAllSheet()

    '==========================================
    ' CONFIGURATION
    '==========================================
    Dim sheetList       As Variant
    Dim milestoneColMap As Object
    
    sheetList = Array("Asset", "ImagingScenes", "ImagingOutlines", "VizScenes", "LightingOutlines")
    
    Set milestoneColMap = CreateObject("Scripting.Dictionary")
    milestoneColMap("Asset")            = "K"
    milestoneColMap("ImagingScenes")    = "AJ"
    milestoneColMap("ImagingOutlines")  = "AF"
    milestoneColMap("VizScenes")        = "Z"
    milestoneColMap("LightingOutlines") = "T"
    
    '==========================================
    ' SAFETY: Global error handler
    '==========================================
    On Error GoTo GlobalErrorHandler
    
    '==========================================
    ' STEP 1: Validate "All" sheet exists
    '==========================================
    Dim wsAll As Worksheet
    Set wsAll = GetSheetSafely(ThisWorkbook, "All")
    
    If wsAll Is Nothing Then
        MsgBox "Critical Error: A sheet named 'All' was not found in this workbook." & vbNewLine & _
               "Please make sure the 'All' sheet exists before running this macro.", _
               vbCritical, "Missing Sheet: All"
        Exit Sub
    End If
    
    '==========================================
    ' STEP 2: Validate current (active) sheet
    '         and read Month / Week
    '==========================================
    Dim wsCurrent As Worksheet
    Set wsCurrent = ActiveSheet
    
    Dim monthName As String
    Dim weekName  As String
    
    monthName = SafeGetCellValue(wsCurrent, "C22")
    weekName  = SafeGetCellValue(wsCurrent, "C23")
    
    If monthName = "" Then _
        MsgBox "Warning: C22 (Month) on the active sheet is empty.", vbExclamation, "Missing Value"
    If weekName = "" Then _
        MsgBox "Warning: C23 (Week) on the active sheet is empty.", vbExclamation, "Missing Value"
    
    '==========================================
    ' STEP 3: Check which sheets exist / missing
    '==========================================
    Dim missingSheets   As String
    Dim foundSheets     As String
    Dim validSheets()   As Variant
    Dim validCount      As Integer
    validCount    = 0
    missingSheets = ""
    foundSheets   = ""
    
    ReDim validSheets(UBound(sheetList))
    
    Dim i As Integer
    For i = 0 To UBound(sheetList)
        Dim ws As Worksheet
        Set ws = GetSheetSafely(ThisWorkbook, CStr(sheetList(i)))
        If ws Is Nothing Then
            missingSheets = missingSheets & "  - " & CStr(sheetList(i)) & vbNewLine
        Else
            validSheets(validCount) = CStr(sheetList(i))
            validCount = validCount + 1
            foundSheets = foundSheets & "  + " & CStr(sheetList(i)) & vbNewLine
        End If
        Set ws = Nothing
    Next i
    
    ' If NO valid sheets found at all, abort
    If validCount = 0 Then
        MsgBox "Critical Error: None of the required source sheets were found." & vbNewLine & vbNewLine & _
               "Expected sheets:" & vbNewLine & Join(sheetList, vbNewLine) & vbNewLine & vbNewLine & _
               "Please check the workbook and try again.", _
               vbCritical, "No Source Sheets Found"
        Exit Sub
    End If
    
    ' Inform user about missing sheets (non-blocking warning)
    If missingSheets <> "" Then
        Dim continueChoice As Integer
        continueChoice = MsgBox("The following sheets were NOT found and will be skipped:" & vbNewLine & vbNewLine & _
                                missingSheets & vbNewLine & _
                                "Sheets that WERE found and will be processed:" & vbNewLine & vbNewLine & _
                                foundSheets & vbNewLine & _
                                "Do you want to continue with the available sheets?", _
                                vbExclamation + vbYesNo, "Some Sheets Missing")
        If continueChoice = vbNo Then
            MsgBox "Operation cancelled by user.", vbInformation, "Cancelled"
            Exit Sub
        End If
    End If
    
    '==========================================
    ' STEP 4: Build dictionaries for unique
    '         projects, launch dates, milestones
    '==========================================
    Dim dictProjects  As Object   ' Key: ProjectName  -> insertion index
    Dim dictLaunch    As Object   ' Key: ProjectName  -> comma-separated launch dates
    Dim dictMilestone As Object   ' Key: ProjectName|ColLetter -> comma-separated milestone dates
    
    Set dictProjects  = CreateObject("Scripting.Dictionary")
    Set dictLaunch    = CreateObject("Scripting.Dictionary")
    Set dictMilestone = CreateObject("Scripting.Dictionary")
    
    Dim projectOrder() As String
    Dim projectCount   As Long
    projectCount = 0
    ReDim projectOrder(0)
    
    Dim sheetName    As String
    Dim projName     As String
    Dim launchVal    As String
    Dim milestoneVal As String
    Dim milCol       As String
    Dim msKey        As String
    Dim r            As Long
    
    '==========================================
    ' STEP 5: Loop valid source sheets
    '==========================================
    For i = 0 To validCount - 1
        sheetName = CStr(validSheets(i))
        
        Dim wsSource As Worksheet
        Set wsSource = GetSheetSafely(ThisWorkbook, sheetName)
        
        ' Double-check (safety net — sheet could theoretically be deleted mid-run)
        If wsSource Is Nothing Then
            GoTo NextSheet
        End If
        
        ' Get milestone column for this sheet
        milCol = ""
        If milestoneColMap.exists(sheetName) Then milCol = milestoneColMap(sheetName)
        
        '--------------------------------------
        ' Loop data rows E22:G50
        '--------------------------------------
        For r = 22 To 50
            
            ' Safely read each cell
            projName     = SafeGetCellValue(wsSource, "E" & r)
            launchVal    = SafeGetCellValue(wsSource, "G" & r)
            milestoneVal = SafeGetCellValue(wsSource, "F" & r)
            
            ' Skip blank project names
            If projName = "" Then GoTo NextRow
            
            '--- Register unique project ---
            If Not dictProjects.exists(projName) Then
                dictProjects(projName) = projectCount
                ReDim Preserve projectOrder(projectCount)
                projectOrder(projectCount) = projName
                projectCount = projectCount + 1
                dictLaunch(projName) = ""
            End If
            
            '--- Accumulate unique launch dates (supports multiple comma-separated) ---
            If launchVal <> "" Then
                Dim launchParts As Variant
                launchParts = Split(launchVal, ",")
                Dim lp As Integer
                For lp = 0 To UBound(launchParts)
                    Dim oneDate As String
                    oneDate = Trim(launchParts(lp))
                    If oneDate <> "" Then
                        If Not ValueExistsInList(dictLaunch(projName), oneDate) Then
                            If dictLaunch(projName) = "" Then
                                dictLaunch(projName) = oneDate
                            Else
                                dictLaunch(projName) = dictLaunch(projName) & ", " & oneDate
                            End If
                        End If
                    End If
                Next lp
            End If
            
            '--- Accumulate unique milestone dates per project+column ---
            If milCol <> "" And milestoneVal <> "" Then
                msKey = projName & "|" & milCol
                If Not dictMilestone.exists(msKey) Then dictMilestone(msKey) = ""
                If Not ValueExistsInList(dictMilestone(msKey), milestoneVal) Then
                    If dictMilestone(msKey) = "" Then
                        dictMilestone(msKey) = milestoneVal
                    Else
                        dictMilestone(msKey) = dictMilestone(msKey) & ", " & milestoneVal
                    End If
                End If
            End If
            
NextRow:
        Next r
        
NextSheet:
        Set wsSource = Nothing
    Next i
    
    '==========================================
    ' STEP 6: Validate we actually found data
    '==========================================
    If projectCount = 0 Then
        MsgBox "No project data was found in any of the source sheets." & vbNewLine & vbNewLine & _
               "Please check that project names exist in column E (rows 22-50) " & _
               "of the source sheets.", vbExclamation, "No Data Found"
        Exit Sub
    End If
    
    '==========================================
    ' STEP 7: Clear old data in "All" sheet
    '==========================================
    Dim lastClearRow As Long
    lastClearRow = 25 + projectCount + 20   ' buffer of 20 extra rows
    
    On Error Resume Next
    wsAll.Range("B25:B" & lastClearRow).ClearContents
    wsAll.Range("C25:C" & lastClearRow).ClearContents
    wsAll.Range("K25:K" & lastClearRow).ClearContents
    wsAll.Range("T25:T" & lastClearRow).ClearContents
    wsAll.Range("Z25:Z" & lastClearRow).ClearContents
    wsAll.Range("AF25:AF" & lastClearRow).ClearContents
    wsAll.Range("AJ25:AJ" & lastClearRow).ClearContents
    On Error GoTo GlobalErrorHandler
    
    '==========================================
    ' STEP 8: Write data to "All" sheet
    '==========================================
    Dim writeRow As Long
    Dim idx      As Long
    Dim s        As Integer
    
    For idx = 0 To projectCount - 1
        projName = projectOrder(idx)
        writeRow = 25 + idx
        
        ' --- B: Project Name ---
        SafeSetCellValue wsAll, "B" & writeRow, projName
        
        ' --- C: Launch Dates ---
        SafeSetCellValue wsAll, "C" & writeRow, dictLaunch(projName)
        
        ' --- Milestone columns (only for valid sheets) ---
        For s = 0 To validCount - 1
            sheetName = CStr(validSheets(s))
            If milestoneColMap.exists(sheetName) Then
                milCol = milestoneColMap(sheetName)
                msKey  = projName & "|" & milCol
                If dictMilestone.exists(msKey) Then
                    Dim cellAddr    As String
                    Dim existingVal As String
                    cellAddr    = milCol & writeRow
                    existingVal = SafeGetCellValue(wsAll, cellAddr)
                    
                    If existingVal = "" Then
                        SafeSetCellValue wsAll, cellAddr, dictMilestone(msKey)
                    Else
                        ' Append only truly new dates
                        Dim newParts As Variant
                        newParts = Split(dictMilestone(msKey), ",")
                        Dim np As Integer
                        For np = 0 To UBound(newParts)
                            Dim nd As String
                            nd = Trim(newParts(np))
                            If nd <> "" And Not ValueExistsInList(existingVal, nd) Then
                                existingVal = existingVal & ", " & nd
                            End If
                        Next np
                        SafeSetCellValue wsAll, cellAddr, existingVal
                    End If
                End If
            End If
        Next s
        
    Next idx
    
    '==========================================
    ' STEP 9: Success message
    '==========================================
    Dim summaryMsg As String
    summaryMsg = "Successfully completed!" & vbNewLine & vbNewLine & _
                 "Month : " & monthName & vbNewLine & _
                 "Week  : " & weekName & vbNewLine & vbNewLine & _
                 "Unique Projects Written : " & projectCount & vbNewLine & _
                 "Starting at row 25 in 'All' sheet." & vbNewLine & vbNewLine
    
    If missingSheets <> "" Then
        summaryMsg = summaryMsg & "Skipped (not found):" & vbNewLine & missingSheets
    End If
    
    MsgBox summaryMsg, vbInformation, "Done"
    Exit Sub

'==========================================
' GLOBAL ERROR HANDLER
'==========================================
GlobalErrorHandler:
    MsgBox "An unexpected error occurred:" & vbNewLine & vbNewLine & _
           "Error Number : " & Err.Number & vbNewLine & _
           "Description  : " & Err.Description & vbNewLine & vbNewLine & _
           "The macro has stopped. Please check your data and try again.", _
           vbCritical, "Unexpected Error"
    
    On Error Resume Next
    Set wsAll     = Nothing
    Set wsCurrent = Nothing
    Set wsSource  = Nothing
    On Error GoTo 0

End Sub

'==============================================
' HELPER: Safely get a worksheet from workbook
'         Returns Nothing if sheet not found
'==============================================
Private Function GetSheetSafely(wb As Workbook, sheetName As String) As Worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = wb.Worksheets(sheetName)
    On Error GoTo 0
    Set GetSheetSafely = ws
End Function

'==============================================
' HELPER: Safely read a cell value as String
'         Returns "" on any error
'==============================================
Private Function SafeGetCellValue(ws As Worksheet, cellAddr As String) As String
    Dim result As String
    result = ""
    On Error Resume Next
    If Not ws Is Nothing Then
        result = Trim(CStr(ws.Range(cellAddr).Value))
    End If
    On Error GoTo 0
    SafeGetCellValue = result
End Function

'==============================================
' HELPER: Safely write a value to a cell
'         Silently skips on any error
'==============================================
Private Sub SafeSetCellValue(ws As Worksheet, cellAddr As String, val As String)
    On Error Resume Next
    If Not ws Is Nothing Then
        ws.Range(cellAddr).Value = val
    End If
    On Error GoTo 0
End Sub

'==============================================
' HELPER: Check if a value already exists in
'         a comma-delimited string list
'==============================================
Private Function ValueExistsInList(existingList As String, checkVal As String) As Boolean
    If existingList = "" Then
        ValueExistsInList = False
        Exit Function
    End If
    Dim parts As Variant
    parts = Split(existingList, ",")
    Dim p As Integer
    For p = 0 To UBound(parts)
        If LCase(Trim(parts(p))) = LCase(Trim(checkVal)) Then
            ValueExistsInList = True
            Exit Function
        End If
    Next p
    ValueExistsInList = False
End Function
