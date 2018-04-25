from flask import json, Response, abort
from flask_login import current_user
from datetime import datetime, date
from app import app
from json import JSONEncoder

def response(**kwargs):
    result = {}
    result['fields'] = kwargs.get('fields', [])
    result['total'] = kwargs.get('total', len(result['fields']))
    result['messages'] = kwargs.get('messages', [])
    result['success'] = kwargs.get('success', len(result.get('messages')) == 0)
    status = kwargs.get('status', 200)
    result['status'] = status
    mimetype = kwargs.get('mimetype', 'application/json')

    data = json.dumps(result)

    resp = Response(None, status=status, mimetype=mimetype)
    resp.data = data
    return resp

def get_items_list(cls):
    items = cls.query.all()
    fields = []
    for item in items:
        fields.append(item.to_dict())
    return response(fields=fields)


def add_or_update_items(cls, request):
    try:
        items = json.loads(request.data)
        messages = []
        for item in items:
            save_item(cls, item)
    except Exception as e:
        messages.append(e.message)

    if len(messages) > 0:
        return response(status=500, messages=[e.message])
    return response()


def save_item(cls, item):
    obj = None
    if 'id' in item:
        obj = cls.query.filter_by(id=item.get('id')).first()
    if obj is None:
        obj = cls()

    try:
        obj.from_dict(item)
        obj.get_session.commit()
    except Exception as e:
        obj.get_session.rollback()
        raise e

def get_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
        if item is None:
            abort(404)
    fields = []
    fields.append(item.to_dict())
    return response(fields=fields)    


def delete_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    item.delete()
    item.get_session.commit()
    return response(success=True)
