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

import qgis
from PyQt4.QtCore import (QSettings, 
                          QTranslator, 
                          qVersion, 
                          QCoreApplication,
                          Qt)
from PyQt4.QtGui import (QAction, 
                         QIcon,
                         QDockWidget)
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from search_plus_dockwidget import SearchPlusDockWidget
import os.path

class SearchPlus:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
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
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&searchplus')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SearchPlus')
        self.toolbar.setObjectName(u'SearchPlus')
        
        # create dockwidget when initialization is completed
        #self.iface.initializationCompleted.connect(self.run)
    
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


    def run(self):
        """Run method activated byt the toolbar action button"""
        if self.dlg and not self.dlg.isVisible():
            # check if the plugin is active
            if not self.pluginName in qgis.utils.active_plugins:
                return
            
            self.dlg.show()
        
        randomList = ['Merilyn Mcdonald', 'Angeline Langston', 'Rogelio Locust', 'Laura Henshaw', 'Tawanna Criado', 'Tamiko Hysmith', 'Chrissy Mazer', 'Maryland Blassingame', 'Johnette Mera', 'Vasiliki Launer', 'Trevor Cottle', 'Vicenta Gaut', 'Lavona Uhrig', 'Colton Lyke', 'Russel Hoye', 'Mayola Fullilove', 'Caterina Gabriele', 'Sanford Delisa', 'Coy Kinsley', 'Diedre Luciano', 'Gaynelle Debusk', 'Sonja Kwok', 'Andre Gastelum', 'Marline Murdock', 'Janet Alcala', 'Suzanna Schrum', 'Gwen Rickett', 'Marquitta Mesa', 'Juliann Herrin', 'Marvella Houchins', 'Josef Dragon', 'Lyn Ammon', 'Angelique Kish', 'Jinny Fils', 'Clelia Walder', 'Tandra Sanks', 'Easter Depaul', 'Jann Custard', 'Mariel Partain', 'Noelia Sypher', 'Araceli Burrell', 'Tristan Siller', 'Kathi Guillotte', 'Milan Sadowski', 'Nancey Patnaude', 'Tameka Castille', 'Raleigh Seel', 'Marcy Chico', 'Jovita Johansson', 'Alissa Oathout']
        self.dlg.cboStreet.addItems(randomList)
        