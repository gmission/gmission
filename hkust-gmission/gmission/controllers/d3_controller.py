# -*- coding: utf-8 -*-
__author__ = 'haidaoxiaofei'

from gmission.models import *
from gmission.flask_app import app, ROOT
import os, sys, math

service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from async_jobs.reconstructor import *

def rebuild_3d_sparse_models():
    for hit in HIT.query.filter(HIT.type == '3d').filter(HIT.status == 'open').all():
        rebuild_3d_sparse_model(str(hit.id))



def rebuild_3d_sparse_model(hit_id):
    answers = Answer.query.filter(Answer.hit_id == hit_id).filter(Answer.type == '3d').all()
    prepare_images(hit_id, [a.attachment.value for a in answers])
    build_3d_model(hit_id)
    final_ply_file = find_final_ply_file(hit_id)

    print 'ply_file', final_ply_file

    if  final_ply_file is None:
        return

    attachment = Attachment(name='a sparse 3D model',
                            type='3d',
                            value=final_ply_file)
    db.session.add(attachment)
    db.session.commit()


    HIT.query.filter(HIT.id == hit_id).update(dict(attachment_id=attachment.id))
    db.session.commit()



def calculate_next_best_direction(hit_id):
    answers = Answer.query.filter(Answer.hit_id == hit_id).filter(Answer.type == '3d').all()
    coordinates = [a.location.coordinate for a in answers]
    if len(coordinates) == 0:
        return '0'


    hit = HIT.query.get(hit_id)
    hit_coordinate = hit.location.coordinate

    received_directions = []


    for co in coordinates:
        direction = math.atan2(co.latitude - hit_coordinate.latitude, co.longitude - hit_coordinate.longitude)
        if direction < 0:
            direction += 2 * math.pi

        received_directions.append(direction)
    print received_directions

    received_directions.sort()
    received_directions.append(received_directions[0] + 2 * math.pi)

    max_interval = 0
    max_interval_index = 0

    for i in range(0, len(received_directions) - 1):
        current_interval = received_directions[i+1] - received_directions[i]
        if current_interval >= max_interval:
            max_interval = current_interval
            max_interval_index = i

    next_best_direction = 0
    if  received_directions[max_interval_index + 1] + received_directions[max_interval_index] > 2 * math.pi:
        next_best_direction = (received_directions[max_interval_index + 1] + received_directions[max_interval_index] )/2 - 2 * math.pi
    else:
        next_best_direction = (received_directions[max_interval_index + 1] + received_directions[max_interval_index])/2


    return str(next_best_direction)
