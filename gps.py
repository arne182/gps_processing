folder = 'l:\\gps'
import gpxpy.gpx as gpx
from rdp import rdp
import numpy as np
import datetime
import sqlite3
import gzip
import os

def connectdatabase():
  conn = sqlite3.connect('L:\\reduced.db', isolation_level='DEFERRED')
  c = conn.cursor()
  c.execute("""CREATE TABLE IF NOT EXISTS gps(
               time DECIMAL(12,8),
               lat DECIMAL(3,15),
               lon DECIMAL(3,15),
               altitude DECIMAL(5,15),
               bearing DECIMAL(5,15),
               speed DECIMAL(3,15),
               accuracy DECIMAL(3,15),
               osm_way_id DECIMAL(12,0),
               file_id INTEGER,
               PRIMARY KEY(time, lat, lon))""")
  c.execute("""CREATE TABLE IF NOT EXISTS file(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               file_name TEXT NOT NULL UNIQUE)""")
  return conn

def writedatabase(conn, time, lat, lon, altitude, bearing, speed, accuracy, osm_way_id, file_id):
  c = conn.cursor()
  try:
    c.execute("INSERT INTO gps VALUES(" + str(time) + "," + str(lat) + "," + str(lon) + "," + str(altitude) + "," + str(bearing) + "," + str(speed) + "," + str(accuracy) + "," + str(osm_way_id)  + "," + str(file_id) + ")")
  except:
    pass
  return
  
def writetogpx(f1, file, conn):
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
    c = conn.cursor()
    try:
      c.execute("INSERT INTO file (file_name) VALUES('" + file + "')")
    except:
      pass
    if len(gps_acc) == 0:
      return
    gps = [x[2:4] for x in gps_acc]
    gps_acc = np.array(gps_acc)
    gps_simple_mask = rdp(gps, epsilon=5e-6, return_mask=True)
    gps_acc = gps_acc[gps_simple_mask]
    c.execute("SELECT id from file WHERE file_name='" + file + "'")
    file_id = c.fetchall()[0][0]
    for x in gps_acc:
      if len(x) == 8:
        osm = int(x[7])
      else:
        osm = 0
      writedatabase(conn,x[6],x[2],x[3],x[4],x[1],x[0],x[5],osm, file_id)
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

conn = connectdatabase()
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
      try:
        f1=f.readlines()
      except UnicodeDecodeError:
        f1.pop()
      path = os.path.join(root,file)
    writetogpx(f1, path, conn) 
conn.close()
