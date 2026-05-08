# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoCAT_Analysis
                                 A QGIS plugin
 A QGIS plugin to perform EOO (Extent of Occurrence) and AOO (Area of
 Occupancy) analysis based on GeoCAT principles.
                              -------------------
        begin                : 2024-09-29
        copyright            : (C) 2024 by Diego Sousa Campos
        email                : camposds1@yahoo.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import csv

from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    QCoreApplication,
    Qt,
    QVariant,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import (
    Qgis,
    QgsProject,
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)

# Initialize Qt resources from file resources.py
from .resources import *  # noqa: F401,F403

# Import the code for the DockWidget
from .geocat_analysis_dockwidget import GeoCAT_AnalysisDockWidget


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# IUCN guidelines recommend an equal-area projection for EOO/AOO computation.
# EPSG:6933 = WGS 84 / NSIDC EASE-Grid 2.0 Global (Cylindrical Equal Area, m).
METRIC_CRS_AUTHID = 'EPSG:6933'
DEFAULT_AOO_CELL_M = 2000  # 2 km × 2 km, IUCN standard cell size for AOO
OCCURRENCE_LAYER_NAME = 'Species Occurrences'


class GeoCAT_Analysis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale_value = QSettings().value('locale/userLocale')
        locale = locale_value[0:2] if locale_value else 'en'
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoCAT_Analysis_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoCATer')
        self.toolbar = self.iface.addToolBar(u'GeoCATer')
        self.toolbar.setObjectName(u'GeoCATer')

        self.pluginIsActive = False
        self.dockwidget = None

    # ------------------------------------------------------------------
    # Qt helpers
    # ------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Translation helper."""
        return QCoreApplication.translate('GeoCAT_Analysis', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        """Create a QAction, wire its callback and register it."""
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    # ------------------------------------------------------------------
    # QGIS plugin lifecycle
    # ------------------------------------------------------------------
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/geocat_analysis/icon.png'

        # Single entry point that opens the panel where the user finds all
        # the controls (CSV import, EOO, AOO).
        self.add_action(
            icon_path,
            text=self.tr(u'Open GeoCATer panel'),
            callback=self.run,
            parent=self.iface.mainWindow(),
            status_tip=self.tr(
                u'Open the GeoCATer panel with EOO/AOO tools.'),
        )

    def onClosePlugin(self):
        """Called when the user closes the dockwidget.

        We keep the dockwidget object and its signal connections alive so
        that reopening it via the toolbar action is fast; we just flag the
        plugin as inactive.
        """
        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Close + drop the dockwidget so signal connections don't dangle.
        if self.dockwidget is not None:
            try:
                self.iface.removeDockWidget(self.dockwidget)
                self.dockwidget.deleteLater()
            except RuntimeError:
                pass
            self.dockwidget = None

        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&GeoCATer'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """Open (or focus) the GeoCATer dockwidget."""
        if self.dockwidget is None:
            self.dockwidget = GeoCAT_AnalysisDockWidget()
            # Connect signals only once, when the dock is first created.
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.dockwidget.importCsvRequested.connect(
                self._on_import_csv_signal)
            self.dockwidget.eooRequested.connect(self.calculate_eoo)
            self.dockwidget.aooRequested.connect(self._on_aoo_signal)
            self.iface.addDockWidget(
                Qt.RightDockWidgetArea, self.dockwidget)

        self.pluginIsActive = True
        self.dockwidget.show()
        self.dockwidget.raise_()

    def _on_import_csv_signal(self, path):
        """Receive the importCsvRequested signal from the dockwidget."""
        if path:
            try:
                self.load_csv_data(path)
            except Exception as exc:  # pragma: no cover
                self._msg(f'Erro ao importar CSV: {exc}', Qgis.Critical)
        else:
            # Empty path → fall back to the system file dialog.
            self.import_csv()

    def _on_aoo_signal(self, cell_size_m):
        """Receive the aooRequested signal from the dockwidget."""
        try:
            cell = int(cell_size_m)
        except (TypeError, ValueError):
            cell = DEFAULT_AOO_CELL_M
        if cell <= 0:
            cell = DEFAULT_AOO_CELL_M
        self.calculate_aoo(cell_size_m=cell)

    # ==================================================================
    # CSV import
    # ==================================================================
    def import_csv(self):
        """Open a file dialog and load a CSV of species occurrences."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            self.tr(u'Open CSV File'),
            '',
            'CSV Files (*.csv);;All files (*.*)',
        )
        if not file_path:
            return
        try:
            self.load_csv_data(file_path)
        except Exception as exc:  # pragma: no cover - surfaced to user
            self._msg(f'Erro ao importar CSV: {exc}', Qgis.Critical)

    def load_csv_data(self, file_path):
        """Parse the CSV and create the occurrence layer."""
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            sample = csvfile.read(4096)
            csvfile.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            except csv.Error:
                dialect = csv.excel
            reader = csv.DictReader(csvfile, dialect=dialect)
            rows = [r for r in reader]

        if not rows:
            self._msg(u'CSV vazio ou inválido.', Qgis.Warning)
            return

        # Be tolerant of header variants (PT/EN, X/Y, etc.).
        header_map = {h.lower().strip(): h for h in rows[0].keys() if h}
        lat_key = self._first_key(header_map, ('latitude', 'lat', 'y'))
        lon_key = self._first_key(
            header_map, ('longitude', 'long', 'lon', 'lng', 'x'))
        sp_key = self._first_key(header_map, (
            'especie', 'espécie', 'species', 'scientific_name',
            'scientificname', 'taxon'))

        if lat_key is None or lon_key is None:
            self._msg(
                u'CSV deve conter colunas de Latitude e Longitude '
                u'(aceita também X/Y).',
                Qgis.Critical)
            return

        self._create_occurrence_layer(rows, lat_key, lon_key, sp_key)

    @staticmethod
    def _first_key(header_map, candidates):
        for c in candidates:
            if c in header_map:
                return header_map[c]
        return None

    def _create_occurrence_layer(self, data, lat_key, lon_key, sp_key):
        """Build the in-memory point layer with the imported records."""
        # Replace any previous occurrence layer of the same name
        for lyr in QgsProject.instance().mapLayersByName(OCCURRENCE_LAYER_NAME):
            QgsProject.instance().removeMapLayer(lyr.id())

        layer = QgsVectorLayer(
            'Point?crs=EPSG:4326', OCCURRENCE_LAYER_NAME, 'memory')
        provider = layer.dataProvider()
        provider.addAttributes(
            [QgsField('Scientific_Name', QVariant.String)])
        layer.updateFields()

        added = 0
        skipped = 0
        for row in data:
            lat_raw = row.get(lat_key)
            lon_raw = row.get(lon_key)
            if not lat_raw or not lon_raw:
                skipped += 1
                continue
            try:
                latitude = float(str(lat_raw).strip().replace(',', '.'))
                longitude = float(str(lon_raw).strip().replace(',', '.'))
            except ValueError:
                skipped += 1
                continue

            sp_name = row.get(sp_key, '') if sp_key else ''
            feature = QgsFeature(layer.fields())
            feature.setGeometry(
                QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude)))
            feature.setAttribute('Scientific_Name', sp_name or '')
            provider.addFeature(feature)
            added += 1

        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

        if added == 0:
            self._msg(
                u'Nenhuma ocorrência válida foi importada.', Qgis.Warning)
            return

        msg = f'{added} ocorrência(s) importada(s).'
        if skipped:
            msg += f' {skipped} linha(s) ignorada(s).'
        self._msg(msg, Qgis.Success)

    # ==================================================================
    # Shared helpers
    # ==================================================================
    def _get_occurrence_layer(self):
        layers = QgsProject.instance().mapLayersByName(OCCURRENCE_LAYER_NAME)
        if not layers:
            self._msg(
                f"Camada '{OCCURRENCE_LAYER_NAME}' não encontrada. "
                u'Importe um CSV primeiro.',
                Qgis.Warning)
            return None
        return layers[0]

    @staticmethod
    def _metric_transform(source_crs):
        target_crs = QgsCoordinateReferenceSystem(METRIC_CRS_AUTHID)
        return QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance())

    def _msg(self, text, level=Qgis.Info):
        self.iface.messageBar().pushMessage('GeoCATer', text, level=level)
        # Echo the message to the dockwidget log, when it exists.
        if self.dockwidget is not None:
            try:
                self.dockwidget.append_message(text)
            except RuntimeError:
                # Underlying C++ widget already destroyed
                self.dockwidget = None

    # ==================================================================
    # EOO  —  Extent of Occurrence (Convex Hull)
    # ==================================================================
    def calculate_eoo(self):
        """Compute EOO via Convex Hull and report the area in km²."""
        layer = self._get_occurrence_layer()
        if layer is None:
            return

        geometries = [
            QgsGeometry(f.geometry()) for f in layer.getFeatures()
            if f.hasGeometry() and not f.geometry().isEmpty()
        ]
        if len(geometries) < 3:
            self._msg(
                u'EOO requer ao menos 3 pontos não colineares.',
                Qgis.Warning)
            return

        union_geom = QgsGeometry.unaryUnion(geometries)
        convex_hull = union_geom.convexHull()
        if convex_hull is None or convex_hull.isEmpty():
            self._msg(u'Não foi possível gerar o Convex Hull.', Qgis.Warning)
            return

        # Area in km², computed in equal-area metric CRS
        metric_geom = QgsGeometry(convex_hull)
        metric_geom.transform(self._metric_transform(layer.crs()))
        area_km2 = metric_geom.area() / 1_000_000.0

        eoo_layer = QgsVectorLayer(
            'Polygon?crs=EPSG:4326', 'EOO Polygon', 'memory')
        provider = eoo_layer.dataProvider()
        provider.addAttributes([QgsField('Area_km2', QVariant.Double)])
        eoo_layer.updateFields()
        feat = QgsFeature(eoo_layer.fields())
        feat.setGeometry(convex_hull)
        feat.setAttribute('Area_km2', area_km2)
        provider.addFeature(feat)
        eoo_layer.updateExtents()
        QgsProject.instance().addMapLayer(eoo_layer)

        self._msg(f'EOO calculado: {area_km2:,.2f} km².', Qgis.Success)

    # ==================================================================
    # AOO  —  Area of Occupancy (2 km grid in metric CRS)
    # ==================================================================
    def calculate_aoo(self, cell_size_m=DEFAULT_AOO_CELL_M):
        """Compute AOO on a 2 km grid (default) using an equal-area CRS."""
        layer = self._get_occurrence_layer()
        if layer is None:
            return

        # Reproject all points to metric equal-area CRS
        transform = self._metric_transform(layer.crs())
        metric_points = []
        for feat in layer.getFeatures():
            if not feat.hasGeometry() or feat.geometry().isEmpty():
                continue
            g = QgsGeometry(feat.geometry())
            g.transform(transform)
            pt = g.asPoint()
            metric_points.append((pt.x(), pt.y()))

        if not metric_points:
            self._msg(u'Sem pontos válidos para calcular AOO.', Qgis.Warning)
            return

        # Snap each point to its grid cell and count distinct cells
        occupied = set()
        for x, y in metric_points:
            i = int(x // cell_size_m)
            j = int(y // cell_size_m)
            occupied.add((i, j))

        # Build the grid layer in the metric CRS (preserves cell shape)
        aoo_layer = QgsVectorLayer(
            f'Polygon?crs={METRIC_CRS_AUTHID}', 'AOO Grid', 'memory')
        provider = aoo_layer.dataProvider()
        provider.addAttributes([
            QgsField('cell_i', QVariant.Int),
            QgsField('cell_j', QVariant.Int),
            QgsField('Area_km2', QVariant.Double),
        ])
        aoo_layer.updateFields()

        cell_km2 = (cell_size_m / 1000.0) ** 2
        for (i, j) in occupied:
            x0 = i * cell_size_m
            y0 = j * cell_size_m
            rect = QgsRectangle(
                x0, y0, x0 + cell_size_m, y0 + cell_size_m)
            feat = QgsFeature(aoo_layer.fields())
            feat.setGeometry(QgsGeometry.fromRect(rect))
            feat.setAttribute('cell_i', i)
            feat.setAttribute('cell_j', j)
            feat.setAttribute('Area_km2', cell_km2)
            provider.addFeature(feat)

        aoo_layer.updateExtents()
        QgsProject.instance().addMapLayer(aoo_layer)

        aoo_km2 = len(occupied) * cell_km2
        self._msg(
            f'AOO calculado: {len(occupied)} célula(s) de '
            f'{cell_size_m} m = {aoo_km2:,.2f} km².',
            Qgis.Success)
