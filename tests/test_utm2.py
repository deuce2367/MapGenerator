import mgrs
m = mgrs.MGRS()
s = m.UTMToMGRS(18, 'N', 584482.0, 4505935.0)
lat, lon = m.toLatLon(s)
print(lat, lon)
