__author__ = 'CHEN Zhao'

from gmission.models import *
from gmission.flask_app import db
import time
from collections import defaultdict
import csv
import os.path
from transfer import transfer_mapping


DATA_PATH = 'data'


def clear_db():
    pass

def import_mapping_from_csv():
    pass
    # transfer_mapping()
    # r = csv.reader(file(os.path.join(DATA_PATH, 'mapping_geo.csv')))
    # # r.next()
    # for row in r:
    #     floor, left_top_latitude, left_top_longitude, right_bottom_latitude, right_bottom_longitude, location_name, \
    #         category_name = map(str.strip, row)
    #     left_top_latitude, left_top_longitude, right_bottom_latitude, right_bottom_longitude = \
    #         map(float,  (left_top_latitude, left_top_longitude, right_bottom_latitude, right_bottom_longitude))
    #     if category_name:
    #         c = get_or_create(Category, name=category_name)
    #     if location_name:
    #         location_name = category_name+': '+location_name
    #         bound = get_or_create(LocationBound, left_top_latitude=left_top_latitude,
    #                               left_top_longitude=left_top_longitude, right_bottom_latitude=right_bottom_latitude,
    #                               right_bottom_longitude=right_bottom_longitude,)
    #         print floor, left_top_latitude, left_top_longitude, right_bottom_latitude, \
    #             right_bottom_longitude, location_name, category_name
    #         l = get_or_create(Location, name=location_name, longitude=(left_top_longitude+right_bottom_longitude)/2,
    #                           latitude=(left_top_latitude+right_bottom_latitude)/2, z=floor, category=c, bound=bound)
    #     print l, l.id
    #     a = get_or_create(IndoorRectangle, name=location_name, z=floor, left_top_latitude=left_top_latitude,
    #                       left_top_longitude=left_top_longitude,
    #                       right_bottom_latitude=right_bottom_latitude,
    #                       right_bottom_longitude=right_bottom_longitude,
    #                       location=l)
    # db.session.commit()


def import_predefined_location_from_csv(csv_fname):
    pass
    # r = csv.reader(file(os.path.join(DATA_PATH, csv_fname)))
    # for row in r:
    #     category_name, location_name, longitude, latitude, left_top_longitude, left_top_latitude, \
    #         right_bottom_longitude, right_bottom_latitude = map(str.strip, row)
    #     floor = 0
    #     left_top_latitude, left_top_longitude, right_bottom_latitude, right_bottom_longitude = \
    #         map(float,  (left_top_latitude, left_top_longitude, right_bottom_latitude, right_bottom_longitude))
    #     if category_name:
    #         c = get_or_create(Category, name=category_name)
    #     if location_name:
    #         bound = get_or_create(LocationBound, left_top_latitude=left_top_latitude,
    #                               left_top_longitude=left_top_longitude, right_bottom_latitude=right_bottom_latitude,
    #                               right_bottom_longitude=right_bottom_longitude,)
    #         print floor, left_top_latitude, left_top_longitude, right_bottom_latitude, \
    #             right_bottom_longitude, location_name, category_name
    #         l = get_or_create(Location, name=location_name, longitude=(left_top_longitude+right_bottom_longitude)/2,
    #                           latitude=(left_top_latitude+right_bottom_latitude)/2, z=floor, category=c, bound=bound)
    #     print l, l.id
    #     a = get_or_create(IndoorRectangle, name=location_name, z=floor, left_top_latitude=left_top_latitude,
    #                       left_top_longitude=left_top_longitude,
    #                       right_bottom_latitude=right_bottom_latitude,
    #                       right_bottom_longitude=right_bottom_longitude,
    #                       location=l)
    # db.session.commit()


def clear_and_import_all():
    # clear_db()
    # import_indoor_task_from_csv()
    # import_mapping_from_csv()
    import_predefined_location_from_csv('world_window.csv') #'.csv'
    db.session.commit()


def main():
    print db
    clear_and_import_all()


if __name__ == '__main__':
    main()

