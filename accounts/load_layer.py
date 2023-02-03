import os
from django.contrib.gis.utils import LayerMapping
from .models import  RoadsData

roads_mapping = {
    'osm_id': 'osm_id',
    'code': 'code',
    'fclass': 'fclass',
    'name': 'name',
    'ref': 'ref',
    'oneway': 'oneway',
    'maxspeed': 'maxspeed',
    'layer': 'layer',
    'bridge': 'bridge',
    'tunnel': 'tunnel',
    'geom': 'MULTILINESTRING',
}
roads_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/gis_osm_roads_free_1.shp'))

def run(verbose=True):
    lm = LayerMapping(RoadsData, roads_shp, roads_mapping,transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)
