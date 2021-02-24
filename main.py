from flask import Flask, request, flash, render_template, redirect, url_for, session
from rauth import OAuth2Service
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET")

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
        session.pop('user_id')
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
    session.clear()
    session['user_id'] = new_user_data['person']['id']
    # print(json_data)

    return redirect(url_for('people'))


@app.route('/events')
def events():
    if session.get('event_id'):
        response = nb_session.get(
            f'https://{nation_slug}.nationbuilder.com/api/v1/sites/{nation_slug}/pages/events/{session["event_id"]}',
            params={'format': 'json'},
            headers={'content-type': 'application/json'}
        )
        event_data = json.loads(response.text)
        if "event" in event_data:
            answer = event_data["event"]["name"]
        else:
            answer = 0
    else:
        answer = 0

    return render_template('events.html', answer=answer)


@app.route('/edit_event', methods=['POST'])
def edit_event():
    if session.get('event_id'):

        event_name = request.form['event_name']
        event_data = {
            "status": "unlisted",
            "start_time": "2013-03-01T18:00:00-00:00",
            "end_time": "2013-03-01T21:00:00-00:00",
            "name": event_name
        }

        response = nb_session.put(
            f'https://{nation_slug}.nationbuilder.com/api/v1/sites/{nation_slug}/pages/events/{session["event_id"]}',
            params={'format': 'json'},
            json={'event': event_data},
            headers={'content-type': 'application/json'}
        )
        print(json.loads(response.text))
    else:
        answer = 0

    return redirect(url_for('events'))


@app.route('/delete_event', methods=['POST'])
def delete_event():
    if session.get('event_id'):
        response = nb_session.delete(
            f'https://{nation_slug}.nationbuilder.com/api/v1/sites/{nation_slug}/pages/events/{session["event_id"]}',
        )
        session.pop('event_id')

    return redirect(url_for('events'))


@app.route('/create_event', methods=['POST'])
def create_event():
    event_start = request.form['event_start']
    event_end = request.form['event_end']
    event_name = request.form['event_name']
    event_details = {
        "status": "unlisted",
        "name": event_name,
        "intro": "Take the 24hr nofoodchallenge!!!",
        "time_zone": "Pacific Time (US & Canada)",
        "start_time": event_start,
        "end_time": event_end,
        "contact": {
            "name": "Byron Anderson",
            "contact_phone": "1234567890",
            "show_phone": "true",
            "contact_email": "contact@venue.com",
            "email": "contact@venue.com",
            "show_email": "true"
        },
        "rsvp_form": {
            "phone": "optional",
            "address": "required",
            "allow_guests": "true",
            "accept_rsvps": "true",
            "gather_volunteers": "true"
        },
        "show_guests": "true",
        "capacity": "80",
        "venue": {
            "name": "Ralphs Parking Lot",
            "address": {
                "address1": "123 Foo St",
                "city": "Pasadena",
                "state": "CA"
            }
        }
    }
    # this will create a new endpoint "person"
    response = nb_session.post(
        f'https://{nation_slug}.nationbuilder.com/api/v1/sites/{nation_slug}/pages/events',
        params={'format': 'json'},
        json={'event': event_details},
        headers={'content-type': 'application/json'}
    )
    new_event_data = json.loads(response.text)
    print(new_event_data)
    session['event_id'] = new_event_data['event']['id']

    return redirect(url_for('events'))


@app.route('/survey')
def survey():
    if session.get('question_answer'):
        answer = "question_answered"  # question is answered.
    else:
        if session.get('user_id'):
            answer = "no_answer_given"  # user is created, but not answered survey
        else:
            answer = "no_user_created"  # user not created

    response_all = nb_session.get(
        f'https://{nation_slug}.nationbuilder.com/api/v1/survey_responses',
        params={'format': 'json'},
        headers={'content-type': 'application/json'}
    )
    answer_surveys = json.loads(response_all.text)
    all_emails = {}
    for single_answers in answer_surveys['results']:
        response = nb_session.get(
            f'https://{nation_slug}.nationbuilder.com/api/v1/people/{single_answers["person_id"]}',
            params={'format': 'json'},
            headers={'content-type': 'application/json'}
        )
        user_data = json.loads(response.text)
        user_email = user_data['person']['email']
        all_emails.update({"email": user_email})

    print(all_emails)

    return render_template('survey.html', answer=answer, all_emails=all_emails)


@app.route('/create_survey', methods=['POST'])
def create_survey():
    survey_details = {
        "slug": "surveyTester1",
        "name": "SurveyTester1",
        "tags": ["funny"],
        "status": "published",
        "questions": [{
            "prompt": "is this a test question?",
            "external_id": "null",
            "slug": "test_question",
            "type": "text",
            "status": "published"
        }]
    }
    # this will create a new endpoint "person"
    response = nb_session.post(
        f'https://{nation_slug}.nationbuilder.com/api/v1/sites/{nation_slug}/pages/surveys',
        params={'format': 'json'},
        json={'survey': survey_details},
        headers={'content-type': 'application/json'}
    )
    new_survey_data = json.loads(response.text)
    print(new_survey_data)
    return redirect(url_for('surveys'))


@app.route('/answer_survey', methods=['POST'])
def answer_survey():
    if session.get('question_answer'):
        answer = 0
    else:
        if session.get('user_id'):
            question_answer = request.form['question_answer']
            create_answer = {
                "survey_id": 3,
                "person_id": session['user_id'],
                "question_responses": [{
                    "question_id": 4,
                    "response": question_answer
                }]
            }
            # this will create a new endpoint "survey answer"
            response = nb_session.post(
                f'https://{nation_slug}.nationbuilder.com/api/v1/survey_responses',
                params={'format': 'json'},
                json={'survey_response': create_answer},
                headers={'content-type': 'application/json'}
            )
            new_answer_data = json.loads(response.text)
            print(new_answer_data)
            session['question_answer'] = new_answer_data['survey_response']['id']

    return redirect(url_for('survey'))


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
