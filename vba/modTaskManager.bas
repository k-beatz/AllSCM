Attribute VB_Name = "modTaskManager"
'==========================================================================
' modTaskManager - task IDs, reading and writing the Database table,
' and the macros behind the "New Task" / "Edit Task" buttons.
'==========================================================================
Option Explicit

'--------------------------------------------------------------------------
' Button macros
'--------------------------------------------------------------------------
Public Sub NewTask()
    Dim f As frmTask
    If Not DatabaseReady() Then Exit Sub
    Set f = New frmTask
    f.PrepareNew
    f.Show
    Unload f
End Sub

Public Sub EditTask()
    Dim taskId As String
    If Not DatabaseReady() Then Exit Sub
    taskId = InputBox("Task ID to edit:", APP_NAME, GuessSelectedTaskId())
    taskId = UCase$(Trim$(taskId))
    If Len(taskId) = 0 Then Exit Sub
    EditTaskById taskId
End Sub

Public Sub EditTaskById(ByVal taskId As String)
    Dim f As frmTask
    If Not DatabaseReady() Then Exit Sub
    If FindTaskRow(taskId) = 0 Then
        MsgBox "Task " & taskId & " was not found in the Database.", vbExclamation, APP_NAME
        Exit Sub
    End If
    Set f = New frmTask
    If f.LoadTask(taskId) Then f.Show
    Unload f
End Sub

'--------------------------------------------------------------------------
' Database access
'--------------------------------------------------------------------------
Public Function DbTable() As ListObject
    On Error Resume Next
    Set DbTable = ThisWorkbook.Worksheets(SHEET_DATABASE).ListObjects(TABLE_NAME)
End Function

Public Function IsTaskId(ByVal s As String) As Boolean
    IsTaskId = (UCase$(Trim$(s)) Like UCase$(TASK_PREFIX) & "-####-####")
End Function

' Next free ID for the current year, e.g. SCM-2026-0042
Public Function NextTaskId() As String
    Dim lo As ListObject, cell As Range, prefix As String, s As String
    Dim n As Long, maxN As Long

    prefix = UCase$(TASK_PREFIX) & "-" & Format$(Date, "yyyy") & "-"
    Set lo = DbTable()
    If Not lo Is Nothing Then
        If Not lo.DataBodyRange Is Nothing Then
            For Each cell In lo.ListColumns(COL_ID).DataBodyRange.Cells
                s = UCase$(CStr(cell.Value))
                If Left$(s, Len(prefix)) = prefix Then
                    n = Val(Mid$(s, Len(prefix) + 1))
                    If n > maxN Then maxN = n
                End If
            Next cell
        End If
    End If
    NextTaskId = prefix & Format$(maxN + 1, "0000")
End Function

' Worksheet row of a task (0 = not found)
Public Function FindTaskRow(ByVal taskId As String) As Long
    Dim lo As ListObject, m As Variant
    Set lo = DbTable()
    If lo Is Nothing Then Exit Function
    If lo.DataBodyRange Is Nothing Then Exit Function
    m = Application.Match(taskId, lo.ListColumns(COL_ID).DataBodyRange, 0)
    If Not IsError(m) Then FindTaskRow = lo.DataBodyRange.Rows(m).Row
End Function

' Reads one task into rec(1 To COL_COUNT); folderPath receives the linked folder.
Public Function GetTaskRecord(ByVal taskId As String, ByRef rec As Variant, _
                              ByRef folderPath As String) As Boolean
    Dim ws As Worksheet, r As Long, c As Long
    r = FindTaskRow(taskId)
    If r = 0 Then Exit Function
    Set ws = DbTable().Parent
    ReDim rec(1 To COL_COUNT)
    For c = 1 To COL_COUNT
        rec(c) = ws.Cells(r, c).Value
    Next c
    folderPath = FolderPathOf(ws.Cells(r, COL_FOLDER))
    GetTaskRecord = True
End Function

' Inserts (isNew = True) or updates a task. rec(1 To COL_COUNT) comes from frmTask.
' New tasks get their Task ID here, then the task folder is created and linked.
Public Function SaveTask(ByRef rec As Variant, ByVal isNew As Boolean) As Boolean
    Dim ws As Worksheet, lo As ListObject
    Dim r As Long, c As Long
    Dim folderPath As String, existingPath As String, folderOk As Boolean
    Dim errMsg As String

    Set lo = DbTable()
    If lo Is Nothing Then
        MsgBox "Database table not found. Run SetupWorkbook first.", vbCritical, APP_NAME
        Exit Function
    End If
    Set ws = lo.Parent

    On Error GoTo EH
    Application.ScreenUpdating = False
    ws.Unprotect DB_PASSWORD

    If isNew Then
        rec(COL_ID) = NextTaskId()
        rec(COL_CREATED) = Now
        r = NewDataRow(lo)
    Else
        r = FindTaskRow(CStr(rec(COL_ID)))
        If r = 0 Then Err.Raise vbObjectError + 513, , "Task " & rec(COL_ID) & " no longer exists in the Database."
        rec(COL_CREATED) = ws.Cells(r, COL_CREATED).Value
        existingPath = FolderPathOf(ws.Cells(r, COL_FOLDER))
    End If
    rec(COL_MODIFIED) = Now

    For c = 1 To COL_COUNT
        If c <> COL_FOLDER Then ws.Cells(r, c).Value = rec(c)
    Next c

    ' --- Task folder + clickable link --------------------------------------
    ' Existing tasks keep their folder, even if the base path was changed later.
    ' A folder that failed on creation is retried on every save.
    If Len(existingPath) > 0 Then
        folderPath = existingPath
    Else
        folderPath = TaskFolderPath(CStr(rec(COL_ID)))
    End If
    folderOk = EnsureFolder(folderPath)
    If folderOk Then
        SetFolderLink ws.Cells(r, COL_FOLDER), folderPath
    ElseIf Len(existingPath) = 0 Then
        ws.Cells(r, COL_FOLDER).Value = FOLDER_FAIL_TEXT
    End If

    ProtectDatabase ws
    RefreshDashboard
    Application.ScreenUpdating = True
    SaveTask = True

    ' --- Feedback ---------------------------------------------------------------
    If Not folderOk Then
        MsgBox "Task " & rec(COL_ID) & " was saved, but its folder could not be created:" & vbLf & _
               folderPath & vbLf & vbLf & _
               "Check the Archive base path on the Dashboard (cell C4) and your access rights." & vbLf & _
               "The folder is created automatically the next time you save this task.", _
               vbExclamation, APP_NAME
    ElseIf isNew Then
        If MsgBox("Task " & rec(COL_ID) & " created." & vbLf & vbLf & _
                  "Folder:" & vbLf & folderPath & vbLf & vbLf & _
                  "Open the folder now to add documents?", vbYesNo + vbQuestion, APP_NAME) = vbYes Then
            OpenFolder folderPath
        End If
    Else
        MsgBox "Task " & rec(COL_ID) & " updated.", vbInformation, APP_NAME
    End If
    Exit Function

EH:
    errMsg = Err.Description
    On Error Resume Next
    ProtectDatabase ws
    Application.ScreenUpdating = True
    MsgBox "The task could not be saved:" & vbLf & errMsg, vbCritical, APP_NAME
End Function

Public Sub ProtectDatabase(ByVal ws As Worksheet)
    ws.Protect Password:=DB_PASSWORD, DrawingObjects:=True, Contents:=True, _
               AllowFiltering:=True, AllowFormattingColumns:=True
End Sub

'--------------------------------------------------------------------------
' Shared date helpers (used by frmTask)
'--------------------------------------------------------------------------
Public Function TryParseDate(ByVal s As String, ByRef d As Date) As Boolean
    s = Trim$(s)
    If Len(s) = 0 Then Exit Function
    If Not IsDate(s) Then Exit Function
    d = CDate(s)
    TryParseDate = (Year(d) >= 2000 And Year(d) <= 2100)
End Function

' Uses the Windows regional short date, so it parses back with TryParseDate
Public Function FormatDateShort(ByVal d As Date) As String
    FormatDateShort = Format$(d, "Short Date")
End Function

'--------------------------------------------------------------------------
' Private helpers
'--------------------------------------------------------------------------
Private Function DatabaseReady() As Boolean
    If DbTable() Is Nothing Then
        MsgBox "The Database table was not found." & vbLf & _
               "Run the macro SetupWorkbook once (Alt+F8).", vbExclamation, APP_NAME
        Exit Function
    End If
    DatabaseReady = True
End Function

' A freshly created table contains one empty row - reuse it for the first task.
Private Function NewDataRow(ByVal lo As ListObject) As Long
    If lo.ListRows.Count = 1 Then
        If Application.WorksheetFunction.CountA(lo.ListRows(1).Range) = 0 Then
            NewDataRow = lo.ListRows(1).Range.Row
            Exit Function
        End If
    End If
    NewDataRow = lo.ListRows.Add(AlwaysInsert:=True).Range.Row
End Function

' Task ID of the current selection (Dashboard or Database), used as InputBox default
Private Function GuessSelectedTaskId() As String
    Dim v As Variant
    On Error GoTo Done
    If TypeName(Selection) <> "Range" Then Exit Function
    v = ActiveCell.Value
    If Not IsError(v) Then
        If IsTaskId(CStr(v)) Then GuessSelectedTaskId = CStr(v): Exit Function
    End If
    If ActiveSheet.Name = SHEET_DATABASE And ActiveCell.Row > 1 Then
        v = ActiveSheet.Cells(ActiveCell.Row, COL_ID).Value
        If Not IsError(v) Then
            If IsTaskId(CStr(v)) Then GuessSelectedTaskId = CStr(v)
        End If
    End If
Done:
End Function
