# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : June 2015
        copyright            : (C) 2015 by Luigi Pirelli
        email                : luipir@gmail.com
 ***************************************************************************/
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# 2To3 python compatibility
from __future__ import unicode_literals, division, print_function

import operator
import os.path


from qgis.utils import active_plugins
from qgis.gui import QgsMessageBar, QgsMapCanvasAnnotationItem 
from qgis.core import QgsCredentials, QgsDataSourceUri, QgsGeometry, QgsPointXY, QgsMessageLog, QgsExpression, QgsFeatureRequest, QgsVectorLayer, QgsFeature, QgsField, QgsProject, QgsLayerTreeLayer, QgsTextAnnotation, NULL, Qgis
from qgis.PyQt.QtCore import QObject, QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSignal
from qgis.PyQt.QtGui import  QIcon, QTextDocument, QIntValidator
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMessageBox

from .resources_rc import *
#from utils import *  # @UnusedWildImport
from .search_plus_dockwidget import SearchPlusDockWidget


class SearchPlus(QObject):
    ''' QGIS Plugin Implementation. '''

    connectionEstablished = pyqtSignal()

    def __init__(self, iface):
        ''' Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        '''          
        super(SearchPlus, self).__init__()
        
        # Save reference to the QGIS interface
        self.iface = iface
        
        # initialize plugin directory and locale
        self.plugin_dir = os.path.dirname(__file__)
        self.pluginName = os.path.basename(self.plugin_dir)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'SearchPlus_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)         
        
        # load local settings of the plugin
        self.app_name = "searchplus"        
        self.setting_file = os.path.join(self.plugin_dir, 'config', self.app_name+'.config')
        if not os.path.isfile(self.setting_file):
            message = "Config file not found at: "+self.setting_file            
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)            
            return False        
        self.settings = QSettings(self.setting_file, QSettings.IniFormat)
        self.stylesFolder = self.plugin_dir+"/styles/" 
            
        # load plugin settings
        self.loadPluginSettings()      
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(self.app_name)
        self.annotations = []
        self.streetLayer = None   
        self.placenameLayer = None    
        self.cadastreLayer = None  
        self.equipmentLayer = None  
        self.portalLayer = None           
        self.placenameMemLayer = None    
        self.cadastreMemLayer = None  
        self.equipmentMemLayer = None  
        self.portalMemLayer = None    
        self.coreLayer = None
        self.plotLayer = None
        self.plotMemLayer = None
        self.scape=False

        self.iface.initializationCompleted.connect(self.populateGui) 
    
    
    def loadPluginSettings(self):
        ''' Load plugin settings
        '''           
        # get layers configuration to populate the GUI
        self.STREET_LAYER = ''+self.settings.value('layers/STREET_LAYER', '')+''
        self.STREET_FIELD_CODE = self.settings.value('layers/STREET_FIELD_CODE', '')
        self.STREET_FIELD_NAME = self.settings.value('layers/STREET_FIELD_NAME', '')
        
        self.PORTAL_LAYER = ''+self.settings.value('layers/PORTAL_LAYER', '')+''
        self.PORTAL_FIELD_CODE = self.settings.value('layers/PORTAL_FIELD_CODE', '')
        self.PORTAL_FIELD_NUMBER = self.settings.value('layers/PORTAL_FIELD_NUMBER', '')
        
        self.PLACENAME_LAYER = ''+self.settings.value('layers/PLACENAME_LAYER', '')+''
        self.PLACENAME_FIELD = self.settings.value('layers/PLACENAME_FIELD', '')
        
        self.EQUIPMENT_SCHEMA = ''+self.settings.value('layers/EQUIPMENT_SCHEMA', '')+''
        self.EQUIPMENT_LAYER = ''+self.settings.value('layers/EQUIPMENT_LAYER', '')+''
        self.EQUIPMENT_FIELD_TYPE = self.settings.value('layers/EQUIPMENT_FIELD_TYPE', '')
        self.EQUIPMENT_FIELD_NAME = self.settings.value('layers/EQUIPMENT_FIELD_NAME', '')
        
        self.CADASTRE_LAYER = ''+self.settings.value('layers/CADASTRE_LAYER', '')+''
        self.CADASTRE_FIELD_CODE = self.settings.value('layers/CADASTRE_FIELD_CODE', '')

        self.CORE_LAYER = ''+self.settings.value('layers/CORE_LAYER', '')+''
        self.CORE_FIELD_CODE = self.settings.value('layers/CORE_FIELD_CODE', '')
        self.CORE_FIELD_NAME = self.settings.value('layers/CORE_FIELD_NAME', '')

        self.PLOT_LAYER = ''+self.settings.value('layers/PLOT_LAYER', '')+''
        self.PLOT_FIELD_CODE = self.settings.value('layers/PLOT_FIELD_CODE', '')
        self.PLOT_FIELD_ADDRESS = self.settings.value('layers/PLOT_FIELD_ADDRESS', '')

        self.QML_PORTAL = self.settings.value('layers/QML_PORTAL', 'portal.qml')
        self.QML_TOPONYM = self.settings.value('layers/QML_TOPONYM', 'toponym.qml')
        self.QML_EQUIPMENT = self.settings.value('layers/QML_EQUIPMENT', 'equipment.qml')
        self.QML_CADASTRE = self.settings.value('layers/QML_CADASTRE', 'cadastre.qml')
        self.QML_PLOT = self.settings.value('layers/QML_PLOT', 'plot.qml')
        
        # get initial Scale
        self.defaultZoomScale = self.settings.value('status/defaultZoomScale', 2500)
        
        # Create own plugin toolbar or not?
        self.pluginToolbarEnabled = bool(int(self.settings.value('status/pluginToolbarEnabled', 1)))
        if self.pluginToolbarEnabled:
            self.toolbar = self.iface.addToolBar(u'SearchPlus')
            self.toolbar.setObjectName(u'SearchPlus')        
        
        # Enable action Remove Memory Layers?
        self.removeMemoryLayersAction = bool(int(self.settings.value('status/removeMemoryLayersAction', 1)))


    def initialization(self):
    
        self.getLayers()
        self.getFullExtent() 
            
            
    def getLayers(self): 
                               
        # Iterate over all layers to get the ones set in config file  
        layers = self.iface.mapCanvas().layers()
        
        if layers ==[]: #show info message no layers 
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr("No hay capas cargadas.\n Revisa la configuracion (o carga un proyecto)\n y recarga el plugin."))
            self.scape=True
            return
        for cur_layer in layers:
            uri = cur_layer.dataProvider().dataSourceUri().lower()
            pos_ini = uri.find('table=')
            pos_fi = uri.find('" ')
            if pos_ini != -1 and pos_fi != -1:
                uri_table = uri[pos_ini + 6:pos_fi + 1]
            else:
                # Using current layer_name on TOC
                uri_table = cur_layer.name()

            if self.STREET_LAYER in uri_table:
                self.streetLayer = cur_layer


            if self.PLACENAME_LAYER in uri_table:
                self.placenameLayer = cur_layer
            if self.CADASTRE_LAYER in uri_table:
                self.cadastreLayer = cur_layer


            if self.EQUIPMENT_LAYER in uri_table:
                self.equipmentLayer = cur_layer
            if self.PORTAL_LAYER in uri_table:
                self.portalLayer = cur_layer


            if self.CORE_LAYER in uri_table:
                self.coreLayer = cur_layer
            if self.PLOT_LAYER in uri_table:
                self.plotLayer = cur_layer

        
    def getFullExtent(self):
               
        # get full extent
        canvas = self.iface.mapCanvas()
        self.xMax = int(canvas.fullExtent().xMaximum())
        self.xMin = int(canvas.fullExtent().xMinimum())
        self.yMax = int(canvas.fullExtent().yMaximum())
        self.yMin = int(canvas.fullExtent().yMinimum())
        try:
            self.xOffset = (self.xMax - self.xMin) * 0.10
            self.yOffset = (self.yMax - self.yMin) * 0.10   
        except:
            self.xOffset = 1000
            self.yOffset = 1000      
            
        # set validators for UTM text edit
        self.xMinVal = int(self.xMin - self.xOffset)
        self.xMaxVal = int(self.xMax + self.xOffset)
        self.yMinVal = int(self.yMin - self.yOffset)
        self.yMaxVal = int(self.yMax + self.yOffset)  
        try:
            self.intValidatorX = QIntValidator(self.xMinVal, self.xMaxVal, self.dlg) # assumed that E and W are inserted as - +
            self.intValidatorY = QIntValidator(self.yMinVal, self.yMaxVal, self.dlg) # assumed that S and N are inserted as - +
            self.dlg.txtCoordX.setValidator(self.intValidatorX)
            self.dlg.txtCoordY.setValidator(self.intValidatorY)            
        except:
            pass  
            
            
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        ''' Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        '''
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SearchPlus', message)


    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        ''' Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        '''

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
        else:
            self.iface.addToolBarIcon(action)            

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

        
    def initGui(self):
        ''' Create the menu entries and toolbar icons inside the QGIS GUI
        '''

        icon_path = ':/plugins/SearchPlus/icons/icon_searchplus.png'
        self.add_action(icon_path, self.tr('Advanced searcher'), self.run, parent=self.iface.mainWindow(), add_to_toolbar=self.pluginToolbarEnabled)

        if self.removeMemoryLayersAction:
            icon_path = ':/plugins/SearchPlus/icons/remove_mem_layers.png'
            self.add_action(icon_path, self.tr('Remove memory layers'), self.removeMemoryLayers, parent=self.iface.mainWindow(), add_to_toolbar=self.pluginToolbarEnabled)

        # Create the dock widget and dock it but hide it waiting the ond of qgis loading
        self.dlg = SearchPlusDockWidget(self.iface.mainWindow())
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea, self.dlg)
        self.dlg.setVisible(False)
        
        # add first level combo box events
        self.dlg.cboStreet.currentIndexChanged.connect(self.getStreetNumbers)
        self.dlg.cboStreet.currentIndexChanged.connect(self.zoomOnStreet)
        self.dlg.cboType.currentIndexChanged.connect(self.getEquipments)
        self.dlg.cboUrbanCore.currentIndexChanged.connect(self.getPlots)
        self.dlg.cboUrbanCore.currentIndexChanged.connect(self.zoomOnCore)
        
        # add events to show information o the canvas
        self.dlg.cboNumber.currentIndexChanged.connect(self.displayStreetData)
        self.dlg.cboTopo.currentIndexChanged.connect(self.displayToponym)
        self.dlg.cboEquipment.currentIndexChanged.connect(self.displayEquipment)
        self.dlg.cboCadastre.currentIndexChanged.connect(self.displayCadastre)
        self.dlg.cboPlot.currentIndexChanged.connect(self.displayPlot)
        self.dlg.txtCoordX.returnPressed.connect(self.displayUTM)
        self.dlg.txtCoordY.returnPressed.connect(self.displayUTM)
        
    
    def unload(self):
        ''' Removes the plugin menu item and icon from QGIS GUI
        '''
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(self.app_name), action)
            self.iface.removeToolBarIcon(action)
        
        if self.pluginToolbarEnabled:
            del self.toolbar
        
        if self.dlg:
            self.dlg.deleteLater()
            del self.dlg
            
                 
    def populateGui(self):
        ''' Populate the interface with values get from layers
        '''       
        # Get layers and full extent
        self.initialization() 

        # tab Plots
        self.populatePlots()      
                               
        # tab Cadastre
        self.populateCadastre()
        
        # tab Equipments
        self.populateEquipments()
        
        # tab Toponyms
        self.populateToponyms()    
                
        # tab Streets      
        self.populateStreets()

            
    def populateCadastre(self):

        # Check if we have this search option available
        if self.cadastreLayer is None:
            for x in range(0,  self.dlg.searchPlusTabMain.count()):
                if  self.dlg.searchPlusTabMain.widget(x).objectName() == "searchPlusCadastreTab":
                    self.dlg.searchPlusTabMain.removeTab(x)
                    break
            return      

        layer = self.cadastreLayer
        records = [(-1, '', '')]
        idx_id = layer.fields().indexFromName('id')
        idx_field_code = layer.fields().indexFromName(self.CADASTRE_FIELD_CODE)       
        for feature in layer.getFeatures():
            geom = feature.geometry()
            attrs = feature.attributes()
            field_id = attrs[idx_id]    
            field_code = attrs[idx_field_code]  
            if not (type(field_code) is NULL):
                elem = [field_id, field_code, geom.asWkt()]
                records.append(elem)
        
        # Fill cadastre combo
        self.dlg.cboCadastre.blockSignals(True)
        self.dlg.cboCadastre.clear()
        records_sorted = sorted(records, key = operator.itemgetter(1)) 
        error=[]
        for i in range(len(records_sorted)):
            record = records_sorted[i]
            if record[1] != NULL and type(record[1])==str:
                self.dlg.cboCadastre.addItem(record[1], record)
            else:
                error.append(record[0])
                
        if error!=[]:
            message='List of ids belonging to layer \'{}\' that can not be shown:\n'.format(self.cadastreLayer.name())
            message+='{}'.format(error)
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))

        self.dlg.cboCadastre.blockSignals(False)      
    
   
    def populateEquipments(self):

        # Check if we have this search option available
        if self.equipmentLayer is None:
            for x in range(0,  self.dlg.searchPlusTabMain.count()):
                if  self.dlg.searchPlusTabMain.widget(x).objectName() == "searchPlusEquipmentsTab":
                    self.dlg.searchPlusTabMain.removeTab(x)
                    break
            return      
        
        # Get layer features        
        layer = self.equipmentLayer
        records = ['']
        idx_field_type = layer.fields().indexFromName(self.EQUIPMENT_FIELD_TYPE)  
        for feature in layer.getFeatures():
            attrs = feature.attributes()
            field_type = attrs[idx_field_type] 
            if not (type(idx_field_type) is NULL):
                elem = field_type
                records.append(elem)
                
        # Fill equipment type combo (remove duplicates)km
        records_set = list(set(records))
        records_sorted = records_set
        self.dlg.cboType.blockSignals(True)
        self.dlg.cboType.clear()
#         records_sorted = sorted(records_set, key = operator.itemgetter(1)) 
        error=[]           
        for i in range(len(records_sorted)):
            record = records_sorted[i]
            if record != NULL and type(record)==str:
                self.dlg.cboType.addItem(record, record)
            else:
                error.append(record[0])
        
        if error!=[]:
            message='List of ids belonging to layer \'{}\' that can not be shown:\n'.format(self.equipmentLayer.name())
            message+='{}'.format(error)
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))        
        
        self.dlg.cboType.blockSignals(False)                                
                
        
    def populateToponyms(self):

        # Check if we have this search option available
        if self.placenameLayer is None:
            for x in range(0, self.dlg.searchPlusTabMain.count()):
                if self.dlg.searchPlusTabMain.widget(x).objectName() == "searchPlusToponimsTab":
                    self.dlg.searchPlusTabMain.removeTab(x)
                    break
            return      
        
        # Get layer features        
        layer = self.placenameLayer
        records = [(-1, '', '')]
        idx_id = layer.fields().indexFromName('id')
        idx_field = layer.fields().indexFromName(self.PLACENAME_FIELD)       
        for feature in layer.getFeatures():
            geom = feature.geometry()
            attrs = feature.attributes()
            field_id = attrs[idx_id]    
            field = attrs[idx_field]  
            if not (type(field) is NULL):
                elem = [field_id, field, geom.asWkt()]
                records.append(elem)

        # Fill toponym combo
        self.dlg.cboTopo.blockSignals(True)
        self.dlg.cboTopo.clear()
        records_sorted = sorted(records, key = operator.itemgetter(1)) 
        error=[]           
        for i in range(len(records_sorted)):
            record = records_sorted[i]
            if record[1] != NULL and type(record[1])==str:
                self.dlg.cboTopo.addItem(record[1], record)
            else:
                error.append(record[0])
                
        if error!=[]:
            message='List of ids belonging to layer \'{}\' that can not be shown:\n'.format(self.placenameLayer.name())
            message+='{}'.format(error)
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))                 
                
        self.dlg.cboTopo.blockSignals(False)   
                        
                    
    def populateStreets(self):
        # Check if we have this search option available
        if self.streetLayer is None or self.portalLayer is None:
            for x in range(0, self.dlg.searchPlusTabMain.count()):
                if self.dlg.searchPlusTabMain.widget(x).objectName() == "searchPlusStreetsTab":
                    self.dlg.searchPlusTabMain.removeTab(x)
                    break
            return

        # Get layer features
        layer = self.streetLayer
        records = [(-1, '', '', '')]
        idx_id = layer.fields().indexFromName('id')
        idx_field_name = layer.fields().indexFromName(self.STREET_FIELD_NAME)
        idx_field_code = layer.fields().indexFromName(self.STREET_FIELD_CODE)    
        for feature in layer.getFeatures():
            geom = feature.geometry()
            attrs = feature.attributes()
            field_id = attrs[idx_id]    
            field_name = attrs[idx_field_name]    
            field_code = attrs[idx_field_code]
            # if (not (type(field_code) is NULL)) and geom is not None and (not (type(field_id) is NULL)) and (not (type(field_name) is NULL)):
            if field_id not in ['NULL', None] and field_name not in ['NULL', None] and field_code not in ['NULL', None] and geom not in ['NULL', None]:
                elem = [field_id, field_name, field_code, geom.asWkt()]
                records.append(elem)

        # Fill street combo
        self.dlg.cboStreet.blockSignals(True)
        self.dlg.cboStreet.clear()
        records_sorted = sorted(records, key = operator.itemgetter(1))
        error=[]
        for i in range(len(records_sorted)):
            record = records_sorted[i]
            if record[1] != NULL and type(record[1])==str:
                self.dlg.cboStreet.addItem(record[1], record)
            else:
                error.append(record[0])
        
        if error!=[]:
            message='List of ids belonging to layer \'{}\' that can not be shown:\n'.format(self.streetLayer.name())
            message+='{}'.format(error)
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))
                
        self.dlg.cboStreet.blockSignals(False)    

    def populatePlots(self):
        if self.plotLayer is None or self.coreLayer is None:
            for x in range(0,  self.dlg.searchPlusTabMain.count()):
                if  self.dlg.searchPlusTabMain.widget(x).objectName() == "searchPlusPlotsTab":
                    self.dlg.searchPlusTabMain.removeTab(x)
                    break
            return

        # Get layer features
        layer = self.coreLayer
        records = [(-1, '', '', '')]
        idx_id = layer.fields().indexFromName('id')
        idx_field_name = layer.fields().indexFromName(self.CORE_FIELD_NAME)
        idx_field_code = layer.fields().indexFromName(self.CORE_FIELD_CODE)  
        
        for feature in layer.getFeatures():
            geom = feature.geometry()
            attrs = feature.attributes()
            field_id = attrs[idx_id]    
            field_name = attrs[idx_field_name]    
            field_code = attrs[idx_field_code]  
            if not (type(field_code) is NULL) and geom is not None:
                elem = [field_id, field_name, field_code, geom.asWkt()]
                records.append(elem)

        # Fill core combo
        self.dlg.cboUrbanCore.blockSignals(True)
        self.dlg.cboUrbanCore.clear()
        #records_sorted = sorted(records, key=operator.itemgetter(1))
        error=[]
        for record in records:#_sorted:
            if record[1] != NULL and type(record[1])==str:
                self.dlg.cboUrbanCore.addItem(record[1], record)
            else:
                error.append(record[0])
                
        if error!=[]:
            message='List of ids belonging to layer \'{}\' that can not be shown:\n'.format(self.coreLayer.name())
            message+='{}'.format(error)
            QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))
            
        self.dlg.cboUrbanCore.blockSignals(False)

    def zoomOnStreet(self):
        ''' Zoom on the street with the prefined scale
        '''
        # get selected street
        selected = self.dlg.cboStreet.currentText()
        if selected == '':
            return
        
        # get code
        data = self.dlg.cboStreet.itemData(self.dlg.cboStreet.currentIndex())
        wkt = data[3] # to know the index see the query that populate the combo
        geom = QgsGeometry.fromWkt(wkt)
        if not geom:
            message = self.tr('Can not correctly get geometry')
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return
        
        # zoom on it's centroid
        centroid = geom.centroid()
        self.iface.mapCanvas().setCenter(centroid.asPoint())
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
    
    def zoomOnCore(self):
         # get selected core
        selected = self.dlg.cboUrbanCore.currentText()
        if selected == '':
            return
        
        # get code
        data = self.dlg.cboUrbanCore.itemData(self.dlg.cboUrbanCore.currentIndex())
        wkt = data[3] # to know the index see the query that populate the combo
        geom = QgsGeometry.fromWkt(wkt)
        if not geom:
            message = self.tr('Can not correctly get geometry')
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return
        
        # zoom on it
        self.iface.mapCanvas().setExtent(geom.boundingBox())
        self.iface.mapCanvas().refresh()


    def getStreetNumbers(self):
        ''' Populate civic numbers depending on selected street. 
            Available civic numbers are linked with self.STREET_FIELD_CODE column code in self.PORTAL_LAYER
            and self.STREET_LAYER
        '''       
        # get selected street
        selected = self.dlg.cboStreet.currentText()
        if selected == '':
            return
        
        # get street code
        sel_street = self.dlg.cboStreet.itemData(self.dlg.cboStreet.currentIndex())
        
        code = sel_street[2] # to know the index see the query that populate the combo 
        records = [[-1, '']]
        
        # Set filter expression
        layer = self.portalLayer       
        idx_field_code = layer.fields().indexFromName(self.PORTAL_FIELD_CODE)            
        idx_field_number = layer.fields().indexFromName(self.PORTAL_FIELD_NUMBER)   
        aux = self.PORTAL_FIELD_CODE+"='"+str(code)+"'" 
        
        # Check filter and existence of fields
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 10)        
            return               
        if idx_field_code == -1:    
            message = self.tr("Field '{}' not found in layer '{}'. Open '{}' and check parameter '{}'".
                format(self.PORTAL_FIELD_CODE, layer.name(), self.setting_file, 'PORTAL_FIELD_CODE'))            
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)        
            return      
        if idx_field_number == -1:    
            message = self.tr("Field '{}' not found in layer '{}'. Open '{}' and check parameter '{}'".
                format(self.PORTAL_FIELD_NUMBER, layer.name(), self.setting_file, 'PORTAL_FIELD_NUMBER'))            
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)        
            return      
            
        # Get a featureIterator from an expression:
        # Get features from the iterator and do something
        chk_number=[] #list to avoid duplicate numbers in the same code
        error=[] #list to store the duplicate elements
        it = layer.getFeatures(QgsFeatureRequest(expr))
        for feature in it: 
            attrs = feature.attributes() 
            field_number = attrs[idx_field_number]    
            if (not type(field_number) is NULL) and (field_number not in chk_number):
                chk_number.append(field_number)
                elem = [code, field_number]
                records.append(elem)
            else:
                error.append(field_number)
        
        chk_number=[]
        if error !=[]:
            message = self.tr('Layer {} has duplicated elements in the field {}\n'.format(layer.name(),self.PORTAL_FIELD_NUMBER))
            message+=self.tr('List of duplicates {}:{}'.format(self.PORTAL_FIELD_NUMBER,error))          
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)
            error=[]            
            return
                  
        # Fill numbers combo
        records_sorted = sorted(records, key = operator.itemgetter(1))           
        self.dlg.cboNumber.blockSignals(True)
        self.dlg.cboNumber.clear()
        for record in records_sorted:
            self.dlg.cboNumber.addItem(record[1], record)
        self.dlg.cboNumber.blockSignals(False) 


    def getPlots(self):
        # get selected urban core
        selected = self.dlg.cboUrbanCore.currentText()
        if selected == '':
            return
        
        # get urban core code
        sel_core = self.dlg.cboUrbanCore.itemData(self.dlg.cboUrbanCore.currentIndex())
        code = sel_core[2] # to know the index see the query that populate the combo
        records = [[-1, '']]
        
        # Set filter expression
        layer = self.plotLayer 
        idx_field_code = layer.fields().indexFromName(self.PLOT_FIELD_CODE)            
        idx_field_number = layer.fields().indexFromName(self.PLOT_FIELD_ADDRESS)   
        idx_field_id = layer.fields().indexFromName('id')
        aux = self.PLOT_FIELD_CODE+'=\''+str(code)+'\'' 
        
        # Check filter and existence of fields
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 10)        
            return               
        if idx_field_code == -1:    
            message = self.tr("Field '{}' not found in layer '{}'. Open '{}' and check parameter '{}'".
                format(self.PLOT_FIELD_CODE, layer.name(), self.setting_file, 'PLOT_FIELD_CODE'))            
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)        
            return   
        if idx_field_number == -1:    
            message = self.tr("Field '{}' not found in layer '{}'. Open '{}' and check parameter '{}'".
                format(self.PLOT_FIELD_ADDRESS, layer.name(), self.setting_file, 'PLOT_FIELD_ADDRESS'))            
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)        
            return      
    
        # Get a featureIterator from an expression:
        # Get features from the iterator and do something
        chk_number=[] #list to avoid duplicate numbers in the same code
        error=[] #list to store the duplicate elements
        it = layer.getFeatures(QgsFeatureRequest().setFilterExpression(aux))
        for feature in it: 
            attrs = feature.attributes() 
            plot_id = attrs[idx_field_id]
            field_number = attrs[idx_field_code]    
            if (not (type(field_number) is NULL)) and field_number not in chk_number:
                chk_number.append(field_number)
                elem = [plot_id, plot_id]
                records.append(elem)
            else:
                error.append(field_number)
        
        chk_number=[]
        if error !=[]:
            message = self.tr('Layer {} has duplicated elements in the field {}\n'.format(layer.name(),self.PORTAL_FIELD_ADDRESS))
            message+=self.tr('List of duplicates {}:{}'.format(self.PLOT_FIELD_ADDRESS,error))          
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)
            error=[]            
            return
        
        # Fill numbers combo
        records_sorted = sorted(records)#, key = operator.itemgetter(2))          
        self.dlg.cboPlot.blockSignals(True)
        self.dlg.cboPlot.clear()
        for record in records_sorted:
            self.dlg.cboPlot.addItem(str(record[1]), record)
        self.dlg.cboPlot.blockSignals(False) 
    
    
    def getEquipments(self):
        ''' Populate equipments combo depending on selected type. 
            Available equipments EQUIPMENT_FIELD_NAME belonging to the same EQUIPMENT_FIELD_TYPE of 
            the same layer EQUIPMENT_LAYER
        '''      
        # get selected street
        selectedCode = self.dlg.cboType.currentText()
        if selectedCode == '':
            return
        
        # get street code
        sel_type = self.dlg.cboType.itemData(self.dlg.cboType.currentIndex())
        records = [[-1, '']]
                
        # Set filter expression
        layer = self.equipmentLayer
        idx_id = layer.fields().indexFromName('id')            
        idx_field_name = layer.fields().indexFromName(self.EQUIPMENT_FIELD_NAME)   
        aux = self.EQUIPMENT_FIELD_TYPE+"='"+u'{}'.format(sel_type)+"'" 
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)        
            return               
        
        # Get a featureIterator from an expression:
        # Get features from the iterator and do something
        chk_number=[] #list to avoid duplicate numbers in the same code
        error=[] #list to store the duplicate elements
        it = layer.getFeatures(QgsFeatureRequest(expr))
        for feature in it: 
            attrs = feature.attributes()
            field_id = attrs[idx_id]    
            field_name = attrs[idx_field_name]    
            if (not type(field_name) is NULL) and field_name not in chk_number:
                chk_number.append(field_name)
                elem = [field_id, field_name]
                records.append(elem)
            else: 
                error.append(field_name)
         
        chk_number=[]
        if error !=[]:
            message = self.tr('Layer {} has duplicated elements in the field {}\n'.format(layer.name(),self.EQUIPMENT_FIELD_NAME))
            message+=self.tr('List of duplicates {}:{}'.format(self.EQUIPMENT_FIELD_NAME,error))          
            self.iface.messageBar().pushMessage(message, '', Qgis.Warning, 10)
            error=[]            
            return    
         
        # Fill numbers combo
        records_sorted = sorted(records, key = operator.itemgetter(1))           
        self.dlg.cboEquipment.blockSignals(True)
        self.dlg.cboEquipment.clear()
        for record in records_sorted:
            self.dlg.cboEquipment.addItem(record[1], record)
        self.dlg.cboEquipment.blockSignals(False)  

    
    def validateX(self):   
        X = int(self.dlg.txtCoordX.text())
        if X > self.xMinVal and X < self.xMaxVal:
            return True
        else:
            return False
            
            
    def validateY(self):       
        Y = int(self.dlg.txtCoordY.text())
        if Y > self.yMinVal and Y < self.yMaxVal:
            return True
        else:
            return False      
            
    
    def manageMemLayer(self, layer):
        ''' Delete previous features from all memory layers 
            Make layer not visible '''
        if layer is not None:
            layer.startEditing()        
            it = layer.getFeatures()
            ids = [i.id() for i in it]
            layer.dataProvider().deleteFeatures(ids)    
            layer.commitChanges()  
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)
            #self.iface.legendInterface().setLayerVisible(layer, False)


    def manageMemLayers(self):
        ''' Delete previous features from all memory layers 
        '''        
        self.manageMemLayer(self.placenameMemLayer)
        self.manageMemLayer(self.cadastreMemLayer)
        self.manageMemLayer(self.equipmentMemLayer)
        self.manageMemLayer(self.portalMemLayer)
        self.manageMemLayer(self.plotMemLayer)
      
    
    def copySelected(self, layer, mem_layer, geom_type):
        ''' Copy from selected layer to memory layer 
        '''
        self.manageMemLayers()
        
        # Create memory layer if not already set
        if mem_layer is None: 
            uri = geom_type+"?crs=epsg:25831" 
            mem_layer = QgsVectorLayer(uri, "selected_"+layer.name(), "memory")                     
         
            # Copy attributes from main layer to memory layer
            attrib_names = layer.dataProvider().fields()
            names_list = attrib_names.toList()
            newattributeList = []
            for attrib in names_list:
                aux = mem_layer.fields().indexFromName(attrib.name())
                if aux == -1:
                    newattributeList.append(QgsField(attrib.name(), attrib.type()))
            mem_layer.dataProvider().addAttributes(newattributeList)
            mem_layer.updateFields()
            
            # Insert layer in the top of the TOC           
            root = QgsProject.instance().layerTreeRoot()           
            QgsProject.instance().addMapLayer(mem_layer, False)
            node_layer = QgsLayerTreeLayer(mem_layer)
            root.insertChildNode(0, node_layer)                 
     
        # Prepare memory layer for editing
        mem_layer.startEditing()
        
        # Iterate over selected features   
        cfeatures = []
        for sel_feature in layer.selectedFeatures():
            attributes = []
            attributes.extend(sel_feature.attributes())
            cfeature = QgsFeature()    
            cfeature.setGeometry(sel_feature.geometry())
            cfeature.setAttributes(attributes)
            cfeatures.append(cfeature)
                     
        # Add features, commit changes and refresh canvas
        mem_layer.dataProvider().addFeatures(cfeatures)             
        mem_layer.commitChanges()
        self.iface.mapCanvas().refresh() 
        self.iface.mapCanvas().zoomToSelected(layer)
        
        # Make sure layer is always visible 
        QgsProject.instance().layerTreeRoot().findLayer(mem_layer.id()).setItemVisibilityChecked(True)
        #self.iface.legendInterface().setLayerVisible(mem_layer, True)
                    
        return mem_layer
        
        
    def loadStyle(self, layer, qml):
    
        path_qml = self.stylesFolder+qml      
        if os.path.exists(path_qml): 
            layer.loadNamedStyle(path_qml)          

        
    def displayUTM(self):
        ''' Show UTM location on the canvas when set it in the relative tab
        '''   
        #Obtain the geometry of the Terme_municipal layer
        select=QgsProject.instance().mapLayersByName('Terme municipal')
        if select!=[]:
            layer=select[0].getFeatures() #acces to the layer
                 
        X = self.dlg.txtCoordX.text()
        if not X:
            message = "Coordinate X not specified"
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return
        Y = self.dlg.txtCoordY.text()  
        if not Y:
            message = "Coordinate Y not specified"
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)           
            return
        
        # check if coordinates are within the interval
        valX = self.validateX()
        if not valX:
            message = "Coordinate X is out of the valid interval. It should be between "+str(self.xMinVal)+" and "+str(self.xMaxVal)            
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return
        valY = self.validateY()
        if not valY:
            message = "Coordinate Y is out of the valid interval, It should be between "+str(self.yMinVal)+" and "+str(self.yMaxVal)
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return            
            
        geom = QgsGeometry.fromPointXY(QgsPointXY(float(X), float(Y)))
        
        #check if the geometry is inside the Terme municipal poligon
        if select!=[]:
            inters=False
            for feature in layer:
                if feature.geometry().buffer(50000,-1).intersects(geom): #añadido un buffer de 50Km 
                    inters=True
                    break
            
            if inters:
                message = 'X: {}\nY: {}'.format(X,Y)
            else:
                message='Points X:{} and Y:{} outside the Terme municipal (and the 50 Km buffer).'.format(X,Y)
                QMessageBox.information(self.iface.mainWindow(), self.tr("Searchplus-Informacion"),
                                    self.tr(message))                
                return
        else:
            message = 'X: {}\nY: {}'.format(X,Y)
        # display annotation with message at a specified position
        self.displayAnnotation(geom, message)
    
    
    def displayCadastre(self):
        ''' Show cadastre data on the canvas when selected it in the relative tab 
        '''       
        cadastre = self.dlg.cboCadastre.currentText()
        if cadastre == '':
            return      
        
        # get selected item
        elem = self.dlg.cboCadastre.itemData(self.dlg.cboCadastre.currentIndex())
        if not elem:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(cadastre))
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return

        # select this feature in order to copy to memory layer
        aux = self.CADASTRE_FIELD_CODE + "='" + str(elem[0]) + "'"

        expr = QgsExpression(aux)
        if expr.hasParserError():
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)
            return

        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained             
        it = self.cadastreLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.cadastreLayer.selectByIds(ids)    
                
        # Copy selected features to memory layer          
        self.cadastreMemLayer = self.copySelected(self.cadastreLayer, self.cadastreMemLayer, "Polygon")         
         
        # Load style
        self.loadStyle(self.cadastreMemLayer, self.QML_CADASTRE)  

        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))             
        
         
    def displayEquipment(self):
        ''' Show equipment data on the canvas when selected it in the relative tab 
        '''
        typ = self.dlg.cboType.currentText()
        equipment = self.dlg.cboEquipment.currentText()
        if typ == '' or equipment == '':
            return
        
        # get selected item
        elem = self.dlg.cboEquipment.itemData(self.dlg.cboEquipment.currentIndex())
        if not elem:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(equipment))
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return

        # select this feature in order to copy to memory layer        
        aux = "id = "+str(elem[0]) 
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained      
        it = self.equipmentLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.equipmentLayer.selectByIds(ids)

        # Copy selected features to memory layer          
        self.equipmentMemLayer = self.copySelected(self.equipmentLayer, self.equipmentMemLayer, "Point")       

        # Zoom to point layer
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        
        # Load style
        self.loadStyle(self.equipmentMemLayer, self.QML_EQUIPMENT)          

        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))        
         
         
    def displayToponym(self):
        ''' Show toponym data on the canvas when selected it in the relative tab 
        '''
        toponym = self.dlg.cboTopo.currentText()   
        if toponym == '':
            return
        
        # get selected toponym
        elem = self.dlg.cboTopo.itemData(self.dlg.cboTopo.currentIndex())
        if not elem:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(toponym))
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return

        # select this feature in order to copy to memory layer        
        aux = "id = "+str(elem[0])         
        expr = QgsExpression(aux)            
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained       
        it = self.placenameLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.placenameLayer.selectByIds(ids)    
                
        # Copy selected features to memory layer
        self.placenameMemLayer = self.copySelected(self.placenameLayer, self.placenameMemLayer, "Linestring")
        
        # Load style
        self.loadStyle(self.placenameMemLayer, self.QML_TOPONYM)        
        
        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))        
         
         
    def displayStreetData(self):
        ''' Show street data on the canvas when selected street and number in street tab 
        '''          
        street = self.dlg.cboStreet.currentText()
        civic = self.dlg.cboNumber.currentText()
        if street == '' or civic == '':
            return  
                
        # get selected portal
        elem = self.dlg.cboNumber.itemData(self.dlg.cboNumber.currentIndex())
        if not elem:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(civic))
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return
        
        # select this feature in order to copy to memory layer        
        aux = self.PORTAL_FIELD_CODE+"='"+str(elem[0])+"' AND "+self.PORTAL_FIELD_NUMBER+"='"+str(elem[1])+"'"
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select featureswith the ids obtained             
        it = self.portalLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.portalLayer.selectByIds(ids)
        
        # Copy selected features to memory layer     
        self.portalMemLayer = self.copySelected(self.portalLayer, self.portalMemLayer, "Point")       

        # Zoom to point layer
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        
        # Load style
        self.loadStyle(self.portalMemLayer, self.QML_PORTAL)         
    

    def displayPlot(self):
        equipment = self.dlg.cboEquipment.currentText()
        core = self.dlg.cboUrbanCore.currentText()
        plot = self.dlg.cboPlot.currentText()
        if core == '' or plot == '':
            return
        
        # get selected item
        elem = self.dlg.cboPlot.itemData(self.dlg.cboPlot.currentIndex())
        if not elem:
            # that means that user has edited manually the combo but the element
            # does not correspond to any combo element
            message = self.tr('Element {} does not exist'.format(equipment))
            self.iface.messageBar().pushMessage(message, Qgis.Warning, 5)
            return

        # select this feature in order to copy to memory layer        
        aux = "id = "+str(elem[0])
        expr = QgsExpression(aux)     
        if expr.hasParserError():   
            self.iface.messageBar().pushMessage(expr.parserErrorString() + ": " + aux, self.app_name, Qgis.Warning, 5)        
            return    
        
        # Get a featureIterator from an expression
        # Build a list of feature Ids from the previous result       
        # Select features with the ids obtained             
        it = self.plotLayer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.plotLayer.selectByIds(ids)
        
        # Copy selected features to memory layer          
        self.plotMemLayer = self.copySelected(self.plotLayer, self.plotMemLayer, "Polygon")
        
        # Load style
        self.loadStyle(self.plotMemLayer, self.QML_PLOT)          

        # Zoom to scale
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale)) 
        
    def displayAnnotation(self, geom, message):
        ''' Display a specific message in the centroid of a specific geometry 
        '''
        centroid = geom.centroid()
        
        # clean previous annotations:
        for annotation in self.annotations:
            try:
                scene = annotation.scene()
                if scene:
                    scene.removeItem(annotation)
            except:
                # annotation can be erased by QGIS interface
                pass
        self.annotations = []
        
        # build annotation
        textDoc = QTextDocument(message)
        item = QgsTextAnnotation.create()
        item.setMapPosition(centroid.asPoint())
        item.setFrameSize(textDoc.size())
        item.setDocument(textDoc)
        item.setVisible(True)
        QgsMapCanvasAnnotationItem(item,self.iface.mapCanvas())


        # add to annotations
        self.annotations.append(item)
        
        # center in the centroid
        self.iface.mapCanvas().setCenter(centroid.asPoint())
        self.iface.mapCanvas().zoomScale(float(self.defaultZoomScale))
        self.iface.mapCanvas().refresh()
    
    
    def run(self):
        ''' Run method activated byt the toolbar action button 
        '''    
        
        if self.dlg and not self.dlg.isVisible():
            # check if the plugin is active
            if not self.pluginName in active_plugins:
                return
            self.populateGui()  

            if self.scape==1: #no layers no show
                self.dlg.close()
                return
            
            self.dlg.show()

    
    def removeMemoryLayers(self):
        ''' Iterate over all layers and remove memory ones 
        '''         
        layers = self.iface.mapCanvas().layers()
        for cur_layer in layers:     
            layer_name = cur_layer.name().lower()         
            if "selected_" in layer_name:
                QgsProject.instance().removeMapLayer(cur_layer.id())   
                                             
