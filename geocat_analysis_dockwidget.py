# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoCAT_AnalysisDockWidget
                                 A QGIS plugin
 Painel lateral do GeoCATer com importação de CSV e cálculos EOO/AOO.
                              -------------------
        begin                : 2024-09-29
        copyright            : (C) 2024 by Diego Sousa Campos
        email                : camposds1@yahoo.com.br
 ***************************************************************************/
"""
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal, Qt, QDateTime


class GeoCAT_AnalysisDockWidget(QtWidgets.QDockWidget):
    """Painel principal do plugin GeoCATer.

    A UI é construída totalmente em Python para evitar dependência de um
    arquivo .ui externo. O dockwidget apenas expõe sinais; quem executa
    a lógica é a classe principal do plugin (GeoCAT_Analysis).
    """

    # --- Sinais públicos ------------------------------------------------
    closingPlugin = pyqtSignal()
    importCsvRequested = pyqtSignal(str)   # caminho do CSV (pode ser '')
    eooRequested = pyqtSignal()
    aooRequested = pyqtSignal(int)         # tamanho da célula em metros

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('GeoCAT_AnalysisDockWidget')
        self.setWindowTitle('GeoCATer')
        self._build_ui()
        self._wire_signals()

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        container = QtWidgets.QWidget(self)
        self.setWidget(container)
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        layout.addWidget(self._build_data_group())
        layout.addWidget(self._build_eoo_group())
        layout.addWidget(self._build_aoo_group())
        layout.addWidget(self._build_result_group(), 1)

    def _build_data_group(self):
        group = QtWidgets.QGroupBox('1. Dados de ocorrência')
        v = QtWidgets.QVBoxLayout(group)

        info = QtWidgets.QLabel(
            'Importe um CSV com colunas Latitude/Longitude '
            '(aceita também X/Y, vírgula decimal, ; ou , como separador).')
        info.setWordWrap(True)
        info.setStyleSheet('color: gray;')
        v.addWidget(info)

        row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText('Selecione um arquivo CSV…')
        self.browse_btn = QtWidgets.QToolButton()
        self.browse_btn.setText('…')
        self.browse_btn.setToolTip('Procurar CSV')
        row.addWidget(self.path_edit, 1)
        row.addWidget(self.browse_btn)
        v.addLayout(row)

        self.import_btn = QtWidgets.QPushButton('Importar CSV')
        v.addWidget(self.import_btn)
        return group

    def _build_eoo_group(self):
        group = QtWidgets.QGroupBox('2. EOO – Extent of Occurrence')
        v = QtWidgets.QVBoxLayout(group)

        info = QtWidgets.QLabel(
            'Convex Hull em torno das ocorrências. '
            'Área reportada em km² (EPSG:6933, equal-area, padrão IUCN).')
        info.setWordWrap(True)
        info.setStyleSheet('color: gray;')
        v.addWidget(info)

        self.eoo_btn = QtWidgets.QPushButton('Calcular EOO')
        v.addWidget(self.eoo_btn)
        return group

    def _build_aoo_group(self):
        group = QtWidgets.QGroupBox('3. AOO – Area of Occupancy')
        v = QtWidgets.QVBoxLayout(group)

        info = QtWidgets.QLabel(
            'Conta células ocupadas em uma grade métrica. '
            'O padrão IUCN é 2000 m (2 km × 2 km).')
        info.setWordWrap(True)
        info.setStyleSheet('color: gray;')
        v.addWidget(info)

        cell_row = QtWidgets.QHBoxLayout()
        cell_row.addWidget(QtWidgets.QLabel('Tamanho da célula (m):'))
        self.cell_spin = QtWidgets.QSpinBox()
        self.cell_spin.setRange(100, 100_000)
        self.cell_spin.setSingleStep(100)
        self.cell_spin.setValue(2000)
        self.cell_spin.setSuffix(' m')
        cell_row.addWidget(self.cell_spin)
        cell_row.addStretch(1)
        v.addLayout(cell_row)

        self.aoo_btn = QtWidgets.QPushButton('Calcular AOO')
        v.addWidget(self.aoo_btn)
        return group

    def _build_result_group(self):
        group = QtWidgets.QGroupBox('Resultados')
        v = QtWidgets.QVBoxLayout(group)
        self.result_view = QtWidgets.QPlainTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText('Os resultados aparecerão aqui…')
        v.addWidget(self.result_view)

        self.clear_btn = QtWidgets.QPushButton('Limpar log')
        self.clear_btn.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        v.addWidget(self.clear_btn, 0, Qt.AlignRight)
        return group

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------
    def _wire_signals(self):
        self.browse_btn.clicked.connect(self._browse_csv)
        self.import_btn.clicked.connect(
            lambda: self.importCsvRequested.emit(self.path_edit.text().strip()))
        self.eoo_btn.clicked.connect(self.eooRequested.emit)
        self.aoo_btn.clicked.connect(
            lambda: self.aooRequested.emit(int(self.cell_spin.value())))
        self.clear_btn.clicked.connect(self.result_view.clear)

    def _browse_csv(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open CSV File',
            self.path_edit.text() or '',
            'CSV Files (*.csv);;All files (*.*)')
        if file_path:
            self.path_edit.setText(file_path)

    # ------------------------------------------------------------------
    # API pública para o plugin
    # ------------------------------------------------------------------
    def append_message(self, text):
        """Acrescenta uma mensagem no log do painel, com timestamp."""
        ts = QDateTime.currentDateTime().toString('HH:mm:ss')
        self.result_view.appendPlainText(f'[{ts}] {text}')

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
