import os
from django.contrib.gis.utils import LayerMapping
from .models import  Road

road_mapping = {
    'name': 'name',
    'length_m': 'length_m',
    'lineid': 'lineid',
    'lat_n1': 'lat_n1',
    'long_n1': 'long_n1',
    'long_n2': 'long_n2',
    'lat_n2': 'lat_n2',
    'geom': 'MULTILINESTRING',
}
road_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/segment-intersection.shp'))

def run(verbose=True):
    lm = LayerMapping(Road, road_shp, road_mapping,transform=False, encoding='iso-8859-1')
    lm.save(strict=False, verbose=verbose)
