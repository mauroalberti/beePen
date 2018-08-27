"""
/***************************************************************************
 beePen - plugin for Quantum GIS

 annotation tools for field work
                              -------------------
        begin                : 2015.03.08
        copyright            : (C) 2015-2018 Mauro DeDonatis
        email                : mauro.dedonatis@uniurb.it
        
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import absolute_import

from .beePen_gui import beePen_gui


def classFactory(iface):

    # create qgSurf_gui class   
    return beePen_gui(iface)



