# -*- coding: utf-8 -*-

# This script takes a csv containing gps information from a car doing laps
# around a racetrack. The output is a shapefile containing polylines for each 
# lap around the track. 

import arcpy, csv, os
arcpy.env.overwriteOutput = True

# Set up input variables
spreadsheet = r"C:/Users/.../WakefieldParkRaceway_20160421.csv"
output = r"C:/Users/.../racetrack.shp"

# Create function that will insert lap numbers as keys and coordinates as values of those keys 
# in a dictionary
def lapCoords(lapNums, coord, lapList):
    if lapNums not in lapList:
        lapList[lapNums] = [(coord)]
    else:
        lapList[lapNums].append((coord))

# Set up a try/except to handle errors
try: 
    # Open the CSV file and read the header line
    observations = open(spreadsheet, "r")
    csvReader = csv.reader(observations)
    header = next(csvReader)

    # Determine the indiced of the columns for lap number, lon, and lat
    lapIndex = header.index("Lap")
    latIndex = header.index("Latitude")
    lonIndex = header.index("Longitude")

    # Create an empty dictionary to hold lap numbers and coordinates
    laps = {}

    # Loop through the csv and use the lapCoords function to place each lap key and coordinate 
    # value in the laps dictionary. Use if statement to avoid lap time lines
    # Another if statement removes the first lap and a delete statement removes
    # the final lap to eliminate data that goes outside of the track
    times = []
    for row in csvReader:
        if not row[0].startswith("#"):
            if int(row[1]) > 0:
                lapNumber = int(row[lapIndex])
                lon = float(row[lonIndex])
                lat = float(row[latIndex])
                coords = (lon, lat)
                lapCoords(lapNumber, coords, laps)
    del laps[sorted(laps.keys())[-1]]
      

    # Create new polyline feature class using WGS84. Add a lap field to the feature class
    sr = arcpy.SpatialReference(4326)
    outputFolder = os.path.dirname(output)
    outputFile = os.path.basename(output)
    arcpy.CreateFeatureclass_management(outputFolder, outputFile, "POLYLINE","","","", sr)
    arcpy.AddField_management(output, "Lap", "SHORT")

    # Add a single polyline created from coordinates to the new shapefile
    for lap in laps: 
        with arcpy.da.InsertCursor(output, ("SHAPE@", "Lap")) as cursor: 
            cursor.insertRow((laps[lap], lap))
        del cursor

except:
    print("An error has caused the script to fail.")

    
