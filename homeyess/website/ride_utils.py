from django.forms.models import model_to_dict

import requests
import googlemaps
import pytz
import functools
from datetime import datetime, timedelta

def getRideDict(ride):
    ride_dict = model_to_dict(ride)
    ride_dict['d'] = ride.d
    ride_dict['sd'] = ride.sd
    ride_dict['ed'] = ride.ed
    ride_dict['total_time'] = ride.total_time
    ride_dict['pickup_location'] = ride.pickup_location
    ride_dict['pickup_address'] = ride.homeless.home_address
    return ride_dict

def filterQuerySet(rides, start_datetime, end_datetime, max_range, v_start):
    for ride in rides:
        td_vec = getTimeDistanceVector(
            ride.homeless.home_address,
            v_start,
            ride.interview_address,
            ride.interview_duration
        )
        if td_vec == None:
            ride.d = None
            ride.sd = None
            ride.ed = None
        else:
            ride.d = getDistance(td_vec)
            ride.sd, _, ride.ed, ride.total_time = getTimes(td_vec, ride.interview_datetime)

        #set pickup lat/long
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        pickup_info = gmaps.geocode(ride.homeless.home_address)
        if pickup_info:
            location = pickup_info[0]['geometry']['location']
            ride.pickup_location = location
        else:
            ride.pickup_location = None

    rides = [ride for ride in rides if ride.d != None]
    if start_datetime:
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
        start_datetime = pytz.utc.localize(start_datetime)
        rides = [ride for ride in rides if ride.sd >= start_datetime]
    if end_datetime:
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
        end_datetime = pytz.utc.localize(end_datetime)
        rides = [ride for ride in rides if ride.ed <= end_datetime]
    if max_range:
        max_range = int(max_range)
        rides = [ride for ride in rides if ride.d <= max_range]

    return rides

def getTimeDistanceVector(v_start, hp_start, interview_location, interview_duration):
    URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    PARAMS = {
        'key': GOOGLE_MAPS_API_KEY,
        'origins': v_start + '|' + hp_start + '|' + interview_location,
        'destinations': v_start + '|' + hp_start + '|' + interview_location,
    }

    data = getResponseJson(URL, PARAMS)

    if data['status'] != 'OK':
        return None

    # we need:
    # v_start -> hp_start (0, 1)
    # hp_start -> interview_location (1, 2)
    # interview_location -> hp_start (2, 1)
    # hp_start -> v_start (1, 0)

    INDICES = [(0, 1), (1, 2), (2, 1), (1, 0)]
    time_distance_vector = []
    for index0, index1 in INDICES:
        if data['rows'][index0]['elements'][index1]['status'] != 'OK':
            return None
        distance_in_meters = data['rows'][index0]['elements'][index1]['distance']['value']
        time_in_seconds = data['rows'][index0]['elements'][index1]['duration']['value']

        distance_in_miles = 0.000621371 * distance_in_meters
        time_in_minutes = time_in_seconds / 60

        time_distance_vector.append((time_in_minutes, distance_in_miles))

    # insert the interview in between the driving
    time_distance_vector.insert(2, (interview_duration, 0))
    return time_distance_vector

def getResponseJson(url, params):
    r = requests.get(url=url, params=params)
    return r.json()


def getDistance(vec):
    distances = [distance for (_, distance) in vec]
    dist = functools.reduce(lambda a, b: a + b, distances)
    dist = int(dist)
    return dist

def getTimes(vec, interview_datetime):
    pickup_datetime = interview_datetime - timedelta(minutes=vec[1][0])
    start_datetime = pickup_datetime - timedelta(minutes=vec[0][0])
    times = [time for (time, _) in vec]
    total_time = functools.reduce(lambda a, b: a + b, times)
    total_time_string = getTimeString(int(total_time))
    end_datetime = start_datetime + timedelta(minutes=total_time)
    return start_datetime, pickup_datetime, end_datetime, total_time_string

def getTimeString(mins):
    s = ""
    hours = mins//60
    m = mins%60
    if hours == 1:
        s += str(hours) + ' hr '
    elif hours > 1:
        s += str(hours) + ' hrs '
    if m == 1:
        s += str(m) + ' min'
    elif m > 0:
        s += str(m) + ' mins'
    return s
