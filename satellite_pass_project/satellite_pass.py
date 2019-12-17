#https://www.celestis.com/resources/faq/what-are-the-azimuth-and-elevation-of-a-satellite/
#https://www.timeanddate.com/astronomy/different-types-twilight.html

import pytz
import requests
import json
from pprint import pprint
from datetime import datetime
from keys import *

N2YO_URL = "https://www.n2yo.com/rest/v1/satellite/"
MAPQUEST_GEO_URL = "http://www.mapquestapi.com/geocoding/v1/"
MAPQUEST_ELEVATION_URL = "http://open.mapquestapi.com/elevation/v1/profile"
OPEN_WEATHER_URL = "http://api.openweathermap.org/data/2.5/forecast"
SOLUNAR_URL = "https://api.solunar.org/solunar/"
SUNRISE_SUNSET_URL = "https://api.sunrise-sunset.org/json?"

SATELLITES = {
    "SPACE STATION" : "25544",
    "DAVINCI" : "43857", #North Idaho
    "MAKERSAT-0" : "43016", #NNU
    "NEPALISAT1" : "44329",
    "HST" : "20580",
    "AEOULUS" : "43600",
}


class Satellite_Pass:

    def __init__(self, address, recipient, satellite_id,
        lat=None, lng=None,
        elevation=None,
        passes=None, next_pass=None, pass_count=None, satellite_name=None,
        forecast=None,
        nautical_twilight_dawn = None, nautical_twilight_dusk = None,
        moonrise = None, moonset = None, moon_phase = None):

        #from user
        self.address = address
        self.recipient = recipient
        self.satellite_id = satellite_id

        #from Mapquest Geocode API
        self.lat = lat
        self.lng = lng

        #from Mapquest Open Elevation API
        self.elevation = elevation

        #from N2YO API
        self.passes = passes
        self.next_pass = next_pass
        self.pass_count = pass_count
        self.satellite_name = satellite_name

        #from Open Weather API
        self.forecast = forecast

        #from Sunrise Sunset API
        self.nautical_twilight_dawn = nautical_twilight_dawn
        self.nautical_twilight_dusk = nautical_twilight_dusk
        
        #from Solunar API
        self.moonrise = moonrise
        self.moonset = moonset
        self.moon_phase = moon_phase


    #FUNCTIONS TO UPDATE INSTANCE VARIABLES
    def get_location_data(self):
    #url = "http://www.mapquestapi.com/geocoding/v1/address?key=KEY&location=Washington,DC"
        url = f"{MAPQUEST_GEO_URL}address?key={MAPQUEST_KEY}&location={self.address}"
        response = requests.get(url).json()
        locations = response.get("results")[0].get("locations")[0]
        self.lat = locations.get("latLng").get("lat")
        self.lng = locations.get("latLng").get("lng")
        address = ""
        if locations.get("street"):
            address = address + locations.get("street") + " "
        else:
            address = address + locations.get("adminArea6Type") + " in "
        address = address + locations.get("adminArea5") + ", "
        address = address + locations.get("adminArea4") + ", "
        address = address + locations.get("adminArea3") + ", "
        address = address + locations.get("adminArea1")

        self.address = address
    
    def get_elevation(self):
        url = f"{MAPQUEST_ELEVATION_URL}?key={MAPQUEST_KEY}&unit=f&shapeFormat=raw&latLngCollection={self.lat},{self.lng}"
        response = requests.get(url).json()
        self.elevation = response.get("elevationProfile")[0].get("height")

    def get_visual_passes(self):
        url = f"{N2YO_URL}/visualpasses/{self.satellite_id}/{self.lat}/{self.lng}/{self.elevation}/5/60&apiKey={N2YO_KEY}"
        response = requests.get(url).json()
        self.satellite_name = response.get("info").get("satname")
        self.next_pass = (response.get("passes")[0].get("startUTC"), response.get("passes")[0].get("endUTC"),)
        self.passes = response.get("passes")
        self.pass_count = response.get("info").get("passescount")

    def get_forecast(self):
        url = f"{OPEN_WEATHER_URL}?lat={self.lat}&lon={self.lng}&appid={OPEN_WEATHER_KEY}"
        response = requests.get(url).json()
        weather_list = response.get("list")
        i = 0
        while i+1 < len(weather_list):
            if int(weather_list[i].get("dt")) <= int(self.next_pass[1]):
        	    if int(weather_list[i+1].get("dt")) > int(self.next_pass[1]):
        		    self.forecast = (weather_list[i].get("weather")[0].get("main"),
                      weather_list[i].get("weather")[0].get("description"),)
            i += 1

    def get_lunar_data(self):
        url = f"{SOLUNAR_URL}{self.lat},{self.lng},{datetime.utcfromtimestamp(int(self.next_pass[0])).strftime('%Y%m%d')},0"
        response = requests.get(url).json()
        moonrise = response.get("moonRise")
        moonset = response.get("moonSet")
        self.moon_phase = response.get("moonPhase")

        if moonrise:
            moonrise = f"{datetime.utcfromtimestamp(int(self.next_pass[0])).strftime('%Y%m%d')} {moonrise} UTC"
            self.moonrise = datetime.strptime(moonrise, '%Y%m%d %H:%M %Z')
        else:
            self.moonrise = None

        if moonset:
            moonset = f"{datetime.utcfromtimestamp(int(self.next_pass[0])).strftime('%Y%m%d')} {moonset} UTC"
            self.moonset = datetime.strptime(moonset, '%Y%m%d %H:%M %Z')
        else:
            self.moonset = None

    #ATTRIBUTION: https://sunrise-sunset.org/api
    def get_twilight_data(self):
        pass_day = datetime.utcfromtimestamp(int(self.next_pass[0])).strftime('%Y-%m-%d')
        url = f"{SUNRISE_SUNSET_URL}lat={self.lat}&lng={self.lng}&formatted=0&date={pass_day}"
        response = requests.get(url).json()

        twilight_dusk_start = response.get("results").get("civil_twilight_end")
        twilight_dusk_start = twilight_dusk_start[:-6:] + " UTC"
        twilight_dusk_end = response.get("results").get("nautical_twilight_end")
        twilight_dusk_end = twilight_dusk_end[:-6:] + " UTC"
        twilight_dusk_start = datetime.strptime(twilight_dusk_start, '%Y-%m-%dT%H:%M:%S %Z')
        twilight_dusk_end = datetime.strptime(twilight_dusk_end, '%Y-%m-%dT%H:%M:%S %Z')
        self.nautical_twilight_dusk = (twilight_dusk_start, twilight_dusk_end,)

        twilight_dawn_start = response.get("results").get("nautical_twilight_begin")
        twilight_dawn_start = twilight_dawn_start[:-6:] + " UTC"
        twilight_dawn_end = response.get("results").get("civil_twilight_begin")
        twilight_dawn_end = twilight_dawn_end[:-6:] + " UTC"
        twilight_dawn_start = datetime.strptime(twilight_dawn_start, '%Y-%m-%dT%H:%M:%S %Z')
        twilight_dawn_end = datetime.strptime(twilight_dawn_end, '%Y-%m-%dT%H:%M:%S %Z')
        self.nautical_twilight_dawn = (twilight_dawn_start, twilight_dawn_end,)

    #FUNCTIONS TO DISPLAY DATA
    def get_location_info(self):
        overview = "\nLOCATION INFORMATION\n"
        overview = overview + ("%-25s %s\n" % ("Location", self.address))
        overview = overview + ("%-25s %s%s\n" % ("Latitude", self.lat, "°"))
        overview = overview + ("%-25s %s%s\n" % ("Longitude", self.lng, "°"))
        overview = overview + ("%-25s %s %s\n" % ("Elevation", self.elevation, "ft. above sea level"))
        return overview

    def get_satellite_info(self):
        overview = "\nSATELLITE INFORMATION\n"
        overview = overview + ("%-25s %s\n" % ("Name", self.satellite_name))
        overview = overview + ("%-25s %s\n" % ("NORAD Identifier", self.satellite_id,))
        overview = overview + ("%-25s %s\n" % ("Next Pass Start", datetime.utcfromtimestamp(int(self.next_pass[0])).strftime('%Y-%m-%d %H:%M:%S %Z')))
        overview = overview + ("%-25s %s\n" % ("Next Pass End", datetime.utcfromtimestamp(int(self.next_pass[1])).strftime('%Y-%m-%d %H:%M:%S %Z')))
        overview = overview + ("%-25s %s\n" % ("Time Remaining", 
            strfdelta((datetime.utcfromtimestamp(int(self.next_pass[0])) - datetime.utcnow()),
             "{days} days {hours} hours {minutes} minutes {seconds} seconds")))
        return overview

    def get_conditions_info(self):
        overview = "\nCONDITIONS INFORMATION\n"
        overview = overview + ("%-25s %s\n" % ("Forecast", self.forecast[1].title()))
        overview = overview + ("%-25s %s\n" % ("Moon Phase", self.moon_phase))
        overview = overview + ("%-25s %s\n" % ("Moonrise", self.moonrise))
        overview = overview + ("%-25s %s\n" % ("Moonset", self.moonset))
        overview = overview + ("%-25s %s\n" % ("Dawn Nautical Start", self.nautical_twilight_dawn[0]))
        overview = overview + ("%-25s %s\n" % ("Dawn Nautical End", self.nautical_twilight_dawn[1]))
        overview = overview + ("%-25s %s\n" % ("Dusk Nautical Start", self.nautical_twilight_dusk[0]))
        overview = overview + ("%-25s %s\n" % ("Dusk Nautical End", self.nautical_twilight_dusk[1]))
        return overview

    def get_trajectory_info(self):
        
        if len(self.passes) > 0:
            
            pass_info = self.passes[0]
            duration = str(pass_info.get("duration")) + " seconds"
            starting_azimuth = f'{pass_info.get("startAz")}° {pass_info.get("startAzCompass")} at {pass_info.get("startEl")}° elevation'
            maximum_azimuth = f'{pass_info.get("maxAz")}° {pass_info.get("maxAzCompass")} at {pass_info.get("maxEl")}° elevation'
            ending_azimuth = f'{pass_info.get("endAz")}° {pass_info.get("endAzCompass")} at {pass_info.get("endEl")}° elevation'
            
            overview ="\nTRAJECTORY INFORMATION\n"
            overview = overview + ("%-25s %s\n" % ("Duration of Pass", duration))
            overview = overview + ("%-25s %s\n" % ("Starting Azimuth", starting_azimuth))
            overview = overview + ("%-25s %s\n" % ("Maximum Azimuth", maximum_azimuth))
            overview = overview + ("%-25s %s\n" % ("Ending Azimuth", ending_azimuth))
            return overview

    def get_assessment(self):
        
        #For these, True is good
        azimuth_bool = False
        nautical_bool = False

        #For these, True is bad
        weather_bool = False
        weather_coverage = False
        moon_present_bool = False #True indicates that moon is in sky during satellite pass
        moon_phase_bool = False # Only checked if present, True indicates gibbous or full

        #assess moon
        moon_present_bool = self.assess_moon()
        if "Gibbous" in self.moon_phase or "Full" in self.moon_phase:
            moon_phase_bool = True

        #assess azimuth
        if float(self.passes[0].get("maxEl")) >= 70.0:
            #True only matters if nautical bool is also true
            azimuth_bool = True
        
        #assess_nautical
        nautical_bool = self.assess_nautical()

        #assess weather
        if self.forecast:
            weather_coverage = True
            if self.forecast[0] == "Clear":
            #if "clear" in self.forecast[0].lower() or "clear" in self.forecast[1].lower():
                weather_bool = True
        
        #create assessment
        assess_good = ""
        assess_bad = ""

        if weather_coverage == True:
            if weather_bool == True:
                assess_good = assess_good + f"\n{self.forecast[1].capitalize()} predicted during pass, viewing will be optimal."
            else:
                assess_bad = assess_bad + f"\n{self.forecast[1].capitalize()} predicted during pass, view may be obscured."
        else:
            assess_bad = assess_bad +f"\nWeather forecast not available for {self.address}"

        if nautical_bool == True and azimuth_bool == True:
            assess_good = assess_good + f"\nSatellite will pass at high trajectory with maximum azimuth of {self.passes[0].get('maxEl')}° during nautical twilight."
        
        if float(self.passes[0].get("maxEl")) < 30.0:
            assess_bad = assess_bad + f"\nSatellite will pass at low trajectory with maximum azimuth of {self.passes[0].get('maxEl')}°."

        if moon_present_bool == False:
            assess_good = assess_good + f"\nMoon will not be visible during pass."
        else:
            if moon_phase_bool == True:
                assess_bad = assess_bad + f"\n{self.moon_phase} moon is likely to obstruct visibility during pass."
            else:
                assess_bad = assess_bad + f"\n{self.moon_phase} moon could potentially interfere with viewing."

        if len(assess_good) > 0 and len(assess_bad) >0:
                assess = f"\nAssessment: <strong>Mixed</strong>\n"
                assess = assess + "\nThe Good"
                assess = assess + assess_good + "\n"
                assess = assess + "\nThe Bad"
                assess = assess + assess_bad + "\n"
                return assess

        if len(assess_good) > 0 and len(assess_bad) == 0:
                assess = f"\nAssessment: <strong>Good</strong>\n"
                assess = assess + assess_good + "\n"
                return assess

        if len(assess_good) == 0 and len(assess_bad) > 0:
                assess = f"\nAssessment: <strong>Bad</strong>\n"
                assess = assess + assess_bad + "\n"
                return assess
    
    def assess_nautical(self):

        next_pass_start = datetime.utcfromtimestamp(self.next_pass[0])
        next_pass_end = datetime.utcfromtimestamp(self.next_pass[1])
        
        #pass begins before nautical dusk ends and pass ends after or during nautical dusk begins
        if next_pass_start <= self.nautical_twilight_dusk[1] and next_pass_end >= self.nautical_twilight_dusk[0]:
            return True
        elif next_pass_start <= self.nautical_twilight_dawn[1] and next_pass_end >= self.nautical_twilight_dawn[0]:
            return True

    def assess_moon(self):
        #True boolean indicates that moon is in sky during satellite pass
        #True is not a desirable condition
        next_pass_start = datetime.utcfromtimestamp(self.next_pass[0])
        next_pass_end = datetime.utcfromtimestamp(self.next_pass[1])

        #not in sky or new moon
        if self.moonrise == None and self.moonset == None:
            return False
        
        #moon already in sky before nightfall and sets during night
        if self.moonrise == None and self.moonset:

            #moon sets before satellite pass
            if self.moonset < next_pass_start:
                return False
            
            #moon sets during or after pass
            return True
        
        #moon rises during night but sets after daybreak
        if self.moonrise and self.moonset == None:
            
            #moon rises before or during satellite pass
            if self.moonrise <= next_pass_end:
                return True

            #moon rises after satellite pass
            return False
        
        #moon rises and sets during the night
        else:
            #moon rises during or before pass ends and sets during after passes starts
            if self.moonrise < next_pass_end and self.moonset >= next_pass_start:
                return True
            return False

    def get_sequence(self):
        this_pass = self.pass_count - (len(self.passes) - 1)
        sequence = f"This information is for pass {this_pass} out of {self.pass_count}\n"
        return sequence



    def get_all_html(self):
        remaining = strfdelta((datetime.utcfromtimestamp(int(self.next_pass[0])) - datetime.utcnow()), "{days} days {hours} hours {minutes} minutes {seconds} seconds")

        all = ""
        all = all + self.get_sequence()
        all = all + self.get_assessment()

        all = all + '<table style="width:100%">'
        all = all + "<tr><td COLSPAN='2'><h3>Location Information</h3><td>"
        all = all + f'<tr><td>Location</td><td> {self.address}</td></tr>'
        all = all + f'<tr><td>Latitude</td><td>{self.lat}°</td></tr>'
        all = all + f'<tr><td>Longitude</td><td>{self.lng}°</td></tr>'
        all = all + f'<tr><td>Elevation</td><td>{self.elevation} ft. above sea level</td></tr>'

        all = all + "<tr><td COLSPAN='2'><h3>Satellite Information</h3><td>"
        all = all + f'<tr><td>Satellite Name</td><td>{self.satellite_name}</td></tr>'
        all = all + f'<tr><td>NORAD Identifier</td><td>{self.satellite_id}</td></tr>'
        all = all + f'<tr><td>Next Pass Start</td><td>{datetime.utcfromtimestamp(int(self.next_pass[0])).strftime("%Y-%m-%d %H:%M:%S %Z")}</td></tr>'
        all = all + f'<tr><td>Next Pass End</td><td>{datetime.utcfromtimestamp(int(self.next_pass[1])).strftime("%Y-%m-%d %H:%M:%S %Z")}</td></tr>'
        all = all + f'<tr><td>Time Remaining</td><td>{remaining}</td></tr>'

        if len(self.passes) > 0:
            pass_info = self.passes[0]
            duration = str(pass_info.get("duration")) + " seconds"
            starting_azimuth = f'{pass_info.get("startAz")}° {pass_info.get("startAzCompass")} at {pass_info.get("startEl")}° elevation'
            maximum_azimuth = f'{pass_info.get("maxAz")}° {pass_info.get("maxAzCompass")} at {pass_info.get("maxEl")}° elevation'
            ending_azimuth = f'{pass_info.get("endAz")}° {pass_info.get("endAzCompass")} at {pass_info.get("endEl")}° elevation'
            
            all = all + "<tr><td COLSPAN='2'><h3>Trajectory Information</h3><td>"
            all = all + f'<tr><td>Duration of Pass</td><td>{duration}</td></tr>'
            all = all + f'<tr><td>Starting Azimuth</td><td>{starting_azimuth}</td></tr>'
            all = all + f'<tr><td>Maximum Azimuth</td><td>{maximum_azimuth}</td></tr>'
            all = all + f'<tr><td>Ending Azimuth</td><td>{ending_azimuth}</td></tr>'

        all = all + "<tr><td COLSPAN='2'><h3>Conditions Information</h3><td>"
        if self.forecast:
            all = all + f'<tr><td>Forecast</td><td>{self.forecast[1].title()}</td></tr>'
        else:
            all = all + f'<tr><td>Forecast</td><td>Not available for this location</td></tr>'
        all = all + f'<tr><td>Moon Phase</td><td>{self.moon_phase}</td></tr>'
        all = all + f'<tr><td>Moon Rise</td><td>{self.moonrise}</td></tr>'
        all = all + f'<tr><td>Moon Set</td><td>{self.moonset}</td></tr>'
        all = all + f'<tr><td>Dawn Nautical Twilight Start</td><td>{self.nautical_twilight_dawn[0]}</td></tr>'
        all = all + f'<tr><td>Dawn Nautical Twilight End</td><td>{self.nautical_twilight_dawn[1]}</td></tr>'
        all = all + f'<tr><td>Dusk Nautical Twilight Start</td><td>{self.nautical_twilight_dusk[0]}</td></tr>'
        all = all + f'<tr><td>Dusk Nautical Twilight End</td><td>{self.nautical_twilight_dusk[1]}</td></tr></table>'
        return all



def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


    

if __name__ == "__main__":

    s = Satellite_Pass("Seattle, WA", RECIPIENT, SATELLITES.get("NEPALISAT1"))
    s.get_location_data()
    s.get_elevation()
    s.get_visual_passes()
    s.get_forecast()
    s.get_lunar_data()
    s.get_twilight_data()

    print(s.get_assessment())
    print(s.get_location_info())
    print(s.get_satellite_info())
    print(s.get_trajectory_info())
    print(s.get_conditions_info())
