#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ImVolTool import xyz2vol as xv
import numpy as np
import VoxelizedDoseContainer as vdc

# initialize an instance of vdc
rootdir = '/data3/G4data_Clare'
geodir = '{}/G4INPUT/GeometryIM/binIM/MIBGPT1_segCT'.format(rootdir)
dosedir = '{}/G4.9.6.p02work/VoxelizedHumanDoseMultiSDv3-build/data/GEO_MIBGPT1_segCT/SRCMP_MIBGPT1_segCT/Spleen/I131'.format(rootdir)
nxyz = [512,512,295]
dxyz = [1.36719,1.36719,5.0]
thedoseobj = vdc.VoxelizedDoseContainer(geodir,nxyz,dxyz)
thedoseobj.getInfo2Dict()
#print thedoseobj.theinfodict
thedoseobj.loadGeoVol()
#print thedoseobj.theGeoVol.shape
thedoseobj.loadEdepVol(dosedir,1,1)
#print thedoseobj.theDoseVol.shape
thedoseobj.ComputeSvalue()
#print thedoseobj.theSVdict.items()

"""
    Future work:
    - save Svalue result into the mySQL database for better data management
"""