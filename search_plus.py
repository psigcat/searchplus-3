# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SearchPlus - A QGIS plugin Toponomastic searcher
                              -------------------
        begin                : 2015-06-19
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli
        email                : luipir@gmail.com
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
# 2To3 python compatibility
from __future__ import print_function
from __future__ import unicode_literals

from qgis.utils import active_plugins
from qgis.gui import (QgsMessageBar)
from qgis.core import (QgsCredentials,
                       QgsDataSourceURI)
from PyQt4.QtCore import (QObject,
                          QSettings, 
                          QTranslator, 
                          qVersion, 
                          QCoreApplication,
                          Qt,
                          pyqtSignal)
from PyQt4.QtGui import (QAction, 
                         QIcon,
                         QDockWidget)

# PostGIS import
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from search_plus_dockwidget import SearchPlusDockWidget
import os.path

class SearchPlus(QObject):
    """QGIS Plugin Implementation."""

    connectionEstablished = pyqtSignal()

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super(SearchPlus, self).__init__()
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.pluginName = os.path.basename(self.plugin_dir)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SearchPlus_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        # load local settings of the plugin
        settingFile = os.path.join(self.plugin_dir, 'config', 'config.properties')
        self.settings = QSettings(settingFile, QSettings.IniFormat)
        self.settings.setIniCodec("UTF-8")
        
        # load plugin settings
        self.loadPluginSettings()
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&searchplus')
        self.connection = None
        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SearchPlus')
        self.toolbar.setObjectName(u'SearchPlus')
        
        # establish connection when all is completly running 
        self.iface.initializationCompleted.connect(self.initConnection)
        
        # when connection is established, then set all GUI values
        self.connectionEstablished.connect(self.populateGui)
    
    def loadPluginSettings(self):
        ''' Load plugin settings
        '''
        # get all db configuration table/columns to load to populate the GUI
        self.STREET_SCHEMA= self.settings.value('db/STREET_SCHEMA', '')
        self.STREET_LAYER= self.settings.value('db/STREET_LAYER', '')
        self.STREET_FIELD_CODE= self.settings.value('db/STREET_FIELD_CODE', '')
        self.STREET_FIELD_NAME= self.settings.value('db/STREET_FIELD_NAME', '')
        
        self.PORTAL_SCHEMA= self.settings.value('db/PORTAL_SCHEMA', '')
        self.PORTAL_LAYER= self.settings.value('db/PORTAL_LAYER', '')
        self.PORTAL_FIELD_CODE= self.settings.value('db/PORTAL_FIELD_CODE', '')
        self.PORTAL_FIELD_NUMBER= self.settings.value('db/PORTAL_FIELD_NUMBER', '')
        
        self.PLACENAME_SCHEMA= self.settings.value('db/PLACENAME_SCHEMA', '')
        self.PLACENAME_LAYER= self.settings.value('db/PLACENAME_LAYER', '')
        self.PLACENAME_FIELD= self.settings.value('db/PLACENAME_FIELD', '')
        
        self.EQUIPMENT_SCHEMA= self.settings.value('db/EQUIPMENT_SCHEMA', '')
        self.EQUIPMENT_LAYER= self.settings.value('db/EQUIPMENT_LAYER', '')
        self.EQUIPMENT_FIELD_TYPE= self.settings.value('db/EQUIPMENT_FIELD_TYPE', '')
        self.EQUIPMENT_FIELD_NAME= self.settings.value('db/EQUIPMENT_FIELD_NAME', '')
        
        self.CADASTRE_SCHEMA= self.settings.value('db/CADASTRE_SCHEMA', '')
        self.CADASTRE_LAYER= self.settings.value('db/CADASTRE_LAYER', '')
        self.CADASTRE_FIELD_CODE= self.settings.value('db/CADASTRE_FIELD_CODE', '')
        
    
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SearchPlus', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

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
        """

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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SearchPlus/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Cercador toponomàstica'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Create the dock widget and dock it but hide it waiting the ond of qgis loading
        self.dlg = SearchPlusDockWidget(self.iface.mainWindow())
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea, self.dlg)
        self.dlg.setVisible(False)
        
        # add dlg event managenment
        self.dlg.cboStreet.currentIndexChanged.connect(self.resetNumbers)
        self.dlg.cboType.currentIndexChanged.connect(self.resetEquipments)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&searchplus'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
        if self.dlg:
            self.dlg.deleteLater()
            del self.dlg

    
    def initConnection(self):
        ''' Establish connection with the default credentials
        Connection name is get from QGIS connection. Will be used the connection
        configured int he plugin settings
        '''
        # eventually close opened connections
        try:
            self.connection.close()
        except:
            pass
        
        # get default configured connection name
        connName = self.settings.value('db/CONNECTION_NAME', '')
        if not connName:
            confFileName = self.setting.fileName()
            message = self.tr('No default connection is configured in {}'.format(confFileName))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        # look for connection data in QGIS configration
        # get connection data
        qgisSettings = QSettings()
        
        root = "/PostgreSQL/connections/"+connName+"/"
        DATABASE_HOST = qgisSettings.value(root+"host", '')
        DATABASE_NAME = qgisSettings.value(root+"database", '')
        DATABASE_PORT = qgisSettings.value(root+"port", '')
        DATABASE_USER = qgisSettings.value(root+"username", '')
        DATABASE_PWD = qgisSettings.value(root+"password", '')
        
        (ok, DATABASE_USER, DATABASE_PWD) = QgsCredentials.instance().get( "", DATABASE_USER, DATABASE_PWD );
        self.uri = QgsDataSourceURI()
        self.uri.setConnection(DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PWD)
        
        # connect
        try:
            self.connection = psycopg2.connect( self.uri.connectionInfo().encode('utf-8') )
        except Exception as ex:
            message = self.tr('Can not connect to connection named: {} for reason: {} '.format(connName, str(ex)))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        # emit signal that connection is established
        self.connectionEstablished.emit()
    
    def populateGui(self):
        ''' Populate the interface with values get from DB
        '''
        if not self.connection:
            return
        
        # get cursor on wich execute query
        cursor = self.connection.cursor()
        
        # tab Carrerer
        sqlquery = 'SELECT "{}" FROM "{}"."{}" ORDER BY "{}"'.format(self.STREET_FIELD_NAME, self.STREET_SCHEMA, self.STREET_LAYER, self.STREET_FIELD_NAME)
        cursor.execute(sqlquery)
        records = ['']
        records.extend([x[0] for x in cursor.fetchall() if x[0]]) # remove None values
        self.dlg.cboStreet.blockSignals(True)
        self.dlg.cboStreet.clear()
        self.dlg.cboStreet.addItems(records)
        self.dlg.cboStreet.blockSignals(False)
        
        # tab Toponyms
        sqlquery = 'SELECT "{}" FROM "{}"."{}" ORDER BY "{}"'.format(self.PLACENAME_FIELD, self.PLACENAME_SCHEMA, self.PLACENAME_LAYER, self.PLACENAME_FIELD)
        cursor.execute(sqlquery)
        records = ['']
        records.extend([x[0] for x in cursor.fetchall() if x[0]]) # remove None values
        self.dlg.cboTopo.blockSignals(True)
        self.dlg.cboTopo.clear()
        self.dlg.cboTopo.addItems(records)
        self.dlg.cboTopo.blockSignals(False)
        
        # tab equipments
        sqlquery = 'SELECT "{}" FROM "{}"."{}" GROUP BY "{}" ORDER BY "{}"'.format(self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER, self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_FIELD_TYPE)
        cursor.execute(sqlquery)
        records = ['']
        records.extend([x[0] for x in cursor.fetchall() if x[0]]) # remove None values
        self.dlg.cboType.blockSignals(True)
        self.dlg.cboType.clear()
        self.dlg.cboType.addItems(records)
        self.dlg.cboType.blockSignals(False)
    
    def resetNumbers(self):
        ''' Populate civic numbers depending on selected street. 
        Available civic numbers are linked with self.STREET_FIELD_CODE column code in self.PORTAL_LAYER
        and self.STREET_LAYER
        '''
        if not self.connection:
            return
        
        # get selected street
        selected = self.dlg.cboStreet.currentText()
        if selected == '':
            return
        
        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # get self.STREET_FIELD_CODE related to the current selected street
        sqlquery = 'SELECT "{}" FROM "{}"."{}" WHERE "{}" = %s; '.format(self.STREET_FIELD_CODE, self.STREET_SCHEMA, self.STREET_LAYER, self.STREET_FIELD_NAME)
        params = [selected]
        cursor.execute(sqlquery, params)
        records = [x[0] for x in cursor.fetchall() if x[0]] # remove None values
        if len(records) != 1:
            message = self.tr('There are {} streets with name "{}"'.format(len(records), selected))
            self.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        code = records[0]
        
        # now get the list of indexes belonging to the current code
        sqlquery = 'SELECT "{}" FROM "{}"."{}" WHERE "{}" = %s ORDER BY "{}"; '.format(self.PORTAL_FIELD_NUMBER, self.STREET_SCHEMA, self.PORTAL_LAYER, self.PORTAL_FIELD_CODE, self.PORTAL_FIELD_NUMBER)
        params = [code]
        cursor.execute(sqlquery, params)
        records = ['']
        records.extend( [x[0] for x in cursor.fetchall() if x[0]] ) # remove None values
        self.dlg.cboNumber.blockSignals(True)
        self.dlg.cboNumber.clear()
        self.dlg.cboNumber.addItems(records)
        self.dlg.cboNumber.blockSignals(False)        
    
    def resetEquipments(self):
        ''' Populate equipments combo depending on selected type. 
        Available equipments EQUIPMENT_FIELD_NAME belonging to the same EQUIPMENT_FIELD_TYPE of 
        the same layer EQUIPMENT_LAYER
        '''
        if not self.connection:
            return
        
        # get selected street
        selectedCode = self.dlg.cboType.currentText()
        if selectedCode == '':
            return
        
        # get cursor on wich execute query
        cursor = self.connection.cursor()

        # now get the list of names belonging to the current type
        sqlquery = 'SELECT "{}" FROM "{}"."{}" WHERE "{}" = %s ORDER BY "{}"; '.format(self.EQUIPMENT_FIELD_NAME, self.EQUIPMENT_SCHEMA, self.EQUIPMENT_LAYER, self.EQUIPMENT_FIELD_TYPE, self.EQUIPMENT_FIELD_NAME)
        params = [selectedCode]
        cursor.execute(sqlquery, params)
        records = ['']
        records.extend( [x[0] for x in cursor.fetchall() if x[0]] ) # remove None values
        self.dlg.cboEquipment.blockSignals(True)
        self.dlg.cboEquipment.clear()
        self.dlg.cboEquipment.addItems(records)
        self.dlg.cboEquipment.blockSignals(False) 
    
    def run(self):
        """Run method activated byt the toolbar action button"""
        if self.dlg and not self.dlg.isVisible():
            # check if the plugin is active
            if not self.pluginName in active_plugins:
                return
            
            self.dlg.show()
        
        # if not, setup connection
        if not self.connection:
            self.initConnection()
        
        #randomList = ['Merilyn Mcdonald', 'Angeline Langston', 'Rogelio Locust', 'Laura Henshaw', 'Tawanna Criado', 'Tamiko Hysmith', 'Chrissy Mazer', 'Maryland Blassingame', 'Johnette Mera', 'Vasiliki Launer', 'Trevor Cottle', 'Vicenta Gaut', 'Lavona Uhrig', 'Colton Lyke', 'Russel Hoye', 'Mayola Fullilove', 'Caterina Gabriele', 'Sanford Delisa', 'Coy Kinsley', 'Diedre Luciano', 'Gaynelle Debusk', 'Sonja Kwok', 'Andre Gastelum', 'Marline Murdock', 'Janet Alcala', 'Suzanna Schrum', 'Gwen Rickett', 'Marquitta Mesa', 'Juliann Herrin', 'Marvella Houchins', 'Josef Dragon', 'Lyn Ammon', 'Angelique Kish', 'Jinny Fils', 'Clelia Walder', 'Tandra Sanks', 'Easter Depaul', 'Jann Custard', 'Mariel Partain', 'Noelia Sypher', 'Araceli Burrell', 'Tristan Siller', 'Kathi Guillotte', 'Milan Sadowski', 'Nancey Patnaude', 'Tameka Castille', 'Raleigh Seel', 'Marcy Chico', 'Jovita Johansson', 'Alissa Oathout']
        #self.dlg.cboStreet.addItems(randomList)
        