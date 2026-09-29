# AllSCM – SCM & Logistics Task Manager (Excel VBA)

A task manager for Amazon, Paypal and AMOS logistics work that runs entirely inside one
macro-enabled Excel workbook (`.xlsm`). You don't need a database, Python, add-ins or Windows API calls.

* **Dashboard** shows KPI tiles, open tasks by category and status, and a list of
  **blocked and critical items**. For example: Paypal tasks stuck in customs, AMOS repairs
  past their expected return date, and tasks waiting on a third party with no update.
* **Database** is a protected Excel table (`tblTasks`) that holds every task. You never edit it
  by hand. All changes go through the form.
* **Task form (`frmTask`)** has base fields plus sections that change with the category. The
  controls are generated in code, so you don't have to draw anything.
* **Folders**: every new task automatically gets its own folder, `<base path>\<Task ID>`,
  and the Database row gets a clickable link to it.

## Files

| File | Where it goes in the VBA editor |
|---|---|
| `vba/modConfig.bas` | Standard module: settings, column map, drop-down lists |
| `vba/modFolders.bas` | Standard module: folder creation, hyperlinks, opening Explorer |
| `vba/modTaskManager.bas` | Standard module: IDs, saving and loading tasks, button macros |
| `vba/modDashboard.bas` | Standard module: Dashboard refresh and alert rules |
| `vba/modSetup.bas` | Standard module: one-time builder for both sheets |
| `vba/frmTask.txt` | Code of the UserForm `frmTask` |
| `vba/ThisWorkbook.txt` | Code of `ThisWorkbook` (refreshes the Dashboard on open) |
| `vba/Sheet_Dashboard.txt` | Code of the Dashboard sheet (double-click a Task ID to edit it) |
| `vba/Sheet_Database.txt` | Code of the Database sheet (double-click a row to edit it) |

---

## Step-by-step setup (about 10 minutes)

### 1. Create the workbook
1. Open a new, blank workbook in Excel.
2. **File → Save As →** type **Excel Macro-Enabled Workbook (*.xlsm)**, for example
   `SCM_TaskManager.xlsm`.
3. If your IT blocks macros in general, save the file in a **Trusted Location**
   (File → Options → Trust Center → Trust Center Settings → Trusted Locations) or ask
   IT which location is trusted. If the file was downloaded, right-click it →
   Properties → tick **Unblock**.

### 2. Import the standard modules
1. Press **Alt+F11** to open the VBA editor.
2. **File → Import File…** and import these five files, one at a time:
   `modConfig.bas`, `modFolders.bas`, `modTaskManager.bas`, `modDashboard.bas`, `modSetup.bas`.
   * If importing is blocked, use **Insert → Module** instead. Rename the module in the Properties window
     (**F4**, field *(Name)*) to the file name, for example `modConfig`, and paste the file's content
     **without** the first line `Attribute VB_Name = ...`.

### 3. Create the UserForm
1. **Insert → UserForm**.
2. Press **F4**. In the Properties window, set **(Name)** to `frmTask`. It must be exactly that name.
3. Right-click the form → **View Code**, delete everything in the code window, and paste the
   whole content of `vba/frmTask.txt`.
4. Don't add any controls. The form builds all of them itself when it opens.

### 4. Add the ThisWorkbook code
Under *Microsoft Excel Objects*, double-click **ThisWorkbook** and paste
`vba/ThisWorkbook.txt`.

### 5. Compile
Choose **Debug → Compile VBAProject**. It should finish without an error message.
(The error *"User-defined type not defined: frmTask"* means the form isn't named `frmTask`.)

### 6. Build the sheets
1. Go back to Excel, press **Alt+F8**, select **SetupWorkbook**, and click **Run**.
2. This creates:
   * **Dashboard**, with a title, four buttons (*New Task, Edit Task, Refresh, Open Archive*),
     the **Archive base path** cell (C4, yellow) and the report area.
   * **Database**, with the `tblTasks` table, formats, frozen header and sheet protection
     (password `scm`, set in `modConfig`).
3. You can delete the default empty sheet (`Sheet1`/`Tabelle1`).

### 7. Add the sheet double-click code (optional, recommended)
In the VBA editor, the new sheets now appear under *Microsoft Excel Objects*.
Double-click **Dashboard** and paste `vba/Sheet_Dashboard.txt`. Then double-click **Database**
and paste `vba/Sheet_Database.txt`.

### 8. Set the archive folder
Type your base folder into **Dashboard!C4**. Examples:

| Example | Note |
|---|---|
| `C:\SCM_Archive` | Default. Many corporate PCs block writing to the root of `C:\`. |
| `%USERPROFILE%\Documents\SCM_Archive` | Always writable. Environment variables are expanded. |
| `\\fileserver\logistics\SCM_Archive` | Network share (UNC). The share itself must exist. |
| `S:\Logistics\SCM_Archive` | Mapped network drive. |

Missing parent folders are created automatically. Save the workbook.

---

## Daily use

| Action | How |
|---|---|
| New task | **New Task** button → fill in the form → **Create Task**. The ID is generated, the row is written, the folder is created and linked, and the Dashboard refreshes. You're then asked whether to open the folder. |
| Edit a task / change its status | **Edit Task** button (enter the ID), or double-click a Task ID on the Dashboard, or double-click a row on the Database sheet. |
| Open a task's folder | Click the path in the Database column **Folder**, the **Open** link on the Dashboard, or **Open Folder** in the form. |
| Refresh the Dashboard | Happens automatically after each save and when the workbook opens. You can also use the **Refresh** button. |

### Form behaviour
* **Base fields:** Task ID (read-only, format `SCM-2026-0001`, the counter restarts every year),
  Title, Date (**Today** button; uses your Windows date format), Status, Category.
* **Amazon** shows *Order Number* and ☐ *Sent to Invoice Team for payment*.
* **Paypal** shows ☐ *Sent to Invoice Team for archiving* and *Customs/Import Charges Status*
  (pick from the list or type free text).
* **AMOS** shows *Part Type* (Rotable/Offpart) and *Handling Type* (Standard/Advance Payment/
  Third-Party Repair). **Third-Party Repair** also shows *Current Location/Vendor* (required)
  and *Expected Return Date*.
* The form resizes to show only the section for the selected category. When you switch
  category, the fields of the other categories are **not** saved, so the Database stays clean.

### Dashboard alert rules

| Severity | Rule |
|---|---|
| CRITICAL | Paypal task whose customs status is *Pending customs clearance*, *Held at customs*, *Import charges invoiced - unpaid*, or free text containing *pending/held/unpaid/waiting/outstanding* |
| CRITICAL | AMOS third-party repair **past** its expected return date |
| WARNING | AMOS third-party repair due back within 7 days |
| WARNING | AMOS third-party repair without an expected return date |
| WARNING | Amazon task not sent to the Invoice Team after 14 days |
| WARNING | Status *Waiting on Third Party* with no update for 14 days |

Tasks with status **Done** never raise alerts. You can change the thresholds and customs states in
`modConfig` (`REPAIR_DUE_SOON_DAYS`, `WAITING_STALE_DAYS`, `AMAZON_INVOICE_DAYS`,
`BlockedCustomsList`). To add rules, edit `CheckTask` in `modDashboard`.

### Database columns
`Task ID | Title | Task Date | Status | Category | Order Number | Sent to Invoice (Payment) |
Sent to Invoice (Archiving) | Customs/Import Charges Status | Part Type | Handling Type |
Current Location/Vendor | Expected Return Date | Notes | Folder | Created On | Last Modified`

---

## Customising

| What | Where |
|---|---|
| Status, category, part type, handling and customs lists | List functions in `modConfig` |
| Task ID prefix | `TASK_PREFIX` in `modConfig` |
| Database password | `DB_PASSWORD` in `modConfig` (run `SetupWorkbook` again after changing it, **before** the old password is lost) |
| Default archive path | `DEFAULT_BASE_PATH` in `modConfig` (used only while Dashboard C4 is empty) |
| New category | Add a `CAT_…` constant and add it to `CategoryList`. Add a frame in `frmTask` (`UserForm_Initialize`, `LayoutForm`, `cmdSave_Click`) and add columns at the end of the column map and `DbHeaders`. |

## Troubleshooting

* **"Folder not created"** in the Folder column: the base path isn't reachable or writable.
  Fix C4, then open the task and click **Save Changes**. The folder and link are created then.
* **Links still work after moving the workbook.** The Folder column uses `=HYPERLINK()` formulas
  with absolute paths, so Excel can't rewrite them as relative links.
* **Changing the base path later** affects new tasks only. Existing tasks keep their folder.
* **Buttons do nothing:** macros are disabled. See step 1.3.
* **To edit the Database by hand** (for example, to delete a test row): Review → Unprotect Sheet →
  password `scm`. Afterwards, run `SetupWorkbook` or save any task, which protects the sheet again.
