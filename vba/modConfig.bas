Attribute VB_Name = "modConfig"
'==========================================================================
' modConfig - central settings, Database column map and drop-down lists.
' Change values here; every other module reads its settings from this one.
'==========================================================================
Option Explicit

Public Const APP_NAME As String = "SCM Task Manager"

' --- Sheets / table ----------------------------------------------------------
Public Const SHEET_DASHBOARD As String = "Dashboard"
Public Const SHEET_DATABASE As String = "Database"
Public Const TABLE_NAME As String = "tblTasks"
Public Const DB_PASSWORD As String = "scm"      ' protects Database against accidental edits

' --- Folder archive ------------------------------------------------------------
' Used only when the "Archive base path" cell on the Dashboard (C4) is empty.
' Environment variables are expanded, e.g. "%USERPROFILE%\Documents\SCM_Archive".
' Network paths work too, e.g. "\\fileserver\logistics\SCM_Archive".
Public Const DEFAULT_BASE_PATH As String = "C:\SCM_Archive"
Public Const NAME_BASEPATH As String = "SCM_BasePath"   ' workbook name -> Dashboard!$C$4
Public Const FOLDER_FAIL_TEXT As String = "Folder not created"

' --- Task IDs: SCM-2026-0001 (sequence restarts every year) -----------------
Public Const TASK_PREFIX As String = "SCM"

' --- Dashboard alert thresholds (days) ----------------------------------------
Public Const REPAIR_DUE_SOON_DAYS As Long = 7    ' AMOS repair due back within n days -> warning
Public Const WAITING_STALE_DAYS As Long = 14     ' "Waiting on Third Party" without update -> warning
Public Const AMAZON_INVOICE_DAYS As Long = 14    ' Amazon task not sent to invoice team after n days -> warning

' --- Display formats -----------------------------------------------------------
Public Const DATE_FMT As String = "dd-mmm-yyyy"
Public Const STAMP_FMT As String = "dd-mmm-yyyy hh:mm"

' --- Fixed values ---------------------------------------------------------------
Public Const STATUS_OPEN As String = "Open"
Public Const STATUS_INPROGRESS As String = "In Progress"
Public Const STATUS_WAITING As String = "Waiting on Third Party"
Public Const STATUS_DONE As String = "Done"

Public Const CAT_AMAZON As String = "Amazon"
Public Const CAT_PAYPAL As String = "Paypal"
Public Const CAT_AMOS As String = "AMOS"

Public Const HANDLING_STANDARD As String = "Standard"
Public Const HANDLING_ADVANCE As String = "Advance Payment"
Public Const HANDLING_REPAIR As String = "Third-Party Repair"

' --- Database column map (column numbers on the Database sheet) --------------
Public Const COL_ID As Long = 1
Public Const COL_TITLE As Long = 2
Public Const COL_DATE As Long = 3
Public Const COL_STATUS As Long = 4
Public Const COL_CATEGORY As Long = 5
Public Const COL_ORDERNO As Long = 6        ' Amazon
Public Const COL_INV_PAY As Long = 7        ' Amazon  - Sent to Invoice Team for payment
Public Const COL_INV_ARCH As Long = 8       ' Paypal  - Sent to Invoice Team for archiving
Public Const COL_CUSTOMS As Long = 9        ' Paypal  - Customs/Import Charges Status
Public Const COL_PARTTYPE As Long = 10      ' AMOS
Public Const COL_HANDLING As Long = 11      ' AMOS
Public Const COL_VENDOR As Long = 12        ' AMOS third-party repair
Public Const COL_RETURN As Long = 13        ' AMOS third-party repair
Public Const COL_NOTES As Long = 14
Public Const COL_FOLDER As Long = 15        ' =HYPERLINK() to the task folder
Public Const COL_CREATED As Long = 16
Public Const COL_MODIFIED As Long = 17
Public Const COL_COUNT As Long = 17

Public Function DbHeaders() As Variant
    DbHeaders = Array("Task ID", "Title", "Task Date", "Status", "Category", _
                      "Order Number", "Sent to Invoice (Payment)", "Sent to Invoice (Archiving)", _
                      "Customs/Import Charges Status", "Part Type", "Handling Type", _
                      "Current Location/Vendor", "Expected Return Date", "Notes", _
                      "Folder", "Created On", "Last Modified")
End Function

' --- Drop-down lists ---------------------------------------------------------------
Public Function StatusList() As Variant
    StatusList = Array(STATUS_OPEN, STATUS_INPROGRESS, STATUS_WAITING, STATUS_DONE)
End Function

Public Function CategoryList() As Variant
    CategoryList = Array(CAT_AMAZON, CAT_PAYPAL, CAT_AMOS)
End Function

Public Function PartTypeList() As Variant
    PartTypeList = Array("Rotable", "Offpart")
End Function

Public Function HandlingList() As Variant
    HandlingList = Array(HANDLING_STANDARD, HANDLING_ADVANCE, HANDLING_REPAIR)
End Function

Public Function CustomsList() As Variant
    CustomsList = Array("Not applicable", "Pending customs clearance", "Held at customs", _
                        "Import charges invoiced - unpaid", "Import charges paid", "Cleared")
End Function

' Customs states that block a Paypal task (shown as CRITICAL on the Dashboard)
Public Function BlockedCustomsList() As Variant
    BlockedCustomsList = Array("Pending customs clearance", "Held at customs", _
                               "Import charges invoiced - unpaid")
End Function

Public Function IsBlockedCustoms(ByVal s As String) As Boolean
    Dim v As Variant
    s = LCase$(Trim$(s))
    If Len(s) = 0 Then Exit Function
    For Each v In BlockedCustomsList()
        If s = LCase$(v) Then IsBlockedCustoms = True: Exit Function
    Next v
    ' Free-text entries: typical "still blocked" keywords count as blocked too
    For Each v In Array("pending", "held", "unpaid", "waiting", "outstanding")
        If InStr(1, s, v) > 0 Then IsBlockedCustoms = True: Exit Function
    Next v
End Function
