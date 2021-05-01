# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import firestore
from flask import current_app, flash, Flask, Markup, redirect, render_template
from flask import request, url_for, session
from flask_mail import Mail, Message
from google.cloud import error_reporting
import google.cloud.logging
import storage
import datetime
import nltk


# [START upload_image_file]
def upload_image_file(img):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not img:
        return None

    public_url = storage.upload_file(
        img.read(),
        img.filename,
        img.content_type
    )

    current_app.logger.info(
        'Uploaded file %s as %s.', img.filename, public_url)

    return public_url
# [END upload_image_file]


app = Flask(__name__)
app.config.update(
    SECRET_KEY='secret',
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg', 'gif'])
)

app.debug = False
app.testing = False
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply.gymsearch@gmail.com'
app.config['MAIL_PASSWORD'] = 'Test@12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client()
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging()

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'gymList' in session:
        session.pop('gymList', None)
    if 'list_with_hours' in session:
        session.pop('list_with_hours', None)
    if 'gym_full_list' in session:
        session.pop('gym_full_list', None)
    if 'typeCityMessage' in session:
        session.pop('typeCityMessage', None)
    if 'city' in session:
        session.pop('city', None)
    if "filter_type" in session:
        session.pop('filter_type', None)
    if 'full_list_with_hours' in session:
        session.pop('full_list_with_hours', None)
 
    result = ""
    hideForm = True
    if request.method == 'POST':
        details = request.form
        result, gymName = firestore.gymLogin(details["email"], details["password"])
        hideForm = False
        if result == "Success":
            #session['user'] = 'gym'
            return redirect(url_for('.viewForGymUser', gym_id=gymName))
    return render_template('home.html', message=result, hideForm=hideForm)

@app.route('/logout')
def logout():
    #session.pop('user', None)
    return redirect(url_for('.home'))

@app.route('/list', methods=['GET', 'POST'])
def list_on_pref():
    if request.method == 'POST':
        message=""
        details = request.form
        # print(details)
        area = details['area']        
        session['city'] = area
        books, last_title, sortedList = firestore.list_on_pref(area)
        session['gym_full_list'] = sortedList 
        session['gymList'] = sortedList
        session['list_with_hours'] = books
        session['full_list_with_hours'] = books
        session["filter_type"] = "All"
        return render_template('gym_list.html', gymNames=books, last_title=last_title, fitnessType="All", message=message, area=session["city"], fitnessHour="All", sortBy="Recommended")
    else:
        if "typeCityMessage" in session and 'city' not in session:
            message = session["typeCityMessage"]
        else:
            message=""
        books = []
        last_title = None

        if 'list_with_hours' in session:
            books = session['list_with_hours']

        if 'city' in session:
            city = session['city']
        else:
            city=""

        if 'filter_type' in session:
            filter_type = session["filter_type"]
        else:
            filter_type = "All"
        
        if filter_type == "All":
            if 'full_list_with_hours' in session:
                books = session['full_list_with_hours']
                session['list_with_hours'] = session['full_list_with_hours'] 

        return render_template('gym_list.html', gymNames=books, last_title=last_title, fitnessType=filter_type, message=message, area=city, fitnessHour="All", sortBy="Recommended")

@app.route('/list/<filter_type>', methods=['GET', 'POST'])
def filter_list_on_pref(filter_type):
    message = ""
    if filter_type == "All":
        session['filter_type'] = "All"
        return redirect(url_for('.list_on_pref'))

    if 'gym_full_list' not in session:
        message = "Please enter city first!"
        session["typeCityMessage"] = message
        return redirect(url_for('.list_on_pref'))
    else:
        books, last_title, sortedList = firestore.list_gyms_on_filter(session['city'], filter_type, session['gym_full_list'])
        session['gymList'] = sortedList
        session['list_with_hours'] = books
        session["filter_type"] = filter_type
        return render_template('gym_list.html', gymNames=books, last_title=last_title, fitnessType=filter_type, message=message, area=session["city"], fitnessHour="All", sortBy="Recommended")

@app.route('/list/hours/<filter_hour>', methods=['GET', 'POST'])
def filter_list_on_hours(filter_hour):
    books, last_title = firestore.list_gyms_on_filter_hours(session['city'], filter_hour, session['list_with_hours'])
    return render_template('gym_list.html', gymNames=books, last_title=last_title, fitnessHour=filter_hour, fitnessType=session['filter_type'], area=session["city"],  sortBy="Recommended")

@app.route('/list/distance/<user_location>', methods=['GET', 'POST'])
def sort_list_by_distance(user_location):
    # print("here in sort by distance")
    books, last_title = firestore.gyms_sorted_by_distance(user_location, session['list_with_hours'], session['city'])
    return render_template('gym_list.html', gymNames=books, last_title=last_title, userLocation=user_location, fitnessType=session['filter_type'], area=session["city"],  sortBy="Distance", fitnessHour= "All" )

@app.route('/gyms/<gym_id>')
def viewGym(gym_id):
    gym = viewHelper(gym_id) 
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType="All", message="")

def viewHelper(gym_id):
    gym = firestore.readGym(gym_id)
    if "Frequent_Words" in gym:
        freq_word_list=[]
        for word in gym["Frequent_Words"]:
            freq_word_list.append(str(word)+"("+str(gym["Frequent_Words"][word])+")") 
        gym["freq_word_list"]=freq_word_list
    return gym 

@app.route('/gyms/<gym_id>/view')
def viewForGymUser(gym_id):
    gym = viewHelper(gym_id)
    return render_template('view_gym_user.html', gym=gym, gym_id=gym_id, reviewType="All")

@app.route('/gyms/<gym_id>/subscribe')
def subscribe(gym_id):
    gym = firestore.add_subscriber(request.args.get('email'), gym_id)
    if "Frequent_Words" in gym:
        freq_word_list=[]
        for word in gym["Frequent_Words"]:
            freq_word_list.append(str(word)+"("+str(gym["Frequent_Words"][word])+")") 
        gym["freq_word_list"]=freq_word_list
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType="All", message = "Subscribed Successfully!")

@app.route('/gyms/<gym_id>/<review_type>')
def filterGym(gym_id, review_type):
    gym = viewHelper(gym_id)
    gym['Reviews'] = firestore.getSpecificReviews(gym_id,review_type)    
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType=review_type, message="")

@app.route('/gyms/user/<gym_id>/<review_type>')
def filterGymUser(gym_id, review_type):
    gym = viewHelper(gym_id)
    gym['Reviews'] = firestore.getSpecificReviews(gym_id,review_type)
    return render_template('view_gym_user.html', gym=gym, gym_id=gym_id, reviewType=review_type)

@app.route('/gyms/add/<gym_id>', methods=['GET', 'POST'])
def addReview(gym_id):
    if request.method == 'POST':
        #print(request.form)
        data = request.form.to_dict(flat=True)
        data["date"] = datetime.datetime.now()
        firestore.add_review(data, gym_id)
        return redirect(url_for('.viewGym', gym_id=gym_id))

    return render_template('add_review.html', action='Add', gyms={}, gymName=gym_id)

@app.route('/gyms/add', methods=['GET', 'POST'])
def addGym():
    message = ""
    if request.method == 'POST':
        data = request.form.to_dict()
        gymName = data["name"]
        user = firestore.readGymUser(data["email"])
        gym = firestore.readGym(gymName)
        if(user == None and gym == None):
            i = 1
            events = []
            userDict = {}
            while(True):
                key = "event" + str(i) + "type"
                if key in data:
                    dict = {}
                    dict = {"type" : data[key], "name" : data["event" + str(i) + "name"], "time" : data["event" + str(i) + "time"], "days" : data["event" + str(i) + "days"], "occupancy" : data["event"+ str(i) + "occupancy"]}
                    events.append(dict)
                    del data[key]
                    del data["event" + str(i) + "name"]
                    del data["event" + str(i) + "time"]
                    del data["event" + str(i) + "days"]
                    del data["event" + str(i) + "occupancy"]
                    i += 1
                else:
                    break 
            data["events"] = events
            data["location"] = data["addressLine1"]+ ", " + data["city"] + ", " + data["state"] + " " + data["zipCode"]
            data["Area"] = data["city"]
            userDict["email"] = data["email"]
            userDict["password"] = data["password"]
            userDict["contact"] = data["contact"]
            userDict["name"] = data["name"]

            del data["addressLine1"]
            del data["city"]
            del data["state"]
            del data["zipCode"]

            del data["email"]
            del data["password"]
            
            firestore.add_gym(data)
            firestore.add_gym_user(userDict)
            
            flag = firestore.add_extracted_gym_details(gymName)
            if flag==1:
                message = "Could not find gym!!"
                return render_template('add_gym.html', action='Add', gym={}, message=message)
            return redirect(url_for('.viewForGymUser', gym_id=gymName))
        elif gym == None:
            message = "User Already Exists! Please Try to Login."
        else:
            message = "Gym is already registered with other email address!"

    return render_template('add_gym.html', action='Add', gym={}, message=message, eventNum=2)

@app.route('/gyms/<gym_id>/edit', methods=['GET', 'POST'])
def editGym(gym_id):
    gym = firestore.readGym(gym_id)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        i = 1
        events = []
        while(True):
            key = "event" + str(i) + "type"
            if key in data:
                dict = {}
                dict = {"type" : data[key], "name" : data["event" + str(i) + "name"], "time" : data["event" + str(i) + "time"], "days" : data["event" + str(i) + "days"], "occupancy" : data["event"+ str(i) + "occupancy"]}
                events.append(dict)
                del data[key]
                del data["event" + str(i) + "name"]
                del data["event" + str(i) + "time"]
                del data["event" + str(i) + "days"]
                del data["event" + str(i) + "occupancy"]
                i += 1
            else:
                break 
        data["events"] = events
        data["Time"] = {"Monday" : data["Monday"], "Tuesday" : data["Tuesday"], "Wednesday" : data["Wednesday"], "Thursday" : data["Thursday"], "Friday" : data["Friday"], "Saturday" : data["Saturday"], "Sunday" : data["Sunday"]}
        del data["Monday"]
        del data["Tuesday"]
        del data["Wednesday"]
        del data["Thursday"]
        del data["Friday"]
        del data["Saturday"]
        del data["Sunday"]
        gym = firestore.updateGym(data, gym_id)
        status = send_emails(gym_id)
        print(status)
        return redirect(url_for('.viewForGymUser', gym_id=gym_id)) 

    return render_template('edit_gym.html', gym=gym, gym_id=gym_id, eventNum=len(gym["events"])+1)

def send_emails(gym_id):
    subscribers, parsed_url = firestore.getSubscribers(gym_id)
    if subscribers:
        msg = Message('Hello', sender = 'noreply.gymsearch@gmail.com', recipients = subscribers)
        # msg.body = "Hello User, Gym information is updated ! https://8080-cs-621499849372-default.cs-us-west1-olvl.cloudshell.dev/gyms/Spot%20Fitness%20and%20Spa"
        msg.body = "Hello Subscriber, " + gym_id + " gym's information has been updated! Check it out at "+ parsed_url
        mail.send(msg)
        return "Sent"
    else:
        return "No subscribers"

@app.route('/logs')
def logs():
    logging.info('Hey, you triggered a custom log entry. Good job!')
    flash(Markup('''You triggered a custom log entry. You can view it in the
        <a href="https://console.cloud.google.com/logs">Cloud Console</a>'''))
    return redirect(url_for('.list'))


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


# Add an error handler that reports exceptions to Stackdriver Error
# Reporting. Note that this error handler is only used when debug
# is False
@app.errorhandler(500)
def server_error(e):
    client = error_reporting.Client()
    client.report_exception(
        http_context=error_reporting.build_flask_context(request))
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
