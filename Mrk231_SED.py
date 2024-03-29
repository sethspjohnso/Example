import sys, logging, os, re
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
from readcol import readcol
from scipy import stats
import scipy.constants as const


### Observed Mrk231 SED
l_Kis,f_Kis,ferr_Kis          = readcol("Mrk231_Kishimoto.dat",twod=False)
l_MMT,f_MMT,ferr_MMT          = readcol("Mrk231_MMT.dat",twod=False)
l_Ima,f_Ima,caca,ferr_Ima     = readcol("Mrk231_Imanishi.dat",twod=False)
l_CCSpec,f_CCSpec,ferr_CCSpec = readcol("Mrk231_CCSpec.dat",twod=False)
l_CCIma,f_CCIma,ferr_CCIma    = readcol("Mrk231_CCIma.dat",twod=False)

f_CCSpec = f_CCSpec*1000.
ferr_CCSpec = ferr_CCSpec*1000.

###Concatenate arrays
l_mrk231 = np.concatenate((l_Kis,l_MMT,l_Ima,l_CCSpec,l_CCIma))
f_mrk231 = np.concatenate((f_Kis,f_MMT,f_Ima,f_CCSpec,f_CCIma))
ferr_mrk231 = np.concatenate((ferr_Kis,ferr_MMT,ferr_Ima,ferr_CCSpec,ferr_CCIma))


### 2-phase Clumpy SED from  Siebenmorgen , Heymann, & Efstathiou A&A 2015,
ClumpySED_path = '/Users/enrique/Desktop/Clumpy_2phase_SHE15/Clumpy_2phase/agnsed/'
ClumpySED_list = ClumpySED_path+'ClumpySED.list'
ClumpySED_list = readcol(ClumpySED_list)

nSEDm = len(ClumpySED_list)
nSEDpt = len(l_mrk231)

templates1 = np.empty(nSEDm,dtype=[('modelname','a29'),('Rin','f8'),('Vc','f8'),('Tau_c','f8'),
                                   ('Tau_m','f8'),('Angle','f8'),('lum','f8'),
                                   ('wavesim','f8',(nSEDpt,)),
                                   ('fluxsim','f8',(nSEDpt,)),
                                   ])

templates = templates1.view(np.recarray)


###Fill the variables in the wrapper
sed_zero = zeros(len(l_mrk231))

#Bandwidth to estimate the flux from the SED library of Siebenmorgen.
#for now I just assume a bandwith of 0.3 um per photometric data. Just to check the code
Dl = 0.3

c    = 2.9979e14          #speed of light (microns/s)
dist = 174.6              #Mpc
z    = 70.*dist/3.e5      #Redshift

for ii in range(0,len(ClumpySED_list)):
    l_i,f_i = readcol(ClumpySED_path+ClumpySED_list[ii][0],twod=False)
    for jj in range(0,len(l_mrk231)):
        sed_zero[jj] = np.mean(f_i[np.where((l_i < l_mrk231[jj]+Dl) & (l_i > l_mrk231[jj]-Dl))])
    
    #Create array of templates
    string=re.findall(r'[-+]?\d*\.\d+|\d+',ClumpySED_list[ii][0])
    Rin   = string[0]
    Vc    = string[1]
    Tau_c = string[2]
    Tau_m = string[3]
    Angle = string[4]
    
    #Calculate fluxes & luminosities
    lnu = (sed_zero/(1+z))/(4*3.141592*(dist/3.08568E22)**2) * 1E-26 * l_mrk231/c                       #L_sun
    lum = abs(np.trapz(lnu,c/l_mrk231))
    flux = sed_zero * (1.+z) * (lum/3.856E26) * 4. * 3.141592 * (dist*3.08568E22)**2 *1E-26 *1E-8*1000  #mJy
    
    #Filling Templates
    templates['modelname'][ii] = ClumpySED_list[ii][0]
    templates[ii]['Rin']       = Rin
    templates[ii]['Vc']        = Vc
    templates[ii]['Tau_c']     = Tau_c
    templates[ii]['Tau_m']     = Tau_m
    templates[ii]['Angle']     = Angle
    templates[ii]['lum']       = lum
    templates[ii]['wavesim'][:] = l_mrk231
    templates[ii]['fluxsim'][:] = flux