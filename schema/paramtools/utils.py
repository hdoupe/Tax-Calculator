import json

from marshmallow import fields

from paramtools.schema import Float64, Int8, Bool_

# def get_type(data, max_dim=2):
#     """
#     Use "boolean_value" and "integer_value" to figure out what type the value
#     should be. Use the shape of the data in "value" to figure out what
#     shape the parameter should have.
#     """
#     if data['boolean_value']:
#         fieldtype = Bool_()
#     elif data['integer_value']:
#         fieldtype = Int8()
#     else:
#         fieldtype = Float64()
#     if isinstance(data['value'], list):
#         if isinstance(data['value'][0], list):
#             dim = 2
#         else:
#             dim = 1
#     else:
#         dim = 0
#     while dim > 0:
#         fieldtype = fields.List(fieldtype)
#         dim -= 1
#     return fieldtype

def get_type(data):
    """
    would be used if "type" is defined
    """
    types = {
        'integer': Int8(),
        'bool': Bool_(),
        'float': Float64(),
    }
    fieldtype = types[data['type']]
    dim = data['number_dims']
    while dim > 0:
        fieldtype = fields.List(fieldtype)
        dim -= 1
    return fieldtype

def read_json(path):
    """
    Read JSON file shortcut
    """
    with open(path, 'r') as f:
        r = json.loads(f.read())
    return r
