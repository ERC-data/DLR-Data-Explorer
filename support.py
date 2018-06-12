#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:48:14 2018

@author: saintlyvi
"""

import ckanapi
import pandas as pd
import os
import feather
from pathlib import Path

import urllib
import shutil

table_dir = os.path.join('data','table')

csv_table = os.path.join(table_dir, 'csv')
feather_table = os.path.join(table_dir, 'feather')
os.makedirs(csv_table, exist_ok=True)
os.makedirs(feather_table, exist_ok=True)

csv_adtd = os.path.join('data', 'seasonProfiles', 'csv')
feather_adtd = os.path.join('data', 'seasonProfiles', 'feather')
os.makedirs(csv_adtd, exist_ok=True)
os.makedirs(feather_adtd, exist_ok=True)

def appData():
    
    #fetch tables from energydata.uct.ac.za
    apikey = input('Enter your APIKEY from http://energydata.uct.ac.za/user/YOUR_USERNAME: ')
    headers = {'Authorization':apikey}
    ckan = ckanapi.RemoteCKAN('http://energydata.uct.ac.za/', apikey=apikey, get_only=True)

    tables = ckan.action.package_show(id='dlr-database-tables-94-14')        
    for i in range(0, len(tables['resources'])):
        name = tables['resources'][i]['name']
        print('... fetching ' + name + ' from energydata.uct.ac.za')
        r_url = tables['resources'][i]['url']
        # Download resources from data portal
        request = urllib.request.Request(r_url, headers = headers)
        with urllib.request.urlopen(request) as response, open(os.path.join(csv_table, name + '.csv'), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)            
        table = pd.read_csv(os.path.join(csv_table, name + '.csv'))            
        #write profiles to disk                
        feather.write_dataframe(table, os.path.join(feather_table, name + '.feather'))
    
    profiles = ckan.action.package_show(id='dlr-seasonal-adtd-profiles')        
    for i in range(0, len(profiles['resources'])):
        name = profiles['resources'][i]['name']
        print('... fetching ' + profiles['resources'][i]['name'] + ' from energydata.uct.ac.za')
        r_url = profiles['resources'][i]['url']
        # Download resources from data portal
        request = urllib.request.Request(r_url, headers = headers)
        with urllib.request.urlopen(request) as response, open(os.path.join(csv_adtd, name + '.csv'), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        adtd = pd.read_csv(os.path.join(csv_adtd, name + '.csv'))
        #write profiles to disk                
        feather.write_dataframe(adtd, os.path.join(feather_adtd, name + '.feather'))
    return

def readAggProfiles(year, directory = 'seasonProfiles'):
    """
    This function fetches aggregate load profile data from disk. aggfunc can be one of pp, aggpp_M, aMd, adtd
    """
    path = os.path.join('data', directory, 'feather')
#    
#    if len(os.listdir(path)) != 21:
#        appData()
#    
#    else:         
    path = Path(path)        
    for child in path.iterdir():
        n = child.name
        nu = n.split('.')[0].split('_')[-1]
        if int(nu)==year:
            df = feather.read_dataframe(str(child))
            return df     

def appProfiles(yearstart, yearend):
    
    data = pd.DataFrame()
    
    for y in range(yearstart, yearend+1):
        d = readAggProfiles(y)
        data = data.append(d)
        
    return data