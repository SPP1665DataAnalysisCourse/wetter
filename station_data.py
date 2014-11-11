from ftplib import FTP
import csv
import os


def unicode_csv_reader(latin1_data, **kwargs):
    csv_reader = csv.reader(latin1_data, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, "latin-1") for cell in row]


def get_station_data():
    filename = "/tmp/station_list.txt"
    # remove old filename
    try:
        os.remove(filename)
    except OSError:
        pass
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
    # parse csv file
    with open(filename, 'r') as csvfile:
        spamreader = unicode_csv_reader(csvfile, delimiter=';')
        for row in spamreader:
            # first row contains header info
            if first:
                first = False
            else:
                name2id[row[4].strip()] = int(row[0].strip())
                id2meta[int(row[id_idx].strip())] = {}
                id2meta[int(row[id_idx].strip())]['id'] = int(row[id_idx].strip())
                id2meta[int(row[id_idx].strip())]['height'] = row[1].strip()
                id2meta[int(row[id_idx].strip())]['latitude'] = row[2].strip()
                id2meta[int(row[id_idx].strip())]['longitude'] = row[3].strip()
                id2meta[int(row[id_idx].strip())]['name'] = row[4].strip()
                id2meta[int(row[id_idx].strip())]['state'] = row[5].strip()
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
            id2file[int(l.split("_")[2])] = "ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/" + l
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
    station_names=sorted(list(name2id.keys()))
    return [st for st in station_names if unicode(name,"utf8").lower() in st.lower()]


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
