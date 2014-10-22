#import the toolbox for converting a flat coor txt file to a flat or 3d volum
from ImVolTool import xyz2vol as xv
import glob
import numpy as np
import Transformer as tf
import sys
import shutil

if __name__ == '__main__':
    #inputdata = open(sys.argv[1])
    ftype = 'uint8'
    organname = ['Lungs','Adrenal','Brain','Heart','Liver','SalivaryGlands','Spleen','Bladder']

    """
    # ==== CT image Segmentation via Threshold and manual VOIs ======
    # make a binary out of the dicom images
    
    # prior to segmentation, prepare the binary mask
    fdir = '/home/clare/pythoncode/VHDMSD/SegmentedCTs'
    ctdir = '/home/clare/IM/cbpet2/13-0415PET/4'
    xyz0 = [-349.316,-356.815,5.07339]  # specific to this particular PET/CT data set (should change this when working with a different data set)
    dxyz = [1.36719,1.36719,5.0]
    nxyz = [512,512,295]
    for nn in organname:
        fname = '%s/roi_raw_data_{%s}.tsv' % (fdir,nn)
        vol = xv.Xyz2Vol(fname,dxyz,xyz0,nxyz)
        binfname = '%s/%s_Day5.bin' % (fdir,nn)
        xv.SaveFlattenVol(vol,binfname,ftype)

    dxyz,nxyz,ctvol = xv.Dicom2Vol(ctdir)
    #ctfname = '%s/CT_Day5.bin' % fdir
    #xv.SaveFlattenVol(dcvol,ctfname,'float32')
    print dxyz,nxyz
    
    
    # segment via threshold 
    thresh = [-5000,-400,145,1440,5000]
    segvol1,maxsegval = xv.SegmentVol_ThreshMask(ctvol,thresh)
    #segfname = '%s/segvol1_Day5.bin' % fdir
    #xv.SaveFlattenVol(segvol1,segfname,'uint8')
    
    
    # generate a list of organ mask
    organfname = [ '%s_Day5.bin' % ss for ss in organname]
    tumorfname = ['50pIsoContVOI_Tumor%d_Day5.bin' % n for n in range(1,13)]
    allfname = organfname + tumorfname
    allfullfname = ['%s/%s' % (fdir,ss) for ss in allfname]
    #print allfname

    segvol2 = xv.SegmentVol_ImMask(segvol1,allfullfname,'uint8',segval0=maxsegval+1)
    fwdir = '/data3/G4data_Clare/G4INPUT/GeometryIM/binIM'
    geotag = 'MIBGPT1_segCT'
    fbindir = '{}/{}'.format(fwdir,geotag)
    xv.MakeDir(fbindir)
    segfname = '{}/GeoVol.bin'.format(fbindir)
    xv.SaveFlattenVol(segvol2,segfname,'uint8')
    
    """
    # ========= Write G4-friendly geometry and source map files ==========
    fwgeodir = '/data3/G4data_Clare/G4INPUT/GeometryIM/G4IM/MIBGPT1_segCT'
    fwsrcdir = '/data3/G4data_Clare/G4INPUT/SourceMap/MIBGPT1_segCT'
    frdir = '/data3/G4data_Clare/G4INPUT/GeometryIM/binIM/MIBGPT1_segCT'
    fname = '{}/GeoVol.bin'.format(frdir)
    nxyz_ct = [512,512,295]
    dxyz_ct = [1.36719,1.36719,5.0]

    # transform a binary file into workable file
    tf = tf.Transformer(fname,ftype,fwgeodir,fwsrcdir,nxyz=nxyz_ct,dxyz=dxyz_ct)
    print tf.nx,tf.ny,tf.nz,tf.dx,tf.dy,tf.dz

    # convert a binary file to a volume
    tf.Bin2Vol()

    # get the appropriate info about the volume for G4file writing
    tf.GetPixelDim()
    organinfofile = '{}/OrgantagvsName.txt'.format(frdir)
    tf.GetOrganInfo(organinfofile)
    
    # copy the necessary files to G4 folders
    ecompfile = '{}/ECompDensity.txt'.format(frdir)
    shutil.copy2(organinfofile,fwgeodir)
    shutil.copy2(ecompfile,fwgeodir)

    # write G4files of the transformed volume
    tf.Vol2G4file()

    # write sourcemap based on the geometry volume
    srclist = range(4,24)
    tumorname = ['Tumor%d' % n for n in range(1,13)]
    srcname = organname + tumorname
    #print srclist
    #print srcname
    
    for i in range(len(srcname)):
        tf.makeSourceMapFile(srcname[i],srclist[i])
