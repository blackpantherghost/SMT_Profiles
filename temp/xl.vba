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
    
    ' === Clear previous output from J20 downward before writing fresh ===
    Dim lastUsedRow As Long
    lastUsedRow = glossaryWS.Cells(glossaryWS.Rows.Count, 10).End(xlUp).Row
    If lastUsedRow >= 20 Then
        glossaryWS.Range("J20:J" & lastUsedRow).ClearContents
    End If
    
    ' === Output starts at J20, each line gets its own row ===
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
            
            Dim dueDateLaunchMap As Object
            Set dueDateLaunchMap = CreateObject("Scripting.Dictionary")
            Dim dueDateOrder As Object
            Set dueDateOrder = CreateObject("Scripting.Dictionary")
            Dim orderIdx As Long
            orderIdx = 0
            
            Dim r As Long
            For r = 2 To lastDataRow
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
                
                If Not dueDateOrder.Exists(dueVal) Then
                    dueDateOrder.Add dueVal, orderIdx
                    orderIdx = orderIdx + 1
                End If
                
                If Not dueDateLaunchMap.Exists(dueVal) Then
                    Dim innerDict As Object
                    Set innerDict = CreateObject("Scripting.Dictionary")
                    dueDateLaunchMap.Add dueVal, innerDict
                End If
                
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
                    
                    If launchVal <> "" And launchVal <> "0" Then
                        If Not dueDateLaunchMap(dueVal).Exists(launchVal) Then
                            dueDateLaunchMap(dueVal).Add launchVal, 1
                        End If
                    End If
                End If
                
NextRow2:
            Next r
            
            ' Build sorted due date keys
            Dim keysSorted() As String
            ReDim keysSorted(dueDateOrder.Count - 1)
            Dim k As Variant
            For Each k In dueDateOrder.Keys
                keysSorted(dueDateOrder(k)) = CStr(k)
            Next k
            
            ' === Write one line per due date into its own row in column J ===
            Dim idx As Long
            For idx = 0 To UBound(keysSorted)
                Dim thisDueDate As String
                thisDueDate = keysSorted(idx)
                If thisDueDate = "" Then GoTo NextDueDate
                
                Dim launchDatesStr As String
                launchDatesStr = ""
                If dueDateLaunchMap.Exists(thisDueDate) Then
                    launchDatesStr = Join(dueDateLaunchMap(thisDueDate).Keys, ", ")
                End If
                
                Dim lineStr As String
                lineStr = dueColName & ">>" & projectName & ">>" & thisDueDate & ">>" & launchDatesStr
                
                ' Write to column J, current output row
                With glossaryWS.Cells(outputRow, 10)   ' Column J = 10
                    .Value = lineStr
                    .HorizontalAlignment = xlLeft
                    .VerticalAlignment = xlCenter
                End With
                
                outputRow = outputRow + 1   ' Move to next row for next line
                
NextDueDate:
            Next idx
            
            Set dueDateLaunchMap = Nothing
            Set dueDateOrder = Nothing
            
NextDueCol:
        Next d
        
        Set dataWS = Nothing
        
NextRow:
    Next i
    
    ' Auto-fit column J width to fit content
    glossaryWS.Columns(10).AutoFit
    
    MsgBox "Done! " & (outputRow - 20) & " rows written to Glossary column J starting at J20.", vbInformation

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

          
