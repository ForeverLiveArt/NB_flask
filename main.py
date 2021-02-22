from flask import Flask, request, flash, jsonify, render_template, redirect, url_for, session
from rauth import OAuth2Service
import os
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

nation_slug = os.getenv("NATION_SLUG")
oauth_id = os.getenv("OAUTH_ID")
oauth_secret = os.getenv("OAUTH_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
session_token = os.getenv("SESSION_TOKEN")

access_token_url = f'https://{nation_slug}.nationbuilder.com/oauth/token'
authorize_url = f'{nation_slug}.nationbuilder.com/oauth/authorize'
service = OAuth2Service(
    client_id=oauth_id,
    client_secret=oauth_secret,
    name='BIITECH NB',
    authorize_url=authorize_url,
    access_token_url=access_token_url,
    base_url=f'{nation_slug}.nationbuilder.com')
print(service.base_url)

nb_session = service.get_session(session_token)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/events')
def events():
    return render_template('events.html')


@app.route('/survey')
def survey():
    return render_template('survey.html')


@app.route('/people')
def people():
    # this will get all person data with id
    if session.get('user_id'):
        response = nb_session.get(
            f'https://{nation_slug}.nationbuilder.com/api/v1/people/{session["user_id"]}',
            params={'format': 'json'},
            headers={'content-type': 'application/json'}
        )
        person = json.loads(response.text)
        if "person" in person:
            answer = person["person"]["first_name"] + ' ' + person["person"]["last_name"]
        else:
            answer = 0
    else:
        answer = 0

    # this will get all people data
    response_all = nb_session.get(
        f'https://{nation_slug}.nationbuilder.com/api/v1/people/',
        params={'format': 'json'},
        headers={'content-type': 'application/json'}
    )
    userlist = json.loads(response_all.text)

    return render_template('people.html', answer=answer, userlist=userlist)


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if session.get('user_id'):
        response = nb_session.delete(
            f'https://{nation_slug}.nationbuilder.com/api/v1/people/{session["user_id"]}',
        )
        session.clear()

    return redirect(url_for('people'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    if session.get('user_id'):
        # get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        update_person = {
            "first_name": first_name,
            "last_name": last_name
        }
        # put new data to user
        response = nb_session.put(
            f'https://{nation_slug}.nationbuilder.com/api/v1/people/{session["user_id"]}',
            params={'format': 'json'},
            json={'person': update_person},
            headers={'content-type': 'application/json'}
        )
    else:
        answer = 0
    #
    # json_data = json.loads(response.text)
    # print(json_data)
    return redirect(url_for('people'))


@app.route('/create_user', methods=['POST'])
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    create_person = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "sex": "M",
        "signup_type": 0,
        "employer": "BIITECH",
        "party": "P",
        "registered_address": {
            "state": "BC",
            "country_code": "CA"
        }
    }
    # this will create a new endpoint "person"
    response = nb_session.post(
        f'https://{nation_slug}.nationbuilder.com/api/v1/people',
        params={'format': 'json'},
        json={'person': create_person},
        headers={'content-type': 'application/json'}
    )
    new_user_data = json.loads(response.text)
    session['user_id'] = new_user_data['person']['id']
    # print(json_data)
    return redirect(url_for('people'))


@app.route('/create_event', methods=['POST'])
def create_event():
    event_date = request.form['event_date']
    event_name = request.form['last_name']
    create_event = {
        "event": {
            "status": "unlisted",
            "name": "Fasting Day",
            "intro": "Take the 24hr nofoodchallenge!!!",
            "time_zone": "Pacific Time (US & Canada)",
            "start_time": "2013-05-08T17:00:00-00:00",
            "end_time": "2013-05-08T19:00:00-00:00",
            "contact": {
                "name": "Byron Anderson",
                "contact_phone": "1234567890",
                "show_phone": true,
                "contact_email": "contact@venue.com",
                "email": "contact@venue.com",
                "show_email": true
            },
            "rsvp_form": {
                "phone": "optional",
                "address": "required",
                "allow_guests": true,
                "accept_rsvps": true,
                "gather_volunteers": true
            },
            "show_guests": true,
            "capacity": 80,
            "venue": {
                "name": "Ralphs Parking Lot",
                "address": {
                    "address1": "123 Foo St",
                    "city": "Pasadena",
                    "state": "CA"
                }
            }
        }
    }
    # this will create a new endpoint "person"
    response = nb_session.post(
        f'https://{nation_slug}.nationbuilder.com/api/v1/people',
        params={'format': 'json'},
        json={'person': create_person},
        headers={'content-type': 'application/json'}
    )
    new_user_data = json.loads(response.text)
    session['user_id'] = new_user_data['person']['id']
    # print(json_data)
    return redirect(url_for('people'))


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
