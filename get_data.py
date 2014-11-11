import urllib
import zipfile

import os
import shutil

fname = "tageswerte_KL_00044_akt.zip"

if not os.path.exists(fname):
    fln, headers = urllib.urlretrieve('ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/' + fname)
    shutil.copyfile(fln, fname)

datazip = zipfile.ZipFile(fname, 'r')
datazip.namelist()

datacsv = datazip.read('produkt_klima_Tageswerte_20131009_20141108_00044.txt')

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

import pylab

datelabels = sorted(data.keys())

pylab.figure()
pylab.plot(timeseries["LUFTTEMPERATUR"])
pylab.grid()
pylab.xticks(range(len(datelabels))[::30], datelabels[::30], rotation=45)
pylab.show()
