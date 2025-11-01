<<<<<<< HEAD
# QMS System - Thi Qar Oil Company (Quality & Performance Division)
# GUI if Qt is available (PyQt6 preferred, fallback to PyQt5). Otherwise, run in CLI/headless mode.
# SQLite backend + centered company logo + optional background music (GUI only)
# Designed by Chief Engineer Tareq Majeed Al-Karimi

import sys, os, csv, shutil, sqlite3

# -------- Optional Excel support --------
try:
    import pandas as pd  # requires openpyxl for .xlsx
    HAS_PANDAS = True
except Exception:
    pd = None
    HAS_PANDAS = False

# ================================================================
# Qt Compatibility Layer (may be unavailable in this environment)
# ================================================================
QT_API = 0  # 0=headless, 6=PyQt6, 5=PyQt5
HEADLESS = True

try:  # Prefer PyQt6
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QListWidget, QStackedWidget, QFileDialog, QMessageBox, QTableView, QToolBar,
        QStatusBar, QSplitter, QLineEdit, QTextEdit, QFormLayout, QDateEdit, QComboBox,
        QCheckBox, QInputDialog, QAbstractItemView
    )
    from PyQt6.QtCore import Qt, QDate, QUrl
    try:
        from PyQt6.QtGui import QAction  # PyQt6 puts QAction in QtGui
    except Exception:
        from PyQt6.QtWidgets import QAction
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    except Exception:
        QMediaPlayer = QAudioOutput = None
    QT_API = 6
    HEADLESS = False
    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    SMOOTH = Qt.TransformationMode.SmoothTransformation
    HORIZONTAL = Qt.Orientation.Horizontal
    SELECT_ROWS = QTableView.SelectionBehavior.SelectRows
    EDIT_DBL = QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.EditKeyPressed
    EDIT_NONE = QAbstractItemView.EditTrigger.NoEditTriggers
except Exception:
    try:  # Fallback to PyQt5
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QListWidget, QStackedWidget, QFileDialog, QMessageBox, QTableView, QToolBar,
            QStatusBar, QSplitter, QLineEdit, QTextEdit, QFormLayout, QDateEdit, QComboBox,
            QCheckBox, QAction, QInputDialog, QAbstractItemView
        )
        from PyQt5.QtCore import Qt, QDate, QUrl
        from PyQt5.QtGui import QIcon, QPixmap
        from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
        try:
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
        except Exception:
            QMediaPlayer = None
            QMediaContent = None
        QT_API = 5
        HEADLESS = False
        ALIGN_CENTER = Qt.AlignCenter
        SMOOTH = Qt.SmoothTransformation
        HORIZONTAL = Qt.Horizontal
        SELECT_ROWS = QTableView.SelectRows
        EDIT_DBL = (QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        EDIT_NONE = QAbstractItemView.NoEditTriggers
    except Exception:
        QT_API = 0
        HEADLESS = True

APP_TITLE = "QMS – Quality & Performance Division | Thi Qar Oil Company"
DB_NAME = "qms.sqlite"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATHS = [
    "/mnt/data/logo.png",
    os.path.join(BASE_DIR, "logo.png"),
    os.path.join(BASE_DIR, "sold.png"),
    os.path.join(BASE_DIR, "company_logo.png"),
    "logo.png",
    "sold.png",
    "company_logo.png",
    os.path.join(BASE_DIR, "resources", "sold.png"),
]
AUDIO_PATHS = [
    "/mnt/data/Audio.mp3",
    os.path.join(BASE_DIR, "Audio.mp3"),
    os.path.join(BASE_DIR, "audio.mp3"),
    "Audio.mp3",
    "audio.mp3",
    os.path.join(BASE_DIR, "resources", "audio.mp3"),
]
FOOTER_TEXT = "Designed by Chief Engineer Tareq Majeed Al-Karimi"

# ================================================================
# Per-section write passwords (no login screen)  
# Empty string => section remains read-only (cannot unlock)
# ================================================================
SECTION_PASSWORDS = {
    # ضع كلمة سر للأقسام التي تريد السماح بالتحرير فيها بعد إدخالها.
    # أقسام بلا كلمة سر ستبقى قراءة فقط.
    "policies":        "P0l!cy@2025",
    "objectives":      "0bj@2025",
    "documents":       "Doc@2025",
    "audit_plan":      "Plan@2025",
    "audits":          "Aud1t@2025",
    "nonconformities": "NC@2025",
    "capa":            "CAPA@2025",
    "knowledge_base":  "KB@2025",
    "reports":         "Rep@2025",
    "notifications":   "Noti@2025",
    "signatures":      "Sign@2025",
}

def check_section_password(section_key: str, parent=None) -> bool:
    """Ask for the section password; True if correct. If not configured -> False."""
    expected = SECTION_PASSWORDS.get(section_key, "")
    if not expected:
        return False
    # PyQt6/5 compatibility for password echo mode
    try:
        text, ok = QInputDialog.getText(parent, "Unlock", f"Enter password for [{section_key}]",
                                        QLineEdit.EchoMode.Password)
    except Exception:
        text, ok = QInputDialog.getText(parent, "Unlock", f"Enter password for [{section_key}]",
                                        QLineEdit.Password)
    if not ok:
        return False
    return text == expected

# ================================================================
# Schema (used by both GUI/Qt and headless/CLI)
# ================================================================
SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT,
        version TEXT,
        approved_by TEXT,
        approved_on TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS objectives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        metric TEXT,
        target TEXT,
        period TEXT,
        owner TEXT,
        progress INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT,
        version TEXT,
        owner TEXT,
        status TEXT,
        review_date TEXT,
        file_path TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,
        planned_date TEXT,
        auditor TEXT,
        scope TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,
        audit_date TEXT,
        auditor TEXT,
        findings TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS nonconformities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        root_cause TEXT,
        owner TEXT,
        due_date TEXT,
        status TEXT,
        related_audit INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS capa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nc_id INTEGER,
        action TEXT,
        owner TEXT,
        due_date TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        tags TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        period TEXT,
        notes TEXT,
        created_on TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        due_date TEXT,
        assigned_to TEXT,
        seen INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person TEXT,
        role TEXT,
        image_path TEXT,
        signed_on TEXT
    );
    """
]

# ================================================================
# DB Helpers (Qt or sqlite3)
# ================================================================

def ensure_schema_sqlite3():
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        for sql in SCHEMA_SQL:
            cur.executescript(sql)
        con.commit()
    finally:
        con.close()

if not HEADLESS:
    def get_db_connection_qt():
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(DB_NAME)
        if not db.open():
            raise RuntimeError("Failed to open database")
        return db

    def ensure_schema_qt():
        for sql in SCHEMA_SQL:
            QSqlQuery().exec(sql)

# ================================================================
# GUI Implementation (only if Qt available)
# ================================================================
if not HEADLESS:
    class TablePage(QWidget):
        def __init__(self, table_name: str, headers: dict[str, str], section_key: str | None = None):
            super().__init__()
            self.table_name = table_name
            self.headers = headers
            self.section_key = section_key or table_name
            self.unlocked = False

            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)

            self.model = QSqlTableModel(self)
            self.model.setTable(table_name)
            self.model.select()

            for col in range(self.model.columnCount()):
                field = self.model.record().fieldName(col)
                if field in headers:
                    self.model.setHeaderData(col, HORIZONTAL, headers[field])

            self.view = QTableView()
            self.view.setModel(self.model)
            # Better readability: row/column sizing
            try:
                vh = self.view.verticalHeader()
                hh = self.view.horizontalHeader()
                vh.setDefaultSectionSize(28)
                hh.setStretchLastSection(True)
            except Exception:
                pass
            self.view.setSelectionBehavior(SELECT_ROWS)
            self.view.setAlternatingRowColors(True)
            self.view.resizeColumnsToContents()
            self.view.setStyleSheet(
                "QTableView{selection-background-color:#cbdfff;}"
                "QHeaderView::section{background:#f2f4f8;border:1px solid #e5e9f0;}"
            )
            # read-only until unlocked
            try:
                self.view.setEditTriggers(EDIT_NONE)
            except Exception:
                pass

            btn_bar = QHBoxLayout()
            self.btn_add = QPushButton("Add Row")
            self.btn_del = QPushButton("Delete Selected")
            self.btn_save = QPushButton("Save")
            self.btn_export = QPushButton("Export CSV…")
            self.btn_import = QPushButton("Import CSV…")
            self.btn_import_excel = QPushButton("Import Excel…")
            self.btn_unlock = QPushButton("Unlock")

            for b in (self.btn_add, self.btn_del, self.btn_save, self.btn_export, self.btn_import, self.btn_import_excel, self.btn_unlock):
                btn_bar.addWidget(b)

            # Documents extras
            self.btn_attach = None
            self.btn_openfile = None
            if table_name == "documents":
                self.btn_attach = QPushButton("Attach File…")
                self.btn_openfile = QPushButton("Open File")
                btn_bar.addWidget(self.btn_attach)
                btn_bar.addWidget(self.btn_openfile)

            btn_bar.addStretch(1)

            layout.addWidget(self.view)
            layout.addLayout(btn_bar)

            # default locked controls
            def set_write_enabled(on: bool):
                self.btn_add.setEnabled(on)
                self.btn_del.setEnabled(on)
                self.btn_save.setEnabled(on)
                self.btn_import.setEnabled(on)
                self.btn_import_excel.setEnabled(on)
                if self.btn_attach:
                    self.btn_attach.setEnabled(on)
                # export/open are read-only actions -> keep enabled
                self.btn_export.setEnabled(True)
                if self.btn_openfile:
                    self.btn_openfile.setEnabled(True)

            self._set_write_enabled = set_write_enabled
            set_write_enabled(False)

            # connections
            self.btn_add.clicked.connect(self.add_row)
            self.btn_del.clicked.connect(self.delete_selected)
            self.btn_save.clicked.connect(self.save)
            self.btn_export.clicked.connect(self.export_csv)
            self.btn_import.clicked.connect(self.import_csv)
            self.btn_import_excel.clicked.connect(self.import_excel)
            self.btn_unlock.clicked.connect(self.try_unlock)
            if self.btn_attach:
                self.btn_attach.clicked.connect(self.attach_file)
            if self.btn_openfile:
                self.btn_openfile.clicked.connect(self.open_file)

        def try_unlock(self):
            expected = SECTION_PASSWORDS.get(self.section_key, "")
            if not expected:
                QMessageBox.information(self, "Read-only", "This section is read-only (no password configured).")
                return
            if self.unlocked:
                QMessageBox.information(self, "Unlocked", "Already unlocked.")
                return
            if check_section_password(self.section_key, self):
                self.unlocked = True
                self._set_write_enabled(True)
                try:
                    self.view.setEditTriggers(EDIT_DBL)
                except Exception:
                    pass
                QMessageBox.information(self, "Unlocked", "Editing enabled for this section.")
            else:
                QMessageBox.warning(self, "Wrong password", "Password is incorrect.")

        def _require_unlocked(self):
            if not self.unlocked:
                QMessageBox.warning(self, "Locked", "Unlock this section first.")
                return False
            return True

        def add_row(self):
            if not self._require_unlocked():
                return
            self.model.insertRow(self.model.rowCount())
            self.view.scrollToBottom()

        def delete_selected(self):
            if not self._require_unlocked():
                return
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return
            for idx in sorted(indexes, key=lambda i: i.row(), reverse=True):
                self.model.removeRow(idx.row())

        def save(self):
            if not self._require_unlocked():
                return
            if not self.model.submitAll():
                QMessageBox.critical(self, "Save Error", self.model.lastError().text())
            else:
                self.model.select()
                QMessageBox.information(self, "Saved", "Changes saved successfully.")

        def export_csv(self):
            path, _ = QFileDialog.getSaveFileName(self, "Export CSV", f"{self.table_name}.csv", "CSV Files (*.csv)")
            if not path:
                return
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                headers = [self.model.headerData(c, HORIZONTAL) for c in range(self.model.columnCount())]
                writer.writerow(headers)
                for r in range(self.model.rowCount()):
                    row = []
                    for c in range(self.model.columnCount()):
                        idx = self.model.index(r, c)
                        row.append(self.model.data(idx))
                    writer.writerow(row)
            QMessageBox.information(self, "Export", f"Exported to {path}")

        def import_csv(self):
            if not self._require_unlocked():
                return
            path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cols = [self.model.record().fieldName(c) for c in range(self.model.columnCount())]
            with open(path, newline='', encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    QMessageBox.information(self, "Import", "CSV is empty.")
                    con.close(); return
                placeholders = ",".join(["?"] * len(cols))
                sql = f"INSERT INTO {self.table_name}({','.join(cols)}) VALUES ({placeholders})"
                imported = 0
                for r in rows:
                    vals = [r.get(c, None) for c in cols]
                    try:
                        cur.execute(sql, vals)
                        imported += 1
                    except Exception:
                        pass
                con.commit(); con.close()
            self.model.select()
            QMessageBox.information(self, "Import", f"Imported {imported} rows from {os.path.basename(path)}")

        def import_excel(self):
            if not self._require_unlocked():
                return
            path, _ = QFileDialog.getOpenFileName(self, "Import Excel", "", "Excel Files (*.xlsx *.xls)")
            if not path:
                return
            if not HAS_PANDAS:
                QMessageBox.critical(
                    self,
                    "Excel Support Missing",
                    "Excel import requires pandas (and openpyxl for .xlsx).\n\n"
                    "Install with: pip install pandas openpyxl"
                )
                return
            try:
                df = pd.read_excel(path, dtype=str)
            except Exception as e:
                QMessageBox.critical(self, "Read Excel Error", str(e))
                return

            # Map columns by name (case-insensitive)
            df_cols_norm = {c.lower().strip(): c for c in df.columns}
            table_cols = [self.model.record().fieldName(c) for c in range(self.model.columnCount())]
            mapped_cols = []
            for c in table_cols:
                key = c.lower().strip()
                src = df_cols_norm.get(key)
                mapped_cols.append(src)

            rows = []
            for _, rec in df.iterrows():
                vals = [rec[src] if (src in df.columns) else None for src in mapped_cols]
                rows.append(vals)

            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            placeholders = ",".join(["?"] * len(table_cols))
            sql = f"INSERT INTO {self.table_name}({','.join(table_cols)}) VALUES ({placeholders})"
            imported = 0
            for vals in rows:
                try:
                    norm_vals = []
                    for v in vals:
                        if HAS_PANDAS and isinstance(v, float) and pd.isna(v):
                            norm_vals.append(None)
                        else:
                            norm_vals.append(v)
                    cur.execute(sql, norm_vals)
                    imported += 1
                except Exception:
                    pass
            con.commit()
            con.close()

            self.model.select()
            QMessageBox.information(self, "Import", f"Imported {imported} rows from {os.path.basename(path)}")

        # ---- Documents-specific helpers ----
        def _selected_row_id(self):
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return None
            row = indexes[0].row()
            idx = self.model.index(row, 0)
            return self.model.data(idx), row

        def attach_file(self):
            if not self._require_unlocked():
                return
            if self.table_name != "documents":
                return
            sel = self._selected_row_id()
            if sel is None:
                QMessageBox.warning(self, "No selection", "Select a document row first.")
                return
            _id, row = sel
            src, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*.*)")
            if not src:
                return
            attachments_dir = os.path.join(BASE_DIR, "attachments")
            try:
                os.makedirs(attachments_dir, exist_ok=True)
                dst = os.path.join(attachments_dir, os.path.basename(src))
                shutil.copyfile(src, dst)
                # write file_path
                col = None
                for c in range(self.model.columnCount()):
                    if self.model.record().fieldName(c) == "file_path":
                        col = c; break
                if col is not None:
                    self.model.setData(self.model.index(row, col), dst)
                    self.model.submitAll(); self.model.select()
                    QMessageBox.information(self, "Attached", f"File attached to record #{_id}.")
            except Exception as e:
                QMessageBox.critical(self, "Attach Error", str(e))

        def open_file(self):
            if self.table_name != "documents":
                return
            sel = self._selected_row_id()
            if sel is None:
                QMessageBox.warning(self, "No selection", "Select a document row first.")
                return
            _id, row = sel
            col = None
            for c in range(self.model.columnCount()):
                if self.model.record().fieldName(c) == "file_path":
                    col = c; break
            if col is None:
                QMessageBox.warning(self, "No file_path column", "This table has no file_path column configured.")
                return
            path = self.model.data(self.model.index(row, col))
            if not path or not os.path.exists(path):
                QMessageBox.warning(self, "Missing File", "No file is attached or file not found.")
                return
            try:
                if sys.platform.startswith('win'):
                    os.startfile(path)  # type: ignore
                elif sys.platform == 'darwin':
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception as e:
                QMessageBox.critical(self, "Open Error", str(e))

    class DashboardPage(QWidget):
        def __init__(self):
            super().__init__()
            lay = QVBoxLayout(self)
            lay.setContentsMargins(24, 16, 24, 16)
            lay.setSpacing(12)

            # Centered company logo
            logo_label = QLabel()
            logo_label.setAlignment(ALIGN_CENTER)

            def resolve_existing(paths):
                for p in paths:
                    try:
                        if p and os.path.exists(p):
                            return os.path.abspath(p)
                    except Exception:
                        pass
                return None

            logo_file = resolve_existing(LOGO_PATHS)
            if logo_file:
                pix = QPixmap(logo_file)
                if not pix.isNull():
                    logo_label.setPixmap(pix.scaledToHeight(96, SMOOTH))
                else:
                    logo_label.setText("[Logo not readable]")
                    logo_label.setStyleSheet("color:#777; border:1px dashed #aaa; padding:8px;")
            else:
                logo_label.setText("[Thi Qar Oil Company Logo]")
                logo_label.setStyleSheet("color:#777; border:1px dashed #aaa; padding:8px;")
            lay.addWidget(logo_label)

            title = QLabel("Quality Management System – Quality & Performance Division")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:20px; font-weight:600; margin-top:6px;")
            subtitle = QLabel("Internal automation for policies, audits, NCs, CAPA, objectives and reports.")
            subtitle.setAlignment(ALIGN_CENTER)
            subtitle.setStyleSheet("color:#444;")

            lay.addWidget(title)
            lay.addWidget(subtitle)

            tips = QLabel(
                "• Use the left menu to open modules.\n"
                "• Right-click inside tables for copy/paste.\n"
                "• Use Export to create CSV files; attach to reports.\n"
                "• Keep data synchronized: save after edits.\n"
                "• In Documents: use Attach File to copy/link PDFs, Excel, Word, images, etc."
            )
            tips.setStyleSheet("background:#f5f7fb; border:1px solid #e2e6ef; padding:10px; border-radius:8px; margin-top:10px;")
            lay.addWidget(tips)
            lay.addStretch(1)

    class SignaturePage(QWidget):
        """Simple E-Signature page (stores name/role and optional image path)."""
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)
            title = QLabel("E-Signature")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:18px; font-weight:600;")
            layout.addWidget(title)

            form = QFormLayout()
            try:
                form.setSpacing(12)
            except Exception:
                pass
            self.person = QLineEdit()
            self.role = QLineEdit()
            self.image_path = QLineEdit()
            self.btn_browse = QPushButton("Browse Image…")
            self.btn_browse.clicked.connect(self.browse)
            form.addRow("Person", self.person)
            form.addRow("Role", self.role)
            row = QHBoxLayout()
            row.addWidget(self.image_path)
            row.addWidget(self.btn_browse)
            form.addRow("Image", row)
            layout.addLayout(form)

            self.btn_save = QPushButton("Save Signature")
            self.btn_save.clicked.connect(self.save)
            layout.addWidget(self.btn_save)

            # per-section unlock for signatures
            self.unlocked = False
            self.btn_unlock = QPushButton("Unlock")
            layout.addWidget(self.btn_unlock)
            self.btn_save.setEnabled(False)

            def on_unlock():
                expected = SECTION_PASSWORDS.get("signatures", "")
                if not expected:
                    QMessageBox.information(self, "Read-only", "This section is read-only (no password configured).")
                    return
                if self.unlocked:
                    QMessageBox.information(self, "Unlocked", "Already unlocked.")
                    return
                if check_section_password("signatures", self):
                    self.unlocked = True
                    self.btn_save.setEnabled(True)
                    QMessageBox.information(self, "Unlocked", "Editing enabled for signatures.")
                else:
                    QMessageBox.warning(self, "Wrong password", "Password is incorrect.")

            self.btn_unlock.clicked.connect(on_unlock)
            layout.addStretch(1)

        def browse(self):
            path, _ = QFileDialog.getOpenFileName(self, "Select Signature", "", "Images (*.png *.jpg *.jpeg)")
            if path:
                self.image_path.setText(path)

        def save(self):
            if not self.unlocked:
                QMessageBox.warning(self, "Locked", "Unlock this section first.")
                return
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute(
                "INSERT INTO signatures(person, role, image_path, signed_on) VALUES (?,?,?,date('now'))",
                (self.person.text(), self.role.text(), self.image_path.text())
            )
            con.commit()
            con.close()
            QMessageBox.information(self, "Saved", "Signature saved.")
            self.person.clear(); self.role.clear(); self.image_path.clear()

    class NotificationsPage(QWidget):
        """Notifications view using QSqlTableModel for consistency."""
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)
            title = QLabel("Notifications")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:18px; font-weight:600;")
            layout.addWidget(title)

            self.model = QSqlTableModel(self)
            self.model.setTable("notifications")
            self.model.select()

            self.view = QTableView()
            self.view.setModel(self.model)
            self.view.setSelectionBehavior(SELECT_ROWS)
            self.view.resizeColumnsToContents()
            layout.addWidget(self.view)

            bar = QHBoxLayout()
            self.btn_add = QPushButton("Quick Add")
            self.btn_seen = QPushButton("Mark Seen")
            self.btn_refresh = QPushButton("Refresh")
            for b in (self.btn_add, self.btn_seen, self.btn_refresh):
                bar.addWidget(b)
            bar.addStretch(1)
            layout.addLayout(bar)

            self.btn_add.clicked.connect(self.quick_add)
            self.btn_seen.clicked.connect(self.mark_seen)
            self.btn_refresh.clicked.connect(self.model.select)

        def quick_add(self):
            q = QSqlQuery()
            q.exec("INSERT INTO notifications(title, due_date, assigned_to, seen) VALUES ('Review documents', date('now','+3 day'), 'Quality Team', 0)")
            self.model.select()

        def mark_seen(self):
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return
            q = QSqlQuery()
            for idx in indexes:
                rowid = self.model.data(self.model.index(idx.row(), 0))
                q.exec(f"UPDATE notifications SET seen=1 WHERE id={rowid}")
            self.model.select()

    class AudioHelper:
        def __init__(self, parent=None):
            self.available = QMediaPlayer is not None
            self.player = None
            self.output = None
            self.api = QT_API
            if not self.available:
                return
            if QT_API == 6:
                self.player = QMediaPlayer(parent)
                self.output = QAudioOutput(parent) if 'QAudioOutput' in globals() and QAudioOutput else None
                if self.output:
                    try:
                        self.player.setAudioOutput(self.output)
                        self.output.setVolume(0.25)
                    except Exception:
                        pass
                self.player.mediaStatusChanged.connect(self._on_status)
            else:
                self.player = QMediaPlayer(parent)
                try:
                    self.player.setVolume(25)
                except Exception:
                    pass
                self.player.mediaStatusChanged.connect(self._on_status)

        def _on_status(self, status):
            try:
                if self.api == 6:
                    from PyQt6.QtMultimedia import QMediaPlayer as _P6
                    if status == _P6.MediaStatus.EndOfMedia:
                        self.player.setPosition(0)
                        self.player.play()
                else:
                    if int(status) == 7:  # EndOfMedia for PyQt5
                        self.player.setPosition(0)
                        self.player.play()
            except Exception:
                pass

        def start(self, paths):
            if not self.available:
                return False
            path = next((p for p in paths if os.path.exists(p)), None)
            if not path:
                return False
            url = QUrl.fromLocalFile(os.path.abspath(path))
            try:
                if QT_API == 6:
                    self.player.setSource(url)
                else:
                    from PyQt5.QtMultimedia import QMediaContent
                    self.player.setMedia(QMediaContent(url))
            except Exception:
                return False
            try:
                if QT_API == 6 and self.output:
                    self.output.setVolume(0.25)
                else:
                    self.player.setVolume(25)
            except Exception:
                pass
            self.player.play()
            return True

        def toggle_mute(self):
            if not self.available or not self.player:
                return False
            try:
                if QT_API == 6 and self.output:
                    self.output.setVolume(0 if self.output.volume() > 0 else 0.25)
                else:
                    self.player.setMuted(not self.player.isMuted())
            except Exception:
                pass
            return True

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_TITLE)
            self.resize(1200, 720)

            tb = QToolBar("Main")
            self.addToolBar(tb)

            act_backup = QAction("Backup DB", self)
            act_backup.triggered.connect(self.backup_db)
            tb.addAction(act_backup)

            act_open = QAction("Open DB Folder", self)
            act_open.triggered.connect(self.open_folder)
            tb.addAction(act_open)

            self.audio = AudioHelper(self)
            self.audio.start(AUDIO_PATHS)
            act_mute = QAction("Music On/Off", self)
            act_mute.triggered.connect(self.audio.toggle_mute)
            tb.addAction(act_mute)

            self.status = QStatusBar()
            self.setStatusBar(self.status)

            splitter = QSplitter()
            splitter.setChildrenCollapsible(False)
            self.menu = QListWidget()
            self.menu.addItems([
                "Dashboard",
                "Quality Policy",
                "Objectives",
                "Document Control",
                "Audit Plan",
                "Audits",
                "Non-Conformance",
                "CAPA",
                "Knowledge Base",
                "Reports",
                "Performance Evaluation (KPI)",
                "E-Signature",
                "Notifications"
            ])
            self.menu.setMinimumWidth(260)
            self.menu.setMaximumWidth(320)

            self.stack = QStackedWidget()
            splitter.addWidget(self.menu)
            splitter.addWidget(self.stack)
            splitter.setStretchFactor(1, 1)
            self.setCentralWidget(splitter)

            # Pages
            self.pages = []
            self.add_page(DashboardPage())
            self.add_page(TablePage("policies", {
                "id": "ID", "title": "Title", "body": "Body", "version": "Version",
                "approved_by": "Approved By", "approved_on": "Approved On"
            }, section_key="policies"))
            self.add_page(TablePage("objectives", {
                "id": "ID", "title": "Title", "metric": "Metric", "target": "Target",
                "period": "Period", "owner": "Owner", "progress": "Progress %"
            }, section_key="objectives"))
            self.add_page(TablePage("documents", {
                "id": "ID", "name": "Name", "code": "Code", "version": "Version",
                "owner": "Owner", "status": "Status", "review_date": "Review Date",
                "file_path": "File Path"
            }, section_key="documents"))
            self.add_page(TablePage("audit_plan", {
                "id": "ID", "area": "Area", "planned_date": "Planned Date",
                "auditor": "Auditor", "scope": "Scope", "status": "Status"
            }, section_key="audit_plan"))
            self.add_page(TablePage("audits", {
                "id": "ID", "area": "Area", "audit_date": "Audit Date", "auditor": "Auditor",
                "findings": "Findings", "status": "Status"
            }, section_key="audits"))
            self.add_page(TablePage("nonconformities", {
                "id": "ID", "date": "Date", "description": "Description",
                "root_cause": "Root Cause", "owner": "Owner", "due_date": "Due Date",
                "status": "Status", "related_audit": "Related Audit"
            }, section_key="nonconformities"))
            self.add_page(TablePage("capa", {
                "id": "ID", "nc_id": "NC ID", "action": "Action",
                "owner": "Owner", "due_date": "Due Date", "status": "Status"
            }, section_key="capa"))
            self.add_page(TablePage("knowledge_base", {
                "id": "ID", "title": "Title", "content": "Content", "tags": "Tags"
            }, section_key="knowledge_base"))
            self.add_page(TablePage("reports", {
                "id": "ID", "title": "Title", "period": "Period", "notes": "Notes",
                "created_on": "Created On"
            }, section_key="reports"))
            self.add_page(TablePage("objectives", {
                "id": "ID", "title": "Title", "metric": "Metric", "target": "Target",
                "period": "Period", "owner": "Owner", "progress": "Progress %"
            }, section_key="objectives"))
            self.add_page(SignaturePage())
            self.add_page(NotificationsPage())

            self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)
            self.menu.setCurrentRow(0)

            footer = QLabel(FOOTER_TEXT)
            footer.setAlignment(ALIGN_CENTER)
            footer.setStyleSheet("color:#666; padding:6px; border-top:1px solid #e5e5e5;")
            self.status.addPermanentWidget(footer, 1)

        def add_page(self, widget: QWidget):
            self.pages.append(widget)
            self.stack.addWidget(widget)

        def backup_db(self):
            path, _ = QFileDialog.getSaveFileName(self, "Backup SQLite", "qms_backup.sqlite", "SQLite DB (*.sqlite)")
            if not path:
                return
            try:
                shutil.copyfile(DB_NAME, path)
                QMessageBox.information(self, "Backup", f"Database copied to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Backup Error", str(e))

        def open_folder(self):
            folder = os.path.abspath(os.path.dirname(DB_NAME) or ".")
            QMessageBox.information(self, "DB Folder", folder)

# ================================================================
# Self-tests & CLI tools (work in both modes)
# ================================================================

def selftest_basic() -> int:
    """Test: create/open DB and ensure all tables exist."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = {r[0] for r in cur.fetchall()}
        required = {
            "policies", "objectives", "documents", "audit_plan", "audits",
            "nonconformities", "capa", "knowledge_base", "reports",
            "notifications", "signatures"
        }
        missing = required - names
        if missing:
            print("[SELFTEST] Missing tables:", ", ".join(sorted(missing)))
            return 2
        print(f"[SELFTEST] OK: schema present; Qt API={QT_API}; headless={HEADLESS}")
        return 0
    except Exception as e:
        print("[SELFTEST] ERROR:", e)
        return 1

def selftest_extended() -> int:
    """Test: insert a sample record and read it back (policies table)."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO policies(title, body, version, approved_by, approved_on) VALUES (?,?,?,?,date('now'))",
                    ("Quality Policy", "Initial test policy", "v1", "Head of Division",))
        con.commit()
        cur.execute("SELECT COUNT(*) FROM policies")
        cnt = cur.fetchone()[0]
        print(f"[SELFTEST-EXT] Policies rows: {cnt}")
        con.close()
        return 0
    except Exception as e:
        print("[SELFTEST-EXT] ERROR:", e)
        return 1

def selftest_nc() -> int:
    """Test: insert NC + CAPA and verify linkage."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO nonconformities(date, description, root_cause, owner, due_date, status, related_audit) VALUES (date('now'), ?, ?, ?, date('now','+7 day'), 'Open', 1)",
                    ("Sample NC", "Root cause test", "Quality Team"))
        nc_id = cur.lastrowid
        cur.execute("INSERT INTO capa(nc_id, action, owner, due_date, status) VALUES (?,?,?,?,?)",
                    (nc_id, "Corrective action", "Quality Team", "2099-01-01", "Planned"))
        con.commit()
        cur.execute("SELECT COUNT(*) FROM capa WHERE nc_id=?", (nc_id,))
        cnt = cur.fetchone()[0]
        print(f"[SELFTEST-NC] CAPA linked rows: {cnt}")
        con.close()
        return 0 if cnt >= 1 else 2
    except Exception as e:
        print("[SELFTEST-NC] ERROR:", e)
        return 1

def selftest_notify() -> int:
    """Test: add notification and mark as seen (simulated)."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO notifications(title, due_date, assigned_to, seen) VALUES ('Review documents', date('now','+3 day'), 'Quality Team', 0)")
        nid = cur.lastrowid
        cur.execute("UPDATE notifications SET seen=1 WHERE id=?", (nid,))
        con.commit()
        cur.execute("SELECT seen FROM notifications WHERE id=?", (nid,))
        seen = cur.fetchone()[0]
        print(f"[SELFTEST-NOTIFY] Notification seen={seen}")
        con.close()
        return 0 if int(seen) == 1 else 2
    except Exception as e:
        print("[SELFTEST-NOTIFY] ERROR:", e)
        return 1

def cli_usage():
    print(
        "Usage:\n"
        "  python main.py --selftest            # basic DB/schema test\n"
        "  python main.py --selftest-extended   # insert & count sample row (policies)\n"
        "  python main.py --selftest-nc         # insert NC & CAPA and verify linkage\n"
        "  python main.py --selftest-notify     # add notification and mark as seen\n"
        "  python main.py --import-docs <folder>  # bulk create document records from files (pdf/xlsx/docx/...)\n"
        "  python main.py --import-csv <table> <csvpath>  # import CSV into a table (columns by header names)\n"
        "  python main.py --import-xlsx <table> <xlsxpath>  # import Excel into a table (requires pandas+openpyxl)\n"
        "  python main.py                        # launch GUI if Qt available; otherwise stay in headless mode"
    )

# ================================================================
# App Entry
# ================================================================

def main() -> int:
    # Self-tests & imports path
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--selftest":
            return selftest_basic()
        if arg == "--selftest-extended":
            return selftest_extended()
        if arg == "--selftest-nc":
            return selftest_nc()
        if arg == "--selftest-notify":
            return selftest_notify()
        if arg == "--import-docs" and len(sys.argv) >= 3:
            folder = sys.argv[2]
            ensure_schema_sqlite3()
            count = 0
            if os.path.isdir(folder):
                con = sqlite3.connect(DB_NAME)
                cur = con.cursor()
                for name in os.listdir(folder):
                    path = os.path.join(folder, name)
                    if not os.path.isfile(path):
                        continue
                    ext = os.path.splitext(name)[1].lower()
                    if ext in (".pdf", ".xlsx", ".xls", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"):
                        cur.execute(
                            "INSERT INTO documents(name, code, version, owner, status, review_date, file_path) VALUES (?,?,?,?,?,?,?)",
                            (name, "", "v1", "Quality Team", "New", None, os.path.abspath(path))
                        )
                        count += 1
                con.commit(); con.close()
                print(f"[IMPORT-DOCS] Inserted {count} document records from {folder}")
                return 0
            else:
                print("[IMPORT-DOCS] Folder not found:", folder)
                return 2
        if arg == "--import-csv" and len(sys.argv) >= 4:
            table = sys.argv[2]; csvpath = sys.argv[3]
            ensure_schema_sqlite3()
            if not os.path.exists(csvpath):
                print("[IMPORT-CSV] File not found:", csvpath); return 2
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            with open(csvpath, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    print("[IMPORT-CSV] CSV is empty"); return 2
                cur.execute(f"PRAGMA table_info({table})")
                cols = [r[1] for r in cur.fetchall()]
                placeholders = ",".join(["?"] * len(cols))
                sql = f"INSERT INTO {table}({','.join(cols)}) VALUES ({placeholders})"
                imported = 0
                for r in rows:
                    vals = [r.get(c, None) for c in cols]
                    try:
                        cur.execute(sql, vals)
                        imported += 1
                    except Exception:
                        pass
                con.commit(); con.close()
                print(f"[IMPORT-CSV] Imported {imported} rows from {csvpath}")
                return 0
        if arg == "--import-xlsx" and len(sys.argv) >= 4:
            table = sys.argv[2]; xlsxpath = sys.argv[3]
            ensure_schema_sqlite3()
            if not HAS_PANDAS:
                print("[IMPORT-XLSX] Requires pandas+openpyxl"); return 2
            if not os.path.exists(xlsxpath):
                print("[IMPORT-XLSX] File not found:", xlsxpath); return 2
            try:
                df = pd.read_excel(xlsxpath, dtype=str)
            except Exception as e:
                print("[IMPORT-XLSX] Read error:", e); return 2
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute(f"PRAGMA table_info({table})")
            cols = [r[1] for r in cur.fetchall()]
            df_cols_norm = {c.lower().strip(): c for c in df.columns}
            mapped = [df_cols_norm.get(c.lower().strip()) for c in cols]
            placeholders = ",".join(["?"] * len(cols))
            sql = f"INSERT INTO {table}({','.join(cols)}) VALUES ({placeholders})"
            imported = 0
            for _, rec in df.iterrows():
                vals = [rec[m] if (m in df.columns) else None for m in mapped]
                try:
                    cur.execute(sql, vals)
                    imported += 1
                except Exception:
                    pass
            con.commit(); con.close()
            print(f"[IMPORT-XLSX] Imported {imported} rows from {xlsxpath}")
            return 0

    # If Qt available -> GUI
    try:
        ensure_schema_qt()
    except Exception:
        pass
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
=======
# QMS System - Thi Qar Oil Company (Quality & Performance Division)
# GUI if Qt is available (PyQt6 preferred, fallback to PyQt5). Otherwise, run in CLI/headless mode.
# SQLite backend + centered company logo + optional background music (GUI only)
# Designed by Chief Engineer Tareq Majeed Al-Karimi

import sys, os, csv, shutil, sqlite3

# -------- Optional Excel support --------
try:
    import pandas as pd  # requires openpyxl for .xlsx
    HAS_PANDAS = True
except Exception:
    pd = None
    HAS_PANDAS = False

# ================================================================
# Qt Compatibility Layer (may be unavailable in this environment)
# ================================================================
QT_API = 0  # 0=headless, 6=PyQt6, 5=PyQt5
HEADLESS = True

try:  # Prefer PyQt6
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QListWidget, QStackedWidget, QFileDialog, QMessageBox, QTableView, QToolBar,
        QStatusBar, QSplitter, QLineEdit, QTextEdit, QFormLayout, QDateEdit, QComboBox,
        QCheckBox, QInputDialog, QAbstractItemView
    )
    from PyQt6.QtCore import Qt, QDate, QUrl
    try:
        from PyQt6.QtGui import QAction  # PyQt6 puts QAction in QtGui
    except Exception:
        from PyQt6.QtWidgets import QAction
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    except Exception:
        QMediaPlayer = QAudioOutput = None
    QT_API = 6
    HEADLESS = False
    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    SMOOTH = Qt.TransformationMode.SmoothTransformation
    HORIZONTAL = Qt.Orientation.Horizontal
    SELECT_ROWS = QTableView.SelectionBehavior.SelectRows
    EDIT_DBL = QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.EditKeyPressed
    EDIT_NONE = QAbstractItemView.EditTrigger.NoEditTriggers
except Exception:
    try:  # Fallback to PyQt5
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QListWidget, QStackedWidget, QFileDialog, QMessageBox, QTableView, QToolBar,
            QStatusBar, QSplitter, QLineEdit, QTextEdit, QFormLayout, QDateEdit, QComboBox,
            QCheckBox, QAction, QInputDialog, QAbstractItemView
        )
        from PyQt5.QtCore import Qt, QDate, QUrl
        from PyQt5.QtGui import QIcon, QPixmap
        from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
        try:
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
        except Exception:
            QMediaPlayer = None
            QMediaContent = None
        QT_API = 5
        HEADLESS = False
        ALIGN_CENTER = Qt.AlignCenter
        SMOOTH = Qt.SmoothTransformation
        HORIZONTAL = Qt.Horizontal
        SELECT_ROWS = QTableView.SelectRows
        EDIT_DBL = (QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        EDIT_NONE = QAbstractItemView.NoEditTriggers
    except Exception:
        QT_API = 0
        HEADLESS = True

APP_TITLE = "QMS – Quality & Performance Division | Thi Qar Oil Company"
DB_NAME = "qms.sqlite"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATHS = [
    "/mnt/data/logo.png",
    os.path.join(BASE_DIR, "logo.png"),
    os.path.join(BASE_DIR, "sold.png"),
    os.path.join(BASE_DIR, "company_logo.png"),
    "logo.png",
    "sold.png",
    "company_logo.png",
    os.path.join(BASE_DIR, "resources", "sold.png"),
]
AUDIO_PATHS = [
    "/mnt/data/Audio.mp3",
    os.path.join(BASE_DIR, "Audio.mp3"),
    os.path.join(BASE_DIR, "audio.mp3"),
    "Audio.mp3",
    "audio.mp3",
    os.path.join(BASE_DIR, "resources", "audio.mp3"),
]
FOOTER_TEXT = "Designed by Chief Engineer Tareq Majeed Al-Karimi"

# ================================================================
# Per-section write passwords (no login screen)  
# Empty string => section remains read-only (cannot unlock)
# ================================================================
SECTION_PASSWORDS = {
    # ضع كلمة سر للأقسام التي تريد السماح بالتحرير فيها بعد إدخالها.
    # أقسام بلا كلمة سر ستبقى قراءة فقط.
    "policies":        "P0l!cy@2025",
    "objectives":      "0bj@2025",
    "documents":       "Doc@2025",
    "audit_plan":      "Plan@2025",
    "audits":          "Aud1t@2025",
    "nonconformities": "NC@2025",
    "capa":            "CAPA@2025",
    "knowledge_base":  "KB@2025",
    "reports":         "Rep@2025",
    "notifications":   "Noti@2025",
    "signatures":      "Sign@2025",
}

def check_section_password(section_key: str, parent=None) -> bool:
    """Ask for the section password; True if correct. If not configured -> False."""
    expected = SECTION_PASSWORDS.get(section_key, "")
    if not expected:
        return False
    # PyQt6/5 compatibility for password echo mode
    try:
        text, ok = QInputDialog.getText(parent, "Unlock", f"Enter password for [{section_key}]",
                                        QLineEdit.EchoMode.Password)
    except Exception:
        text, ok = QInputDialog.getText(parent, "Unlock", f"Enter password for [{section_key}]",
                                        QLineEdit.Password)
    if not ok:
        return False
    return text == expected

# ================================================================
# Schema (used by both GUI/Qt and headless/CLI)
# ================================================================
SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT,
        version TEXT,
        approved_by TEXT,
        approved_on TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS objectives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        metric TEXT,
        target TEXT,
        period TEXT,
        owner TEXT,
        progress INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT,
        version TEXT,
        owner TEXT,
        status TEXT,
        review_date TEXT,
        file_path TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,
        planned_date TEXT,
        auditor TEXT,
        scope TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,
        audit_date TEXT,
        auditor TEXT,
        findings TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS nonconformities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        root_cause TEXT,
        owner TEXT,
        due_date TEXT,
        status TEXT,
        related_audit INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS capa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nc_id INTEGER,
        action TEXT,
        owner TEXT,
        due_date TEXT,
        status TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        tags TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        period TEXT,
        notes TEXT,
        created_on TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        due_date TEXT,
        assigned_to TEXT,
        seen INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person TEXT,
        role TEXT,
        image_path TEXT,
        signed_on TEXT
    );
    """
]

# ================================================================
# DB Helpers (Qt or sqlite3)
# ================================================================

def ensure_schema_sqlite3():
    con = sqlite3.connect(DB_NAME)
    try:
        cur = con.cursor()
        for sql in SCHEMA_SQL:
            cur.executescript(sql)
        con.commit()
    finally:
        con.close()

if not HEADLESS:
    def get_db_connection_qt():
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(DB_NAME)
        if not db.open():
            raise RuntimeError("Failed to open database")
        return db

    def ensure_schema_qt():
        for sql in SCHEMA_SQL:
            QSqlQuery().exec(sql)

# ================================================================
# GUI Implementation (only if Qt available)
# ================================================================
if not HEADLESS:
    class TablePage(QWidget):
        def __init__(self, table_name: str, headers: dict[str, str], section_key: str | None = None):
            super().__init__()
            self.table_name = table_name
            self.headers = headers
            self.section_key = section_key or table_name
            self.unlocked = False

            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)

            self.model = QSqlTableModel(self)
            self.model.setTable(table_name)
            self.model.select()

            for col in range(self.model.columnCount()):
                field = self.model.record().fieldName(col)
                if field in headers:
                    self.model.setHeaderData(col, HORIZONTAL, headers[field])

            self.view = QTableView()
            self.view.setModel(self.model)
            # Better readability: row/column sizing
            try:
                vh = self.view.verticalHeader()
                hh = self.view.horizontalHeader()
                vh.setDefaultSectionSize(28)
                hh.setStretchLastSection(True)
            except Exception:
                pass
            self.view.setSelectionBehavior(SELECT_ROWS)
            self.view.setAlternatingRowColors(True)
            self.view.resizeColumnsToContents()
            self.view.setStyleSheet(
                "QTableView{selection-background-color:#cbdfff;}"
                "QHeaderView::section{background:#f2f4f8;border:1px solid #e5e9f0;}"
            )
            # read-only until unlocked
            try:
                self.view.setEditTriggers(EDIT_NONE)
            except Exception:
                pass

            btn_bar = QHBoxLayout()
            self.btn_add = QPushButton("Add Row")
            self.btn_del = QPushButton("Delete Selected")
            self.btn_save = QPushButton("Save")
            self.btn_export = QPushButton("Export CSV…")
            self.btn_import = QPushButton("Import CSV…")
            self.btn_import_excel = QPushButton("Import Excel…")
            self.btn_unlock = QPushButton("Unlock")

            for b in (self.btn_add, self.btn_del, self.btn_save, self.btn_export, self.btn_import, self.btn_import_excel, self.btn_unlock):
                btn_bar.addWidget(b)

            # Documents extras
            self.btn_attach = None
            self.btn_openfile = None
            if table_name == "documents":
                self.btn_attach = QPushButton("Attach File…")
                self.btn_openfile = QPushButton("Open File")
                btn_bar.addWidget(self.btn_attach)
                btn_bar.addWidget(self.btn_openfile)

            btn_bar.addStretch(1)

            layout.addWidget(self.view)
            layout.addLayout(btn_bar)

            # default locked controls
            def set_write_enabled(on: bool):
                self.btn_add.setEnabled(on)
                self.btn_del.setEnabled(on)
                self.btn_save.setEnabled(on)
                self.btn_import.setEnabled(on)
                self.btn_import_excel.setEnabled(on)
                if self.btn_attach:
                    self.btn_attach.setEnabled(on)
                # export/open are read-only actions -> keep enabled
                self.btn_export.setEnabled(True)
                if self.btn_openfile:
                    self.btn_openfile.setEnabled(True)

            self._set_write_enabled = set_write_enabled
            set_write_enabled(False)

            # connections
            self.btn_add.clicked.connect(self.add_row)
            self.btn_del.clicked.connect(self.delete_selected)
            self.btn_save.clicked.connect(self.save)
            self.btn_export.clicked.connect(self.export_csv)
            self.btn_import.clicked.connect(self.import_csv)
            self.btn_import_excel.clicked.connect(self.import_excel)
            self.btn_unlock.clicked.connect(self.try_unlock)
            if self.btn_attach:
                self.btn_attach.clicked.connect(self.attach_file)
            if self.btn_openfile:
                self.btn_openfile.clicked.connect(self.open_file)

        def try_unlock(self):
            expected = SECTION_PASSWORDS.get(self.section_key, "")
            if not expected:
                QMessageBox.information(self, "Read-only", "This section is read-only (no password configured).")
                return
            if self.unlocked:
                QMessageBox.information(self, "Unlocked", "Already unlocked.")
                return
            if check_section_password(self.section_key, self):
                self.unlocked = True
                self._set_write_enabled(True)
                try:
                    self.view.setEditTriggers(EDIT_DBL)
                except Exception:
                    pass
                QMessageBox.information(self, "Unlocked", "Editing enabled for this section.")
            else:
                QMessageBox.warning(self, "Wrong password", "Password is incorrect.")

        def _require_unlocked(self):
            if not self.unlocked:
                QMessageBox.warning(self, "Locked", "Unlock this section first.")
                return False
            return True

        def add_row(self):
            if not self._require_unlocked():
                return
            self.model.insertRow(self.model.rowCount())
            self.view.scrollToBottom()

        def delete_selected(self):
            if not self._require_unlocked():
                return
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return
            for idx in sorted(indexes, key=lambda i: i.row(), reverse=True):
                self.model.removeRow(idx.row())

        def save(self):
            if not self._require_unlocked():
                return
            if not self.model.submitAll():
                QMessageBox.critical(self, "Save Error", self.model.lastError().text())
            else:
                self.model.select()
                QMessageBox.information(self, "Saved", "Changes saved successfully.")

        def export_csv(self):
            path, _ = QFileDialog.getSaveFileName(self, "Export CSV", f"{self.table_name}.csv", "CSV Files (*.csv)")
            if not path:
                return
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                headers = [self.model.headerData(c, HORIZONTAL) for c in range(self.model.columnCount())]
                writer.writerow(headers)
                for r in range(self.model.rowCount()):
                    row = []
                    for c in range(self.model.columnCount()):
                        idx = self.model.index(r, c)
                        row.append(self.model.data(idx))
                    writer.writerow(row)
            QMessageBox.information(self, "Export", f"Exported to {path}")

        def import_csv(self):
            if not self._require_unlocked():
                return
            path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cols = [self.model.record().fieldName(c) for c in range(self.model.columnCount())]
            with open(path, newline='', encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    QMessageBox.information(self, "Import", "CSV is empty.")
                    con.close(); return
                placeholders = ",".join(["?"] * len(cols))
                sql = f"INSERT INTO {self.table_name}({','.join(cols)}) VALUES ({placeholders})"
                imported = 0
                for r in rows:
                    vals = [r.get(c, None) for c in cols]
                    try:
                        cur.execute(sql, vals)
                        imported += 1
                    except Exception:
                        pass
                con.commit(); con.close()
            self.model.select()
            QMessageBox.information(self, "Import", f"Imported {imported} rows from {os.path.basename(path)}")

        def import_excel(self):
            if not self._require_unlocked():
                return
            path, _ = QFileDialog.getOpenFileName(self, "Import Excel", "", "Excel Files (*.xlsx *.xls)")
            if not path:
                return
            if not HAS_PANDAS:
                QMessageBox.critical(
                    self,
                    "Excel Support Missing",
                    "Excel import requires pandas (and openpyxl for .xlsx).\n\n"
                    "Install with: pip install pandas openpyxl"
                )
                return
            try:
                df = pd.read_excel(path, dtype=str)
            except Exception as e:
                QMessageBox.critical(self, "Read Excel Error", str(e))
                return

            # Map columns by name (case-insensitive)
            df_cols_norm = {c.lower().strip(): c for c in df.columns}
            table_cols = [self.model.record().fieldName(c) for c in range(self.model.columnCount())]
            mapped_cols = []
            for c in table_cols:
                key = c.lower().strip()
                src = df_cols_norm.get(key)
                mapped_cols.append(src)

            rows = []
            for _, rec in df.iterrows():
                vals = [rec[src] if (src in df.columns) else None for src in mapped_cols]
                rows.append(vals)

            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            placeholders = ",".join(["?"] * len(table_cols))
            sql = f"INSERT INTO {self.table_name}({','.join(table_cols)}) VALUES ({placeholders})"
            imported = 0
            for vals in rows:
                try:
                    norm_vals = []
                    for v in vals:
                        if HAS_PANDAS and isinstance(v, float) and pd.isna(v):
                            norm_vals.append(None)
                        else:
                            norm_vals.append(v)
                    cur.execute(sql, norm_vals)
                    imported += 1
                except Exception:
                    pass
            con.commit()
            con.close()

            self.model.select()
            QMessageBox.information(self, "Import", f"Imported {imported} rows from {os.path.basename(path)}")

        # ---- Documents-specific helpers ----
        def _selected_row_id(self):
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return None
            row = indexes[0].row()
            idx = self.model.index(row, 0)
            return self.model.data(idx), row

        def attach_file(self):
            if not self._require_unlocked():
                return
            if self.table_name != "documents":
                return
            sel = self._selected_row_id()
            if sel is None:
                QMessageBox.warning(self, "No selection", "Select a document row first.")
                return
            _id, row = sel
            src, _ = QFileDialog.getOpenFileName(self, "Attach File", "", "All Files (*.*)")
            if not src:
                return
            attachments_dir = os.path.join(BASE_DIR, "attachments")
            try:
                os.makedirs(attachments_dir, exist_ok=True)
                dst = os.path.join(attachments_dir, os.path.basename(src))
                shutil.copyfile(src, dst)
                # write file_path
                col = None
                for c in range(self.model.columnCount()):
                    if self.model.record().fieldName(c) == "file_path":
                        col = c; break
                if col is not None:
                    self.model.setData(self.model.index(row, col), dst)
                    self.model.submitAll(); self.model.select()
                    QMessageBox.information(self, "Attached", f"File attached to record #{_id}.")
            except Exception as e:
                QMessageBox.critical(self, "Attach Error", str(e))

        def open_file(self):
            if self.table_name != "documents":
                return
            sel = self._selected_row_id()
            if sel is None:
                QMessageBox.warning(self, "No selection", "Select a document row first.")
                return
            _id, row = sel
            col = None
            for c in range(self.model.columnCount()):
                if self.model.record().fieldName(c) == "file_path":
                    col = c; break
            if col is None:
                QMessageBox.warning(self, "No file_path column", "This table has no file_path column configured.")
                return
            path = self.model.data(self.model.index(row, col))
            if not path or not os.path.exists(path):
                QMessageBox.warning(self, "Missing File", "No file is attached or file not found.")
                return
            try:
                if sys.platform.startswith('win'):
                    os.startfile(path)  # type: ignore
                elif sys.platform == 'darwin':
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception as e:
                QMessageBox.critical(self, "Open Error", str(e))

    class DashboardPage(QWidget):
        def __init__(self):
            super().__init__()
            lay = QVBoxLayout(self)
            lay.setContentsMargins(24, 16, 24, 16)
            lay.setSpacing(12)

            # Centered company logo
            logo_label = QLabel()
            logo_label.setAlignment(ALIGN_CENTER)

            def resolve_existing(paths):
                for p in paths:
                    try:
                        if p and os.path.exists(p):
                            return os.path.abspath(p)
                    except Exception:
                        pass
                return None

            logo_file = resolve_existing(LOGO_PATHS)
            if logo_file:
                pix = QPixmap(logo_file)
                if not pix.isNull():
                    logo_label.setPixmap(pix.scaledToHeight(96, SMOOTH))
                else:
                    logo_label.setText("[Logo not readable]")
                    logo_label.setStyleSheet("color:#777; border:1px dashed #aaa; padding:8px;")
            else:
                logo_label.setText("[Thi Qar Oil Company Logo]")
                logo_label.setStyleSheet("color:#777; border:1px dashed #aaa; padding:8px;")
            lay.addWidget(logo_label)

            title = QLabel("Quality Management System – Quality & Performance Division")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:20px; font-weight:600; margin-top:6px;")
            subtitle = QLabel("Internal automation for policies, audits, NCs, CAPA, objectives and reports.")
            subtitle.setAlignment(ALIGN_CENTER)
            subtitle.setStyleSheet("color:#444;")

            lay.addWidget(title)
            lay.addWidget(subtitle)

            tips = QLabel(
                "• Use the left menu to open modules.\n"
                "• Right-click inside tables for copy/paste.\n"
                "• Use Export to create CSV files; attach to reports.\n"
                "• Keep data synchronized: save after edits.\n"
                "• In Documents: use Attach File to copy/link PDFs, Excel, Word, images, etc."
            )
            tips.setStyleSheet("background:#f5f7fb; border:1px solid #e2e6ef; padding:10px; border-radius:8px; margin-top:10px;")
            lay.addWidget(tips)
            lay.addStretch(1)

    class SignaturePage(QWidget):
        """Simple E-Signature page (stores name/role and optional image path)."""
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)
            title = QLabel("E-Signature")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:18px; font-weight:600;")
            layout.addWidget(title)

            form = QFormLayout()
            try:
                form.setSpacing(12)
            except Exception:
                pass
            self.person = QLineEdit()
            self.role = QLineEdit()
            self.image_path = QLineEdit()
            self.btn_browse = QPushButton("Browse Image…")
            self.btn_browse.clicked.connect(self.browse)
            form.addRow("Person", self.person)
            form.addRow("Role", self.role)
            row = QHBoxLayout()
            row.addWidget(self.image_path)
            row.addWidget(self.btn_browse)
            form.addRow("Image", row)
            layout.addLayout(form)

            self.btn_save = QPushButton("Save Signature")
            self.btn_save.clicked.connect(self.save)
            layout.addWidget(self.btn_save)

            # per-section unlock for signatures
            self.unlocked = False
            self.btn_unlock = QPushButton("Unlock")
            layout.addWidget(self.btn_unlock)
            self.btn_save.setEnabled(False)

            def on_unlock():
                expected = SECTION_PASSWORDS.get("signatures", "")
                if not expected:
                    QMessageBox.information(self, "Read-only", "This section is read-only (no password configured).")
                    return
                if self.unlocked:
                    QMessageBox.information(self, "Unlocked", "Already unlocked.")
                    return
                if check_section_password("signatures", self):
                    self.unlocked = True
                    self.btn_save.setEnabled(True)
                    QMessageBox.information(self, "Unlocked", "Editing enabled for signatures.")
                else:
                    QMessageBox.warning(self, "Wrong password", "Password is incorrect.")

            self.btn_unlock.clicked.connect(on_unlock)
            layout.addStretch(1)

        def browse(self):
            path, _ = QFileDialog.getOpenFileName(self, "Select Signature", "", "Images (*.png *.jpg *.jpeg)")
            if path:
                self.image_path.setText(path)

        def save(self):
            if not self.unlocked:
                QMessageBox.warning(self, "Locked", "Unlock this section first.")
                return
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute(
                "INSERT INTO signatures(person, role, image_path, signed_on) VALUES (?,?,?,date('now'))",
                (self.person.text(), self.role.text(), self.image_path.text())
            )
            con.commit()
            con.close()
            QMessageBox.information(self, "Saved", "Signature saved.")
            self.person.clear(); self.role.clear(); self.image_path.clear()

    class NotificationsPage(QWidget):
        """Notifications view using QSqlTableModel for consistency."""
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(24, 16, 24, 16)
            layout.setSpacing(12)
            title = QLabel("Notifications")
            title.setAlignment(ALIGN_CENTER)
            title.setStyleSheet("font-size:18px; font-weight:600;")
            layout.addWidget(title)

            self.model = QSqlTableModel(self)
            self.model.setTable("notifications")
            self.model.select()

            self.view = QTableView()
            self.view.setModel(self.model)
            self.view.setSelectionBehavior(SELECT_ROWS)
            self.view.resizeColumnsToContents()
            layout.addWidget(self.view)

            bar = QHBoxLayout()
            self.btn_add = QPushButton("Quick Add")
            self.btn_seen = QPushButton("Mark Seen")
            self.btn_refresh = QPushButton("Refresh")
            for b in (self.btn_add, self.btn_seen, self.btn_refresh):
                bar.addWidget(b)
            bar.addStretch(1)
            layout.addLayout(bar)

            self.btn_add.clicked.connect(self.quick_add)
            self.btn_seen.clicked.connect(self.mark_seen)
            self.btn_refresh.clicked.connect(self.model.select)

        def quick_add(self):
            q = QSqlQuery()
            q.exec("INSERT INTO notifications(title, due_date, assigned_to, seen) VALUES ('Review documents', date('now','+3 day'), 'Quality Team', 0)")
            self.model.select()

        def mark_seen(self):
            indexes = self.view.selectionModel().selectedRows()
            if not indexes:
                return
            q = QSqlQuery()
            for idx in indexes:
                rowid = self.model.data(self.model.index(idx.row(), 0))
                q.exec(f"UPDATE notifications SET seen=1 WHERE id={rowid}")
            self.model.select()

    class AudioHelper:
        def __init__(self, parent=None):
            self.available = QMediaPlayer is not None
            self.player = None
            self.output = None
            self.api = QT_API
            if not self.available:
                return
            if QT_API == 6:
                self.player = QMediaPlayer(parent)
                self.output = QAudioOutput(parent) if 'QAudioOutput' in globals() and QAudioOutput else None
                if self.output:
                    try:
                        self.player.setAudioOutput(self.output)
                        self.output.setVolume(0.25)
                    except Exception:
                        pass
                self.player.mediaStatusChanged.connect(self._on_status)
            else:
                self.player = QMediaPlayer(parent)
                try:
                    self.player.setVolume(25)
                except Exception:
                    pass
                self.player.mediaStatusChanged.connect(self._on_status)

        def _on_status(self, status):
            try:
                if self.api == 6:
                    from PyQt6.QtMultimedia import QMediaPlayer as _P6
                    if status == _P6.MediaStatus.EndOfMedia:
                        self.player.setPosition(0)
                        self.player.play()
                else:
                    if int(status) == 7:  # EndOfMedia for PyQt5
                        self.player.setPosition(0)
                        self.player.play()
            except Exception:
                pass

        def start(self, paths):
            if not self.available:
                return False
            path = next((p for p in paths if os.path.exists(p)), None)
            if not path:
                return False
            url = QUrl.fromLocalFile(os.path.abspath(path))
            try:
                if QT_API == 6:
                    self.player.setSource(url)
                else:
                    from PyQt5.QtMultimedia import QMediaContent
                    self.player.setMedia(QMediaContent(url))
            except Exception:
                return False
            try:
                if QT_API == 6 and self.output:
                    self.output.setVolume(0.25)
                else:
                    self.player.setVolume(25)
            except Exception:
                pass
            self.player.play()
            return True

        def toggle_mute(self):
            if not self.available or not self.player:
                return False
            try:
                if QT_API == 6 and self.output:
                    self.output.setVolume(0 if self.output.volume() > 0 else 0.25)
                else:
                    self.player.setMuted(not self.player.isMuted())
            except Exception:
                pass
            return True

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(APP_TITLE)
            self.resize(1200, 720)

            tb = QToolBar("Main")
            self.addToolBar(tb)

            act_backup = QAction("Backup DB", self)
            act_backup.triggered.connect(self.backup_db)
            tb.addAction(act_backup)

            act_open = QAction("Open DB Folder", self)
            act_open.triggered.connect(self.open_folder)
            tb.addAction(act_open)

            self.audio = AudioHelper(self)
            self.audio.start(AUDIO_PATHS)
            act_mute = QAction("Music On/Off", self)
            act_mute.triggered.connect(self.audio.toggle_mute)
            tb.addAction(act_mute)

            self.status = QStatusBar()
            self.setStatusBar(self.status)

            splitter = QSplitter()
            splitter.setChildrenCollapsible(False)
            self.menu = QListWidget()
            self.menu.addItems([
                "Dashboard",
                "Quality Policy",
                "Objectives",
                "Document Control",
                "Audit Plan",
                "Audits",
                "Non-Conformance",
                "CAPA",
                "Knowledge Base",
                "Reports",
                "Performance Evaluation (KPI)",
                "E-Signature",
                "Notifications"
            ])
            self.menu.setMinimumWidth(260)
            self.menu.setMaximumWidth(320)

            self.stack = QStackedWidget()
            splitter.addWidget(self.menu)
            splitter.addWidget(self.stack)
            splitter.setStretchFactor(1, 1)
            self.setCentralWidget(splitter)

            # Pages
            self.pages = []
            self.add_page(DashboardPage())
            self.add_page(TablePage("policies", {
                "id": "ID", "title": "Title", "body": "Body", "version": "Version",
                "approved_by": "Approved By", "approved_on": "Approved On"
            }, section_key="policies"))
            self.add_page(TablePage("objectives", {
                "id": "ID", "title": "Title", "metric": "Metric", "target": "Target",
                "period": "Period", "owner": "Owner", "progress": "Progress %"
            }, section_key="objectives"))
            self.add_page(TablePage("documents", {
                "id": "ID", "name": "Name", "code": "Code", "version": "Version",
                "owner": "Owner", "status": "Status", "review_date": "Review Date",
                "file_path": "File Path"
            }, section_key="documents"))
            self.add_page(TablePage("audit_plan", {
                "id": "ID", "area": "Area", "planned_date": "Planned Date",
                "auditor": "Auditor", "scope": "Scope", "status": "Status"
            }, section_key="audit_plan"))
            self.add_page(TablePage("audits", {
                "id": "ID", "area": "Area", "audit_date": "Audit Date", "auditor": "Auditor",
                "findings": "Findings", "status": "Status"
            }, section_key="audits"))
            self.add_page(TablePage("nonconformities", {
                "id": "ID", "date": "Date", "description": "Description",
                "root_cause": "Root Cause", "owner": "Owner", "due_date": "Due Date",
                "status": "Status", "related_audit": "Related Audit"
            }, section_key="nonconformities"))
            self.add_page(TablePage("capa", {
                "id": "ID", "nc_id": "NC ID", "action": "Action",
                "owner": "Owner", "due_date": "Due Date", "status": "Status"
            }, section_key="capa"))
            self.add_page(TablePage("knowledge_base", {
                "id": "ID", "title": "Title", "content": "Content", "tags": "Tags"
            }, section_key="knowledge_base"))
            self.add_page(TablePage("reports", {
                "id": "ID", "title": "Title", "period": "Period", "notes": "Notes",
                "created_on": "Created On"
            }, section_key="reports"))
            self.add_page(TablePage("objectives", {
                "id": "ID", "title": "Title", "metric": "Metric", "target": "Target",
                "period": "Period", "owner": "Owner", "progress": "Progress %"
            }, section_key="objectives"))
            self.add_page(SignaturePage())
            self.add_page(NotificationsPage())

            self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)
            self.menu.setCurrentRow(0)

            footer = QLabel(FOOTER_TEXT)
            footer.setAlignment(ALIGN_CENTER)
            footer.setStyleSheet("color:#666; padding:6px; border-top:1px solid #e5e5e5;")
            self.status.addPermanentWidget(footer, 1)

        def add_page(self, widget: QWidget):
            self.pages.append(widget)
            self.stack.addWidget(widget)

        def backup_db(self):
            path, _ = QFileDialog.getSaveFileName(self, "Backup SQLite", "qms_backup.sqlite", "SQLite DB (*.sqlite)")
            if not path:
                return
            try:
                shutil.copyfile(DB_NAME, path)
                QMessageBox.information(self, "Backup", f"Database copied to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Backup Error", str(e))

        def open_folder(self):
            folder = os.path.abspath(os.path.dirname(DB_NAME) or ".")
            QMessageBox.information(self, "DB Folder", folder)

# ================================================================
# Self-tests & CLI tools (work in both modes)
# ================================================================

def selftest_basic() -> int:
    """Test: create/open DB and ensure all tables exist."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = {r[0] for r in cur.fetchall()}
        required = {
            "policies", "objectives", "documents", "audit_plan", "audits",
            "nonconformities", "capa", "knowledge_base", "reports",
            "notifications", "signatures"
        }
        missing = required - names
        if missing:
            print("[SELFTEST] Missing tables:", ", ".join(sorted(missing)))
            return 2
        print(f"[SELFTEST] OK: schema present; Qt API={QT_API}; headless={HEADLESS}")
        return 0
    except Exception as e:
        print("[SELFTEST] ERROR:", e)
        return 1

def selftest_extended() -> int:
    """Test: insert a sample record and read it back (policies table)."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO policies(title, body, version, approved_by, approved_on) VALUES (?,?,?,?,date('now'))",
                    ("Quality Policy", "Initial test policy", "v1", "Head of Division",))
        con.commit()
        cur.execute("SELECT COUNT(*) FROM policies")
        cnt = cur.fetchone()[0]
        print(f"[SELFTEST-EXT] Policies rows: {cnt}")
        con.close()
        return 0
    except Exception as e:
        print("[SELFTEST-EXT] ERROR:", e)
        return 1

def selftest_nc() -> int:
    """Test: insert NC + CAPA and verify linkage."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO nonconformities(date, description, root_cause, owner, due_date, status, related_audit) VALUES (date('now'), ?, ?, ?, date('now','+7 day'), 'Open', 1)",
                    ("Sample NC", "Root cause test", "Quality Team"))
        nc_id = cur.lastrowid
        cur.execute("INSERT INTO capa(nc_id, action, owner, due_date, status) VALUES (?,?,?,?,?)",
                    (nc_id, "Corrective action", "Quality Team", "2099-01-01", "Planned"))
        con.commit()
        cur.execute("SELECT COUNT(*) FROM capa WHERE nc_id=?", (nc_id,))
        cnt = cur.fetchone()[0]
        print(f"[SELFTEST-NC] CAPA linked rows: {cnt}")
        con.close()
        return 0 if cnt >= 1 else 2
    except Exception as e:
        print("[SELFTEST-NC] ERROR:", e)
        return 1

def selftest_notify() -> int:
    """Test: add notification and mark as seen (simulated)."""
    try:
        ensure_schema_sqlite3()
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO notifications(title, due_date, assigned_to, seen) VALUES ('Review documents', date('now','+3 day'), 'Quality Team', 0)")
        nid = cur.lastrowid
        cur.execute("UPDATE notifications SET seen=1 WHERE id=?", (nid,))
        con.commit()
        cur.execute("SELECT seen FROM notifications WHERE id=?", (nid,))
        seen = cur.fetchone()[0]
        print(f"[SELFTEST-NOTIFY] Notification seen={seen}")
        con.close()
        return 0 if int(seen) == 1 else 2
    except Exception as e:
        print("[SELFTEST-NOTIFY] ERROR:", e)
        return 1

def cli_usage():
    print(
        "Usage:\n"
        "  python main.py --selftest            # basic DB/schema test\n"
        "  python main.py --selftest-extended   # insert & count sample row (policies)\n"
        "  python main.py --selftest-nc         # insert NC & CAPA and verify linkage\n"
        "  python main.py --selftest-notify     # add notification and mark as seen\n"
        "  python main.py --import-docs <folder>  # bulk create document records from files (pdf/xlsx/docx/...)\n"
        "  python main.py --import-csv <table> <csvpath>  # import CSV into a table (columns by header names)\n"
        "  python main.py --import-xlsx <table> <xlsxpath>  # import Excel into a table (requires pandas+openpyxl)\n"
        "  python main.py                        # launch GUI if Qt available; otherwise stay in headless mode"
    )

# ================================================================
# App Entry
# ================================================================

def main() -> int:
    # Self-tests & imports path
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--selftest":
            return selftest_basic()
        if arg == "--selftest-extended":
            return selftest_extended()
        if arg == "--selftest-nc":
            return selftest_nc()
        if arg == "--selftest-notify":
            return selftest_notify()
        if arg == "--import-docs" and len(sys.argv) >= 3:
            folder = sys.argv[2]
            ensure_schema_sqlite3()
            count = 0
            if os.path.isdir(folder):
                con = sqlite3.connect(DB_NAME)
                cur = con.cursor()
                for name in os.listdir(folder):
                    path = os.path.join(folder, name)
                    if not os.path.isfile(path):
                        continue
                    ext = os.path.splitext(name)[1].lower()
                    if ext in (".pdf", ".xlsx", ".xls", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"):
                        cur.execute(
                            "INSERT INTO documents(name, code, version, owner, status, review_date, file_path) VALUES (?,?,?,?,?,?,?)",
                            (name, "", "v1", "Quality Team", "New", None, os.path.abspath(path))
                        )
                        count += 1
                con.commit(); con.close()
                print(f"[IMPORT-DOCS] Inserted {count} document records from {folder}")
                return 0
            else:
                print("[IMPORT-DOCS] Folder not found:", folder)
                return 2
        if arg == "--import-csv" and len(sys.argv) >= 4:
            table = sys.argv[2]; csvpath = sys.argv[3]
            ensure_schema_sqlite3()
            if not os.path.exists(csvpath):
                print("[IMPORT-CSV] File not found:", csvpath); return 2
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            with open(csvpath, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    print("[IMPORT-CSV] CSV is empty"); return 2
                cur.execute(f"PRAGMA table_info({table})")
                cols = [r[1] for r in cur.fetchall()]
                placeholders = ",".join(["?"] * len(cols))
                sql = f"INSERT INTO {table}({','.join(cols)}) VALUES ({placeholders})"
                imported = 0
                for r in rows:
                    vals = [r.get(c, None) for c in cols]
                    try:
                        cur.execute(sql, vals)
                        imported += 1
                    except Exception:
                        pass
                con.commit(); con.close()
                print(f"[IMPORT-CSV] Imported {imported} rows from {csvpath}")
                return 0
        if arg == "--import-xlsx" and len(sys.argv) >= 4:
            table = sys.argv[2]; xlsxpath = sys.argv[3]
            ensure_schema_sqlite3()
            if not HAS_PANDAS:
                print("[IMPORT-XLSX] Requires pandas+openpyxl"); return 2
            if not os.path.exists(xlsxpath):
                print("[IMPORT-XLSX] File not found:", xlsxpath); return 2
            try:
                df = pd.read_excel(xlsxpath, dtype=str)
            except Exception as e:
                print("[IMPORT-XLSX] Read error:", e); return 2
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute(f"PRAGMA table_info({table})")
            cols = [r[1] for r in cur.fetchall()]
            df_cols_norm = {c.lower().strip(): c for c in df.columns}
            mapped = [df_cols_norm.get(c.lower().strip()) for c in cols]
            placeholders = ",".join(["?"] * len(cols))
            sql = f"INSERT INTO {table}({','.join(cols)}) VALUES ({placeholders})"
            imported = 0
            for _, rec in df.iterrows():
                vals = [rec[m] if (m in df.columns) else None for m in mapped]
                try:
                    cur.execute(sql, vals)
                    imported += 1
                except Exception:
                    pass
            con.commit(); con.close()
            print(f"[IMPORT-XLSX] Imported {imported} rows from {xlsxpath}")
            return 0

    # If Qt available -> GUI
    try:
        ensure_schema_qt()
    except Exception:
        pass
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
>>>>>>> 58e6beb (Add files via upload)
