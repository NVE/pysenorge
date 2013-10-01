'''
Created on 25.09.2013

@author: kmu
update: rl

Creates clt files for wind_1500m_daily 
'''

def __clt_avg_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Gjennomsnittlig vindhastighet',
              'Gjennomsnittlig vindhastighet i 10 m hoeyde',
              'Vindstyrke')
    cltlist = [CLTitem(36.7, 300.0, (255,74,74), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (126, 0, 255), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (255,194,74), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (255,255,74), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (194,224,74), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (134,194,74), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (74,164,74), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (74,194,134), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (74,224,194), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (74,255,255), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (74,194,224), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\avg_wind_speed_10_no.clt")


def __clt_max_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Maksimal vindhastighet',
              'Maksimal vindhastighet i 1500 m hoeyde',
              'Vindstyrke')
    
    cltlist = [CLTitem(36.7, 300.0, (80,0,153), 'Orkan (over 32,6 m/s)'),
               CLTitem(28.5, 32.6, (80,13,243), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(24.5, 28.4, (205,13,243), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(20.8, 24.4, (243,13,186), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(17.2, 20.7, (243,13,76), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(13.9, 17.1, (243,66,13), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(10.8, 13.7, (243,150,13), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(8.0, 10.7, (243,234,13), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(5.5, 7.9, (182,243,13), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(3.4, 5.4, (48,243,13), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(1.6, 3.3, (13,243,115), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(0.0, 1.6, (174,174,174), 'Vindstille (<1,6 m/s)'),
               CLTitem(300.1, FloatFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\max_wind_speed_10_no.clt")


def __clt_bil_max_wind_speed_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Maksimal vindhastighet',
              'Maksimal vindhastighet i 10 m h�yde',
              'Vindstyrke')
    
    cltlist = [CLTitem(367, 3000, (80,0,153), 'Orkan (over 32,6 m/s)'),
               CLTitem(285, 326, (80,13,243), 'Sterk storm (28,5-32,6 m/s)'),
               CLTitem(245, 284, (205,13,243), 'Full storm (24,5-28,4 m/s)'),
               CLTitem(208, 244, (243,13,186), 'Liten storm (20,8-24,4 m/s)'),
               CLTitem(172, 207, (243,13,76), 'Sterk kuling (17,2-20,7 m/s)'),
               CLTitem(139, 171, (243,66,13), 'Stiv kuling (13,9-17,1 m/s)'),
               CLTitem(108, 137, (243,150,13), 'Liten kuling (10,8-13,7 m/s)'),
               CLTitem(80, 107, (243,234,13), 'Frisk bris (8-10,7 m/s)'),
               CLTitem(55, 79, (182,243,13), 'Laber bris (5,5-7,9 m/s)'),
               CLTitem(34, 54, (100,224,121), 'Lett bris (3,4-5,4 m/s)'),
               CLTitem(16, 33, (100,224,187), 'Svak vind (1,6-3,3 m/s)'),
               CLTitem(0, 16, (174,174,174), 'Vindstille (<1,6 m/s)'),
               CLTitem(3001, UintFillValue, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\snowsim\wind_speed_max_10m\wind_speed_max_10m_no_bil.clt")


def __clt_wind_direction_no():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Hovedvindretning',
              'Hovedvindretning i 10 m h�yde',
              'Himmelretning')
    cltlist = [CLTitem(0, 1, (0,0,255), 'N'),
               CLTitem(1, 2, (126, 0, 255), 'N�'),
               CLTitem(2, 3, (255, 0, 215), '�'),
               CLTitem(3, 4, (255, 126, 0), 'S�'),
               CLTitem(4, 5, (255, 0, 0), 'S'),
               CLTitem(5, 6, (255, 245, 0), 'SV'),
               CLTitem(6, 7, (0, 255, 0), 'V'),
               CLTitem(7, 8, (0, 230, 255), 'NV'),
               CLTitem(8, 255, (255, 255, 255), 'Ingen data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\wind_direction_10_no.clt")


def __clt_wind_direction_en():
    from pysenorge.io.png import CLT, HDR, CLTitem
    hdr = HDR(255, 8,
              'Prevailing wind direction',
              'Prevailing wind direction at 10 m above ground',
              'Cardinal direction')
    cltlist = [CLTitem(0, 1, (0,0,255), 'N'),
               CLTitem(1, 2, (126, 0, 255), 'NE'),
               CLTitem(2, 3, (255, 0, 215), 'E'),
               CLTitem(3, 4, (255, 126, 0), 'SE'),
               CLTitem(4, 5, (255, 0, 0), 'S'),
               CLTitem(5, 6, (255, 245, 0), 'SW'),
               CLTitem(6, 7, (0, 255, 0), 'W'),
               CLTitem(7, 8, (0, 230, 255), 'NW'),
               CLTitem(8, 255, (255, 255, 255), 'No data')]
    
    cltfile = CLT()
    cltfile.new(hdr, cltlist)
    cltfile.write(r"Z:\tmp\wind_10m_daily\wind_direction_10_en.clt")
    
if __name__ == "__main__":
    pass
