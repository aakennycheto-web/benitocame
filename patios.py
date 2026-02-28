"""
FlotaControl - Sistema de Gestión de Transportes
Requiere: pip install PyQt5
Ejecutar: python control_flota.py
"""

import sys
import json
import os
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QGridLayout,
    QMessageBox, QScrollArea, QDoubleSpinBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush


# ──────────────────────────────────────────────
# Paleta de colores (tema oscuro tipo camión)
# ──────────────────────────────────────────────
BG         = "#0d0f14"
SURFACE    = "#161b24"
SURFACE2   = "#1e2535"
BORDER     = "#2a3347"
ACCENT     = "#f5a623"
GREEN      = "#2ecc71"
RED        = "#e74c3c"
BLUE       = "#3b82f6"
TEXT       = "#e8edf5"
MUTED      = "#8896ab"

DATA_FILE = os.path.join(os.path.dirname(__file__), "flota_data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def fmt(n):
    return f"${n:,.2f}"


# ──────────────────────────────────────────────
# Widget: Tarjeta de resumen
# ──────────────────────────────────────────────
class SummaryCard(QFrame):
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-top: 3px solid {color};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"color: {MUTED}; font-size: 11px; letter-spacing: 1px; border: none;")

        self.value_lbl = QLabel("$0.00")
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: bold; border: none;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)

    def set_value(self, val):
        self.value_lbl.setText(val)


# ──────────────────────────────────────────────
# Ventana Principal
# ──────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.records = load_data()
        self.setWindowTitle("🚌 FlotaControl — Gestión de Transportes")
        self.setMinimumSize(1000, 700)
        self.setup_palette()
        self.build_ui()
        self.refresh()

    def setup_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(BG))
        palette.setColor(QPalette.WindowText, QColor(TEXT))
        palette.setColor(QPalette.Base, QColor(SURFACE2))
        palette.setColor(QPalette.AlternateBase, QColor(SURFACE))
        palette.setColor(QPalette.Text, QColor(TEXT))
        palette.setColor(QPalette.Button, QColor(SURFACE))
        palette.setColor(QPalette.ButtonText, QColor(TEXT))
        self.setPalette(palette)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {BG}; color: {TEXT}; font-family: Arial; font-size: 13px; }}
            QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE}; }}
            QTabBar::tab {{
                background: {SURFACE2}; color: {MUTED}; padding: 10px 20px;
                border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 3px;
            }}
            QTabBar::tab:selected {{ background: {ACCENT}; color: #000; font-weight: bold; }}
            QTabBar::tab:hover:!selected {{ background: {SURFACE}; color: {TEXT}; }}
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {{
                background: {SURFACE2}; border: 1px solid {BORDER}; border-radius: 6px;
                padding: 7px 10px; color: {TEXT}; font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {ACCENT};
            }}
            QComboBox QAbstractItemView {{ background: {SURFACE2}; color: {TEXT}; selection-background-color: {ACCENT}; selection-color: #000; }}
            QPushButton {{
                background: {ACCENT}; color: #000; font-weight: bold;
                border: none; border-radius: 7px; padding: 10px 22px; font-size: 13px;
            }}
            QPushButton:hover {{ background: #e09510; }}
            QPushButton:pressed {{ background: #c07c00; }}
            QPushButton#btnDelete {{
                background: {RED}; color: white; padding: 4px 12px; font-size: 11px;
            }}
            QPushButton#btnDelete:hover {{ background: #c0392b; }}
            QTableWidget {{
                background: {SURFACE}; border: none; gridline-color: {BORDER};
                color: {TEXT}; font-size: 12px;
            }}
            QTableWidget::item {{ padding: 6px; }}
            QTableWidget::item:selected {{ background: {SURFACE2}; color: {TEXT}; }}
            QHeaderView::section {{
                background: {SURFACE2}; color: {MUTED}; border: none;
                border-bottom: 1px solid {BORDER}; padding: 8px; font-size: 11px;
                text-transform: uppercase; letter-spacing: 1px;
            }}
            QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 20px; }}
            QLabel#sectionTitle {{ font-size: 18px; font-weight: bold; color: {ACCENT}; letter-spacing: 1px; }}
            QLabel#fieldLabel {{ color: {MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
        """)

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"background: {SURFACE}; border-bottom: 2px solid {ACCENT};")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 0, 24, 0)
        logo = QLabel("🚌  FLOTACONTROL")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 22px; font-weight: bold; letter-spacing: 3px;")
        sub = QLabel("Sistema de Gestión de Transportes")
        sub.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        h_lay.addWidget(logo)
        h_lay.addSpacing(16)
        h_lay.addWidget(sub)
        h_lay.addStretch()
        main_layout.addWidget(header)

        # ── Summary cards ──
        cards_widget = QWidget()
        cards_widget.setStyleSheet(f"background: {BG};")
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(24, 16, 24, 8)
        cards_layout.setSpacing(14)

        self.card_income  = SummaryCard("Ingresos Totales", GREEN)
        self.card_expense = SummaryCard("Gastos Totales", RED)
        self.card_profit  = SummaryCard("Ganancia Neta", ACCENT)
        self.card_trips   = SummaryCard("Viajes Registrados", BLUE)
        self.card_trips.value_lbl.setText("0")

        for c in [self.card_income, self.card_expense, self.card_profit, self.card_trips]:
            cards_layout.addWidget(c)
        main_layout.addWidget(cards_widget)

        # ── Tabs ──
        tab_container = QWidget()
        tab_container.setStyleSheet(f"background: {BG};")
        tab_lay = QVBoxLayout(tab_container)
        tab_lay.setContentsMargins(24, 8, 24, 16)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_dashboard_tab(), "📊  Dashboard")
        self.tabs.addTab(self.build_trip_tab(),      "➕  Registrar Viaje")
        self.tabs.addTab(self.build_expense_tab(),   "💸  Registrar Gasto")
        self.tabs.addTab(self.build_movements_tab(), "📋  Movimientos")
        self.tabs.addTab(self.build_trucks_tab(),    "🚌  Camiones")

        tab_lay.addWidget(self.tabs)
        main_layout.addWidget(tab_container)

    # ── Dashboard ──────────────────────────────
    def build_dashboard_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("RESUMEN POR UNIDAD")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background: {SURFACE};")
        self.dashboard_content = QWidget()
        self.dashboard_layout = QVBoxLayout(self.dashboard_content)
        self.dashboard_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.dashboard_content)
        layout.addWidget(scroll)
        return w

    # ── Registrar Viaje ────────────────────────
    def build_trip_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("NUEVO INGRESO POR VIAJE")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("fieldLabel")
            return l

        grid.addWidget(lbl("Camión / Unidad"), 0, 0)
        self.v_camion = QLineEdit(); self.v_camion.setPlaceholderText("Ej. Unidad 01")
        grid.addWidget(self.v_camion, 1, 0)

        grid.addWidget(lbl("Chofer"), 0, 1)
        self.v_chofer = QLineEdit(); self.v_chofer.setPlaceholderText("Nombre del chofer")
        grid.addWidget(self.v_chofer, 1, 1)

        grid.addWidget(lbl("Ruta (Origen → Destino)"), 0, 2)
        self.v_ruta = QLineEdit(); self.v_ruta.setPlaceholderText("Ej. CDMX → Guadalajara")
        grid.addWidget(self.v_ruta, 1, 2)

        grid.addWidget(lbl("Ingreso del Viaje ($)"), 2, 0)
        self.v_ingreso = QDoubleSpinBox()
        self.v_ingreso.setRange(0, 9_999_999); self.v_ingreso.setPrefix("$ "); self.v_ingreso.setSingleStep(100)
        grid.addWidget(self.v_ingreso, 3, 0)

        grid.addWidget(lbl("Fecha"), 2, 1)
        self.v_fecha = QDateEdit(QDate.currentDate()); self.v_fecha.setCalendarPopup(True)
        grid.addWidget(self.v_fecha, 3, 1)

        layout.addLayout(grid)

        btn = QPushButton("✓  Registrar Viaje")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.add_trip)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    # ── Registrar Gasto ────────────────────────
    def build_expense_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("REGISTRAR GASTO")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("fieldLabel")
            return l

        grid.addWidget(lbl("Camión / Unidad"), 0, 0)
        self.g_camion = QLineEdit(); self.g_camion.setPlaceholderText("Ej. Unidad 01")
        grid.addWidget(self.g_camion, 1, 0)

        grid.addWidget(lbl("Tipo de Gasto"), 0, 1)
        self.g_tipo = QComboBox()
        self.g_tipo.addItems(["⛽  Combustible", "👷  Sueldo Chofer", "🛣️  Peajes y Casetas"])
        grid.addWidget(self.g_tipo, 1, 1)

        grid.addWidget(lbl("Descripción (opcional)"), 0, 2)
        self.g_desc = QLineEdit(); self.g_desc.setPlaceholderText("Detalle adicional")
        grid.addWidget(self.g_desc, 1, 2)

        grid.addWidget(lbl("Monto ($)"), 2, 0)
        self.g_monto = QDoubleSpinBox()
        self.g_monto.setRange(0, 9_999_999); self.g_monto.setPrefix("$ "); self.g_monto.setSingleStep(50)
        grid.addWidget(self.g_monto, 3, 0)

        grid.addWidget(lbl("Fecha"), 2, 1)
        self.g_fecha = QDateEdit(QDate.currentDate()); self.g_fecha.setCalendarPopup(True)
        grid.addWidget(self.g_fecha, 3, 1)

        layout.addLayout(grid)

        btn = QPushButton("✓  Registrar Gasto")
        btn.setFixedWidth(200)
        btn.clicked.connect(self.add_expense)
        layout.addWidget(btn)
        layout.addStretch()
        return w

    # ── Movimientos ────────────────────────────
    def build_movements_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("TODOS LOS MOVIMIENTOS")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.mov_table = QTableWidget()
        self.mov_table.setColumnCount(6)
        self.mov_table.setHorizontalHeaderLabels(["Fecha", "Camión", "Tipo", "Descripción", "Monto", ""])
        self.mov_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mov_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.mov_table.setColumnWidth(5, 70)
        self.mov_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mov_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mov_table.verticalHeader().setVisible(False)
        self.mov_table.setAlternatingRowColors(True)
        layout.addWidget(self.mov_table)
        return w

    # ── Camiones ────────────────────────────────
    def build_trucks_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("ESTADO DE FLOTA")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none;")
        self.trucks_content = QWidget()
        self.trucks_layout = QGridLayout(self.trucks_content)
        self.trucks_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.trucks_layout.setSpacing(14)
        scroll.setWidget(self.trucks_content)
        layout.addWidget(scroll)
        return w

    # ── Acciones ───────────────────────────────
    def add_trip(self):
        camion  = self.v_camion.text().strip()
        chofer  = self.v_chofer.text().strip()
        ruta    = self.v_ruta.text().strip()
        ingreso = self.v_ingreso.value()
        fecha   = self.v_fecha.date().toString("yyyy-MM-dd")

        if not camion or ingreso <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Por favor ingresa el camión y un monto mayor a 0.")
            return

        self.records.append({
            "id": int(QDate.currentDate().toJulianDay() * 100000 + len(self.records)),
            "type": "income",
            "camion": camion, "chofer": chofer,
            "desc": ruta or "Viaje", "amount": ingreso, "fecha": fecha
        })
        save_data(self.records)
        self.v_camion.clear(); self.v_chofer.clear(); self.v_ruta.clear(); self.v_ingreso.setValue(0)
        QMessageBox.information(self, "✅ Registrado", f"Viaje de {camion} registrado: {fmt(ingreso)}")
        self.refresh()

    def add_expense(self):
        camion = self.g_camion.text().strip()
        tipo   = self.g_tipo.currentText().split("  ")[-1]
        desc   = self.g_desc.text().strip() or tipo
        monto  = self.g_monto.value()
        fecha  = self.g_fecha.date().toString("yyyy-MM-dd")

        if not camion or monto <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Por favor ingresa el camión y un monto mayor a 0.")
            return

        self.records.append({
            "id": int(QDate.currentDate().toJulianDay() * 100000 + len(self.records)),
            "type": "expense",
            "camion": camion, "expType": tipo,
            "desc": desc, "amount": monto, "fecha": fecha
        })
        save_data(self.records)
        self.g_camion.clear(); self.g_desc.clear(); self.g_monto.setValue(0)
        QMessageBox.information(self, "✅ Registrado", f"Gasto en {camion} registrado: {fmt(monto)}")
        self.refresh()

    def delete_record(self, rec_id):
        reply = QMessageBox.question(self, "Eliminar", "¿Deseas eliminar este movimiento?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.records = [r for r in self.records if r["id"] != rec_id]
            save_data(self.records)
            self.refresh()

    # ── Render / Refresh ───────────────────────
    def refresh(self):
        income_total  = sum(r["amount"] for r in self.records if r["type"] == "income")
        expense_total = sum(r["amount"] for r in self.records if r["type"] == "expense")
        profit        = income_total - expense_total
        trips         = sum(1 for r in self.records if r["type"] == "income")

        self.card_income.set_value(fmt(income_total))
        self.card_expense.set_value(fmt(expense_total))
        self.card_profit.set_value(fmt(profit))
        self.card_trips.set_value(str(trips))

        self._refresh_movements()
        self._refresh_trucks()
        self._refresh_dashboard()

    def _refresh_movements(self):
        sorted_records = sorted(self.records, key=lambda r: r["fecha"], reverse=True)
        self.mov_table.setRowCount(len(sorted_records))

        for row, r in enumerate(sorted_records):
            is_income = r["type"] == "income"
            tipo_text = "Ingreso Viaje" if is_income else r.get("expType", "Gasto")
            amount_text = ("+  " if is_income else "-  ") + fmt(r["amount"])
            color = QColor(GREEN) if is_income else QColor(RED)

            items = [
                QTableWidgetItem(r["fecha"]),
                QTableWidgetItem(r["camion"]),
                QTableWidgetItem(tipo_text),
                QTableWidgetItem(r.get("desc", "")),
                QTableWidgetItem(amount_text),
            ]
            for col, item in enumerate(items):
                item.setForeground(QBrush(color if col == 4 else QColor(TEXT)))
                self.mov_table.setItem(row, col, item)

            del_btn = QPushButton("✕ Eliminar")
            del_btn.setObjectName("btnDelete")
            rec_id = r["id"]
            del_btn.clicked.connect(lambda _, rid=rec_id: self.delete_record(rid))
            self.mov_table.setCellWidget(row, 5, del_btn)
            self.mov_table.setRowHeight(row, 36)

    def _build_camiones(self):
        camiones = {}
        for r in self.records:
            k = r["camion"]
            if k not in camiones:
                camiones[k] = {"income": 0, "expense": 0, "trips": 0,
                                "combustible": 0, "sueldos": 0, "peajes": 0}
            if r["type"] == "income":
                camiones[k]["income"] += r["amount"]
                camiones[k]["trips"] += 1
            else:
                camiones[k]["expense"] += r["amount"]
                t = r.get("expType", "")
                if "Combustible" in t:      camiones[k]["combustible"] += r["amount"]
                elif "Sueldo" in t:         camiones[k]["sueldos"] += r["amount"]
                else:                       camiones[k]["peajes"] += r["amount"]
        return camiones

    def _refresh_trucks(self):
        # Limpiar layout
        while self.trucks_layout.count():
            item = self.trucks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        camiones = self._build_camiones()
        if not camiones:
            lbl = QLabel("Registra viajes o gastos para ver el estado de tus unidades.")
            lbl.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
            self.trucks_layout.addWidget(lbl, 0, 0)
            return

        for idx, (name, c) in enumerate(camiones.items()):
            net = c["income"] - c["expense"]
            card = QFrame()
            card.setFixedWidth(260)
            card.setStyleSheet(f"""
                QFrame {{ background: {SURFACE2}; border: 1px solid {BORDER}; border-radius: 10px; }}
                QFrame:hover {{ border: 1px solid {ACCENT}; }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(6)

            name_lbl = QLabel(f"🚌  {name}")
            name_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 16px; font-weight: bold; border: none;")
            trips_lbl = QLabel(f"{c['trips']} viaje(s) registrado(s)")
            trips_lbl.setStyleSheet(f"color: {MUTED}; font-size: 11px; border: none;")
            cl.addWidget(name_lbl)
            cl.addWidget(trips_lbl)

            sep = QFrame(); sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
            cl.addWidget(sep)

            def stat_row(label, value, color):
                row = QHBoxLayout()
                l = QLabel(label); l.setStyleSheet(f"color: {MUTED}; font-size: 12px; border: none;")
                v = QLabel(value); v.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold; border: none;")
                row.addWidget(l); row.addStretch(); row.addWidget(v)
                return row

            cl.addLayout(stat_row("Ingresos",     fmt(c["income"]),      GREEN))
            cl.addLayout(stat_row("⛽ Combustible", fmt(c["combustible"]), RED))
            cl.addLayout(stat_row("👷 Sueldos",    fmt(c["sueldos"]),    RED))
            cl.addLayout(stat_row("🛣️ Peajes",     fmt(c["peajes"]),     RED))

            sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
            sep2.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
            cl.addWidget(sep2)

            net_color = GREEN if net >= 0 else RED
            cl.addLayout(stat_row("💰 Ganancia Neta", fmt(net), net_color))

            row_idx = idx // 3
            col_idx = idx % 3
            self.trucks_layout.addWidget(card, row_idx, col_idx)

    def _refresh_dashboard(self):
        while self.dashboard_layout.count():
            item = self.dashboard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        camiones = self._build_camiones()
        if not camiones:
            lbl = QLabel("Agrega viajes y gastos para ver estadísticas por camión.")
            lbl.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
            self.dashboard_layout.addWidget(lbl)
            return

        max_income = max((c["income"] for c in camiones.values()), default=1) or 1

        for name, c in camiones.items():
            frame = QFrame()
            frame.setStyleSheet(f"background: {SURFACE2}; border-radius: 8px; border: 1px solid {BORDER};")
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(14, 12, 14, 12)

            title = QLabel(f"🚌  {name}   —   {c['trips']} viaje(s)")
            title.setStyleSheet(f"color: {TEXT}; font-weight: bold; font-size: 13px; border: none;")
            fl.addWidget(title)

            def bar_row(label, value, max_val, color):
                row_w = QWidget()
                row_w.setStyleSheet("background: transparent; border: none;")
                rlay = QHBoxLayout(row_w)
                rlay.setContentsMargins(0, 0, 0, 0); rlay.setSpacing(10)

                lbl_w = QLabel(label)
                lbl_w.setFixedWidth(90)
                lbl_w.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                lbl_w.setStyleSheet(f"color: {MUTED}; font-size: 11px; border: none;")

                pct = max(int((value / max_val) * 100), 3) if max_val > 0 else 3
                bar_container = QFrame()
                bar_container.setFixedHeight(22)
                bar_container.setStyleSheet(f"background: {SURFACE}; border-radius: 4px; border: none;")
                bar_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                bar = QFrame(bar_container)
                bar.setGeometry(0, 0, 0, 22)
                bar.setStyleSheet(f"background: {color}; border-radius: 4px;")
                # Usamos un QLabel con geometría para simular la barra
                bar_lbl = QLabel(fmt(value), bar_container)
                bar_lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                bar_lbl.setStyleSheet(f"color: #000; font-size: 11px; font-weight: bold; padding-left: 6px; border: none;")
                bar_lbl.setGeometry(0, 0, max(120, int(pct * 4)), 22)
                bar_lbl.setStyleSheet(
                    f"background: {color}; color: #000; font-size: 11px; font-weight: bold;"
                    f"padding-left: 6px; border-radius: 4px; border: none;"
                )

                rlay.addWidget(lbl_w)
                rlay.addWidget(bar_container)
                return row_w

            fl.addWidget(bar_row("Ingresos", c["income"], max_income, GREEN))
            fl.addWidget(bar_row("Gastos",   c["expense"], max_income, RED))
            self.dashboard_layout.addWidget(frame)


# ──────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())