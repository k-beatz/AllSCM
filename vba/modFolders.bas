Attribute VB_Name = "modFolders"
'==========================================================================
' modFolders - local / network folder creation and folder hyperlinks.
' Pure VBA (MkDir / GetAttr / Shell), no FileSystemObject or API calls.
'==========================================================================
Option Explicit

' Archive root, read from the Dashboard cell named SCM_BasePath (Dashboard!C4).
Public Function GetBasePath() As String
    Dim p As String
    On Error Resume Next
    p = Trim$(CStr(ThisWorkbook.Names(NAME_BASEPATH).RefersToRange.Value))
    On Error GoTo 0
    If Len(p) = 0 Then p = DEFAULT_BASE_PATH
    p = ExpandEnv(p)
    Do While Len(p) > 3 And Right$(p, 1) = "\"
        p = Left$(p, Len(p) - 1)
    Loop
    GetBasePath = p
End Function

' <base path>\<Task ID>
Public Function TaskFolderPath(ByVal taskId As String) As String
    TaskFolderPath = GetBasePath() & "\" & taskId
End Function

' Creates the folder including all missing parent folders.
' Returns True when the folder exists afterwards.
Public Function EnsureFolder(ByVal folderPath As String) As Boolean
    Dim parent As String, pos As Long

    If Right$(folderPath, 1) = "\" Then folderPath = Left$(folderPath, Len(folderPath) - 1)
    If Len(folderPath) = 0 Then Exit Function
    If FolderExists(folderPath) Then EnsureFolder = True: Exit Function
    ' Drive roots (C:) and UNC shares (\\server\share) cannot be created by MkDir
    If IsRootPath(folderPath) Then Exit Function

    pos = InStrRev(folderPath, "\")
    If pos > 1 Then
        parent = Left$(folderPath, pos - 1)
        If Not IsRootPath(parent) Then
            If Not EnsureFolder(parent) Then Exit Function
        End If
    End If

    On Error Resume Next
    MkDir folderPath
    On Error GoTo 0
    EnsureFolder = FolderExists(folderPath)
End Function

Public Function FolderExists(ByVal folderPath As String) As Boolean
    If Len(folderPath) = 0 Then Exit Function
    If Right$(folderPath, 1) = ":" Then folderPath = folderPath & "\"
    On Error Resume Next
    FolderExists = ((GetAttr(folderPath) And vbDirectory) = vbDirectory)
    On Error GoTo 0
End Function

' Writes a clickable link to the folder. A HYPERLINK() formula is used instead of
' an inserted hyperlink because Excel silently turns inserted file links into
' relative links when the workbook is saved, which breaks them if the workbook moves.
Public Sub SetFolderLink(ByVal cell As Range, ByVal folderPath As String)
    cell.Formula = "=HYPERLINK(""" & folderPath & """,""" & folderPath & """)"
    cell.Font.Color = RGB(5, 99, 193)
    cell.Font.Underline = xlUnderlineStyleSingle
End Sub

' Folder path stored in a cell written by SetFolderLink ("" if none).
Public Function FolderPathOf(ByVal cell As Range) As String
    If cell.HasFormula Then
        If Not IsError(cell.Value) Then FolderPathOf = CStr(cell.Value)
    End If
End Function

Public Sub OpenFolder(ByVal folderPath As String)
    If Not FolderExists(folderPath) Then
        MsgBox "Folder not found:" & vbLf & folderPath, vbExclamation, APP_NAME
        Exit Sub
    End If
    Shell "explorer.exe """ & folderPath & """", vbNormalFocus
End Sub

' Dashboard button: open the archive root folder
Public Sub OpenArchiveRoot()
    Dim p As String
    p = GetBasePath()
    If Not EnsureFolder(p) Then
        MsgBox "The archive folder could not be created or reached:" & vbLf & p & vbLf & vbLf & _
               "Change the Archive base path on the Dashboard (cell C4).", vbExclamation, APP_NAME
        Exit Sub
    End If
    OpenFolder p
End Sub

'--------------------------------------------------------------------------
' Helpers
'--------------------------------------------------------------------------
Private Function IsRootPath(ByVal p As String) As Boolean
    Dim rest As String
    If Len(p) <= 2 And Right$(p, 1) = ":" Then IsRootPath = True: Exit Function
    If Left$(p, 2) = "\\" Then
        rest = Mid$(p, 3)                            ' server\share\...
        IsRootPath = (Len(rest) - Len(Replace(rest, "\", "")) <= 1)
    End If
End Function

' Replaces %VAR% with the value of the Windows environment variable.
Private Function ExpandEnv(ByVal s As String) As String
    Dim p1 As Long, p2 As Long, v As String
    p1 = InStr(1, s, "%")
    Do While p1 > 0
        p2 = InStr(p1 + 1, s, "%")
        If p2 = 0 Then Exit Do
        v = Environ$(Mid$(s, p1 + 1, p2 - p1 - 1))
        If Len(v) = 0 Then
            p1 = p2                                  ' unknown variable - leave as is
        Else
            s = Left$(s, p1 - 1) & v & Mid$(s, p2 + 1)
            p1 = InStr(p1 + Len(v), s, "%")
        End If
    Loop
    ExpandEnv = s
End Function
