import functools
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import googlemaps
import pytz
import requests
from django.core.mail import send_mail
from django.forms.models import model_to_dict
from homeyess.settings import GOOGLE_MAPS_API_KEY, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID
from twilio.rest import Client


def getRideDict(ride):
    """converts ride to a dictionary to use in the templates

    :param ride: the ride
    :type ride: Ride
    :return: dictionary version of the ride with extra fields (d: distance, sd: start_datetime, ed: end_datetime, total_time, pickup_location, pickup_address)
    :rtype: dict
    """
    ride_dict = model_to_dict(ride)
    ride_dict['d'] = ride.d
    ride_dict['sd'] = ride.sd
    ride_dict['ed'] = ride.ed
    ride_dict['total_time'] = ride.total_time
    ride_dict['pickup_location'] = ride.pickup_location
    ride_dict['pickup_address'] = ride.homeless.home_address
    return ride_dict

def filterQuerySet(rides, start_datetime, end_datetime, max_range, v_start):
    """Filters a list of rides given filters

    :param rides: the rides to filter
    :type rides: iterable of Rides
    :param start_datetime: the time the volunteer can start driving
    :type start_datetime: (optional) datetime
    :param end_datetime: the time the volunteer must be done driving
    :type end_datetime: (optional) datetime
    :param max_range: the max in miles the volunteer is willing to drive
    :type max_range: (optional) int
    :param v_start: home address of volunteer
    :type v_start: string
    :return: the list of rides that obeys the filters
    :rtype: iterable of Rides
    """
    # get all td_vecs concurrently
    td_vecs = getTimeDistanceVectors(rides, v_start)

    for ride, td_vec in zip(rides, td_vecs):
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

def getTimeDistanceVectors(rides, v_start):
    """ gets time and distance information for all rides concurrently

    :param rides: rides to get timedistance vectors for
    :type rides: iterable of rides
    :param v_start: home address of volunteer
    :type v_start: string
    :return: vector of timedistance vectors in same order as the rides
    :type: vector of timedistance vectors
    """
    # perform all api calls concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                getTimeDistanceVector,
                ride.homeless.home_address,
                v_start,
                ride.interview_address,
                ride.interview_duration
            ) for ride in rides]
    return [future.result() for future in as_completed(futures)]

def getTimeDistanceVector(v_start, hp_start, interview_location, interview_duration):
    """Gets a time and distance information for the ride

    :param v_start: home address of volunteer
    :type v_start: string
    :param hp_start: pickup address of homeless person
    :type hp_start: string
    :param interview_location: address of interview
    :type interview_location: string
    :param interview_duration: how long the interveriw will last (minutes)
    :type interview_duration: int
    :return:
    :rtype: vector where each element is a tuple (minutes, miles)
        Elements in order are:
        volunteer -> homeless pickup,
        pickup -> interview,
        (interview_duration, 0),
        interview -> pickup,
        pickup -> volunteer home
    """

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
    """makes a GET request and returns the json response

    :param url: the url
    :type url: string
    :param params: the params associated with the request
    :type params: dict
    :return: the http response
    :rtype: json
    """
    r = requests.get(url=url, params=params)
    return r.json()

def getDistance(vec):
    """gets the total distance from a timedistance vector

    :param vec: the timedistance vector
    :type vec: vector where each element is a tuple of form (time in minutes, distance in miles)
    :return: total distance in miles
    :rtype: int
    """
    distances = [distance for (_, distance) in vec]
    dist = functools.reduce(lambda a, b: a + b, distances)
    dist = int(dist)
    return dist

def getTimes(vec, interview_datetime):
    """gets the time information from a timedistance vector

    :param vec: the timedistance vector
    :type vec: vector where each element is a tuple of form (time in minutes, distance in miles)
    :param interview_datetime: the time and date of the interview
    :type interview_datetime: DateTime
    :return: start_datetime (when volunteer leaves house),
        pickup_datetime (when volunteer picks up homeless),
        end_datetime (when volunteer arrives back at their house),
        total_time_string (total amount of time as a formatted string)
    :rtype: DateTime, DateTime, DateTime, string
    """
    pickup_datetime = interview_datetime - timedelta(minutes=vec[1][0])
    start_datetime = pickup_datetime - timedelta(minutes=vec[0][0])
    times = [time for (time, _) in vec]
    total_time = functools.reduce(lambda a, b: a + b, times)
    total_time_string = getTimeString(int(total_time))
    end_datetime = start_datetime + timedelta(minutes=total_time)
    return start_datetime, pickup_datetime, end_datetime, total_time_string

def getTimeString(mins):
    """Generates time string

    :param mins: the number of minutes
    :type mins: int
    :return: time string of form 'x hr y min' (hrs or mins if plural)
    :rtype: string
    """
    s = ""
    hours = mins//60
    m = mins%60
    if hours == 1:
        s += str(hours) + ' hr '
    elif hours > 1:
        s += str(hours) + ' hrs '
    if m == 1:
        s += str(m) + ' min'
    else:
        s += str(m) + ' mins'
    return s

def send_message(message, profile):
    """Sends texts and emails to people

    :param message: the message to send to the user
    :type message: String
    :param profile: The user's profile
    :type profile: Profile
    """
    res = [None, None]

    if profile == None:
        return res

    if profile.phone != "":
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        res[0] = client.messages.create(body=message, from_='+12055089181', to=profile.phone)

    if profile.user.email != "":
        res[1] = send_mail('Homeyess Notification', message, 'from@example.com', [profile.user.email], fail_silently=False)

    return res
