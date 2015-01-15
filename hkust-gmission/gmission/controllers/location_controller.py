__author__ = 'chenzhao'

from gmission.models import *


def indoor_nearby_user_count(location_id):
    location_rect = IndoorLocationRectangle.query.filter_by(location_id=location_id).first()
    """:type location_rect:IndoorLocationRectangle"""

    P = UserLastPosition
    in_rect = (P.longitude>=location_rect.left_top_longitude) & (P.longitude<=location_rect.right_bottom_longitude) \
              & (P.latitude<=location_rect.left_top_latitude) & (P.latitude>=location_rect.right_bottom_latitude)
    c = P.query.filter(in_rect).count()

    return c


def global_nearby_user_count(location_id):
    location = GlobalLocation.query.get(location_id)
    P = UserLastPosition
    r = 10 # TODO
    in_rect = (P.longitude>=location.longitude-r) & (P.longitude<=location.longitude+r) \
              & (P.latitude>=location.latitude-r) & (P.latitude<=location.latitude+r)
    c = P.query.filter(in_rect).count()

    return c


def create_new_gps_location():
    # TODO
    return


def query_indoor(j):
    longitude, latitude, z = j['longitude'], j['latitude'], j['z']
    Rect = IndoorLocationRectangle
    # condsider the north, east semisphere only
    # TODO
    #
    #  longitude,latitude      0,90   <   180, 90
    #                           V
    #                          0,0        180,0
    rects = Rect.query.filter( Rect.z==z\
                (Rect.left_top_longitude<=longitude) & (Rect.right_bottom_longitude>=longitude)
                &(Rect.left_top_latitude>=latitude) & (Rect.right_bottom_latitude<=latitude) \
            )
    return [{'location_name': r.location.name, 'location_id':r.location_id} for r in rects.all()]






if __name__=='__main__':
    pass
    # check_expired()
