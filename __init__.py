# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SearchPlus - A QGIS plugin for Toponomastic searcher
                             -------------------
        begin                : 2015-06-19
        copyright            : (C) 2015 by Luigi Pirelli
        email                : luipir@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SearchPlus class from file SearchPlus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .search_plus import SearchPlus
    return SearchPlus(iface)
