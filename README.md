GeoCATer
GeoCATer is a QGIS plugin designed to assist conservationists, ecologists, and GIS professionals in performing geospatial conservation assessments. The plugin facilitates the calculation of two essential metrics: Extent of Occurrence (EOO) and Area of Occupancy (AOO), based on species occurrence data. These metrics are key components of biodiversity assessments and are used in line with the guidelines provided by the International Union for Conservation of Nature (IUCN).

Features
CSV Import: Easily import species occurrence data, including coordinates and scientific names, from CSV files.
EOO Calculation: Automatically calculate the Extent of Occurrence using the Convex Hull method.
AOO Calculation: Create a grid and calculate Area of Occupancy based on the number of occupied cells, with a customizable cell size (default is 2x2 km).
Visualization: Generate and visualize polygons for EOO and AOO directly within QGIS.
Installation
To install GeoCATer, follow these steps:

Download the plugin files from this repository or from the official QGIS Plugin Repository.
Open QGIS and go to Plugins > Manage and Install Plugins.
Click on Install from ZIP (if manually downloaded), or search for "GeoCATer" in the plugin repository.
Install the plugin and restart QGIS if necessary.
Usage Instructions
Import CSV Data:

Once the plugin is installed, you can start by importing species occurrence data from a CSV file.
Ensure that your CSV includes columns for latitude, longitude, and scientific name.
Use the Import CSV button in the plugin’s dock widget to load the data.
Calculate EOO:

After importing the CSV, click the Calculate EOO button.
The plugin will calculate the Convex Hull, which represents the smallest area that includes all points of occurrence, and display the result on the map.
Calculate AOO:

Use the Calculate AOO button to generate a grid and calculate the Area of Occupancy based on species occurrence.
You can adjust the grid size (default is 2x2 km) in the dock widget.
Visualizing Results:

Both EOO and AOO polygons will be displayed as new layers in QGIS, allowing you to visualize and export the results for further analysis.
Requirements
QGIS version 3.10 or higher.
Python 3.
Contributing
Contributions are welcome! If you would like to contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -am 'Add a new feature').
Push to the branch (git push origin feature-branch).
Create a new Pull Request.
Bug Reports & Feature Requests
If you encounter any issues or would like to request a new feature, please submit them via the Issue Tracker.

License
GeoCATer is released under the GPL v3 license.
