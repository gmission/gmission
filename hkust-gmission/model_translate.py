__author__ = 'chenzhao'


import inspect
import os
import os.path
import shutil
from gmission.models import *


def columns(cls):
    for cln in cls.__mapper__.columns:
        yield cln


def all_models():
    for cls in globals().values():
        if inspect.isclass(cls) and issubclass(cls, db.Model):
            yield cls


def to_java_type(sql_type):
    type_mapping = {'REAL': 'double',
                    'FLOAT': 'double',
                    'INTEGER': 'int',
                    'DATETIME': 'String',
                    'BOOLEAN': 'boolean',
                    }
    return type_mapping.get(str(sql_type), 'String')


def generate_java_class(model):
    jclass = 'public class %s {\n' % model.__name__
    for cln in columns(model):
        jclass += '\t%s %s;\n' %(to_java_type(cln.type), cln.name)

    jclass += '\tString urlname = "%s";\n'%model.urlname()
    jclass += '}\n'
    return jclass


def generate_java_code():
    java_dir = 'java_models'

    shutil.rmtree(java_dir)
    os.makedirs(java_dir)

    for model in all_models():
        jclass = generate_java_class(model)
        jfname = os.path.join(java_dir, '%s.java' % model.__name__)
        with file(jfname, 'w') as jf:
            jf.write(jclass)


def main():
    generate_java_code()
    pass


if __name__=='__main__':
    main()
