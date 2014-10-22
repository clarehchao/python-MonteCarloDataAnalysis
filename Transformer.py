from __future__ import division
import numpy as np
import dicom  # dicom reader package
import glob   # get all the files in a directory
from math import ceil
import os
import errno

# note: don't need get element composition info as it's not really used in the Data.dat in VHDMSD
# not everything needs to in a class in python
# @staticmethod is mostly useless in python

def IsEven(x):
# a helper method; does not need to be in a class: return true if x is even, otherwise
    return x % 2 == 0

def GetDimension(n,dn):
#a helper method; does not need to be in a class
    if IsEven(n):
        halfn = n/2
        #nn = np.linspace(-halfn*dn,halfn*dn,n,endpoint=True)  # check to make sure the output the same as the matlab ooutput
        nn = np.arange(-halfn*dn,dn*(halfn+1),dn,dtype='float32')
    else:
        halfn = ceil(n/2)
        halfdn = dn/2
        #nn = np.linspace(-halfn*dn+halfdn,halfn*dn-halfdn,n,endpoint=True)
        nn = np.arange(-halfn*dn+halfdn,halfn*dn+halfdn,dn,dtype='float32')
    return nn

def MakeDir(fdir):
# source: http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    try:
        os.mkdir(fdir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            print '\nBe careful! directory %s already exists!' % fdir

class Transformer:
    def __init__(self,*args,**kwargs):
        self.theVolfile = args[0]
        self.theFtype = args[1]
        self.theFwgeodir = args[2]
        self.theFwsrcdir = args[3]
        print self.theVolfile, self.theFtype
        if kwargs.get('nxyz'):
            self.nx,self.ny,self.nz = kwargs.get('nxyz')
        else:
            self.nx = self.ny = self.nz = None
        if kwargs.get('dxyz'):
            self.dx,self.dy,self.dz = kwargs.get('dxyz')
        else:
            self.dx = self.dy = self.dz = None
        
        self.thex0 = self.thex1 = self.they0 = self.they1 = 0
        self.thezz = np.empty(0)
        self.theVol = np.empty(0,dtype=self.theFtype)
        self.theElecomp = np.empty(0)
        self.theOrganInfo = []
    

    def Bin2Vol(self):      #instance member function
        tmp = np.fromfile(self.theVolfile,dtype=self.theFtype)
        self.theVol = tmp.reshape((self.nz,self.ny,self.nx),order='C')
    
    """
    def Dicom2Vol(self):    #instance member function
        alldcfiles = glob.glob('%s/*.DCM' % self.theVolfile)
        for i in range(0,nz):
            dc = dicom.read_file(alldcfiles[i])
            if i == 0:  # initialize
                self.dx,self.dy = dc.PixelSpacing
                self.dz = dc.SliceThickness
                self.nx = dc.Columns
                self.ny = dc.Rows
                self.nz = len(alldcfiles)
                self.vol = np.empty((self.nz,self.ny,self.nx))
            im = thedc.pixel_array
            self.theVol[i,:,:] = im
    """
           
    def GetOrganInfo(self,fname):  #instance member function
        tmp = {}
        with open(fname,'r') as text:
            for line in text:
                key,val = line.split()
                if key not in tmp:
                    tmp[int(key)] = val
                else:
                    print 'found duplicate! key: ', key
        # sort the dictionary and return list of tuples
        self.theOrganInfo = tmp.items()
        #self.theOrganInfo = sorted(tmp.items())  # sort by key
        #self.theOrganInfo = sorted(tmp.items(),key=lambda x: x[1])  # sort by value
        # we can decide what to do with this leave it as a dict or a list...
    
    def GetPixelDim(self):
        # get pixel spacing
        ll = [(self.nx,self.dx),(self.ny,self.dy),(self.nz,self.dz)]
        xx,yy,self.thezz = [GetDimension(t,dt) for t,dt in ll]
        #print len(xx),len(yy),len(self.thezz)
        self.thex0 = xx[0]
        self.thex1 = xx[-1]
        self.they0 = yy[0]
        self.they1 = yy[-1]
        
    def Vol2G4file(self):  #instance member function
        # create a directory for file writing
        MakeDir(self.theFwgeodir)
        
        # write volume and organtag info to a .g4m
        fnamelist = []
        for i in range(self.nz):
            ftag = 'G4_%0.4d.g4m' % i
            fname = '%s/%s' % (self.theFwgeodir,ftag)
            fnamelist.append(ftag)
            f = open(fname,'w')  # check if fname exists?
            # write organ info
            f.write('%d\n' % len(self.theOrganInfo))
            for k in self.theOrganInfo:
                f.write('%s %s\n' % k)
            
            # write image slice x,y,z info
            f.write('%d %d %d\n%4.3f %4.3f\n%4.3f %4.3f\n%4.3f %4.3f\n' % (self.nx,self.ny,1,self.thex0,self.thex1,self.they0,self.they1,self.thezz[i],self.thezz[i+1]))
            
            # write the pixel value
            imtuple = tuple(map(tuple,self.theVol[i,:,:]))
            f.write('\n'.join(" ".join(map(str, x)) for x in imtuple))  # map function: apply *the function* over items of iterable and return a list of result.  
            #e.g. map(str,x): apply str(n) for all elements in x and join them together with ' '
            f.close()
        
        # write Data.dat
        fname = '%s/Data.dat' % (self.theFwgeodir)
        f = open(fname,'w')
        f.write('%d\n' % len(fnamelist))
        f.write('\n'.join(ii for ii in fnamelist))
        f.close()
    def makeSourceMapFile(self,srcname,srclist):
        probmap = np.zeros(self.nx*self.ny*self.nz,dtype='float32')
        isSrc = np.in1d(self.theVol,np.array(srclist))  # a boolean array of the size of self.theVol
        probmap[isSrc] = 1.0
        probmap = probmap/np.sum(probmap)
        # sparsify the array
        indx = np.nonzero(probmap != 0)[0]
        val = probmap[indx]
        output = np.hstack((indx[:,np.newaxis],val[:,np.newaxis]))
        #print output
        
        # write to files
        # create a directory for file writing
        thesrcdir = '{}/{}'.format(self.theFwsrcdir,srcname)
        MakeDir(thesrcdir)
        fname = '{}/SparseDoseMap.g4d'.format(thesrcdir)
        f = open(fname,'w')  # check if fname exists?
        # write image slice x,y,z info
        f.write('%d %d %d\n%4.3f %4.3f\n%4.3f %4.3f\n%4.3f %4.3f\n' % (self.nx,self.ny,self.nz,self.thex0,self.thex1,self.they0,self.they1,self.thezz[0],self.thezz[-1]))
        outputtuple = tuple(map(tuple,output))
        f.write('\n'.join('{:.0f} {:2.5e}'.format(x[0],x[1]) for x in outputtuple))  # print the (indx,val) tuple in the desired print format
        f.close()
        print 'write sourcemap: {}!'.format(fname)
    
    
    
