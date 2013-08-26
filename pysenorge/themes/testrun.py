# '''
# Created on 20.08.2013
#  
# @author: ralf
#
#test two different 
# '''
from PIL import Image
from random import sample

ob_img = Image.open("/home/ralf/Dokumente/summerjob/data/wind_speed_avg_1500m/2013/wind_speed_avg_1500m_2013_08_17.png")
ob_img_old = Image.open("/home/ralf/Dokumente/summerjob/windmodel/data/wind_speed_avg_10m/2012/old_wind_speed_avg_10m_2012_01_06.png")


img = ob_img.load()
img_old = ob_img_old.load()

li = {}
height, width = ob_img.size
for j in sample(xrange(width),250):
    count=0
    for i in xrange(height):
        if img[i,j] != (255, 255, 255, 255):
            if img_old[i-1,j]==(255, 255, 255, 255) and img_old[i,j]!=(255, 255, 255, 255):
                print "New and Old pic have the same raster",i
                break
            else: 
                "Error in new Raster"
        else:
            count+=1    
    if count != i:
        if count == height:
            print "only NA values"
        else:
            print "Problem: ","height:",count," width:",j
            li.update({count:j})

print li
print len(li)

lisa = "GIT PULL"
print lisa 

