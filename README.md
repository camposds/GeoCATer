GeoCATer
GeoCATer is a QGIS plugin designed for conservationists, ecologists, and GIS professionals to perform geospatial conservation assessments efficiently. The plugin facilitates the calculation of two essential metrics: Extent of Occurrence (EOO) and Area of Occupancy (AOO), based on species occurrence data. These metrics are key components of biodiversity assessments in accordance with guidelines provided by the International Union for Conservation of Nature (IUCN).

Features
CSV Import: Easily import species occurrence data, including coordinates and scientific names, from CSV files.
EOO Calculation: Automatically calculate the Extent of Occurrence using the Convex Hull method.
AOO Calculation: Create a grid and calculate the Area of Occupancy based on the number of occupied cells, with a customizable cell size (default is 2x2 km).
Visualization: Generate and visualize polygons for EOO and AOO directly within QGIS.
Installation
To install GeoCATer, follow these steps:

Download the plugin files from this repository or from the official QGIS Plugin Repository.
Open QGIS and go to Plugins > Manage and Install Plugins.
Click on Install from ZIP (if manually downloaded), or search for "GeoCATer" in the plugin repository.
Install the plugin and restart QGIS if necessary.
Usage Instructions
Import CSV Data:
Once the plugin is installed, click the Import CSV button in the plugin’s dock widget.
Ensure that your CSV includes columns for latitude, longitude, and scientific name, named exactly as follows: Latitude, Longitude, Scientific_Name.
Calculate EOO:
After importing the CSV, click the Calculate EOO button.
The plugin will calculate the Convex Hull, which represents the smallest area that includes all points of occurrence, and display the result on the map.
Calculate AOO:
Use the Calculate AOO button to generate a grid and calculate the Area of Occupancy.
Adjust the grid size (default is 2x2 km) in the dock widget if needed.
Exporting Results:
You can export the generated EOO and AOO polygons as shapefiles or other GIS formats for further analysis.
Requirements
QGIS version 3.10 or higher.
Python 3.
Required Python libraries: qgis.core, qgis.PyQt.
Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch: git checkout -b feature-branch.
Commit your changes: git commit -am 'Add a new feature'.
Push to the branch: git push origin feature-branch.
Create a new Pull Request.
Bug Reports & Feature Requests
If you encounter any issues or would like to request a new feature, please submit them via the Issue Tracker.

License
GeoCATer is released under the GPL v3 license.

