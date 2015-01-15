import csv
import os

DATA_PATH = 'data'


def transfer_mapping():

    r = csv.reader(file(os.path.join(DATA_PATH, 'mapping.csv')))
    w = csv.writer(file(os.path.join(DATA_PATH, 'mapping_geo.csv'), 'wb'))
    anchor = csv.reader(file(os.path.join(DATA_PATH, 'anchor.csv')))
    anchor_list = []

    for row in anchor:
        areaid, lat, lng, x, y, floor = map(str.strip, row)
        an = [areaid, lat, lng, x, y, floor]
        print areaid, lat, lng, x, y, floor
        anchor_list.append(an)

    for row in r:
        area_id, point_x, point_y, range_x, range_y, location, category = map(str.strip, row)
        #print area_id, point_x, point_y, range_x, range_y, location, category
        floor = int(area_id) - 2000

        for an in anchor_list:
            if int(an[5]) == floor:
                print "anchor ", an[0], an[3], an[4], an[1], an[2]
                lat, lng, r_x, r_y = Piexel2Geo(an[3], an[4], an[1], an[2], point_x, point_y, float(range_x),
                                                float(range_y))
                # print floor, lat, lng, r_x, r_y, location, category
                # w.writerow([floor, lat, lng,  lat - r_x, lng + r_y, location, category])
                w.writerow([floor, lat, lng,  r_x, r_y, location, category])


def Piexel2Geo(an_x, an_y, an_lat, an_lng, x, y, r_x, r_y):

    scalex = 0.000510/835
    scaley = 0.00060/1400

    # print scaley, scalex
    print x, y, r_x, r_y

    lat = float(an_lat) - (float(y) - float(an_y)) * scaley
    lng = float(an_lng) + (float(x) - float(an_x)) * scalex


    range_x = float(an_lat) - (float(r_y) - float(an_y)) * scaley
    range_y = float(an_lng) + (float(r_x) - float(an_x)) * scalex

    # range_x = r_x * scalex
    # range_y = r_y * scaley

    return lat, lng, range_x, range_y


def main():
    transfer_mapping()

if __name__ == '__main__':
    main()


"""
public LatLng Pixel2Geo(Point2D p,Point2D q){

    Log.i("coordinate:", "anchor:["+p.lat+","+p.lng+"]"+"["+p.x+","+p.y+"]"+p.areaid);
    double lat = p.lat - (q.x - p.x) * scaleX;
    double lng = p.lng - (q.y - p.y) * scaleY;
    q.lat = lat;
    q.lng = lng;
    q.areaid = p.areaid;
    Log.i("coordinate:", q.lat+","+q.lng);
    return new LatLng(q.lat,q.lng);
}"""
