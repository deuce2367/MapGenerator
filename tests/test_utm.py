import mgrs
m = mgrs.MGRS()
mgrs_str = m.toMGRS(40.7, -74.0)
print(mgrs_str)
utm = m.MGRSToUTM(mgrs_str)
print(utm)
