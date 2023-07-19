# Green Spatial Engineering
We introduce some common practices doing spatial data science in a carbon effective way.

## Introduction
Spatial data science offers insights into various domains, but also uses computing resources and emits greenhouse gases.

*We honestly believe, that if we focus on carbon effective spatial data science, we become part of the climate solution. We are focusing on reducing the negative impacts of spatial data science calculations on our climate by reducing the carbon emissions.*

We introduce some common practices doing spatial data science in a carbon effective way.

If you are interested in the common green software engineering approach. You should have a look at the [Green Software Foundation](https://greensoftware.foundation/).

## Setup your spatial data science environment

Our spatial data science environment is based upon Python and pip/conda. So that we are using a lightweight Python module estimating the amount of carbon dioxide produced by the spatial data science compute workflow.

If you are using conda you can install CodeCarbon using the condaforge channel.

### Installing CodeCarbon into a conda environment

```
conda install -c codecarbon -c conda-forge codecarbon=2.2
```

* [CodeCarbon Motivation](https://mlco2.github.io/codecarbon/motivation.html)
* [CodeCarbon Methodology](https://mlco2.github.io/codecarbon/methodology.html)
* [CodeCarbon Installation](https://mlco2.github.io/codecarbon/installation.html)

## Methods
The spatial data science workflows represents the most common use cases we experienced during our daily work.

ArcGIS Notebooks provide a cloud-native Software-as-a-Service solution optimized for spatial data science. Every notebook starts a dedicated instance running in the cloud. So that we can easily extend this Python environment using the CodeCarbon module.

### Live Traffic
The city of Bonn provides real-time traffic information on the three Rhine bridges and the most important inner-city main roads of Bonn. Every 5 minutes the traffic information is updated.

We want to collect the real-time traffic information using a dedicated feature service running in our ArcGIS Online instance. The estimated carbon emissions need to be preprocessed and serialized into a feature service. The emission tracker uses a location API detecting in which cloud region the Python process is running.

#### ArcGIS utility functions for collecting and estimating
```python
from arcgis.gis import GIS
from arcgis.features import FeatureSet, GeoAccessor
from codecarbon import EmissionsTracker
import logging
import pandas as pd
import requests
import sys

def query_traffic():
    url = 'http://stadtplan.bonn.de/geojson?Thema=19584'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def prepare_emissions(tracker):
    emissions_data = tracker.final_emissions_data
    emissions_df = pd.DataFrame.from_records([dict(emissions_data.values)])
    emissions_df['timestamp'] = pd.to_datetime(emissions_df['timestamp'])
    emissions_sdf = GeoAccessor.from_xy(emissions_df, 'longitude', 'latitude')
    emissions_sdf.rename(columns={
        'project_name': 'project',
        'emissions_rate': 'rate',
        'energy_consumed': 'consumed',
        'country_name': 'country',
        'country_iso_code': 'iso_code',
        'cloud_provider': 'provider',
        'cloud_region': 'cloud',
        'codecarbon_version': 'codecarbon',
        'python_version': 'python',
        'ram_total_size': 'ram_total',
        'tracking_mode': 'tracking'
    }, inplace=True)
    return emissions_sdf

def prepare_traffic(traffic_featureset):
    traffic_sdf = traffic_featureset.sdf[['strecke_id', 'auswertezeit', 'geschwindigkeit', 'verkehrsstatus', 'SHAPE']]
    traffic_sdf['auswertezeit'] = pd.to_datetime(traffic_sdf['auswertezeit'])
    traffic_sdf['geschwindigkeit'] = pd.to_numeric(traffic_sdf['geschwindigkeit'])
    traffic_sdf.rename(columns={
        'strecke_id': 'seg_id',
        'auswertezeit': 'time',
        'geschwindigkeit': 'speed',
        'verkehrsstatus': 'traffic'
    }, inplace=True)
    return traffic_sdf

def publish_emissions(tracker):
    emissions_sdf = prepare_emissions(tracker)
    return emissions_sdf.spatial.to_featurelayer(title='Carbon Emissions', folder='Stadt Bonn', tags=['Open Data', 'Carbon', 'Digital Twin'])

def publish_traffic(traffic_featureset):
    traffic_sdf = prepare_traffic(traffic_featureset)
    return traffic_sdf.spatial.to_featurelayer(title='Stadt Bonn - Aktuelle Straßenverkehrslage', folder='Stadt Bonn', tags=['Open Data', 'Traffic', 'Digital Twin'])

def add_emissions(emissions_featurelayer, tracker):
    emissions_sdf = prepare_emissions(tracker)
    new_features = emissions_sdf.spatial.to_featureset().features      
    edit_result = emissions_featurelayer.edit_features(adds=new_features)
    return edit_result

def add_traffic(traffic_featurelayer, traffic_featureset):
    traffic_sdf = prepare_traffic(traffic_featureset)
    new_features = traffic_sdf.spatial.to_featureset().features      
    edit_result = traffic_featurelayer.edit_features(adds=new_features)
    return edit_result

def find_emissions(gis):
    portal_items = gis.content.search(query='title:Carbon Emissions AND tags:"Open Data"', item_type='Feature Layer')
    if 0 < len(portal_items):
        first_portal_item = portal_items[0]
        if 0 < len(first_portal_item.layers):
            return first_portal_item.layers[0]
        
    return None

def find_traffic(gis):
    portal_items = gis.content.search(query='title:Stadt Bonn - Aktuelle Straßenverkehrslage AND tags:"Open Data"', item_type='Feature Layer')
    if 0 < len(portal_items):
        first_portal_item = portal_items[0]
        if 0 < len(first_portal_item.layers):
            return first_portal_item.layers[0]
        
    return None
```

The emission tracker estimates the carbon emissions. The following snippet represents the live traffic implementation. It validates whether or not a dedicated feature layer was already published. If not a new feature service hosting the carbon emissions and the traffic information is created.

#### Snippet for collecting and estimating
```python
gis = GIS("home")

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
root.addHandler(handler)

tracker = EmissionsTracker(project_name='Open Data Bonn', output_dir='/arcgis/home/')
tracker.start()

traffic_geojson = query_traffic()
traffic_featureset = FeatureSet.from_geojson(traffic_geojson)

traffic_featurelayer = find_traffic(gis)
if None is traffic_featurelayer:
    publish_result = publish_traffic(traffic_featureset)
    logging.info(publish_result)
else:
    delete_result = traffic_featurelayer.delete_features(where='1=1')
    logging.info(delete_result)
    add_result = add_traffic(traffic_featurelayer, traffic_featureset)
    logging.info(add_result)

emissions = tracker.stop()

emissions_featurelayer = find_emissions(gis)
if None is emissions_featurelayer:
    publish_result = publish_emissions(tracker)
    logging.info(publish_result)
else:
    add_result = add_emissions(emissions_featurelayer, tracker)
    logging.info(add_result)

emissions
```

## Results
The Green Spatial Engineering Dashboard shows the estimated carbon equivalents in kilograms for our spatial data science workflows. The first use case represents the carbon footprint for querying and collecting the real-time traffic information from the city of Bonn every 15 minutes.

![Screenshot Green Spatial Engineering](https://github.com/EsriDE/green-spatial-engineering/assets/3008093/738c522e-fef0-46cb-8d8f-057c20148cfd)

## Links
* [GeoDev Germany Community](https://community.esri.com/t5/geodev-germany/ct-p/geodev-germany)
