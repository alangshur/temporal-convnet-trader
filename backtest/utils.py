import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime
from os import walk


def get_filenames(path):
    fs = []
    for (dirpath, dirnames, filenames) in walk(path): 
        fs.extend(filenames)
    return fs


def get_feeds(path):    
    fs = get_filenames(path)
    feeds = {}

    for f in fs:
        f_str = f.split('.')[0]
        feeds[f_str] = btfeeds.GenericCSVData(
            dataname=path + f,
            fromdate=datetime(2015, 1, 1),
            todate=datetime(2018, 12, 31),
            openinterest=-1,
            timeframe=bt.TimeFrame.Minutes,
            compression=15
        )

    return feeds