import requests

"""This class contains few geolocation functions. The constructor of this class takes a string as parameter. The string is your access key 
obtained after creating an account on mapbox
The class has 3 methods. 1) calculateDistance(), this function takes two coordinates as inputs, the coordinates are to be inputted as 
strings in the format "lat,long" without any spaces. The function returns the shortest road distance between the two coordinates in km
2) calculateTravelTime(), this function takes two coordinates as inputs and returns the time taken to travel from the first 
coordinate to second coordinate. The travel time is in minutes.
3) servicesNearby(), this function takes three inputs, the central coordinate, the radius around the coordinate and the type of service
The method then finds all the services around the central coordinate within the given radius and returns the coordinates and addresses
of the services."""
class Geolocation():
    def __init__(self, key):
        self.key = key

    def calculateDistance(self, start, end):
        start = start.split(",")
        end = end.split(",")
        start.reverse()
        end.reverse()

        revstart = "" + start[0] + "," + start[1]
        revend = "" + end[0] + "," + end[1]

        url = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
        r = requests.get(url + revstart + ';' + revend + '?geometries=geojson&access_token=' + self.key)
        y = r.json()

        distance = y['routes'][0]['distance']
        return distance/1000.0

    def calculateTravelTime(self, start, end):
        start = start.split(",")
        end = end.split(",")
        start.reverse()
        end.reverse()

        revstart = "" + start[0] + "," + start[1]
        revend = "" + end[0] + "," + end[1]

        url = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
        r = requests.get(url + revstart + ';' + revend + '?geometries=geojson&access_token=' + self.key)
        y = r.json()

        time = y['routes'][0]['duration']
        return time/60.0

    def servicesNearby(self, central, radius, service):
        central = central.split(",")

        url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/'

        invertedCentral = central[1] + "," + central[0]
        coordinateList = [invertedCentral]

        addressList = []

        increments = 1

        if radius <= 3:
            minlong = float(central[1]) - radius/100.0
            minlat = float(central[0]) - radius/100.0
            maxlong = float(central[1]) + radius/100.0
            maxlat = float(central[0]) + radius/100.0
            r = requests.get(url + service + '.json?bbox=' + str(minlong) +','+ str(minlat) +','+ str(maxlong) +','+ str(maxlat) + '&access_token=' + self.key)

            x = r.json()
            url2 = 'https://api.mapbox.com/directions/v5/mapbox/driving/'

            for i in x["features"]:
                r2 = requests.get(url2 + invertedCentral + ';' + str(i["center"][0]) + "," + str(i["center"][1]) + '?geometries=geojson&access_token=' + self.key)
                y = r2.json()
                distance = int(y['routes'][0]['distance'])

                if distance < radius * 1000:
                    coordinateList.append(str(i["center"][1]) + "," + str(i["center"][0]))
                    addressList.append(i["place_name"])
        else:
            currentRad = increments
            while currentRad <= radius:
                minlong = float(central[1]) - currentRad/100.0
                minlat = float(central[0]) - currentRad/100.0
                maxlong = float(central[1]) + currentRad/100.0
                maxlat = float(central[0]) + currentRad/100.0

                r = requests.get(url + service + '.json?bbox=' + str(minlong) +','+ str(minlat) +','+ str(maxlong) +','+ str(maxlat) + '&access_token=' + self.key)

                x = r.json()
                url2 = 'https://api.mapbox.com/directions/v5/mapbox/driving/'

                for i in x["features"]:
                    if str(i["center"][0]) + "," + str(i["center"][1]) not in coordinateList:
                        r2 = requests.get(url2 + invertedCentral + ';' + str(i["center"][0]) + "," + str(i["center"][1]) + '?geometries=geojson&access_token=' + self.key)
                        y = r2.json()
                        distance = int(y['routes'][0]['distance'])

                        if distance < radius * 1000:
                            coordinateList.append(str(i["center"][1]) + "," + str(i["center"][0]))
                            addressList.append(i["place_name"])

                if currentRad == radius:
                    currentRad = radius + 1
                else:
                    if currentRad + increments > radius:
                        currentRad = radius
                    else:
                        currentRad += increments

        return {"coordinates": coordinateList, "addresses": addressList}
