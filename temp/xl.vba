Sub CollectDueDates()

    Dim currentWB As Workbook
    Dim dataWB As Workbook
    Dim glossaryWS As Worksheet
    Dim dataWS As Worksheet
    Dim outputWS As Worksheet
    
    Dim projectName As String
    Dim allDataPath As String
    
    ' === CONFIGURATION ===
    allDataPath = "C:\local\alldata.xlsx"
    
    ' Due date column labels to search for (must match headers in alldata.xlsx B1:Q1)
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
    
    ' Prepare output sheet
    On Error Resume Next
    Set outputWS = currentWB.Sheets("DueDates_Output")
    On Error GoTo 0
    If outputWS Is Nothing Then
        Set outputWS = currentWB.Sheets.Add(After:=currentWB.Sheets(currentWB.Sheets.Count))
        outputWS.Name = "DueDates_Output"
    Else
        outputWS.Cells.Clear
    End If
    
    ' Header
    outputWS.Cells(1, 1).Value = "Output"
    Dim outputRow As Long
    outputRow = 2
    
    Dim i As Long
    For i = 6 To 15
        projectName = Trim(glossaryWS.Cells(i, 8).Value)  ' Column H
        
        If projectName = "" Then GoTo NextRow
        
        ' Find matching sheet in alldata.xlsx
        On Error Resume Next
        Set dataWS = dataWB.Sheets(projectName)
        On Error GoTo 0
        
        If dataWS Is Nothing Then GoTo NextRow
        
        ' Map headers B1:Q1 to column indices
        Dim j As Integer
        Dim colMap(2 To 17) As String
        For j = 2 To 17
            colMap(j) = Trim(LCase(dataWS.Cells(1, j).Value))
        Next j
        
        ' Find Launch dates column index
        Dim launchColIdx As Integer
        launchColIdx = 0
        For j = 2 To 17
            If LCase(colMap(j)) = LCase(launchColName) Then
                launchColIdx = j
                Exit For
            End If
        Next j
        
        ' Find last data row
        Dim lastDataRow As Long
        lastDataRow = dataWS.Cells(dataWS.Rows.Count, 2).End(xlUp).Row
        
        ' Loop through each due column type
        Dim d As Integer
        For d = 0 To UBound(dueCols)
            Dim dueColName As String
            dueColName = Trim(dueCols(d))
            
            ' Find this due column index
            Dim dueColIdx As Integer
            dueColIdx = 0
            For j = 2 To 17
                If LCase(colMap(j)) = LCase(dueColName) Then
                    dueColIdx = j
                    Exit For
                End If
            Next j
            
            If dueColIdx = 0 Then GoTo NextDueCol
            
            ' --- KEY CHANGE: Build a dictionary of due date -> unique launch dates ---
            ' dueDateLaunchMap: Key = due date string, Value = Dictionary of unique launch dates
            Dim dueDateLaunchMap As Object
            Set dueDateLaunchMap = CreateObject("Scripting.Dictionary")
            
            ' Also track insertion order of due dates
            Dim dueDateOrder As Object
            Set dueDateOrder = CreateObject("Scripting.Dictionary")
            Dim orderIdx As Long
            orderIdx = 0
            
            Dim r As Long
            For r = 2 To lastDataRow
                ' Get due date value
                Dim dueCell As Variant
                dueCell = dataWS.Cells(r, dueColIdx).Value
                
                Dim dueVal As String
                dueVal = ""
                If dueCell <> "" And Not IsEmpty(dueCell) Then
                    If IsDate(dueCell) Then
                        dueVal = Format(CDate(dueCell), "YYYY-MM-DD")
                    Else
                        dueVal = Trim(CStr(dueCell))
                    End If
                End If
                
                If dueVal = "" Or dueVal = "0" Then GoTo NextRow2
                
                ' Track insertion order
                If Not dueDateOrder.Exists(dueVal) Then
                    dueDateOrder.Add dueVal, orderIdx
                    orderIdx = orderIdx + 1
                End If
                
                ' Initialize inner launch date dictionary if needed
                If Not dueDateLaunchMap.Exists(dueVal) Then
                    Dim innerDict As Object
                    Set innerDict = CreateObject("Scripting.Dictionary")
                    dueDateLaunchMap.Add dueVal, innerDict
                End If
                
                ' Get launch date for this row
                If launchColIdx > 0 Then
                    Dim launchCell As Variant
                    launchCell = dataWS.Cells(r, launchColIdx).Value
                    
                    Dim launchVal As String
                    launchVal = ""
                    If launchCell <> "" And Not IsEmpty(launchCell) Then
                        If IsDate(launchCell) Then
                            launchVal = Format(CDate(launchCell), "YYYY-MM-DD")
                        Else
                            launchVal = Trim(CStr(launchCell))
                        End If
                    End If
                    
                    ' Add launch date to this due date's inner dictionary (unique only)
                    If launchVal <> "" And launchVal <> "0" Then
                        If Not dueDateLaunchMap(dueVal).Exists(launchVal) Then
                            dueDateLaunchMap(dueVal).Add launchVal, 1
                        End If
                    End If
                End If
                
NextRow2:
            Next r
            
            ' --- Write one line per unique due date ---
            ' Sort by insertion order (dueDateOrder values)
            Dim keysSorted() As String
            ReDim keysSorted(dueDateOrder.Count - 1)
            Dim k As Variant
            For Each k In dueDateOrder.Keys
                keysSorted(dueDateOrder(k)) = CStr(k)
            Next k
            
            Dim idx As Long
            For idx = 0 To UBound(keysSorted)
                Dim thisDueDate As String
                thisDueDate = keysSorted(idx)
                
                If thisDueDate = "" Then GoTo NextDueDate
                
                ' Build launch dates string (comma separated)
                Dim launchDatesStr As String
                launchDatesStr = ""
                If dueDateLaunchMap.Exists(thisDueDate) Then
                    launchDatesStr = Join(dueDateLaunchMap(thisDueDate).Keys, ", ")
                End If
                
                ' Format: due type>>SheetName>>due date>>launch dates
                Dim outputStr As String
                outputStr = dueColName & ">>" & projectName & ">>" & thisDueDate & ">>" & launchDatesStr
                
                outputWS.Cells(outputRow, 1).Value = outputStr
                outputRow = outputRow + 1
                
NextDueDate:
            Next idx
            
            Set dueDateLaunchMap = Nothing
            Set dueDateOrder = Nothing
            
NextDueCol:
        Next d
        
        Set dataWS = Nothing
        
NextRow:
    Next i
    
    outputWS.Columns(1).AutoFit
    
    MsgBox "Done! Results written to 'DueDates_Output' sheet. " & (outputRow - 2) & " rows generated.", vbInformation

End Sub
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

          
