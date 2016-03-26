# -*- coding: utf-8 -*-
__author__ = 'haidaoxiaofei'

from gmission.models import *
from gmission.flask_app import app, ROOT
import os, sys

service_path = os.path.join(ROOT, '../../services')
sys.path.append(service_path)
from bundler.reconstructor import *

def rebuild_3d_sparse_model(hit_id):
    answers = Answer.query.filter(Answer.hit_id == hit_id).filter(Answer.type == '3d').all()
    prepare_images(hit_id, [a.attachment.value for a in answers])
    build_3d_model(hit_id)
    final_ply_file = find_final_ply_file(hit_id)

    attachment = Attachment(name='a sparse 3D model',
                            type='3d',
                            value=final_ply_file)
    db.session.add(attachment)
    db.session.commit()

    print 'attachment_id', attachment.id

    HIT.query.filter(HIT.id == hit_id).update({'attachment_id', attachment.id}, synchronize_session=False)
    db.session.commit()