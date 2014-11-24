def readin_file(fname):
    """This function reads the data file in"""
    flh = open(fname)
    # read the content and store it in a string
    content = flh.read()
    return content

myfile = "produkt_klima_Tageswerte_20131023_20141122_00044.txt"
mydata = readin_file(myfile)
print(mydata)

