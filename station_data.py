#!/usr/bin/env python

from ftplib import FTP
import os
import datetime
import tempfile


def get_daily_recent_path():
    """
    Helper function to return the path for the recent observations.
    """
    return "/pub/CDC/observations_germany/climate/daily/kl/recent/"


def get_daily_hist_path():
    """
    Helper function to return the path for the historical observations.
    """
    return "/pub/CDC/observations_germany/climate/daily/kl/historical/"


def get_station_path():
    """
    Helper function to return the absolute path of the file containing
    the station names, ids and metadata.
    """
    return "/pub/CDC/help/KL_Tageswerte_Beschreibung_Stationen.txt"


def get_dwd_domain():
    """
    Helper function to return the domain name of the FTP server of
    Deutscher Wetterdienst.
    """
    return "ftp-cdc.dwd.de"


def get_temp_dir():
    """
    Helper function to return the path for temporary files on the system.
    """
    # Get tmp directory of system
    tmpdir = tempfile.gettempdir()
    # Return tmp directory with trailing slash
    return os.path.join(tmpdir, '')
        
    
def get_station_data(filename=get_temp_dir() + "station_list.txt"):
    """
    Return a dictionary that maps station names to numeric ids
    (name2id) and a dictionary that contains the metadata for all
    stations keyed with their ids (id2meta)

    This function performs the following steps:
      1. Download the station data file if it is here already.
      2. Create empty dictionaries for the data
      3. Parse each line in the station data file (except the first
         line) into data fields and put them into the dictionaries
      4. Return the dictionaries to the caller

    Arguments:
      filename - The name of the station data file.
    """

    if not os.path.isfile(filename):
        # write stations_list_soil.txt into filename
        with open(filename,'wb') as file:
            ftp = FTP(get_dwd_domain())
            ftp.login()
            ftp.retrbinary('RETR %s' % get_station_path(), file.write)
            ftp.quit()
    id_idx = 0
    name2id = {}
    id2meta = {}
    first = True
    second = True
    # parse csv file
    with open(filename, 'r') as file:
        for line in file:
            # first row contains header info
            if first:
                first = False
            elif second:
                second = False
            else:
                try:
                    st_id = int(line[0:11].strip())
                    from_date = datetime.datetime.strptime(line[12:20].strip(),"%Y%m%d")
                    to_date = datetime.datetime.strptime(line[21:29].strip(),"%Y%m%d")
                    height = int(line[32:44].strip())
                    latitude = float(line[46:57].strip())
                    longitude = float(line[58:66].strip())
                    name = unicode(line[67:107].strip(), "latin-1")
                    state = unicode(line[108:].strip(), "latin-1")

                    name2id[name] = st_id
                    id2meta[st_id] = {}
                    id2meta[st_id]['id'] = st_id
                    id2meta[st_id]['from_date'] = from_date
                    id2meta[st_id]['to_date'] = to_date
                    id2meta[st_id]['height'] = height
                    id2meta[st_id]['latitude'] = latitude
                    id2meta[st_id]['longitude'] = longitude
                    id2meta[st_id]['name'] = name
                    id2meta[st_id]['state'] = state
                    
                except:
                    continue
    return name2id, id2meta


def get_daily(recent=True):
    """
    Return a dictionary providing a mapping between ids and filenames
    for either recent or historical observation data.
    """

    ftp = FTP(get_dwd_domain())
    ftp.login()
    if recent:
        ftp.cwd(get_daily_recent_path())
    else:
        ftp.cwd(get_daily_hist_path())

    ls = []
    ftp.retrlines('NLST', ls.append)
    id2file = {}
    id_idx = 2 if recent else 1
    for l in ls:
        try:
            id2file[int(l.split("_")[id_idx])] = l
        except:
            continue

    ftp.quit()
    return id2file


def suggest_names(name, name2id):
    """
    Return a list of all station names that contain a certain fragment
    of a station name given.

    Arguments:
      name    - the fragment of the station name to search for.
      name2id - The dictionary that contains the name to id map for
                the stations
    """
    return [st for st in name2id.keys() if unicode(name,"utf8").lower() in st.lower()]


def compare(user, data, epsilon=0.1):
    """
    Helper function to compare data entered by the user and data in
    the program. For floating point numbers, an epsilon can be defined
    to provide a coarser search.

    Arguments:
      user    - The data provided by the user.
      data    - The data in the program.
      epsilon - How much can floation point numbers differ?
    """

    if type(data) is int:
        return user == data
    elif type(data) is float:
        return abs(user-data) < epsilon
    elif type(data) is unicode:
        return unicode(user,"utf8").lower() in data.lower()
    elif type(data) is datetime.datetime:
        return datetime.datetime.strptime(user,"%Y%m%d") == data


def suggest_id(value, key, id2meta):
    """
    Return a list of station ids that fulfil a certain criterion based
    on a search for a value for a certain key in a dictionary.

    Arguments:
      value - The value to search for in the data.
      key - The key the value belongs to.
      id2meta - The data dictionary to search in.
    """
    return [i for i, meta in id2meta.iteritems() if compare(value, meta[key])]


def get_name(name2id):
    """Return a station name based on user entry. This function will
    iterate until the selection is reduced to a single station
    name. Before the selection is unique, it will iterate the prompt
    together with a list of station names matching the user input.

    Arguments:
      name2id - A dictionary mapping station names to ids.
    """

    while True:
        name = raw_input("Enter station name: ")
        ns = suggest_names(name, name2id)
        if len(ns) == 1:
            return ns[0]
        elif len(ns) == 0:
            print "Nothing found. Repeat!"
        else:
            for elem in ns:
                if name.lower() == elem.lower():
                    return elem
            print "Reduce selection: ",
            for n in ns:
                print "'"+n+"'",
            print


def cli():
    """
    A simple command line interface that uses the functions in this
    module and prompts the user for a station name and prints out the
    metadata for the station when it is uniquely defined.
    """

    name2id, id2meta = get_station_data()
    id2recent = get_daily(recent=True)
    id2hist = get_daily(recent=False)
    print "# Stations: ", len(name2id)
    print "# recent: ", len(id2recent)
    print "# hist: ", len(id2hist)
    station_name = get_name(name2id)
    
    station_id = name2id[station_name]
    print "Station name:", station_name
    print " - id:", station_id
    print " - height:", id2meta[station_id]['height']
    print " - from time:", id2meta[station_id]['from_date']
    print " - to time:", id2meta[station_id]['to_date']
    print " - latitude:", id2meta[station_id]['latitude']
    print " - longitude:", id2meta[station_id]['longitude']
    print " - federal state:", id2meta[station_id]['state']
    if station_id in id2recent:
        print " - Recent file:", id2recent[station_id]
    else:
        print " - No recent file found!"

    if station_id in id2hist:
        print " - History file:", id2hist[station_id]
    else:
        print " - No history file found!"


if __name__ == '__main__':
    # This block is run if the script is called as a stand-alone
    # program and not imported as a module. In the latter case,
    # __name__ would be set to the name under which the file has been
    # imported (usually the file name).
    cli()
