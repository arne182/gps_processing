folder = 'l:\\gps'
import gpxpy.gpx as gpx
from rdp import rdp
import numpy as np
import datetime
import os
def writetogpx(file):
  try:
    f = open(file,"r")
    f1=f.readlines()
    content = [x.strip() for x in f1]
    content = [i for i in content if i.count("[") == 1 and i.count("]") == 1]
    content2 = []
    for x in content:
      try:
        content2.append(eval(x))
      except ValueError:
        continue
    gps_acc = []
    for x in content2:
      if x[5] < 2.0:
        gps_acc.append(x)
    gps = [x[2:4] for x in gps_acc]
    gps_acc = np.array(gps_acc)
    gps_simple_mask = rdp(gps, epsilon=5e-6, return_mask=True)
    gps_acc = gps_acc[gps_simple_mask]
    gpx2 = gpx.GPX()
    gpx_track2 = gpx.GPXTrack()
    gpx2.tracks.append(gpx_track2)
    gpx_segment2 = gpx.GPXTrackSegment()
    gpx_track2.segments.append(gpx_segment2)
    for x in gps_acc:
      gpx_segment2.points.append(gpx.GPXTrackPoint(x[2], x[3], elevation=x[4], time=datetime.datetime.utcfromtimestamp(x[6])))
    with open(file+'reduced.gpx', "w") as f:
      f.write(gpx2.to_xml())
  except:
    pass

for root, subFolders, files in os.walk(folder):
  for file in files:
    writetogpx(os.path.join(root,file))

