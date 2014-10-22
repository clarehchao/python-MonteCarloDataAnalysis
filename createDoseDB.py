#! /usr/bin/env python
# -*- coding: utf-8 -*-
# must write the above line /usr/bin/env python if using a different python version from the default python version to make execuatable

from __future__ import division
import MySQLdb as mdb
import re
import pandas as ps
import sys
import numpy as np
import glob as gb


def ReadFile2DF(fname,isheader):
    if isheader:
        df = ps.read_table(fname,index_col=0)  # index_col = specify the column to use as the row labels of the data frame
    else:
        df = ps.read_table(fname,header=None,index_col=0)  # header = row number to use as the column names, header = None if the file has no header row  
    return df
    
def CreateTableDB(con):
    with con: # 'with' keyword automatically release the resource (i.e. close the db, catch error)
        cur = con.cursor()
        # create table for simulation info of the dose table
        cur.execute("DROP TABLE IF EXISTS SimInfo")
        cur.execute("CREATE TABLE SimInfo(sim_id INT UNSIGNED NOT NULL PRIMARY KEY, \
                     simpkg VARCHAR(25) NOT NULL, name VARCHAR(25) NULL, geo_id VARCHAR(100) NOT NULL, \
                     src_particle VARCHAR(25) NOT NULL, src_organ VARCHAR(25) NOT NULL, \
                     Nevent INT NULL, Nrun INT NULL);")
                     

        # create table for dose
        cur.execute("DROP TABLE IF EXISTS DoseInfo")
        cur.execute("CREATE TABLE DoseInfo(sim_id INT UNSIGNED NOT NULL, \
                     target_organ VARCHAR(25) NOT NULL, SV_mean DECIMAL(20,15) NULL, SV_std DECIMAL(20,15) NULL, \
                     PRIMARY KEY(sim_id,target_organ));")
    
def Insert2DB(con,df,varags):
    target_organs = df.index
    src_organs = df.columns
    simpkg,geo_id,src_particle,last_sim_id = varags
    with con:
        cur = con.cursor()
        for ii in range(len(src_organs)):
            tmp1 = [last_sim_id+ii+1,simpkg,geo_id,src_particle,src_organs[ii]]
            cur.execute("INSERT INTO SimInfo(sim_id,simpkg,geo_id,src_particle,src_organ) VALUES(%s,%s,%s,%s,%s);",tmp1)
            for jj in range(len(target_organs)):
                tmp2 = [last_sim_id+ii+1,target_organs[jj],df[src_organs[ii]][jj]]
                cur.execute("INSERT INTO DoseInfo(sim_id,target_organ,SV_mean) VALUES(%s,%s,%s);",tmp2)
                
def Insert2DB_fancy(con,df,varags):
    target_organs = df.index
    
    last_sim_id = ReadDBSize(con)
    start_sim_id = int(last_sim_id) + 1
    #simpkg,geo_id,src_particle,src_organ,Nevent,Nrun = varags
    with con:
        cur = con.cursor()
        varags.insert(0,start_sim_id)
        cur.execute("INSERT INTO SimInfo(sim_id,simpkg,geo_id,src_particle,src_organ,Nevent,Nrun) VALUES(%s,%s,%s,%s,%s,%s,%s);",varags)
        for i in range(len(target_organs)):
            to = target_organs[i]
            tmp = [start_sim_id,to,df[1][to],df[2][to]]
            cur.execute("INSERT INTO DoseInfo(sim_id,target_organ,SV_mean,SV_std) VALUES(%s,%s,%s,%s);",tmp)
          
def ReadDBSize(con):
    with con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM SimInfo")
        tmp = cur.fetchone()
    return tmp[0]
    
def GetNevent(fname):
    # Determine the number of total events in the dose log file
    with open(fname,'r') as f:
        nevent = re.findall(r'Number of Events in this run: ([\w]+)',f.read())[0]
    return int(nevent)

def Log2Data(dosedir,runlist):
    neventlist = []
    for r in runlist:
        logfile = '{}/Run{}/log.txt'.format(dosedir,r)
        neventlist.append(GetNevent(logfile))
    return neventlist
    
def FindIntermIrun(dosedir,run1,inc1,neventlist):
    for i in range(1,11):
        irun = run1 + i*inc1
        logfile = '{}/Run{}/log.txt'.format(dosedir,irun)
        neventeh = GetNevent(logfile)
        if neventeh == neventlist[1]:
            break
    return irun
     
def Fname2Data(fname,simfdir):
    # example: SVstatsufh10f_1_ufh10f_1_UBCont_I131_Run1-69_rinc20_4_G4.9.6.p02.txt
    tmp1 = re.findall(r'SVstats([\w-]+)_(\w+)_(\w+)_Run(\d+)-(\d+)_rinc([\w-]*)_([\w.]+).txt',fname)  #this separate the filename into sim info
    print tmp1
    junk,src_organ,src_particle,run1,run2,inc,pkg = tmp1[0]
    tmp2 = re.findall(r'(.+?)_\1+',fname)  #this finds the repeated str, e.g. \1 means 'repeat the pattern in the space before \1, which is '(.+?)_'
    geo_id = tmp2[0]
    
    # get Nevent info
    ddir = '{}/GEO_{}/SRCMP_{}/{}/{}'.format(simfdir,geo_id,geo_id,src_organ,src_particle)
    run_l = [int(run1),int(run2)]
    nevent_l = Log2Data(ddir,run_l)
    #print nevent_l
    
    # check for multiple entris of increment
    check = re.findall(r'(\d+)_(\d+)',inc)
    if check:  # found something in check
        inc_l = [int(s) for s in check[0]]
        iirun = FindIntermIrun(ddir,run_l[0],inc_l[0],nevent_l)
        run1_ar = np.array([run_l[0],iirun])
        run2_ar = np.array([iirun-run_l[0],run_l[1]+inc_l[1]-1])
        y = run2_ar - run1_ar + 1
        #print iirun,run1_ar,run2_ar,y
        Nrun = int(sum(y/np.array(inc_l)))  # number of simulations
        Nevent = int(inc_l[0]*nevent_l[0])  # number of particles simulated PER event
        #np.array(inc_l)*np.array(nevent_l)
    else:
        iinc = int(inc)
        # original: Nrun = (run_l[1] + iinc - 1 - run_l[0] + 1)/iinc, simplified to the below
        Nrun = int((run_l[1] + iinc - run_l[0])/iinc)
        Nevent = int(nevent_l[0]*iinc)
    
    return [pkg,geo_id,src_particle,src_organ,Nevent,Nrun]
    
if __name__ == '__main__':
    #inputdata = open(sys.argv[1])
    fdir = '/home/clare/pythoncode/VHDMSD/SVdata'

    # import the OLINDA & MCNPX data into DB
    tag = ['UFH00F/Svalue_I131_OLINDA_MassAdjusted_newborn.txt','UFH00F/Svalue_I131_MCNPX_ufh00f.txt','UFH10F/Svalue_I131_OLINDA_MassAdjusted_10yr.txt']
    simpkgs = ['OLINDA1.1','MCNPX','OLINDA1.1']
    geo_ids = ['newborn','ufh00f','10yr']
    src_particles = ['I131','I131','I131']
    
    con = mdb.connect('localhost','testuser','test000','UCSFDoseDB')
    CreateTableDB(con)
    for i in range(len(tag)):
        fname = '{}/{}'.format(fdir,tag[i])
        df = ReadFile2DF(fname,True)
        varargs = [simpkgs[i],geo_ids[i],src_particles[i],ReadDBSize(con)]
        Insert2DB(con,df,varargs)
    
    # import the G4 data into DB
    simfdir = '/data4/G4.9.6.p02work_Clare/VoxelizedHumanDoseMultiSDv1-build/data'
    thedir = '{}/Svalue_Updated/SVstats*'.format(fdir)
    allfiles = gb.glob(thedir)
    for fname in allfiles:
        print fname
        # get simulation info to push into DB
        varags = Fname2Data(fname,simfdir)
        #print varags
        
        # read the data to push into DB
        df = ReadFile2DF(fname,False)
        
        # insert into the DB via mysql
        Insert2DB_fancy(con,df,varags)








            
