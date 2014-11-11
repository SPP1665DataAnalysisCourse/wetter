import urllib
import zipfile

fln, headers = urllib.urlretrieve('ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_00044_akt.zip')

datazip = zipfile.ZipFile(fln, 'r')
datazip.namelist()

datacsv = datazip.read('produkt_klima_Tageswerte_20131009_20141108_00044.txt')
