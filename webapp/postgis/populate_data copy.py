# Populate docker postgis database
# pscopg2 connection, replace *** and *** with your values
import psycopg2
import fiona
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()

def parse_columns(schema):
    columns = []
    for name, value in schema["properties"].items():
        if "LONGITUDE" == name or "LATITUDE" == name:
            continue
        if  "str" in value:
            val_type = "VARCHAR"
        elif "int" in value:
            val_type = "INTEGER"
        elif "float" in value:
            val_type = "DOUBLE PRECISION"
        columns.append(f"{name} {val_type}")
    return columns


files = [file for file in Path("data/shp_plan_regional_parcels").glob("*4326.shp") if "Points" not in file.name]
data = fiona.open(files[0])
parsed_columns = parse_columns(data.schema)
columns = ",".join(["id SERIAL"] + parsed_columns)
connection = psycopg2.connect(f"dbname=postgres user=postgres password='{os.getenv('POSTGRES_PASSWORD')}' host='localhost'")
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS parcels")
cursor.execute(f"""
    CREATE TABLE parcels (
        {columns},

        PRIMARY KEY (id))
""")

cursor.execute("""
    SELECT AddGeometryColumn('parcels', 'geom', 4326, 'MULTIPOLYGON', 2)
""")

cursor.execute("""
    SELECT AddGeometryColumn('parcels', 'geom_c', 4326, 'POINT', 2)
""")

def process_values(row):
    values = []
    for col in parsed_columns:
        value = row["properties"][col.split()[0]]
        if value is None:
            values.append("NULL")
        elif "VARCHAR" in col:
            value = value.replace("'", "")
            values.append(f"'{value}'")
        else:
            values.append(str(value))
    return values
    
def convert_polygon(polygons):
    all_shapes = []
    for polygon in polygons:
        poly = [" ".join([str(item) for item in sublist]) for sublist in polygon]
        poly = f'(({", ".join(poly)}))'
        all_shapes.append(poly)
    return f"{','.join(all_shapes)}"



# use arcpy to get attribute data, populate PostGIS using psycopg2
cols = [col.split()[0] for col in parsed_columns]
for file in files:
    data = fiona.open(file)
    for n, row in enumerate(data):
        if row["properties"]["VIEWID"] == 130605:
            continue
        if row["geometry"]["type"] == "MultiPolygon":
            parcel = ",".join([convert_polygon(shape) for shape in row["geometry"]["coordinates"]])
        else:
            parcel = convert_polygon(row["geometry"]["coordinates"])
        if row["properties"]["LONGITUDE"] == float("inf"):
            point_entry = "NULL"
        else:
            point = str(row["properties"]["LONGITUDE"]) + " " + str(row["properties"]["LATITUDE"])
            point_entry = f"ST_GeometryFromText('POINT({point})', 4326)"
        # the id was transferring as a float so this is just to remove decimal
        row_values = process_values(row)
        # this was tough - everything needs to be a string and text being inserted wrapped in '' including wkt
        try:
            cursor.execute(f"INSERT INTO parcels ({', '.join(cols)}, geom, geom_c) VALUES ({', '.join(row_values)}, ST_GeometryFromText('MULTIPOLYGON({parcel})', 4326), {point_entry})")
        except:
            d = 1
    connection.commit()