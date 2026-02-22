'==============================================
' MODULE: modPopulateAll
' Paste this entire block into a Standard Module
'==============================================

Option Explicit

'==============================================
' MAIN SUB
'==============================================
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
    ' STEP 2: Read Month / Week from "All"
    '         sheet C22 and C23 as filter keys
    '==========================================
    Dim filterMonth As String
    Dim filterWeek  As String
    
    filterMonth = SafeGetCellValue(wsAll, "C22")
    filterWeek  = SafeGetCellValue(wsAll, "C23")
    
    If filterMonth = "" Then
        MsgBox "Warning: C22 (Month filter) on the 'All' sheet is empty." & vbNewLine & _
               "No month filter will be applied.", vbExclamation, "Missing Filter Value"
    End If
    If filterWeek = "" Then
        MsgBox "Warning: C23 (Week filter) on the 'All' sheet is empty." & vbNewLine & _
               "No week filter will be applied.", vbExclamation, "Missing Filter Value"
    End If
    
    '==========================================
    ' STEP 3: Check which sheets exist / missing
    '==========================================
    Dim missingSheets As String
    Dim foundSheets   As String
    Dim validSheets() As Variant
    Dim validCount    As Integer
    
    validCount    = 0
    missingSheets = ""
    foundSheets   = ""
    
    ReDim validSheets(UBound(sheetList))
    
    Dim i As Integer
    Dim ws As Worksheet
    
    For i = 0 To UBound(sheetList)
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
    ' STEP 4: Build dictionaries
    '==========================================
    Dim dictProjects  As Object
    Dim dictLaunch    As Object
    Dim dictMilestone As Object
    
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
    Dim rowMonth     As String
    Dim rowWeek      As String
    Dim monthMatch   As Boolean
    Dim weekMatch    As Boolean
    
    '==========================================
    ' STEP 5: Loop valid source sheets
    '==========================================
    Dim wsSource As Worksheet
    
    For i = 0 To validCount - 1
        sheetName = CStr(validSheets(i))
        Set wsSource = GetSheetSafely(ThisWorkbook, sheetName)
        
        If wsSource Is Nothing Then
            GoTo NextSheet
        End If
        
        milCol = ""
        If milestoneColMap.exists(sheetName) Then milCol = milestoneColMap(sheetName)
        
        For r = 22 To 50
        
            rowMonth = SafeGetCellValue(wsSource, "B" & r)
            rowWeek  = SafeGetCellValue(wsSource, "C" & r)
            projName = SafeGetCellValue(wsSource, "E" & r)
            
            If projName = "" Then GoTo NextRow
            
            monthMatch = (filterMonth = "") Or (LCase(Trim(rowMonth)) = LCase(Trim(filterMonth)))
            weekMatch  = (filterWeek = "")  Or (LCase(Trim(rowWeek))  = LCase(Trim(filterWeek)))
            
            If Not monthMatch Or Not weekMatch Then GoTo NextRow
            
            launchVal    = SafeGetCellValue(wsSource, "G" & r)
            milestoneVal = SafeGetCellValue(wsSource, "F" & r)
            
            ' Register unique project
            If Not dictProjects.exists(projName) Then
                dictProjects(projName) = projectCount
                ReDim Preserve projectOrder(projectCount)
                projectOrder(projectCount) = projName
                projectCount = projectCount + 1
                dictLaunch(projName) = ""
            End If
            
            ' Accumulate unique launch dates
            If launchVal <> "" Then
                Dim launchParts As Variant
                Dim lp          As Integer
                Dim oneDate     As String
                launchParts = Split(launchVal, ",")
                For lp = 0 To UBound(launchParts)
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
            
            ' Accumulate unique milestone dates
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
    ' STEP 6: Validate data found
    '==========================================
    If projectCount = 0 Then
        MsgBox "No matching project data was found." & vbNewLine & vbNewLine & _
               "Filter Applied:" & vbNewLine & _
               "  Month (C22) : " & IIf(filterMonth = "", "(none)", filterMonth) & vbNewLine & _
               "  Week  (C23) : " & IIf(filterWeek = "", "(none)", filterWeek) & vbNewLine & vbNewLine & _
               "Please check that:" & vbNewLine & _
               "  - Column B (rows 22-50) in source sheets contains month values" & vbNewLine & _
               "  - Column C (rows 22-50) in source sheets contains week values" & vbNewLine & _
               "  - Values match C22 and C23 of the 'All' sheet exactly.", _
               vbExclamation, "No Matching Data Found"
        Exit Sub
    End If
    
    '==========================================
    ' STEP 7: Clear old data in "All" sheet
    '==========================================
    Dim lastClearRow As Long
    lastClearRow = 25 + projectCount + 20
    
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
    Dim writeRow    As Long
    Dim idx         As Long
    Dim s           As Integer
    Dim cellAddr    As String
    Dim existingVal As String
    Dim newParts    As Variant
    Dim np          As Integer
    Dim nd          As String
    
    For idx = 0 To projectCount - 1
        projName = projectOrder(idx)
        writeRow = 25 + idx
        
        SafeSetCellValue wsAll, "B" & writeRow, projName
        SafeSetCellValue wsAll, "C" & writeRow, dictLaunch(projName)
        
        For s = 0 To validCount - 1
            sheetName = CStr(validSheets(s))
            If milestoneColMap.exists(sheetName) Then
                milCol   = milestoneColMap(sheetName)
                msKey    = projName & "|" & milCol
                If dictMilestone.exists(msKey) Then
                    cellAddr    = milCol & writeRow
                    existingVal = SafeGetCellValue(wsAll, cellAddr)
                    If existingVal = "" Then
                        SafeSetCellValue wsAll, cellAddr, dictMilestone(msKey)
                    Else
                        newParts = Split(dictMilestone(msKey), ",")
                        For np = 0 To UBound(newParts)
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
                 "Filter Applied:" & vbNewLine & _
                 "  Month (C22) : " & IIf(filterMonth = "", "(none)", filterMonth) & vbNewLine & _
                 "  Week  (C23) : " & IIf(filterWeek = "", "(none)", filterWeek) & vbNewLine & vbNewLine & _
                 "Unique Projects Written : " & projectCount & vbNewLine & _
                 "Starting at row 25 in 'All' sheet." & vbNewLine & vbNewLine
    
    If missingSheets <> "" Then
        summaryMsg = summaryMsg & "Skipped sheets (not found):" & vbNewLine & missingSheets
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
    Set wsAll    = Nothing
    Set wsSource = Nothing
    On Error GoTo 0

End Sub

'==============================================
' HELPER: Safely get a worksheet from workbook
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
'==============================================
Private Sub SafeSetCellValue(ws As Worksheet, cellAddr As String, val As String)
    On Error Resume Next
    If Not ws Is Nothing Then
        ws.Range(cellAddr).Value = val
    End If
    On Error GoTo 0
End Sub

'==============================================
' HELPER: Check if value exists in a
'         comma-delimited string list
'==============================================
Private Function ValueExistsInList(existingList As String, checkVal As String) As Boolean
    Dim parts As Variant
    Dim p     As Integer
    If existingList = "" Then
        ValueExistsInList = False
        Exit Function
    End If
    parts = Split(existingList, ",")
    For p = 0 To UBound(parts)
        If LCase(Trim(parts(p))) = LCase(Trim(checkVal)) Then
            ValueExistsInList = True
            Exit Function
        End If
    Next p
    ValueExistsInList = False
End Function
