import csv, json
from geojson import Feature, FeatureCollection, Point, Polygon
import numpy as np
from math import ceil


features = []
header = []
list_of_points = []


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

def renderGeoData(json_file_path, csv_file_path, rssi_max, rssi_min):
    middle = [0, 0]
    counter = 0
    schrittgröße = 10
    faktor = (rssi_max-rssi_min)/schrittgröße # in dem Fall: 12

    # 3D Array initialisieren
    for i in range(0, ceil(faktor)):
        list_of_points.append([])


    with open(json_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None) #skip header
        for id, gateway_id, timestamp, frequency, data_rate, rssi, alt, lat, lon in reader:
            lat, lon = map(float, (lat, lon))

            for i in range(0,ceil(faktor)):
                if (int(rssi) < -i*schrittgröße and int(rssi) >= -(i+1)*schrittgröße):
                    list_of_points[i].append((lon, lat))
                    middle[0] += lon
                    middle[1] += lat
                    counter += 1

    # Mittelpunkt Approximieren
    middle[0] /= counter
    middle[1] /= counter

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

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["id","rssi"])

        for i in range (0, ceil(faktor)):
            index = ceil(faktor) - i - 1
            if (list_of_points[index].__len__() != 0):
                features.append(
                        Feature(
                            geometry = Polygon(
                                    [
                                        list_of_points[index]
                                    ]
                                ),
                            properties = {
                                'timestamp': -index * schrittgröße,
                                'rssi': -index * schrittgröße,
                            },
                            id = str(index)
                        )
                    )

            writer.writerow([str(i),-i * schrittgröße])
            

    collection = FeatureCollection(features)
    with open("Geo.json", "w") as f:
        f.write('%s' % collection)

    return middle

if __name__ == "__main__":
    json_file_path = 'data.csv'
    csv_file_path = 'data2.csv'

    rssi_min = -120
    rssi_max = 0

    middle = renderGeoData(json_file_path, csv_file_path, rssi_max, rssi_min)
    print(middle)