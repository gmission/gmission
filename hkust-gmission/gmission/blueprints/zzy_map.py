__author__ = 'chenzhao'

import os.path
from werkzeug.utils import secure_filename
from flask import render_template, request, url_for,Blueprint

import csv
from gmission.flask_app import app, ROOT

UPLOAD_FOLDER = 'uploads'
ABS_UPLOAD_FOLDER = os.path.join(ROOT, 'static', UPLOAD_FOLDER)

DATA_PATH = os.path.join(ROOT, 'static', 'data')

mapping_blueprint = Blueprint('mapping', __name__, template_folder='templates')


# labeling
@app.route('/label')
def maplable():
    return render_template('start.html')

@app.route('/map', methods=['GET', 'POST'])
def showmap():
    if request.method == 'POST':
        f = request.files['file']
        info = request.files['info']
        fname = secure_filename(f.filename)
        fpath = ABS_UPLOAD_FOLDER + "/" + fname
        cate, loca = getCate_Location()
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except:
                pass
        f.save(os.path.join(ABS_UPLOAD_FOLDER, fname))
        print os.path.join(UPLOAD_FOLDER, fname)
        print url_for('static', filename=os.path.join(UPLOAD_FOLDER, fname))
        return render_template('map.html', src=os.path.join(UPLOAD_FOLDER, fname), cate=cate, loca=loca)
    else:
        f = request.files['file']
        fname = secure_filename(f.filename)
        fpath = ABS_UPLOAD_FOLDER + "/" + fname
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except:
                pass
        f.save(os.path.join(ABS_UPLOAD_FOLDER, fname))
        return render_template('map.html', src=os.path.join(ABS_UPLOAD_FOLDER, fname))


@app.route('/mapinfo', methods=['POST', 'GET'])
def getinfo():
    if request.method == 'POST':
        insert_into_csv(request.form)
        return render_template('label.html')


def insert_into_csv(form):
    csvfile = file(os.path.join(DATA_PATH, 'new.csv'), 'a')
    writer = csv.writer(csvfile)
    writer.writerow((form['area'], form['x'], form['y'], form['x2'], form['y2']
                     , form['location'], form['category']))



def getCate_Location():
    temppath = os.path.join(ROOT, '..', 'data')
    print temppath
    r = csv.reader(file(os.path.join(temppath, 'tasks.csv')))
    r.next()
    cate = []
    loca = []
    for row in r:
        category, location, xx, question, options, author = map(str.strip, row)
        #print category, location
        if category:
            cate.append(category)
        if not location in loca:
            loca.append(location)
            # print location

    r = csv.reader(file(os.path.join(temppath, 'mapping.csv')))
    r.next()
    for row in r:
        area_id, point_x, point_y, range_x, range_y, location, category = map(str.strip, row)
        if category:
                cate.append(category)
        if location:
            if location in loca:
                loca.remove(location)
                print location


    cate = list(set(cate))
    loca = list(set(loca))
    return cate[1:], loca[1:]
