# GeoCATer

A QGIS plugin for rapid geospatial conservation assessments, inspired by the [GeoCAT tool](https://geocat.kew.org/) from the Royal Botanic Gardens, Kew.

GeoCATer calculates the **Extent of Occurrence (EOO)** and **Area of Occupancy (AOO)** of species directly within QGIS, using occurrence records imported from a CSV file — no external web tools required.

## Features

- Import species occurrence data (latitude/longitude + scientific name) from CSV
- Calculate EOO via convex hull
- Calculate AOO via a customizable grid overlay
- Results generated as vector layers within your QGIS project

## Requirements

- QGIS 3.0 or later

## Installation

1. Download or clone this repository
2. Copy the folder to your QGIS plugins directory:
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - Windows: `C:\Users\<user>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
3. Enable the plugin in QGIS: **Plugins → Manage and Install Plugins → GeoCATer**

## Usage

1. Open the GeoCATer panel from the QGIS toolbar
2. Load your CSV file with occurrence records (columns: species name, longitude, latitude)
3. Select the target species
4. Run EOO and/or AOO calculations
5. Output layers will be added to your QGIS project

## Background

EOO and AOO are key metrics under the [IUCN Red List Categories and Criteria](https://www.iucnredlist.org/resources/redlistguidelines) (Criterion B), widely used to assess extinction risk. GeoCATer brings this assessment workflow into a GIS environment, allowing integration with other spatial data and analyses.

## Author

Diego Sousa Campos — [diegosousa.campos@gmail.com](mailto:diegosousa.campos@gmail.com)

## Issues and contributions

Bug reports and suggestions are welcome at the [issue tracker](https://github.com/camposds/GeoCATer/issues).