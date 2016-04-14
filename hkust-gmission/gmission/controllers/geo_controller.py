import math

import requests

__author__ = 'chenzhao'

from gmission.models import *
from gmission.config import index_server


# 1km is about 0.01, 1m is 0.00001
def location_nearby_user_count(location_id, r=0.01):
    location = Location.query.get(location_id)
    P = UserLastPosition
    in_rect = (P.longitude >= location.coordinate.longitude - r) & (P.longitude <= location.coordinate.longitude + r) \
              & (P.latitude >= location.coordinate.latitude - r) & (P.latitude <= location.coordinate.latitude + r)
    c = P.query.filter(in_rect).count()

    return c


def get_nearest_n_users(longitude, latitude, n, r=0.00001):
    P = UserLastPosition

    in_rect = (P.longitude >= longitude - r) & (P.longitude <= longitude + r) \
              & (P.latitude >= latitude - r) & (P.latitude <= latitude + r)
    c = P.query.filter(in_rect).count()

    #print 'KNN', n, r, c

    if c < n and r < 0.1:
        return get_nearest_n_users(longitude, latitude, n, r * 2)

    ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in ps[:n]]


def get_nearest_n_users_from_index(longitude, latitude, n, r=0.00001, use_rtree=True):

    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    #params = {'k': n, 'longitude': longitude, 'latitude': latitude, 'furthest': r}
    params = {'longitude1': longitude - r / 2, 'latitude1': latitude - r / 2,
              'longitude2': longitude + r / 2, 'latitude2': latitude + r / 2}
    if use_rtree:
        #ids = requests.get(url=index_server.server_addr + '/RTreeIndex/actions/nodes/knn', params=params,
        #                   headers=headers).json()
        ids = requests.get(url=index_server.server_addr + '/Index/actions/nodes/rectangle', params=params,
                           headers=headers).json()
    else:
        ids = requests.get(url=index_server.server_addr + '/Index/actions/nodes/rectangle/linear', params=params,
                           headers=headers).json()
    c = len(ids)

    #print 'KNN', n, r, c

    #if c < n and r < 0.1:
    #    return get_nearest_n_users(longitude, latitude, n, r * 2)

    result = []

    users = {}
    for u in User.query.filter(User.id.in_(ids)):
        users[str(u.id)] = u
    for id in ids:
        result.append(users[str(id)])
    return result


def get_nearby_users(longitude, latitude, r=0.05):
    P = UserLastPosition

    in_rect = (P.longitude >= longitude - r) & (P.longitude <= longitude + r) \
              & (P.latitude >= latitude - r) & (P.latitude <= latitude + r)
    c = P.query.filter(in_rect).count()

    print ('user in %f bound: %d') % (r, c)

    # ps = sorted(P.query.filter(in_rect).all(), key=lambda p: geo_distance(p.longitude, p.latitude, longitude, latitude))
    return [p.user for p in P.query.filter(in_rect).all()]


def geo_angle(startPointLong, startPointLati, endPointLong, endPointLati):
    angle = math.atan2(endPointLati - startPointLati, endPointLong - startPointLong)
    return angle


def geo_distance(long1, lati1, long2, lati2):
    return math.sqrt((long1 - long2) ** 2 + (lati1 - lati2) ** 2)
    pass


def filter_location(data):
    if data.get('location_id', None):
        # print 'location_id provided, pop location'
        data.pop('location', None)
        return
    # if 'location' in data:
    #     # print 'location provided'
    #     uc_keys = ['name', 'longitude','latitude']
    #     existing_location = Location.query.filter_by(**dict(zip(uc_keys, map(data['location'].get, uc_keys)))).first()
    #     # print 'existing location', existing_location
    #     if existing_location:
    #         data.pop('location', None)
    #         data['location_id'] = existing_location.id


if __name__ == '__main__':
    pass
