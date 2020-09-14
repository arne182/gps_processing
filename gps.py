folder = 'l:\\gps'
import gpxpy.gpx as gpx
from rdp import rdp
import numpy as np
import datetime
import gzip
import os
def writetogpx(f1, file):
  try:
    content = [str(x.strip()) for x in f1]
    content = [i for i in content if i.count("[") == 1 and i.count("]") == 1]
    content2 = []
    for x in content:
      try:
        try:
          c2 = eval(x).decode('ascii')
          content2.append(eval(c2))
        except AttributeError:
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
    if file.endswith(".gpx"):
      continue
    elif file.endswith(".gz"):
      if os.path.exists(os.path.join(root,file[:-3]+'reduced.gpx')):
        continue
      with gzip.open(os.path.join(root,file), 'rb') as f:
        print("Processing " + os.path.join(root,file))
        f1 = f.readlines()
        path = os.path.join(root,file)[:-3]
    else:
      if os.path.exists(os.path.join(root,file+'reduced.gpx')):
        continue
      print("Processing " + os.path.join(root,file))
      f = open(os.path.join(root,file),"r")
      f1=f.readlines()
      path = os.path.join(root,file)
    writetogpx(f1, path) 

