def readin_file(fname):
    """This function reads the data file in"""
    flh = open(fname)
    # read the content and store it in a string
    content = flh.read()
    flh.close()
    return content

myfile = "produkt_klima_Tageswerte_20131023_20141122_00044.txt"
mydata = readin_file(myfile)
mydata_lines = mydata.splitlines()
header = mydata_lines[0].split(';')[:-1]

clean_header = []
for field in header:
    clean_header.append(field.strip())

header = clean_header
data = {}

for field in header:
    data[field] = [] 

for line in mydata_lines[1:]:
    fields = line.split(';')
    count = 0
    for field in fields[:-1]:
        data_string = field
        data_value = float(data_string)
        data[header[count]].append(data_value)
        count = count + 1

import pylab
pylab.plot(data['LUFTTEMPERATUR_MAXIMUM'])
pylab.show()
