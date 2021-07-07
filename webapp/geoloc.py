import geopandas as gpd
from shapely.geometry import Point

country_geo = gpd.read_file('/home/pi/Downloads/cb_2019_us_tract_500k.shp')
country_geo.head()

