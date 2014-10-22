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
print thedoseobj.theSVdict.items()

# write Svalue result to a database (!!)
# the svalue is in a dictionary







"""
# Set organs of interest
SrcName = ['Adrenal','Lungs','Spleen']
organname = ['Bone','Lungs','Adrenal','Brain','Heart','Liver','SalivaryGlands','Spleen']
tumorname = ['Tumor%d' % n for n in range(1,13)]
TrgName = organname + tumorname

# get the organtag and density info
infodir = '/home/clare/G4INPUT/GeometryIM/G4IM/MIBGPT1_segCT'
otfname = '{}/OrgantagvsName.txt'.format(infodir)
dsfname = '{}/ECompDensity.txt'.format(infodir)
otdata = xv.TxtFile2Dict(dsfname,otfname)


# get the phantom geometry
geodir = '/home/clare/pythoncode/VHDMSD/SegmentedCTs'
geofname = '{}/segvol2.bin'.format(geodir)
nxyz_ct = [512,512,295]
geoVol = xv.FlattenFile2Vol(geofname)

# Read Energy deposit Geant4 output into a volumn
fdir = '/data3/G4data_Clare/G4.10.0.p02work/VoxelizedHumanDoseMultiSDv3-build/data/GEO_MIBGPT1_segCT/SRCMP_MIBGPT1_segCT/Spleen/I131/Run1/BustOutRoot'
fname = '{}/Edep.dat'.format(fdir)
EdepVol = xv.Coord2Vol(fname,nxyz)
"""





