
Sub CollectDueDates()

    Dim currentWB As Workbook
    Dim dataWB As Workbook
    Dim glossaryWS As Worksheet
    Dim dataWS As Worksheet
    
    Dim projectName As String
    Dim allDataPath As String
    
    ' === CONFIGURATION ===
    allDataPath = "C:\local\alldata.xlsx"
    
    Dim dueCols() As String
    dueCols = Split("asset due,lighting due,imaging due,viz due,imaging scene due", ",")
    Dim launchColName As String
    launchColName = "Launch dates"
    
    Set currentWB = ThisWorkbook
    Set glossaryWS = currentWB.Sheets("glossary")
    
    ' Open alldata.xlsx if not already open
    On Error Resume Next
    Set dataWB = Workbooks(Dir(allDataPath))
    On Error GoTo 0
    If dataWB Is Nothing Then
        Set dataWB = Workbooks.Open(allDataPath)
    End If
    
    ' === Clear previous output from J20 downward ===
    Dim lastUsedRow As Long
    lastUsedRow = glossaryWS.Cells(glossaryWS.Rows.Count, 10).End(xlUp).Row
    If lastUsedRow >= 20 Then
        glossaryWS.Range("J20:J" & lastUsedRow).ClearContents
    End If
    
    Dim outputRow As Long
    outputRow = 20
    
    Dim i As Long
    For i = 6 To 15
        projectName = Trim(glossaryWS.Cells(i, 8).Value)  ' Column H
        
        If projectName = "" Then GoTo NextRow
        
        On Error Resume Next
        Set dataWS = dataWB.Sheets(projectName)
        On Error GoTo 0
        
        If dataWS Is Nothing Then GoTo NextRow
        
        ' Map headers B1:Q1
        Dim j As Integer
        Dim colMap(2 To 17) As String
        For j = 2 To 17
            colMap(j) = Trim(LCase(dataWS.Cells(1, j).Value))
        Next j
        
        ' Find Launch dates column
        Dim launchColIdx As Integer
        launchColIdx = 0
        For j = 2 To 17
            If LCase(colMap(j)) = LCase(launchColName) Then
                launchColIdx = j
                Exit For
            End If
        Next j
        
        Dim lastDataRow As Long
        lastDataRow = dataWS.Cells(dataWS.Rows.Count, 2).End(xlUp).Row
        
        Dim d As Integer
        For d = 0 To UBound(dueCols)
            Dim dueColName As String
            dueColName = Trim(dueCols(d))
            
            Dim dueColIdx As Integer
            dueColIdx = 0
            For j = 2 To 17
                If LCase(colMap(j)) = LCase(dueColName) Then
                    dueColIdx = j
                    Exit For
                End If
            Next j
            
            If dueColIdx = 0 Then GoTo NextDueCol
            
            ' dueDateLaunchMap : due date (as actual Date) -> Dictionary of unique launch dates (as actual Date)
            Dim dueDateLaunchMap As Object
            Set dueDateLaunchMap = CreateObject("Scripting.Dictionary")
            ' Store actual date serial numbers as keys for sorting
            Dim dueDateSerials As Object
            Set dueDateSerials = CreateObject("Scripting.Dictionary")
            
            Dim r As Long
            For r = 2 To lastDataRow
                Dim dueCell As Variant
                dueCell = dataWS.Cells(r, dueColIdx).Value
                
                ' Only process valid dates
                If IsEmpty(dueCell) Or dueCell = "" Then GoTo NextRow2
                If Not IsDate(dueCell) Then GoTo NextRow2
                
                Dim dueSerial As Long
                dueSerial = CLng(CDate(dueCell))   ' Use serial number as unique key for sorting
                
                ' Track unique due date serials
                If Not dueDateSerials.Exists(dueSerial) Then
                    dueDateSerials.Add dueSerial, dueSerial
                End If
                
                ' Initialize inner dictionary for launch dates under this due date
                If Not dueDateLaunchMap.Exists(dueSerial) Then
                    Dim innerDict As Object
                    Set innerDict = CreateObject("Scripting.Dictionary")
                    dueDateLaunchMap.Add dueSerial, innerDict
                End If
                
                ' Get launch date for this row
                If launchColIdx > 0 Then
                    Dim launchCell As Variant
                    launchCell = dataWS.Cells(r, launchColIdx).Value
                    
                    If Not IsEmpty(launchCell) And launchCell <> "" And IsDate(launchCell) Then
                        Dim launchSerial As Long
                        launchSerial = CLng(CDate(launchCell))
                        
                        If Not dueDateLaunchMap(dueSerial).Exists(launchSerial) Then
                            dueDateLaunchMap(dueSerial).Add launchSerial, launchSerial
                        End If
                    End If
                End If
                
NextRow2:
            Next r
            
            ' === Sort due date serials ascending ===
            Dim dueKeys() As Long
            dueKeys = GetSortedKeys(dueDateSerials)
            
            ' === Write one row per due date ===
            Dim idx As Long
            For idx = 0 To UBound(dueKeys)
                Dim thisDueSerial As Long
                thisDueSerial = dueKeys(idx)
                
                ' Format due date as mm/dd/yyyy
                Dim dueDateFormatted As String
                dueDateFormatted = Format(CDate(thisDueSerial), "mm/dd/yyyy")
                
                ' === Sort launch date serials ascending and format ===
                Dim launchSorted() As Long
                launchSorted = GetSortedKeys(dueDateLaunchMap(thisDueSerial))
                
                Dim launchDatesStr As String
                launchDatesStr = ""
                Dim lIdx As Long
                For lIdx = 0 To UBound(launchSorted)
                    Dim formattedLaunch As String
                    formattedLaunch = Format(CDate(launchSorted(lIdx)), "mm/dd/yyyy")
                    If launchDatesStr = "" Then
                        launchDatesStr = formattedLaunch
                    Else
                        launchDatesStr = launchDatesStr & ", " & formattedLaunch
                    End If
                Next lIdx
                
                ' Build final line string
                Dim lineStr As String
                lineStr = dueColName & ">>" & projectName & ">>" & dueDateFormatted & ">>" & launchDatesStr
                
                ' Write to column J
                With glossaryWS.Cells(outputRow, 10)
                    .Value = lineStr
                    .HorizontalAlignment = xlLeft
                    .VerticalAlignment = xlCenter
                End With
                
                outputRow = outputRow + 1
            Next idx
            
            Set dueDateLaunchMap = Nothing
            Set dueDateSerials = Nothing
            
NextDueCol:
        Next d
        
        Set dataWS = Nothing
        
NextRow:
    Next i
    
    glossaryWS.Columns(10).AutoFit
    
    MsgBox "Done! " & (outputRow - 20) & " rows written to Glossary column J starting at J20.", vbInformation

End Sub

' ============================================================
' Helper Function: Returns dictionary keys sorted ascending
' Works on Scripting.Dictionary where keys are Long (date serials)
' ============================================================
Function GetSortedKeys(dict As Object) As Long()
    Dim n As Long
    n = dict.Count
    
    Dim arr() As Long
    ReDim arr(n - 1)
    
    Dim k As Variant
    Dim idx As Long
    idx = 0
    For Each k In dict.Keys
        arr(idx) = CLng(k)
        idx = idx + 1
    Next k
    
    ' Bubble sort ascending
    Dim pass As Long, inner As Long
    Dim temp As Long
    For pass = 0 To n - 2
        For inner = 0 To n - 2 - pass
            If arr(inner) > arr(inner + 1) Then
                temp = arr(inner)
                arr(inner) = arr(inner + 1)
                arr(inner + 1) = temp
            End If
        Next inner
    Next pass
    
    GetSortedKeys = arr
End Function




```

---

## What Changed

**Before (old behavior):**
```
asset due>>ProjectA>>2025-03-01, 2025-04-15>>2025-06-01, 2025-07-30
```

**After (new behavior):**
```
asset due>>ProjectA>>2025-03-01>>2025-06-01, 2025-07-30
asset due>>ProjectA>>2025-04-15>>2025-08-20
lighting due>>ProjectA>>2025-03-10>>2025-06-01
imaging due>>ProjectB>>2025-05-01>>2025-08-15, 2025-09-01

```
Create a excel formula :
1) Given a excel file : c: local\alldata.xlsx
2) In the current excel we have a worksheet named glossary and having Column H containing Project names from H6 to H15, and another column with Filters name from I6 to I15
3) the alldata.xlsx contains worksheets matching with names in the column H of glossary
4) the alldata.xlsx each sheet contains the column from B1 till Q1 with column names matching with Filters values
5) also the Filters  contains other column such as asset due, lighting due, imaging due, viz due and imaging scene due, and Launch dates

Task : 
1) get the Project names list  and  Filters names list in the current excel to find to find matching sheets and get all unique asset due, lighting due, imaging due, viz due and imaging scene due, and Launch dates from alldata.xlsx into a single text
2) the output text should have in the format  asset due>>SheetName>>matching unique due dates from  asset due column>>matching unique launch dates from launch dates column(if multiple then ',' separated)

Note : the it can be all matching unique  for all asset due, lighting due, imaging due, viz due and imaging scene due

idea is to collect all due dates from all individual column with proper namings

well make changes in the formula in the following way:
1) the due dates may have multiple Launch dates and it should be separated by ',' for example :
asset due>>ProjectA>>2025-03-01>>2025-06-01, 2025-07-30
where 2025-03-01 is due date and 2025-06-01, 2025-07-30 are multiple launch dates
2) do not club multiple due dates into one as asset due>>ProjectA>>2025-03-01, 2025-04-15
              
```


```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````

Sub AnalyzeDueDates()

    Dim currentWB     As Workbook
    Dim dataWB        As Workbook
    Dim modelWS       As Worksheet
    Dim dataWS        As Worksheet
    
    Dim allDataPath   As String
    allDataPath = "C:\local\alldata.xlsx"
    
    Set currentWB = ThisWorkbook
    Set modelWS   = currentWB.Sheets("Model")
    
    ' === Open alldata.xlsx if not already open ===
    On Error Resume Next
    Set dataWB = Workbooks(Dir(allDataPath))
    On Error GoTo 0
    If dataWB Is Nothing Then
        Set dataWB = Workbooks.Open(allDataPath)
    End If
    
    ' === Clear previous results in E:J and P from row 22 downward ===
    Dim lastUsedRow As Long
    lastUsedRow = modelWS.Cells(modelWS.Rows.Count, 4).End(xlUp).Row
    If lastUsedRow >= 22 Then
        modelWS.Range("E22:J" & lastUsedRow).ClearContents
        modelWS.Range("E22:J" & lastUsedRow).Font.ColorIndex = xlAutomatic
        modelWS.Range("P22:P" & lastUsedRow).ClearContents
    End If
    
    ' === Loop through D22 downward, stop at first blank ===
    Dim currentRow As Long
    currentRow = 22
    
    Do While Trim(modelWS.Cells(currentRow, 4).Value) <> ""
    
        Dim cellValue As String
        cellValue = Trim(modelWS.Cells(currentRow, 4).Value)
        
        ' === Parse: due type>>ProjectName>>DueDate>>LaunchDates ===
        Dim parts() As String
        parts = Split(cellValue, ">>")
        
        If UBound(parts) < 2 Then
            modelWS.Cells(currentRow, 5).Value  = "Parse Error"
            modelWS.Cells(currentRow, 6).Value  = "Parse Error"
            modelWS.Cells(currentRow, 7).Value  = "Parse Error"
            modelWS.Cells(currentRow, 8).Value  = "Parse Error"
            modelWS.Cells(currentRow, 9).Value  = "Parse Error"
            modelWS.Cells(currentRow, 10).Value = "Parse Error"
            modelWS.Cells(currentRow, 16).Value = "Parse Error"
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        Dim dueType     As String
        Dim sheetName   As String
        Dim dueDateStr  As String
        Dim launchDates As String
        
        dueType     = Trim(parts(0))
        sheetName   = Trim(parts(1))
        dueDateStr  = Trim(parts(2))
        launchDates = IIf(UBound(parts) >= 3, Trim(parts(3)), "")
        
        ' === Write extracted parts to E, F, G ===
        modelWS.Cells(currentRow, 5).Value = sheetName
        modelWS.Cells(currentRow, 5).HorizontalAlignment = xlLeft
        
        modelWS.Cells(currentRow, 6).Value = dueDateStr
        modelWS.Cells(currentRow, 6).HorizontalAlignment = xlCenter
        
        modelWS.Cells(currentRow, 7).Value = launchDates
        modelWS.Cells(currentRow, 7).HorizontalAlignment = xlLeft
        
        If Not IsDate(dueDateStr) Then
            modelWS.Cells(currentRow, 8).Value  = "Invalid Date"
            modelWS.Cells(currentRow, 9).Value  = "Invalid Date"
            modelWS.Cells(currentRow, 10).Value = "Invalid Date"
            modelWS.Cells(currentRow, 16).Value = "Invalid Date"
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        Dim dueDate As Date
        dueDate = CDate(dueDateStr)
        
        ' === Find matching sheet in alldata.xlsx ===
        On Error Resume Next
        Set dataWS = dataWB.Sheets(sheetName)
        On Error GoTo 0
        
        If dataWS Is Nothing Then
            modelWS.Cells(currentRow, 8).Value  = "Sheet Not Found"
            modelWS.Cells(currentRow, 9).Value  = "Sheet Not Found"
            modelWS.Cells(currentRow, 10).Value = "Sheet Not Found"
            modelWS.Cells(currentRow, 16).Value = "Sheet Not Found"
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        ' === Map column headers from B1:Q1 ===
        Dim colIndex          As Integer
        Dim dueColIdx         As Integer : dueColIdx = 0
        Dim tcinColIdx        As Integer : tcinColIdx = 0
        Dim assetStatusColIdx As Integer : assetStatusColIdx = 0
        Dim agencyColIdx      As Integer : agencyColIdx = 0
        
        For colIndex = 2 To 17
            Dim headerVal As String
            headerVal = Trim(LCase(dataWS.Cells(1, colIndex).Value))
            Select Case headerVal
                Case LCase(dueType)      : dueColIdx = colIndex
                Case "tcin"              : tcinColIdx = colIndex
                Case "asset status"      : assetStatusColIdx = colIndex
                Case "internal / agency" : agencyColIdx = colIndex
            End Select
        Next colIndex
        
        ' === Find last data row ===
        Dim lastDataRow As Long
        lastDataRow = dataWS.Cells(dataWS.Rows.Count, 2).End(xlUp).Row
        
        ' === P22 — Total TCIN count, no filter ===
        Dim totalTCINAll As Long : totalTCINAll = 0
        If tcinColIdx > 0 Then
            Dim tcinRow As Long
            For tcinRow = 2 To lastDataRow
                If Trim(CStr(dataWS.Cells(tcinRow, tcinColIdx).Value)) <> "" Then
                    totalTCINAll = totalTCINAll + 1
                End If
            Next tcinRow
        End If
        
        ' === H22, I22, J22 — all filtered by matching due date ===
        Dim totalDueCount     As Long : totalDueCount = 0
        Dim totalDone         As Long : totalDone = 0

        ' --- 4 counters for I22 ---
        Dim countAgency       As Long : countAgency = 0       ' Total rows where Internal/Agency = "Agency"
        Dim countAgencyDone   As Long : countAgencyDone = 0   ' Of those, how many have Asset Status = "Done"
        Dim countInternal     As Long : countInternal = 0     ' Total rows where Internal/Agency = "Internal"
        Dim countInternalDone As Long : countInternalDone = 0 ' Of those, how many have Asset Status = "Done"
        
        Dim dataRow As Long
        For dataRow = 2 To lastDataRow
        
            If dueColIdx > 0 Then
                Dim cellDueVal As Variant
                cellDueVal = dataWS.Cells(dataRow, dueColIdx).Value
                
                If IsDate(cellDueVal) Then
                    If CLng(CDate(cellDueVal)) = CLng(dueDate) Then
                    
                        ' H22 — Count every row matching due date in due type column
                        totalDueCount = totalDueCount + 1
                        
                        ' Read Asset Status once for this row
                        Dim assetStatusVal As String
                        assetStatusVal = ""
                        If assetStatusColIdx > 0 Then
                            assetStatusVal = Trim(LCase(dataWS.Cells(dataRow, assetStatusColIdx).Value))
                        End If
                        
                        ' J22 — Total Done count across all matching rows
                        If assetStatusVal = "done" Then
                            totalDone = totalDone + 1
                        End If
                        
                        ' I22 — Agency and Internal with their own Done sub-counts
                        If agencyColIdx > 0 Then
                            Dim agencyVal As String
                            agencyVal = Trim(LCase(dataWS.Cells(dataRow, agencyColIdx).Value))
                            
                            Select Case agencyVal
                            
                                Case "agency"
                                    countAgency = countAgency + 1
                                    ' Also check if this agency row is Done
                                    If assetStatusVal = "done" Then
                                        countAgencyDone = countAgencyDone + 1
                                    End If
                                    
                                Case "internal"
                                    countInternal = countInternal + 1
                                    ' Also check if this internal row is Done
                                    If assetStatusVal = "done" Then
                                        countInternalDone = countInternalDone + 1
                                    End If
                                    
                            End Select
                        End If
                        
                    End If
                End If
            End If
            
        Next dataRow
        
        ' === Build I22 output text ===
        ' Format: Internal: Done/Total, Agency: Done/Total
        ' Example: Internal: 22/100, Agency: 12/50
        Dim agencyOutput As String
        agencyOutput = "Internal: " & countInternalDone & "/" & countInternal & _
                       ", Agency: " & countAgencyDone & "/" & countAgency
        
        ' === Write all results ===
        With modelWS
        
            ' H22 — Count of rows in due type column matching due date
            With .Cells(currentRow, 8)
                .Value = totalDueCount
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
            End With
            
            ' I22 — Internal Done/Total and Agency Done/Total
            With .Cells(currentRow, 9)
                .Value = agencyOutput
                .HorizontalAlignment = xlLeft
                .Font.ColorIndex = xlAutomatic
            End With
            
            ' J22 — Total Done count across all matching rows
            With .Cells(currentRow, 10)
                .Value = totalDone
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
            End With
            
            ' P22 — Total TCIN count (no filter)
            With .Cells(currentRow, 16)
                .Value = totalTCINAll
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
            End With
            
        End With
        
        Set dataWS = Nothing
        currentRow = currentRow + 1
        
NextLine:
    Loop
    
    ' === Auto-fit columns ===
    modelWS.Columns(5).AutoFit    ' E - Project Name
    modelWS.Columns(6).AutoFit    ' F - Due Date
    modelWS.Columns(7).AutoFit    ' G - Launch Dates
    modelWS.Columns(8).AutoFit    ' H - Due type count filtered by date
    modelWS.Columns(9).AutoFit    ' I - Internal & Agency with Done counts
    modelWS.Columns(10).AutoFit   ' J - Total Done Count
    modelWS.Columns(16).AutoFit   ' P - Total TCIN no filter
    
    MsgBox "Done! " & (currentRow - 22) & " rows processed in Model sheet (D22 to D" & (currentRow - 1) & ").", vbInformation

End Sub
```

---

## How the 4 Counters Work Together

For every row that matches the due date, the macro reads **both** the `Internal / Agency` column and `Asset Status` column **on the same row** and increments the right counter:
```
Row matches due date 03/01/2025?
    ├── Internal/Agency = "Agency"  → countAgency++
    │       └── Asset Status = "Done"? → countAgencyDone++
    │
    └── Internal/Agency = "Internal" → countInternal++
            └── Asset Status = "Done"? → countInternalDone++

```
Column Reference
ColWhat it showsLogicDFull input stringasset due>>ProjectA>>03/01/2025>>06/01/2025, 07/30/2025EProject nameParsed parts(1)FDue dateParsed parts(2)GLaunch datesParsed parts(3)HCount of rows where asset due = 03/01/2025 in ProjectAFiltered count on due column itselfIAgency / InternalFiltered by matching due date rowsJDone countFiltered by matching due date rowsPTotal TCIN entries in entire ProjectA sheet

Internal: 22/100, Agency: 12/50
```

```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````
```````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````

Sub AnalyzeDueDates()

    Dim currentWB     As Workbook
    Dim dataWB        As Workbook
    Dim modelWS       As Worksheet
    Dim dataWS        As Worksheet
    
    Dim allDataPath   As String
    allDataPath = "C:\local\alldata.xlsx"
    
    Set currentWB = ThisWorkbook
    Set modelWS   = currentWB.Sheets("Model")
    
    ' === Open alldata.xlsx if not already open ===
    On Error Resume Next
    Set dataWB = Workbooks(Dir(allDataPath))
    On Error GoTo 0
    If dataWB Is Nothing Then
        Set dataWB = Workbooks.Open(allDataPath)
    End If
    
    ' ================================================================
    ' !! REMOVED: The bulk ClearContents on E:J and P that used to
    '    run before the loop — it was wiping ALL rows regardless of
    '    Q value, destroying preserved data on N rows.
    '    Now clearing happens ONLY row by row when Q = "Y"
    ' ================================================================
    
    Dim currentRow As Long
    currentRow = 22
    
    Do While True
    
        ' ================================================================
        ' STEP 1 — Read Column Q first, before touching ANYTHING
        '          Never modify the row until Q is confirmed as "Y"
        ' ================================================================
        Dim qVal As String
        qVal = Trim(UCase(modelWS.Cells(currentRow, 17).Value))   ' Column Q = 17
        
        If qVal = "" Then
            ' --------------------------------------------------------
            ' Q is blank → ABORT entire macro, preserve everything
            ' --------------------------------------------------------
            MsgBox "Row " & currentRow & ": Column Q is empty. Processing aborted." & _
                   vbNewLine & "Rows processed so far: " & (currentRow - 22), _
                   vbExclamation, "Aborted — Empty Q Cell"
            Exit Do
            
        ElseIf qVal = "N" Then
            ' --------------------------------------------------------
            ' Q = "N" → PRESERVE this row entirely, move to next
            '            Do NOT clear, do NOT write, do NOT touch
            ' --------------------------------------------------------
            currentRow = currentRow + 1
            GoTo NextLine
            
        ElseIf qVal <> "Y" Then
            ' --------------------------------------------------------
            ' Q = something unexpected → clear only this row's
            '     output cells and write error, then move on
            ' --------------------------------------------------------
            Call ClearOutputCells(modelWS, currentRow)
            WriteErrorToRow modelWS, currentRow, "Invalid Q value: " & qVal
            currentRow = currentRow + 1
            GoTo NextLine
            
        End If
        
        ' ================================================================
        ' STEP 2 — Q = "Y" confirmed
        '          NOW safe to clear this row's output cells before
        '          writing fresh results
        ' ================================================================
        Call ClearOutputCells(modelWS, currentRow)
        
        ' ================================================================
        ' STEP 3 — Check Column D is not blank
        ' ================================================================
        Dim dVal As String
        dVal = Trim(modelWS.Cells(currentRow, 4).Value)
        
        If dVal = "" Then
            MsgBox "Row " & currentRow & ": Column Q = Y but Column D is empty. Processing aborted." & _
                   vbNewLine & "Rows processed so far: " & (currentRow - 22), _
                   vbExclamation, "Aborted — Empty D Cell"
            Exit Do
        End If
        
        ' ================================================================
        ' STEP 4 — Parse D: due type>>ProjectName>>DueDate>>LaunchDates
        ' ================================================================
        Dim parts() As String
        parts = Split(dVal, ">>")
        
        If UBound(parts) < 2 Then
            WriteErrorToRow modelWS, currentRow, "Parse Error"
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        Dim dueType     As String
        Dim sheetName   As String
        Dim dueDateStr  As String
        Dim launchDates As String
        
        dueType     = Trim(parts(0))
        sheetName   = Trim(parts(1))
        dueDateStr  = Trim(parts(2))
        launchDates = IIf(UBound(parts) >= 3, Trim(parts(3)), "")
        
        ' === Write extracted parts to E, F, G ===
        With modelWS.Cells(currentRow, 5)
            .Value = sheetName
            .HorizontalAlignment = xlLeft
            .Font.ColorIndex = xlAutomatic
        End With
        
        With modelWS.Cells(currentRow, 6)
            .Value = dueDateStr
            .HorizontalAlignment = xlCenter
            .Font.ColorIndex = xlAutomatic
        End With
        
        With modelWS.Cells(currentRow, 7)
            .Value = launchDates
            .HorizontalAlignment = xlLeft
            .Font.ColorIndex = xlAutomatic
        End With
        
        ' === Validate due date ===
        If Not IsDate(dueDateStr) Then
            WriteErrorToRow modelWS, currentRow, "Invalid Date"
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        Dim dueDate As Date
        dueDate = CDate(dueDateStr)
        
        ' === Find matching sheet in alldata.xlsx ===
        On Error Resume Next
        Set dataWS = dataWB.Sheets(sheetName)
        On Error GoTo 0
        
        If dataWS Is Nothing Then
            WriteErrorToRow modelWS, currentRow, "Sheet Not Found: " & sheetName
            currentRow = currentRow + 1
            GoTo NextLine
        End If
        
        ' === Map column headers from B1:Q1 ===
        Dim colIndex          As Integer
        Dim dueColIdx         As Integer : dueColIdx = 0
        Dim tcinColIdx        As Integer : tcinColIdx = 0
        Dim assetStatusColIdx As Integer : assetStatusColIdx = 0
        Dim agencyColIdx      As Integer : agencyColIdx = 0
        
        For colIndex = 2 To 17
            Dim headerVal As String
            headerVal = Trim(LCase(dataWS.Cells(1, colIndex).Value))
            Select Case headerVal
                Case LCase(dueType)      : dueColIdx = colIndex
                Case "tcin"              : tcinColIdx = colIndex
                Case "asset status"      : assetStatusColIdx = colIndex
                Case "internal / agency" : agencyColIdx = colIndex
            End Select
        Next colIndex
        
        ' === Find last data row ===
        Dim lastDataRow As Long
        lastDataRow = dataWS.Cells(dataWS.Rows.Count, 2).End(xlUp).Row
        
        ' === P — Total TCIN count, no filter ===
        Dim totalTCINAll As Long : totalTCINAll = 0
        If tcinColIdx > 0 Then
            Dim tcinRow As Long
            For tcinRow = 2 To lastDataRow
                If Trim(CStr(dataWS.Cells(tcinRow, tcinColIdx).Value)) <> "" Then
                    totalTCINAll = totalTCINAll + 1
                End If
            Next tcinRow
        End If
        
        ' === H, I, J — filtered by matching due date ===
        Dim totalDueCount     As Long : totalDueCount = 0
        Dim totalDone         As Long : totalDone = 0
        Dim countAgency       As Long : countAgency = 0
        Dim countAgencyDone   As Long : countAgencyDone = 0
        Dim countInternal     As Long : countInternal = 0
        Dim countInternalDone As Long : countInternalDone = 0
        
        Dim dataRow As Long
        For dataRow = 2 To lastDataRow
        
            If dueColIdx > 0 Then
                Dim cellDueVal As Variant
                cellDueVal = dataWS.Cells(dataRow, dueColIdx).Value
                
                If IsDate(cellDueVal) Then
                    If CLng(CDate(cellDueVal)) = CLng(dueDate) Then
                    
                        totalDueCount = totalDueCount + 1
                        
                        Dim assetStatusVal As String
                        assetStatusVal = ""
                        If assetStatusColIdx > 0 Then
                            assetStatusVal = Trim(LCase(dataWS.Cells(dataRow, assetStatusColIdx).Value))
                        End If
                        
                        If assetStatusVal = "done" Then
                            totalDone = totalDone + 1
                        End If
                        
                        If agencyColIdx > 0 Then
                            Dim agencyVal As String
                            agencyVal = Trim(LCase(dataWS.Cells(dataRow, agencyColIdx).Value))
                            Select Case agencyVal
                                Case "agency"
                                    countAgency = countAgency + 1
                                    If assetStatusVal = "done" Then countAgencyDone = countAgencyDone + 1
                                Case "internal"
                                    countInternal = countInternal + 1
                                    If assetStatusVal = "done" Then countInternalDone = countInternalDone + 1
                            End Select
                        End If
                        
                    End If
                End If
            End If
            
        Next dataRow
        
        ' === Build I output text ===
        Dim agencyOutput As String
        agencyOutput = "Internal: " & countInternalDone & "/" & countInternal & _
                       ", Agency: " & countAgencyDone & "/" & countAgency
        
        ' === Write results — only reaches here when Q = "Y" ===
        With modelWS
        
            With .Cells(currentRow, 8)          ' H — Due type count
                .Value = totalDueCount
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
                .Font.ColorIndex = xlAutomatic
            End With
            
            With .Cells(currentRow, 9)          ' I — Internal/Agency with Done
                .Value = agencyOutput
                .HorizontalAlignment = xlLeft
                .Font.ColorIndex = xlAutomatic
            End With
            
            With .Cells(currentRow, 10)         ' J — Total Done
                .Value = totalDone
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
                .Font.ColorIndex = xlAutomatic
            End With
            
            With .Cells(currentRow, 16)         ' P — Total TCIN no filter
                .Value = totalTCINAll
                .NumberFormat = "0"
                .HorizontalAlignment = xlCenter
                .Font.ColorIndex = xlAutomatic
            End With
            
        End With
        
        Set dataWS = Nothing
        currentRow = currentRow + 1
        
NextLine:
    Loop
    
    ' === Auto-fit columns ===
    modelWS.Columns(5).AutoFit
    modelWS.Columns(6).AutoFit
    modelWS.Columns(7).AutoFit
    modelWS.Columns(8).AutoFit
    modelWS.Columns(9).AutoFit
    modelWS.Columns(10).AutoFit
    modelWS.Columns(16).AutoFit
    
    MsgBox "Done! " & (currentRow - 22) & " rows processed in Model sheet.", _
           vbInformation, "AnalyzeDueDates Complete"

End Sub

' ================================================================
' Helper — Clears only output cells E:J and P for a given row
'          Called ONLY when Q = "Y", never for N rows
' ================================================================
Private Sub ClearOutputCells(ws As Worksheet, rowNum As Long)
    ws.Range(ws.Cells(rowNum, 5), ws.Cells(rowNum, 10)).ClearContents    ' E to J
    ws.Range(ws.Cells(rowNum, 5), ws.Cells(rowNum, 10)).Font.ColorIndex = xlAutomatic
    ws.Cells(rowNum, 16).ClearContents                                    ' P
    ws.Cells(rowNum, 16).Font.ColorIndex = xlAutomatic
End Sub

' ================================================================
' Helper — Writes same error message to H, I, J, P in red
'          Called ONLY when Q = "Y" but something else fails
' ================================================================
Private Sub WriteErrorToRow(ws As Worksheet, rowNum As Long, errMsg As String)
    Dim c As Integer
    For Each c In Array(8, 9, 10, 16)   ' H, I, J, P
        With ws.Cells(rowNum, c)
            .Value = errMsg
            .Font.Color = RGB(200, 0, 0)
            .HorizontalAlignment = xlLeft
        End With
    Next c
End Sub

```

---

## Validation Flow for Every Row
```
Read Q column
    │
    ├── Q = BLANK  ──────────────────────→ ABORT with popup, stop entire macro
    │
    ├── Q = "N"    ──────────────────────→ SKIP row silently, move to next row
    │
    ├── Q = "Y"    ──────────────────────→ CHECK Column D next
    │                                           │
    │                                           ├── D = BLANK ──→ ABORT with popup
    │                                           │
    │                                           └── D has value → RUN full calculation
    │
    └── Q = anything else (e.g. "X", "y") ──→ Write red "Invalid Q: X" in H/I/J/P, skip row

