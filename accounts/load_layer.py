import os
from django.contrib.gis.utils import LayerMapping
from .models import LocalAddress, Counties


local_address_mapping = {
    'province': 'PROVINCE',
    'district': 'DISTRICT',
    'unit_type': 'UNIT_TYPE',
    'unit_name': 'UNIT_NAME',
    'district_c': 'DISTRICT_C',
    'shape_leng': 'SHAPE_LENG',
    'shape_area': 'SHAPE_AREA',
    'geom': 'MULTIPOLYGON',
}

local_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/local_level.shp'))




counties_mapping = {
    'counties': 'Counties',
    'codes': 'Codes',
    'cty_code': 'Cty_CODE',
    'dis': 'dis',
    'geom': 'MULTIPOLYGON',
}
counties_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/counties.shp'))

def run_counties(verbose=True):
    lm = LayerMapping(Counties, counties_shp, counties_mapping, transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)



def run(verbose=True):
    lm = LayerMapping(LocalAddress, local_shp, local_address_mapping,transform=False, encoding='iso-8859-1')
    lm.save(strict=False, verbose=verbose)
