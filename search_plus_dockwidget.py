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

from PyQt4 import QtGui
from ui.search_plus_dialog_base_ui import Ui_searchPlusDockWidget

# cannot apply dynaic loading because cannot promote widget 
# belongin to othe modules
# import os
# from PyQt4 import uic
# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'search_plus_dialog_base.ui'))
# class SearchPlusDockWidget(QtGui.QDockWidget, FORM_CLASS):

class SearchPlusDockWidget(QtGui.QDockWidget, Ui_searchPlusDockWidget):
    
    def __init__(self, parent=None):
        """Constructor."""
        super(SearchPlusDockWidget, self).__init__(parent)
        
        # Set up the user interface from Designer.
        self.setupUi(self)