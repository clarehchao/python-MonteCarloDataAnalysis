from __future__ import division
import numpy as np
from ImVolTool import xyz2vol as xv
import os
import errno
import re

"""
Future work: write a funtion for the following..
- keep track of the dose computed from multiple simulations (run's)
- save the dose result into the mysql data base
- pull data from mysql DB to look at the data of interest
e.g. compare the dose result (a src-to-target organs) from different simulation pkgs
pull out mass, position related information of organs for different src-to-target organ pairs
other mysql request to get data out of DB to present for interesting visualizations
"""


def MakeDir(fdir):
# source: http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    try:
        os.mkdir(fdir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            print '\nBe careful! directory %s already exists!' % fdir

class VoxelizedDoseContainer:
    def __init__(self,*args):
        # arguments for the class constructor
        self.theGeoDir = args[0]
        self.theNxyz = args[1]
        self.theDxyz = args[2]
        
        # class private variables
        self.theDoseDir = ''
        self.theGeoVol = np.empty(0,dtype='uint8')
        self.theinfodict = {}
        self.theEdepVol = np.zeros(0,dtype='float32')
        # add more dose volume e.g. fluence volumn when needed
        self.constK = 2.13*10/(3.7e-2)/3600
        self.voxvol = np.prod(0.1*np.array(self.theDxyz))  # voxel volume, unit: cm^3
        #self.Gy2MeVperGram = (1/(1.60217646e-16))*1.0e-3/1000
        organname = ['Bone','Lungs','Adrenal','Brain','Heart','Liver','SalivaryGlands','Spleen']
        tumorname = ['Tumor%d' % n for n in range(1,13)]
        self.TargetOrgan = organname + tumorname
        self.simNevent = 0  #update the number of events in the simulation for dose output
        self.theSVdict = {}
    
    def getInfo2Dict(self):
        # construct a dictionary of organ name storing organ tag and material density
        fname1 = '{}/ECompDensity.txt'.format(self.theGeoDir)
        data1 = np.loadtxt(fname1,skiprows=1)
        tmpdict = {}
        for i in range(data1.shape[0]):
            tmpdict[int(data1[i,0])] = data1[i,-1]
        
        # read a text file and save to a dictionary
        fname2 = '{}/OrgantagvsName.txt'.format(self.theGeoDir)
        f = open(fname2,'r')
        for line in f:
            splitline = line.split()
            organtag = int(splitline[0])
            name = splitline[1]
            if name not in self.theinfodict:
                self.theinfodict.setdefault(name,[])
            self.theinfodict[name].append(organtag)
            self.theinfodict[name].append(tmpdict[organtag])
    
    def loadGeoVol(self):
        thefile = '{}/GeoVol.bin'.format(self.theGeoDir)
        print thefile,self.theGeoDir
        self.theGeoVol = xv.FlattenFile2Vol(thefile,'uint8',self.theNxyz[0],self.theNxyz[1],self.theNxyz[2])
    
    def loadEdepVol(self,fdir,run1,run2):
        # figure out how to pass in  $d in string with run1 and run2 for dose accumulation!
        self.theDoseDir = fdir
        thefile = '{}/Run{}/BustOutRoot/Edep.dat'.format(self.theDoseDir,run1)
        self.theDoseVol = xv.Coord2Vol(thefile,self.theNxyz)
        
        # Determine the number of total events in the dose result file
        thelogfile = '{}/Run{}/log.txt'.format(self.theDoseDir,run1)
        f = open(thelogfile,'r')
        self.simNevent = int(re.findall(r'Number of Events in this run: ([\w]+)',f.read())[0])
    
    def ComputeSvalue(self):
        for oo in self.TargetOrgan:
            tag = self.theinfodict[oo][0]
            indx = (self.theGeoVol == tag)
            totEdep = np.sum(self.theDoseVol[indx])
            mass = self.voxvol*self.theinfodict[oo][1]*np.sum(indx)
            self.theSVdict[oo] = self.constK*totEdep/mass/self.simNevent
            # maybe think about storing these organ tag index into a table ? e.g. key: [xxxxxx] etc.
            
            
            
            
            
    
    
