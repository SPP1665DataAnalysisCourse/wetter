from ftplib import FTP
import os

def get_station_data(filename="/tmp/station_list.txt"):
    if not os.path.isfile(filename):
        # write stations_list_soil.txt into filename
        with open(filename,'wb') as file:
            ftp = FTP("ftp-cdc.dwd.de")
            ftp.login()
            ftp.retrbinary('RETR /pub/CDC/help/stations_list_soil.txt', file.write)
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
                    from_date = line[12:20].strip()
                    to_date = line[21:29].strip()
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


def get_daily_recent():
    ftp = FTP("ftp-cdc.dwd.de")
    ftp.login()
    ftp.cwd("/pub/CDC/observations_germany/climate/daily/kl/recent/")

    ls = []
    ftp.retrlines('NLST', lambda l: ls.append(l))
    id2file = {}
    for l in ls:
        try:
            id2file[int(l.split("_")[2])] = "ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/" + l
        except:
            continue

    ftp.quit()
    return id2file


def get_daily_hist():
    ftp = FTP("ftp-cdc.dwd.de")
    ftp.login()
    ftp.cwd("/pub/CDC/observations_germany/climate/daily/kl/historical/")

    ls = []
    ftp.retrlines('NLST', lambda l: ls.append(l))
    id2file = {}
    for l in ls:
        try:
            id2file[int(l.split("_")[1])] = "ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/historical/" + l
        except:
            continue

    ftp.quit()
    return id2file


def suggest_names(name, name2id):
    return [st for st in name2id.keys() if unicode(name,"utf8").lower() in st.lower()]


def get_name(name2id):
    while True:
        name = raw_input("Enter station name: ")
        ns = suggest_names(name, name2id)
        if len(ns) == 1:
            return ns[0]
        elif len(ns) == 0:
            print "Nothing found. Repeat!"
        else:
            print "Reduce selection: ",
            for n in ns:
                print "'"+n+"'",
            print

def cli():
    name2id, id2meta = get_station_data()
    id2recent = get_daily_recent()
    id2hist = get_daily_hist()
    print "# Stations: ", len(name2id)
    print "# recent: ", len(id2recent)
    print "# hist: ", len(id2hist)
    station_name = get_name(name2id)
    
    station_id = name2id[station_name]
    print "Station name:", station_name
    print " - id:", station_id
    print " - height:", id2meta[station_id]['height']
    print " - latitude:", id2meta[station_id]['latitude']
    print " - longitude:", id2meta[station_id]['longitude']
    print " - federal state:", id2meta[station_id]['state']
    print " - Recent file:", id2recent[station_id]
    print " - History file:", id2hist[station_id]


if __name__ == '__main__':
    cli()
