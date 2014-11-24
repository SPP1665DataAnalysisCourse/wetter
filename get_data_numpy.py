import urllib
import zipfile

import os
import shutil

fname = "tageswerte_00044_19710301_20131231_hist.zip"
url = "ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/historical/"

if not os.path.exists(fname):
    fln, headers = urllib.urlretrieve(url + fname)
    shutil.copyfile(fln, fname)

datazip = zipfile.ZipFile(fname, 'r')
datazip.namelist()

datacsv = datazip.read('produkt_klima_Tageswerte_19710301_20131231_00044.txt')

datalines = datacsv.splitlines()

header = [item.strip() for item in datalines[0].split(";")]

# remove is in-place
header.remove('eor')

data = {}

# last line in the file just contains '\x1a', which is not a useful key
for line in datalines[1:]:

    linedata = line.split(";")
    if len(linedata) < 2:
        continue

    daily = {}

    # Don't try to read the last column, as this is always 'eor'
    for idx, value in enumerate(linedata[:-1]):
        key = header[idx]
        if key not in ("Stations_ID", "Mess_Datum"):
            v = float(value)
            if v == -999:
                daily[key] = None
            else:
                daily[key] = v
        elif key == "Mess_Datum":
            date = value

    data[date] = daily

header.remove("Mess_Datum")
header.remove("Stations_ID")

timeseries = {}
for key in header:
    timeseries[key] = []
    for date in sorted(data.keys()):
        timeseries[key].append(data[date][key])

import numpy
import pylab

airtemp_val = numpy.array(timeseries["LUFTTEMPERATUR"], dtype=float)
airtemp_idx = numpy.arange(len(airtemp_val))

airtemp_mask = numpy.isfinite(airtemp_val)
airtemp_val = airtemp_val[airtemp_mask]
airtemp_idx = airtemp_idx[airtemp_mask]

datelabels = numpy.array(sorted(data.keys()))[airtemp_mask]
datelabel_spacing = numpy.linspace(0, len(airtemp_idx) - 1, 10).astype(int)

firstjanuary_idx = []
for idx, datelabel in enumerate(datelabels):
    if datelabel.endswith("0701"):
        firstjanuary_idx.append(idx)

firstjanuary_idx = numpy.array(firstjanuary_idx)

firstjanuary_temp_val = airtemp_val[firstjanuary_idx]
firstjanuary_temp_idx = airtemp_idx[firstjanuary_idx] 

p = numpy.polyfit(firstjanuary_temp_idx, firstjanuary_temp_val, deg=1)
fit_y = p[1] + firstjanuary_temp_idx * p[0]

pylab.figure()
pylab.title("Local warming")
pylab.plot(airtemp_idx, airtemp_val)
pylab.plot(firstjanuary_temp_idx, firstjanuary_temp_val, "ro", ms=10)
pylab.plot(firstjanuary_temp_idx, fit_y, "g-", lw=2)
pylab.grid()
pylab.xticks(airtemp_idx[datelabel_spacing], datelabels[datelabel_spacing], rotation=45)
pylab.show()
