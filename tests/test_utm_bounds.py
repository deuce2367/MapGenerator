import mgrs
m = mgrs.MGRS()
# New York is zone 18 T
# Let's test a coordinate way outside
try:
    s = m.UTMToMGRS(18, 'T', -500000.0, 4500000.0)
    print("Negative easting worked:", s)
except Exception as e:
    print("Negative easting failed:", e)

try:
    s = m.UTMToMGRS(18, 'T', 500000.0, 95000000.0)
    print("Huge northing worked:", s)
except Exception as e:
    print("Huge northing failed:", e)
