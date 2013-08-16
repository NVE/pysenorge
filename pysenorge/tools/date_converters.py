# Built-in
import os


def iso2datetime(ISOdatein='1970-01-01 00:00:00'):
    """
    Converts an ISO date to at datetime object.
    
    @param ISOdatein: Input date in ISO format: YYYY-MM-DD hh:mm:ss/YYYY-MM-DDThh:mm:ss
    
    @return: I{datetime} object
    """
    from datetime import datetime, date, time
    
    # Set date and time
    if "T" in ISOdatein:
        _split = ISOdatein.split('T')
    else:
        _split = ISOdatein.split(' ')
        
    d = date(int(_split[0].split('-')[0]),
             int(_split[0].split('-')[1]),
             int(_split[0].split('-')[2]))
    
    t = time(int(_split[1].split(':')[0]),
             int(_split[1].split(':')[1]),
             int(_split[1].split(':')[2]))
    
    dtc = datetime.combine(d,t)
    return dtc


def datetime2UMdate(datein):
    """
    Converts a I{datetime} object to the string HH_YYYY_MM_DD used for UM4
    files.
    """
    filedate = "%s_%s_%s_%s" % (str(datein.hour).zfill(2),
                                str(datein.year).zfill(4),
                                str(datein.month).zfill(2),
                                str(datein.day).zfill(2))
    return filedate


def datetime2BILdate(datein):
    """
    Converts a I{datetime} object to the string YYYY_MM_DD used for senorge
    files.
    """
    filedate = "%s_%s_%s" % (str(datein.year).zfill(4),
                             str(datein.month).zfill(2),
                             str(datein.day).zfill(2))
    return filedate


def get_hydroyear(datein):
    """
    Returns the hydrological year the given I{datetime} lies in.
    """
    months = [9, 10, 11, 12]
    if datein.month in months:
        return datein.year+1
    else:
        return datein.year
    

def get_date_filename(filename):
    """
    Splits the standard file name of type "themename_YYYY_MM_DD.bil/.nc"
    and extracts the date.
    
    @return: Strings: "YYYY", "MM", "DD"
    
    @author: kmu
    @since: 14. okt. 2010
    """
    filestr = os.path.splitext( os.path.basename(filename) )[0]
    strlist = filestr.split('_')
    yy = strlist[1]
    mm = strlist[2]
    dd = strlist[3]
    return yy, mm, dd