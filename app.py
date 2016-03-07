import os
import sys
import boto3
from uuid import uuid4

from mandrill import Mandrill
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, abort
from flask_crossdomain import crossdomain

try:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['REGISTRATION_ENABLED'] = os.environ.get('REGISTRATION_ENABLED')
    app.config['SES_SENDER'] = os.environ['SES_SENDER']
    mandrill_client = Mandrill(os.environ['MANDRILL_API_KEY'])
    ses_client = boto3.client('ses',
                              aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                              region_name=os.environ['AWS_REGION'])
    partner_domain = os.environ['PARTNER_DOMAIN']
    db = SQLAlchemy(app)
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise


class User(db.Model):
    def __init__(self, email):
        self.email = email
        self.uuid = str(uuid4())

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    uuid = db.Column(db.String(36), unique=True)


@app.route('/')
def index():
    return redirect('http://samdobson.github.io/fwdform')


@app.route('/register', methods=['POST'])
def register():
    if app.config['REGISTRATION_ENABLED'] != 'True':
        return ('Regsitration disabled', 403)

    user = User.query.filter_by(email=request.form['email']).first()
    if user:
        return ('Email already registered', 403)
    user = User(request.form['email'])
    db.session.add(user)
    db.session.commit()
    return "Token: {}".format(user.uuid)


@app.route('/user/<uuid>', methods=['POST'])
@crossdomain(origin = partner_domain)
def forward(uuid):
    user = User.query.filter_by(uuid=uuid).first()
    if not user:
        return ('User not found', 406)
    message = build_message(user, request)
    result = mandrill_client.messages.send(message=message)
    if result[0]['status'] != 'sent':
        abort(500)
    return 'Success'


@app.route('/to/<uuid>', methods=['POST'])
@crossdomain(origin = partner_domain)
def forward_ses(uuid):
    user = User.query.filter_by(uuid=uuid).first()
    if not user:
        return ('User not found', 406)

    result = ses_client.send_email(
        Source=app.config['SES_SENDER'],
        Destination={
            'ToAddresses': [user.email]
        },
        Message={
            'Subject': {
                'Data': u'Message from {}'.format(unicode(request.form['name'])),
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': build_message_body(request),
                    'Charset': 'UTF-8'
                }
            }
        },
        ReplyToAddresses=[request.form['email']]
    )
    if result['ResponseMetadata']['HTTPStatusCode'] != 200:
        abort(500)
    return 'Success {}'.format(result['MessageId'])


def build_message(user, request):
    from_email = unicode(request.form['email'])
    from_name = unicode(request.form['name'])

    full_text = build_message_body(request)

    message = {
        'to': [{'email': user.email}],
        'from_email': from_email,
        'subject': u'Message from {}'.format(from_name),
        'text': full_text,
        }
    return message


def build_message_body(request):
    message_text = unicode(request.form['message'])
    other_fields = [unicode(key) + ": " + unicode(value) for (key, value) in request.form.items() if key not in ['email', 'name', 'message']]
    other_fields.append(message_text)
    return u"\n".join(other_fields)


@app.errorhandler(400)
def bad_parameters(e):
    return ('<p>Missing information. Press the back button to complete '
            'the empty fields.</p><p><i>Developers: we were expecting '
            'the parameters "name", "email" and "message". You might '
            'also consider using JS validation.</i>', 400)


@app.errorhandler(500)
def error(e):
    print(e)
    return ('Sorry, something went wrong!', 500)

