Attribute VB_Name = "modDashboard"
'==========================================================================
' modDashboard - rebuilds the Dashboard body (row 6 downwards) from the
' Database table: KPI tiles, open tasks by category, blocked/critical items.
' Rows 1-5 (title, buttons, archive base path) are created by modSetup.
'==========================================================================
Option Explicit

Private Const FIRST_BODY_ROW As Long = 6

' Fields of the alerts(field, n) array
Private Const AF_RANK As Long = 1
Private Const AF_SEV As Long = 2
Private Const AF_ID As Long = 3
Private Const AF_CAT As Long = 4
Private Const AF_TITLE As Long = 5
Private Const AF_STATUS As Long = 6
Private Const AF_ISSUE As Long = 7
Private Const AF_DAYS As Long = 8
Private Const AF_FOLDER As Long = 9
Private Const AF_COUNT As Long = 9

Private Const SEV_CRITICAL As String = "CRITICAL"
Private Const SEV_WARNING As String = "WARNING"

Private Const CLR_BRAND As Long = 7949855        ' RGB(31, 78, 121)

Public Sub RefreshDashboard()
    Dim ws As Worksheet, lo As ListObject
    Dim data As Variant, cats As Variant, stats As Variant
    Dim counts() As Long, alerts() As Variant, nAlerts As Long
    Dim i As Long, r As Long, c As Long, k As Long
    Dim catIdx As Long, stIdx As Long, status As String
    Dim nActive As Long, nWaiting As Long, nCritical As Long, nWarning As Long
    Dim firstCatRow As Long, firstAlertRow As Long, prevScreen As Boolean

    Set lo = DbTable()
    If lo Is Nothing Then Exit Sub
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    On Error GoTo 0
    If ws Is Nothing Then Exit Sub

    prevScreen = Application.ScreenUpdating
    Application.ScreenUpdating = False
    On Error GoTo EH

    cats = CategoryList()
    stats = StatusList()
    ReDim counts(0 To UBound(cats), 0 To UBound(stats))
    ReDim alerts(1 To AF_COUNT, 1 To 1)

    ' --- Collect counts and alerts ----------------------------------------------
    If Not lo.DataBodyRange Is Nothing Then
        data = lo.DataBodyRange.Value
        For i = 1 To UBound(data, 1)
            If Len(SafeStr(data(i, COL_ID))) > 0 Then
                status = SafeStr(data(i, COL_STATUS))
                catIdx = IndexOf(cats, SafeStr(data(i, COL_CATEGORY)))
                stIdx = IndexOf(stats, status)
                If catIdx >= 0 And stIdx >= 0 Then counts(catIdx, stIdx) = counts(catIdx, stIdx) + 1
                If status <> STATUS_DONE Then
                    nActive = nActive + 1
                    If status = STATUS_WAITING Then nWaiting = nWaiting + 1
                    CheckTask data, i, alerts, nAlerts
                End If
            End If
        Next i
    End If
    For k = 1 To nAlerts
        If alerts(AF_SEV, k) = SEV_CRITICAL Then nCritical = nCritical + 1 Else nWarning = nWarning + 1
    Next k
    SortAlerts alerts, nAlerts

    ' --- Write --------------------------------------------------------------------
    ClearBody ws
    ws.Range("B2").Value = "Last refreshed: " & Format$(Now, STAMP_FMT)

    ' KPI tiles (rows 7-8)
    WriteTile ws.Range("B7"), "Active tasks", nActive, CLR_BRAND
    WriteTile ws.Range("C7"), "Waiting on 3rd party", nWaiting, RGB(191, 143, 0)
    WriteTile ws.Range("D7"), "Critical", nCritical, RGB(192, 0, 0)
    WriteTile ws.Range("E7"), "Warnings", nWarning, RGB(237, 125, 49)

    ' Open tasks by category (row 10 ff.)
    r = 10
    SectionTitle ws.Cells(r, 2), "Open tasks by category"
    r = r + 1
    ws.Cells(r, 2).Resize(1, 6).Value = Array("Category", STATUS_OPEN, STATUS_INPROGRESS, _
                                              STATUS_WAITING, "Total active", STATUS_DONE)
    HeaderStyle ws.Cells(r, 2).Resize(1, 6)
    firstCatRow = r + 1
    For c = 0 To UBound(cats)
        r = r + 1
        ws.Cells(r, 2).Value = cats(c)
        ws.Cells(r, 3).Value = counts(c, 0)
        ws.Cells(r, 4).Value = counts(c, 1)
        ws.Cells(r, 5).Value = counts(c, 2)
        ws.Cells(r, 6).Value = counts(c, 0) + counts(c, 1) + counts(c, 2)
        ws.Cells(r, 7).Value = counts(c, 3)
        ws.Cells(r, 6).Font.Bold = True
    Next c
    r = r + 1
    ws.Cells(r, 2).Value = "Total"
    For c = 3 To 7
        ws.Cells(r, c).FormulaR1C1 = "=SUM(R" & firstCatRow & "C:R[-1]C)"
    Next c
    With ws.Range(ws.Cells(r, 2), ws.Cells(r, 7))
        .Font.Bold = True
        .Borders(xlEdgeTop).LineStyle = xlContinuous
        .Borders(xlEdgeTop).Color = CLR_BRAND
    End With
    GridStyle ws.Range(ws.Cells(firstCatRow - 1, 2), ws.Cells(r, 7))
    ws.Range(ws.Cells(firstCatRow, 3), ws.Cells(r, 7)).HorizontalAlignment = xlCenter

    ' Blocked / critical items
    r = r + 3
    SectionTitle ws.Cells(r, 2), "Blocked / critical items"
    ws.Cells(r, 5).Value = "Double-click a Task ID to open the task."
    ws.Cells(r, 5).Font.Italic = True
    ws.Cells(r, 5).Font.Color = RGB(128, 128, 128)
    r = r + 1
    ws.Cells(r, 2).Resize(1, 8).Value = Array("Severity", "Task ID", "Category", "Title", _
                                              "Status", "Issue", "Days", "Folder")
    HeaderStyle ws.Cells(r, 2).Resize(1, 8)
    firstAlertRow = r + 1
    If nAlerts = 0 Then
        r = r + 1
        ws.Cells(r, 2).Value = "No blocked or critical items."
        ws.Cells(r, 2).Font.Color = RGB(0, 97, 0)
        ws.Cells(r, 2).Resize(1, 8).Interior.Color = RGB(198, 239, 206)
    Else
        For k = 1 To nAlerts
            r = r + 1
            ws.Cells(r, 2).Value = alerts(AF_SEV, k)
            ws.Cells(r, 3).Value = alerts(AF_ID, k)
            ws.Cells(r, 4).Value = alerts(AF_CAT, k)
            ws.Cells(r, 5).Value = alerts(AF_TITLE, k)
            ws.Cells(r, 6).Value = alerts(AF_STATUS, k)
            ws.Cells(r, 7).Value = alerts(AF_ISSUE, k)
            ws.Cells(r, 8).Value = alerts(AF_DAYS, k)
            If InStr(1, alerts(AF_FOLDER, k), "\") > 0 Then
                ws.Cells(r, 9).Formula = "=HYPERLINK(""" & alerts(AF_FOLDER, k) & """,""Open"")"
                ws.Cells(r, 9).Font.Color = RGB(5, 99, 193)
                ws.Cells(r, 9).Font.Underline = xlUnderlineStyleSingle
            End If
            With ws.Range(ws.Cells(r, 2), ws.Cells(r, 8))
                If alerts(AF_SEV, k) = SEV_CRITICAL Then
                    .Interior.Color = RGB(255, 199, 206)
                    .Font.Color = RGB(156, 0, 6)
                Else
                    .Interior.Color = RGB(255, 235, 156)
                    .Font.Color = RGB(156, 87, 0)
                End If
            End With
            ws.Cells(r, 2).Font.Bold = True
        Next k
    End If
    GridStyle ws.Range(ws.Cells(firstAlertRow - 1, 2), ws.Cells(r, 9))
    ws.Range(ws.Cells(firstAlertRow, 7), ws.Cells(r, 7)).WrapText = True
    ws.Range(ws.Cells(firstAlertRow, 8), ws.Cells(r, 8)).HorizontalAlignment = xlCenter

    Application.ScreenUpdating = prevScreen
    Exit Sub

EH:
    Application.ScreenUpdating = prevScreen
    MsgBox "Dashboard refresh failed:" & vbLf & Err.Description, vbExclamation, APP_NAME
End Sub

'--------------------------------------------------------------------------
' Alert rules - one task (row i of data) may raise several alerts.
' Adjust thresholds in modConfig.
'--------------------------------------------------------------------------
Private Sub CheckTask(data As Variant, ByVal i As Long, alerts() As Variant, nAlerts As Long)
    Dim d As Long, vendor As String, customs As String

    Select Case SafeStr(data(i, COL_CATEGORY))

        Case CAT_PAYPAL
            ' Blocked by customs clearance / unpaid import charges
            customs = SafeStr(data(i, COL_CUSTOMS))
            If IsBlockedCustoms(customs) Then
                AddAlert alerts, nAlerts, SEV_CRITICAL, data, i, _
                         "Blocked - customs: " & customs, DaysSince(data(i, COL_DATE))
            End If

        Case CAT_AMOS
            If SafeStr(data(i, COL_HANDLING)) = HANDLING_REPAIR Then
                vendor = SafeStr(data(i, COL_VENDOR))
                If Len(vendor) = 0 Then vendor = "vendor unknown"
                If IsDate(data(i, COL_RETURN)) Then
                    d = DaysSince(data(i, COL_RETURN))          ' > 0 = overdue
                    If d > 0 Then
                        AddAlert alerts, nAlerts, SEV_CRITICAL, data, i, _
                                 "Repair overdue - expected back " & Format$(data(i, COL_RETURN), DATE_FMT) & _
                                 " (" & vendor & ")", d
                    ElseIf -d <= REPAIR_DUE_SOON_DAYS Then
                        AddAlert alerts, nAlerts, SEV_WARNING, data, i, _
                                 "Repair due back in " & -d & " day(s) (" & vendor & ")", -d
                    End If
                Else
                    AddAlert alerts, nAlerts, SEV_WARNING, data, i, _
                             "Third-party repair without expected return date (" & vendor & ")", _
                             DaysSince(data(i, COL_DATE))
                End If
            End If

        Case CAT_AMAZON
            If SafeStr(data(i, COL_INV_PAY)) <> "Yes" Then
                d = DaysSince(data(i, COL_DATE))
                If d >= AMAZON_INVOICE_DAYS Then
                    AddAlert alerts, nAlerts, SEV_WARNING, data, i, _
                             "Not yet sent to Invoice Team for payment", d
                End If
            End If
    End Select

    ' Any category: waiting on a third party without any update for too long
    If SafeStr(data(i, COL_STATUS)) = STATUS_WAITING Then
        d = DaysSince(data(i, COL_MODIFIED))
        If d >= WAITING_STALE_DAYS Then
            AddAlert alerts, nAlerts, SEV_WARNING, data, i, _
                     "Waiting on third party - no update for " & d & " days", d
        End If
    End If
End Sub

Private Sub AddAlert(alerts() As Variant, nAlerts As Long, ByVal sev As String, _
                     data As Variant, ByVal i As Long, ByVal issue As String, ByVal days As Long)
    nAlerts = nAlerts + 1
    If nAlerts > UBound(alerts, 2) Then ReDim Preserve alerts(1 To AF_COUNT, 1 To nAlerts * 2)
    alerts(AF_RANK, nAlerts) = IIf(sev = SEV_CRITICAL, 1, 2)
    alerts(AF_SEV, nAlerts) = sev
    alerts(AF_ID, nAlerts) = SafeStr(data(i, COL_ID))
    alerts(AF_CAT, nAlerts) = SafeStr(data(i, COL_CATEGORY))
    alerts(AF_TITLE, nAlerts) = SafeStr(data(i, COL_TITLE))
    alerts(AF_STATUS, nAlerts) = SafeStr(data(i, COL_STATUS))
    alerts(AF_ISSUE, nAlerts) = issue
    alerts(AF_DAYS, nAlerts) = days
    alerts(AF_FOLDER, nAlerts) = SafeStr(data(i, COL_FOLDER))
End Sub

' Critical first, then the largest number of days first
Private Sub SortAlerts(alerts() As Variant, ByVal n As Long)
    Dim i As Long, j As Long, k As Long, tmp As Variant
    For i = 1 To n - 1
        For j = i + 1 To n
            If alerts(AF_RANK, j) < alerts(AF_RANK, i) Or _
               (alerts(AF_RANK, j) = alerts(AF_RANK, i) And alerts(AF_DAYS, j) > alerts(AF_DAYS, i)) Then
                For k = 1 To AF_COUNT
                    tmp = alerts(k, i): alerts(k, i) = alerts(k, j): alerts(k, j) = tmp
                Next k
            End If
        Next j
    Next i
End Sub

'--------------------------------------------------------------------------
' Formatting helpers
'--------------------------------------------------------------------------
Private Sub ClearBody(ByVal ws As Worksheet)
    Dim lastRow As Long, rng As Range
    lastRow = ws.UsedRange.Row + ws.UsedRange.Rows.Count
    If lastRow < FIRST_BODY_ROW + 40 Then lastRow = FIRST_BODY_ROW + 40
    Set rng = ws.Range(ws.Rows(FIRST_BODY_ROW), ws.Rows(lastRow))
    rng.Clear
    rng.RowHeight = ws.StandardHeight
End Sub

Private Sub WriteTile(ByVal cell As Range, ByVal caption As String, ByVal value As Long, ByVal color As Long)
    With cell
        .Value = caption
        .Font.Size = 9
        .Font.Color = RGB(89, 89, 89)
        .HorizontalAlignment = xlCenter
    End With
    With cell.Offset(1, 0)
        .Value = value
        .Font.Size = 22
        .Font.Bold = True
        .Font.Color = color
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .RowHeight = 34
    End With
    With cell.Resize(2, 1)
        .Interior.Color = RGB(242, 242, 242)
        .BorderAround xlContinuous, xlThin
        .Borders(xlEdgeLeft).Color = color
        .Borders(xlEdgeLeft).Weight = xlThick
    End With
End Sub

Private Sub SectionTitle(ByVal cell As Range, ByVal caption As String)
    cell.Value = caption
    cell.Font.Size = 12
    cell.Font.Bold = True
    cell.Font.Color = CLR_BRAND
End Sub

Private Sub HeaderStyle(ByVal rng As Range)
    rng.Font.Bold = True
    rng.Font.Color = vbWhite
    rng.Interior.Color = CLR_BRAND
    rng.VerticalAlignment = xlCenter
End Sub

Private Sub GridStyle(ByVal rng As Range)
    With rng.Borders(xlInsideHorizontal)
        .LineStyle = xlContinuous
        .Color = RGB(217, 217, 217)
    End With
    With rng.Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .Color = RGB(217, 217, 217)
    End With
    rng.VerticalAlignment = xlTop
End Sub

'--------------------------------------------------------------------------
' Value helpers
'--------------------------------------------------------------------------
Private Function SafeStr(ByVal v As Variant) As String
    If IsError(v) Or IsNull(v) Or IsEmpty(v) Then Exit Function
    SafeStr = Trim$(CStr(v))
End Function

Private Function DaysSince(ByVal v As Variant) As Long
    If IsError(v) Then Exit Function
    If IsDate(v) Then DaysSince = CLng(Date - Int(CDate(v)))
End Function

' 0-based position of s in arr (case-insensitive), -1 if missing
Private Function IndexOf(ByVal arr As Variant, ByVal s As String) As Long
    Dim i As Long
    For i = LBound(arr) To UBound(arr)
        If StrComp(arr(i), s, vbTextCompare) = 0 Then IndexOf = i - LBound(arr): Exit Function
    Next i
    IndexOf = -1
End Function
