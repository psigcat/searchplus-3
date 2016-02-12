# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : February 2016
        copyright            : (C) 2016 by David Erill
        email                : daviderill79 at gmail dot com
 ***************************************************************************/
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import logging
import os.path
import time
from datetime import datetime


#
# Utility funcions
#
def xstr(s):
    if s is None:
        return ''
    return str(s)


def isNumber(elem):
    try:
        float(elem)
        return True
    except (TypeError, ValueError):
        return False


def get_current_time():
    aux = str(time.strftime('%d/%m/%Y %H:%M:%S'))
    return aux    


def date_to_tstamp(date_aux):
    date_object = datetime.strptime(date_aux, "%Y-%m-%d %H:%M:%S")
    date_aux = date_object.strftime("%Y%m%d%H%M%S")            
    return date_aux
    
    
def set_logging(log_folder, log_name):
    
    global logger 
    
    # Create logger
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    
    # Define filename and format
    tstamp = str(time.strftime('%Y%m%d'))
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)    
    filepath = log_folder+"/"+log_name+"_"+tstamp+".log"
    log_format = '%(asctime)s [%(levelname)s] - %(message)s\n'
    log_date = '%d/%m/%Y %H:%M:%S'
    formatter = logging.Formatter(log_format, log_date)
    
    # Create file handler
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)    
    fh.setFormatter(formatter)
    logger.addHandler(fh)    

    # Create console handler
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#     ch.setFormatter(formatter)
#     logger.addHandler(ch)    

