Attribute VB_Name = "modSetup"
'==========================================================================
' modSetup - run SetupWorkbook ONCE (Alt+F8) to build the Dashboard and
' Database sheets, the task table, the base-path cell and the buttons.
' Safe to run again: existing tasks in the Database are kept.
'==========================================================================
Option Explicit

Public Sub SetupWorkbook()
    Dim wsDash As Worksheet, wsDb As Worksheet

    On Error GoTo EH
    Application.ScreenUpdating = False

    Set wsDash = GetOrCreateSheet(SHEET_DASHBOARD)
    Set wsDb = GetOrCreateSheet(SHEET_DATABASE)
    wsDash.Move Before:=ThisWorkbook.Sheets(1)
    wsDb.Move After:=ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    Set wsDash = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    Set wsDb = ThisWorkbook.Worksheets(SHEET_DATABASE)

    BuildDatabaseSheet wsDb
    BuildDashboardSheet wsDash
    RefreshDashboard

    wsDash.Activate
    wsDash.Range("A1").Select
    Application.ScreenUpdating = True
    MsgBox "Setup complete." & vbLf & vbLf & _
           "1. Enter your archive folder in Dashboard cell C4." & vbLf & _
           "2. Click 'New Task' to create the first task.", vbInformation, APP_NAME
    Exit Sub

EH:
    Application.ScreenUpdating = True
    MsgBox "Setup failed:" & vbLf & Err.Description, vbCritical, APP_NAME
End Sub

'--------------------------------------------------------------------------
Private Sub BuildDatabaseSheet(ByVal ws As Worksheet)
    Dim lo As ListObject, widths As Variant, col As Variant, c As Long

    ws.Unprotect DB_PASSWORD
    On Error Resume Next
    Set lo = ws.ListObjects(TABLE_NAME)
    On Error GoTo 0

    ' Column formats first, so the table and new rows inherit them
    For Each col In Array(COL_ID, COL_TITLE, COL_ORDERNO, COL_CUSTOMS, COL_VENDOR, COL_NOTES)
        ws.Columns(col).NumberFormat = "@"              ' keep text as text (leading zeros, "=...")
    Next col
    ws.Columns(COL_DATE).NumberFormat = DATE_FMT
    ws.Columns(COL_RETURN).NumberFormat = DATE_FMT
    ws.Columns(COL_CREATED).NumberFormat = STAMP_FMT
    ws.Columns(COL_MODIFIED).NumberFormat = STAMP_FMT

    If lo Is Nothing Then
        ws.Cells.Clear
        ws.Cells(1, 1).Resize(1, COL_COUNT).Value = DbHeaders()
        Set lo = ws.ListObjects.Add(xlSrcRange, ws.Cells(1, 1).Resize(1, COL_COUNT), , xlYes)
        lo.Name = TABLE_NAME
    End If
    lo.TableStyle = "TableStyleMedium2"
    lo.HeaderRowRange.WrapText = True
    lo.HeaderRowRange.VerticalAlignment = xlCenter

    widths = Array(15, 36, 12, 20, 10, 22, 12, 12, 26, 10, 18, 24, 12, 40, 36, 16, 16)
    For c = 1 To COL_COUNT
        ws.Columns(c).ColumnWidth = widths(c - 1)
    Next c
    ws.Rows(1).RowHeight = 30

    ws.Activate
    ActiveWindow.FreezePanes = False
    ws.Range("B2").Select
    ActiveWindow.FreezePanes = True
    ws.Tab.Color = RGB(128, 128, 128)

    ProtectDatabase ws
End Sub

'--------------------------------------------------------------------------
Private Sub BuildDashboardSheet(ByVal ws As Worksheet)
    Dim basePath As String, widths As Variant, c As Long, x As Single

    ' Keep a base path that was already entered
    On Error Resume Next
    basePath = CStr(ThisWorkbook.Names(NAME_BASEPATH).RefersToRange.Value)
    ws.Buttons.Delete
    On Error GoTo 0
    If Len(basePath) = 0 Then basePath = DEFAULT_BASE_PATH

    ws.Cells.Clear
    ws.Cells.Font.Size = 10
    widths = Array(2, 16, 18, 14, 38, 22, 48, 8, 14)
    For c = 1 To 9
        ws.Columns(c).ColumnWidth = widths(c - 1)
    Next c

    With ws.Range("B1")
        .Value = "SCM & Logistics Task Dashboard"
        .Font.Size = 18
        .Font.Bold = True
        .Font.Color = RGB(31, 78, 121)
    End With
    ws.Rows(1).RowHeight = 30
    With ws.Range("B2")
        .Font.Italic = True
        .Font.Color = RGB(128, 128, 128)
    End With

    ' Archive base path (editable, named SCM_BasePath)
    ws.Range("B4").Value = "Archive base path:"
    ws.Range("B4").Font.Bold = True
    With ws.Range("C4:E4")
        .Merge
        .HorizontalAlignment = xlLeft
        .Interior.Color = RGB(255, 242, 204)
        .BorderAround xlContinuous, xlThin
        .NumberFormat = "@"
    End With
    ws.Range("C4").Value = basePath
    ws.Range("F4").Value = "New task folders: <base path>\<Task ID>"
    ws.Range("F4").Font.Italic = True
    ws.Range("F4").Font.Color = RGB(128, 128, 128)
    ThisWorkbook.Names.Add Name:=NAME_BASEPATH, RefersTo:="='" & ws.Name & "'!$C$4"

    ' Buttons (Form controls, top right)
    x = ws.Range("F1").Left
    AddMacroButton ws, "New Task", "NewTask", x, 6
    AddMacroButton ws, "Edit Task", "EditTask", x + 100, 6
    AddMacroButton ws, "Refresh", "RefreshDashboard", x + 200, 6
    AddMacroButton ws, "Open Archive", "OpenArchiveRoot", x + 300, 6

    ws.Activate
    ActiveWindow.DisplayGridlines = False
    ws.Tab.Color = RGB(31, 78, 121)
End Sub

Private Sub AddMacroButton(ByVal ws As Worksheet, ByVal caption As String, ByVal macro As String, _
                           ByVal x As Single, ByVal y As Single)
    Dim b As Object
    Set b = ws.Buttons.Add(x, y, 94, 26)
    b.Caption = caption
    b.OnAction = macro
    b.Font.Bold = True
    b.Placement = xlFreeFloating
End Sub

Private Function GetOrCreateSheet(ByVal sheetName As String) As Worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)
    On Error GoTo 0
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        ws.Name = sheetName
    End If
    Set GetOrCreateSheet = ws
End Function
