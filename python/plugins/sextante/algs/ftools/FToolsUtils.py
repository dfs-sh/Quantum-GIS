# -*- coding: utf-8 -*-

"""
***************************************************************************
    FToolsUtils.py
    ---------------------
    Date                 : September 2012
    Copyright            : (C) 2012 by Carson Farmer, Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Carson, Farmer, Victor Olaya'
__date__ = 'September 2012'
__copyright__ = '(C) 2012, Carson Farmer, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from sextante.core.QGisLayers import QGisLayers
from qgis.core import *

def createSpatialIndex(layer):
    idx = QgsSpatialIndex()
    features = QGisLayers.features(layer)
    for ft in features:
        idx.insertFeature(ft)
    return idx

def createUniqueFieldName(fieldName, fieldList):
    shortName = fieldName[:10]

    if len(fieldList) == 0:
        return shortName

    if shortName not in fieldList:
        return shortName

    shortName = fieldName[:8] + "_1"
    changed = True
    while changed:
        changed = False
        for n in fieldList:
            if n == shortName:
                # create unique field name
                num = int(shortName[-1:])
                if num < 9:
                    shortName = shortName[:8] + "_" + str(num + 1)
                else:
                    shortName = shortName[:7] + "_" + str(num + 1)

                changed = True

    return shortName

def findOrCreateField(layer, fieldList, fieldName, fieldLen=24, fieldPrec=15):
    idx = layer.fieldNameIndex(fieldName)
    if idx == -1:
        fn = createUniqueFieldName(fieldName, fieldList)
        field =  QgsField(fn, QVariant.Double, "", fieldLen, fieldPrec)
        idx = len(fieldList)
        fieldList.append(field)

    return idx, fieldList

def extractPoints( geom ):
    points = []
    if geom.type() ==  QGis.Point:
        if geom.isMultipart():
            points = geom.asMultiPoint()
        else:
            points.append(geom.asPoint())
    elif geom.type() == QGis.Line:
        if geom.isMultipart():
            lines = geom.asMultiPolyline()
            for line in lines:
                points.extend(line)
        else:
            points = geom.asPolyline()
    elif geom.type() == QGis.Polygon:
        if geom.isMultipart():
            polygons = geom.asMultiPolygon()
            for poly in polygons:
                for line in poly:
                    points.extend(line)
        else:
            polygon = geom.asPolygon()
            for line in polygon:
                points.extend(line)

    return points

def getUniqueValues(layer, fieldIndex):
    values = []
    layer.select([fieldIndex], QgsRectangle(), False)
    features = QGisLayers.features(layer)
    for feat in features:
        if feat.attributes()[fieldIndex] not in values:
            values.append(feat.attributes()[fieldIndex])
    return values

def getUniqueValuesCount(layer, fieldIndex):
    return len(getUniqueValues(layer, fieldIndex))

# From two input field maps, create single field map
def combineVectorFields( layerA, layerB ):
    fields = []
    fieldsA = layerA.dataProvider().fields()
    fields.extend(fieldsA)
    namesA = [unicode(f.name()).lower() for f in fieldsA]
    fieldsB = layerB.dataProvider().fields()
    for field in fieldsB:
        name = unicode(field.name()).lower()
        if name in namesA:
            idx=2
            newName = name + "_" + unicode(idx)
            while newName in namesA:
                idx += 1
                newName = name + "_" + unicode(idx)
            field = QgsField(newName, field.type(), field.typeName())
        fields.append(field)

    return fields

# Create a unique field name based on input field name
def createUniqueFieldNameFromName( field ):
    check = field.name().right( 2 )
    shortName = field.name().left( 8 )
    if check.startsWith("_"):
        ( val, test ) = check.right( 1 ).toInt()
        if test:
            if val < 2:
                val = 2
            else:
                val = val + 1
            field.setName( shortName.left( len( shortName )-1 ) + unicode( val ) )
        else:
            field.setName( shortName + "_2" )
    else:
        field.setName( shortName + "_2" )
    return field
