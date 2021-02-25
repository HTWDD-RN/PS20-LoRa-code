import csv, json
from geojson import Feature, FeatureCollection, Point, Polygon, MultiPoint
import numpy as np
import time
from math import ceil

def cart2pol(x, y, offsetx, offsety):
    """
        Karthesisch zu Polarcoordinaten
    """
    x += offsetx
    y += offsety 
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi, offsetx, offsety):
    """
        Polarcoordinaten zu Karthesisch
    """
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    x += offsetx
    y += offsety
    return(x, y)

def getGatewayIds(csv_file_in):
    gateways = []

    with open(csv_file_in, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None) #skip header
        for id, gateway_id, timestamp, frequency, data_rate, rssi, alt, lat, lon in reader:
            if gateway_id not in gateways:
                gateways.append(gateway_id)

    return gateways

# class for returning params from returnGeoData()
class ReturnRenderGeoData:
    def __init__(self, param_middle, param_rssi_min, param_rssi_max):
        self.middle = param_middle
        self.rssi_min = param_rssi_min
        self.rssi_max = param_rssi_max

def renderGeoData(csv_file_in, geo_json, csv_file, rssi_max, rssi_min, schrittgröße, filter = None):
    """
        Preprozessing Data that schould be displayed afterwards
    """
    features = []
    header = []
    list_of_points = []
    middle = [0, 0]
    counter = 0
    faktor = (rssi_max - rssi_min) / schrittgröße

    first = True

    # 3D Array initialisieren
    for i in range(0, ceil(faktor)):
        list_of_points.append([])


    with open(csv_file_in, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None) #skip header
        for id, gateway_id, timestamp, frequency, data_rate, rssi, alt, lat, lon in reader:
            if (filter == None):
                lat, lon = map(float, (lat, lon))
            else:
                if (filter != None) and (gateway_id in filter):
                    lat, lon = map(float, (lat, lon))
                else:
                    continue
            if ((int(rssi)<int(rssi_min)) or first):
                rssi_min = int(rssi)
            if ((int(rssi)>int(rssi_max)) or first):
                rssi_max = int(rssi)
            
            first = False

            # Einordnen in Kategorien
            for i in range(0,ceil(faktor)):
                if (int(rssi) < -i*schrittgröße and int(rssi) >= -(i+1)*schrittgröße):
                    list_of_points[i].append((lon, lat))
                    middle[0] += lon
                    middle[1] += lat
                    counter += 1

            # print(f"Rssi Min {rssi_min}")
            # print(f"Rssi Max {rssi_max}")

    # Mittelpunkt Approximieren
    try:
        middle[0] /= counter
        middle[1] /= counter
    except:
        print("Devision by Zero")
        middle[0] = 0
        middle[1] = 0

    # Sortierung + verschiebung
    for i in range(0, ceil(faktor)):
        for j in range(0, len(list_of_points[i])):
            list_of_points[i][j] = cart2pol(list_of_points[i][j][0], list_of_points[i][j][1], -middle[0], -middle[1])
        list_of_points[i].sort(key=lambda x: x[1])
        for j in range(0, len(list_of_points[i])):
            list_of_points[i][j] = pol2cart(list_of_points[i][j][0], list_of_points[i][j][1], +middle[0], +middle[1])
        try:
            list_of_points[i].append(list_of_points[i][0])
        except:
            pass

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["id","rssi"])

        for i in range (0, ceil(faktor)):
            index = ceil(faktor) - i - 1
            if (list_of_points[index].__len__() != 0):
                features.append(
                    Feature(
                        geometry = Polygon(
                            [list_of_points[index]]),
                        properties = {
                            'rssi': -index * schrittgröße,},
                        id = str(index)
                    )
                )
                #features.append(
                #    Feature(
                #        geometry = MultiPoint(
                #            list_of_points[index]),
                #        properties = {
                #            'rssi': -index * schrittgröße,},
                #        id = str(index) + "Multipoint"
                #    )
                #)

            writer.writerow([str(i),-i * schrittgröße])
            

    collection = FeatureCollection(features)
    with open(geo_json, "w") as f:
        f.write('%s' % collection)

    return ReturnRenderGeoData(middle,rssi_min,rssi_max)


if __name__ == "__main__":
    csv_file_in = './archive/2020_12_10_data.csv'
    geo_json = 'data.geo.json'
    csv_file = 'id-rssi.csv'

    # rssi_min = -120 # schon in app.py
    # rssi_max = 0 # schon in app.py

    schrittgröße = 10

    starttime = time.time()
    print(getGatewayIds(csv_file_in))
    middle = renderGeoData(csv_file_in, geo_json, csv_file, rssi_max, rssi_min, schrittgröße)
    #middle = renderGeoData(csv_file_in, geo_json, csv_file, rssi_max, rssi_min, schrittgröße, filter=["DresdenNeustadt", "eui-dca632ffff85afc2"])
    endtime = time.time()

    print(middle)
    print(f"Total time: {endtime - starttime}")
