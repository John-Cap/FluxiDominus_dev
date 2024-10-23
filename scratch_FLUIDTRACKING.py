import nmrglue as ng
import matplotlib.pyplot as plt
import numpy as np

#Import - class must take a directory to be used during runtime
dataFolder = r"C:/Users/user-pc/Desktop/New folder"
dic, raw_data = ng.jcampdx.read(dataFolder + "/nmr_fid.dx") #Class must somehow check if this file has changed

#Create proper data object for ng scripts to understand
npoints = int(dic["$TD"][0])
data = np.empty((npoints, ), dtype='complex128')
data.real = raw_data[0][:]
data.imag = raw_data[1][:]

#Processing
data = ng.proc_base.zf_size(data, int(dic["$TD"][0])*2) # Zerofill, now 2x of total amount of points
data = ng.proc_base.fft(data) # Fourier transformation
data = ng.proc_base.ps(data, p0=float(dic["$PHC0"][0]), p1=float(dic["$PHC1"][0])) # Phasing, values taken from dx file
data = ng.proc_base.di(data)#.tolist() # Removal of imaginairy part

# Set correct PPM scaling
udic = ng.jcampdx.guess_udic(dic, data)
udic[0]['car'] = (float(dic["$BF1"][0]) - float(dic["$SF"][0])) * 1000000 # center of spectrum, set manually by using "udic[0]['car'] = float(dic["$SF"][0]) * x", where x is a ppm value
udic[0]['sw'] = float(dic["$SW"][0]) * float(dic["$BF1"][0])
uc = ng.fileiobase.uc_from_udic(udic)
ppm_scale = uc.ppm_scale().tolist()
data=data.tolist()
length=len(ppm_scale)

#Reduce resolution to ppm range 0 - 15
_ppmScale=[]
_data=[]
_i=0
_ret=[]
while _i < length:
    if (ppm_scale[_i] > 0 and ppm_scale[_i] < 15):
        _ppmScale.append(ppm_scale[_i])
        _data.append(data[_i])
        _ret.append([ppm_scale[_i],data[_i]])
    _i+=3
print(len(_ret))
# Plot spectrum
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(_ppmScale,_data)
plt.xlim((15,0)) # plot as we are used to, from positive to negative
fig.savefig(dataFolder + "/Spectrum.png")

print(max(data))