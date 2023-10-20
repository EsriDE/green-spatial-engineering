from arcgis.features import FeatureSet, GeoAccessor
from codecarbon import track_emissions
from configparser import ConfigParser
import json
import logging
import os
import pandas as pd
import sqlite3 as sql
import warnings

def read_geojson_as_sdf(filepath: str, encoding: str='utf8'):
    """
    Reads a GeoJSON file as a FeatureSet.
    """
    with open(filepath, encoding=encoding) as in_stream:
        return FeatureSet.from_geojson(json.load(in_stream)).sdf
    
def read_sqlite_as_sdf(db_filepath: str, select_statement: str, x_column: str='longitude', y_column: str='latitude'):
    """
    Reads the data from a sqlite database into main memory using a SQL statement.
    """
    with sql.connect(db_filepath) as connection:
        df = pd.read_sql_query(select_statement, connection)
        return GeoAccessor.from_xy(df, x_column, y_column)
    
config = ConfigParser()
config.read('config.user')

@track_emissions(project_name='Urban Digital Twin Bonn', output_file='emissions.user', offline=True, country_iso_code='USA')
def urban_intersect():
    logger = logging.getLogger('codecarbon')
    logger.info('Load urban datasets...')
    districts_sdf = read_geojson_as_sdf(config['DEFAULT']['CityDistrictsFilePath'], encoding='cp1252')
    streets_sdf = read_geojson_as_sdf(config['DEFAULT']['CityStreetFilePath'])
    if 'area' in streets_sdf.columns:
        streets_sdf = streets_sdf[streets_sdf['area'].isna()]
    traffic_sdf = read_sqlite_as_sdf(config['DEFAULT']['TrafficFilePath'], 'SELECT * from agent_pos LIMIT 10;')
    logger.info('Urban datasets loaded.')
    
    logger.info('Intersecting traffic with city districts...')
    traffic_joined_districts_sdf = traffic_sdf.spatial.join(districts_sdf, how='inner', op='intersects')
    logger.info(f'{traffic_joined_districts_sdf.shape[0]} traffic locations have intersections with city districts.')
    
    warnings.filterwarnings('ignore')
    
    logger.info('Projecting city streets...')
    streets_sdf.spatial.project(25832, 'DHDN_To_WGS_1984_4_NTv2')
    logger.info(f'{streets_sdf.shape[0]} city streets were projected.')
    
    logger.info('Projecting traffic locations...')
    traffic_sdf.spatial.project(25832, 'DHDN_To_WGS_1984_4_NTv2')
    logger.info(f'{traffic_sdf.shape[0]} traffic locations were projected.')
    
    warnings.filterwarnings('default')
    
    logger.info('Constructing city streets buffer...')
    buffered_streets_sdf = streets_sdf.copy()
    buffered_streets_sdf.SHAPE = streets_sdf.SHAPE.geom.buffer(50)
    logger.info(f'{buffered_streets_sdf.shape[0]} city streets buffer were constructed.')
    
    logger.info('Intersecting traffic with city streets buffer...')
    traffic_joined_buffered_streets_sdf = traffic_sdf.spatial.join(buffered_streets_sdf, how='inner', op='intersects')
    logger.info(f'{traffic_joined_districts_sdf.shape[0]} traffic locations have intersections with city streets buffer.')
    
    # Join traffic with intersected streets buffer with original streets
    # Calculate distance between traffic location and corresponding streets
    logger.info('Calculating distances to city streets...')
    traffic_joined_streets_sdf = pd.merge(traffic_joined_buffered_streets_sdf, streets_sdf, how='left', on='F_id', suffixes=['', '_street'])
    traffic_joined_streets_sdf['distance_to'] = traffic_joined_streets_sdf.SHAPE.geom.distance_to(traffic_joined_streets_sdf.SHAPE_street)
    logger.info(f'{traffic_joined_streets_sdf.shape[0]} distances to city streets were calculated.') 

urban_intersect()