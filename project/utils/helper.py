from flask import json, Response, abort
from project import app, db, mail
from flask_mail import Message

def response(**kwargs):
    result = {}
    result['json'] = kwargs.get('json', [])
    result['total'] = kwargs.get('total', len(result['json']))
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
    #from IPython import embed; embed()
    items = cls.query.all()
    json = []
    for item in items:
        json.append(item.to_json())
    return response(json=json)


def add_or_update_items(cls, request):
    messages = []
    try:
        #from IPython import embed; embed()
        items = json.loads(request.data.decode('utf-8'))
        for item in items['list']:
            save_item(cls, item)
    except Exception as e:
        messages.append(e)

    if len(messages) > 0:
        return response(status=500, messages=messages)
    return response()


def save_item(cls, item):
    #from IPython import embed; embed()
    obj = None
    if 'id' in item:
        obj = cls.query.filter_by(id=item.get('id')).first()
        obj.copy_values(cls.from_json(item))
    if obj is None:
        obj = cls.from_json(item)

    try:
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def get_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    json = []
    json.append(item.to_json)
    return response(json=json)


def delete_item(cls, item_id):
    item = cls.query.filter_by(id=item_id).first()
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    return response(success=True)

def send_email(subject, recipients, html_body):
    errors = []
    try:
        msg = Message(subject, recipients=recipients)
        msg.sender = "help@featurerequestapp.com"
        msg.html = html_body
        mail.send(msg)
    except Exception as e:
        errors.append(str(e))
    return errors
