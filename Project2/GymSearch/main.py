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
global city

# session['gymList'] = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'gymList' in session:
        session.pop('gymList', None)
    if 'list_with_hours' in session:
        session.pop('list_with_hours', None)
    if 'gym_full_list' in session:
        session.pop('gym_full_list', None)

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

# @app.route('/list')
# def list():
#     gymNames, last_title = firestore.list_details()

#     return render_template('list.html', gymNames=gymNames, last_title=last_title)

@app.route('/list', methods=['GET', 'POST'])
def list_on_pref():
    # data = request.form.to_dict(flat=True)
    # area = "Tempe"
    # books, last_title = firestore.list_on_pref(area)
    if request.method == 'POST':
        message=""
        details = request.form
        # print(details)
        area = details['area']
        print(area)
        global city
        city = area
        books, last_title, sortedList = firestore.list_on_pref(area)
        session['gym_full_list'] = sortedList 
        session['gymList'] = sortedList
        session['list_with_hours'] = books
        session['full_list_with_hours'] = books
        print("session gymList : ", session['gymList'])
        print("session with gyms and hours : ", session['list_with_hours'])
        return render_template('trial_home.html', gymNames=books, last_title=last_title, fitnessType="All", message=message)
    else:
        if "typeCityMessage" in session:
            message = session["typeCityMessage"]
        else:
            message=""
        books = []
        last_title = None
        if 'list_with_hours' in session:
            print("here inside if")
            books = session['full_list_with_hours']
            print(" inside else, session gymList : ", session['gymList'])
            print("session with gyms and hours : ", session['list_with_hours'])
        return render_template('trial_home.html', gymNames=books, last_title=last_title, fitnessType="All", message=message)
    # return render_template('trial_home.html')

@app.route('/list/<filter_type>', methods=['GET', 'POST'])
def filter_list_on_pref(filter_type):
    message = ""
    if 'gym_full_list' not in session:
        message = "Please enter city first!"
        session["typeCityMessage"] = message
        # books={}
        # last_title = None
        # print("here: ", books)
        # return render_template('trial_home.html', gymNames=books, last_title=last_title, fitnessType="All", message=message)
        return redirect(url_for('.list_on_pref'))
    else:
        print("inside filter type, session gymList : ", session['gymList'])
        print("session with gyms and hours : ", session['list_with_hours'])
        books, last_title, sortedList = firestore.list_gyms_on_filter(city, filter_type, session['gym_full_list'])
        session['gymList'] = sortedList
        session['list_with_hours'] = books
        print("after filter type, session gymList : ", session['gymList'])
        print("session with gyms and hours : ", session['list_with_hours'])
        return render_template('trial_home.html', gymNames=books, last_title=last_title, fitnessType=filter_type, message=message)

@app.route('/list/hours/<filter_hour>', methods=['GET', 'POST'])
def filter_list_on_hours(filter_hour):
    print("Here in list hours")
    print("inside list hours, session gymList : ", session['gymList'])
    print("session with gyms and hours : ", session['list_with_hours'])
    books, last_title = firestore.list_gyms_on_filter_hours(city, filter_hour, session['list_with_hours'])
    # session['gymList'] = sortedList
    print("after list hours, session gymList : ", session['gymList'])
    print("session with gyms and hours : ", session['list_with_hours'])
    return render_template('trial_home.html', gymNames=books, last_title=last_title, fitnessHour=filter_hour)

@app.route('/list/distance/<user_location>', methods=['GET', 'POST'])
def sort_list_by_distance(user_location):
    print("here in sort by distance")
    books, last_title = firestore.gyms_sorted_by_distance(user_location, session['list_with_hours'], city)
    return render_template('trial_home.html', gymNames=books, last_title=last_title, userLocation=user_location)

@app.route('/books/<book_id>')
def view(book_id):
    book = firestore.read(book_id)
    return render_template('view.html', book=book)

@app.route('/gyms/<gym_id>')
def viewGym(gym_id):
    gym = firestore.readGym(gym_id)
    if "https://" not in gym["website"] and "http://" not in gym["website"]:
        gym["website"] = "https://" + gym["website"]
        
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType="All", message="")

@app.route('/gyms/<gym_id>/view')
def viewForGymUser(gym_id):
    gym = firestore.readGym(gym_id)
    if "https://" not in gym["website"] and "http://" not in gym["website"]:
        gym["website"] = "https://" + gym["website"]
    return render_template('view_gym_user.html', gym=gym, gym_id=gym_id, reviewType="All")

@app.route('/gyms/<gym_id>/subscribe')
def subscribe(gym_id):
    print(request.args.get('email'))
    print(gym_id)
    gym = firestore.add_subscriber(request.args.get('email'), gym_id)
    
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType="All", message = "Subscribed Successfully!")

@app.route('/gyms/<gym_id>/<review_type>')
def filterGym(gym_id, review_type):
    gym = firestore.readGym(gym_id)
    gym['Reviews'] = firestore.getSpecificReviews(gym_id,review_type)
    if "https://" not in gym["website"] and "http://" not in gym["website"]:
        gym["website"] = "https://" + gym["website"]
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType=review_type, message="")

@app.route('/gyms/user/<gym_id>/<review_type>')
def filterGymUser(gym_id, review_type):
    gym = firestore.readGym(gym_id)
    gym['Reviews'] = firestore.getSpecificReviews(gym_id,review_type)
    if "https://" not in gym["website"] and "http://" not in gym["website"]:
        gym["website"] = "https://" + gym["website"]
    return render_template('view_gym_user.html', gym=gym, gym_id=gym_id, reviewType=review_type)

@app.route('/gyms/add/<gym_id>', methods=['GET', 'POST'])
def addReview(gym_id):
    if request.method == 'POST':
        #print(request.form)
        data = request.form.to_dict(flat=True)
        data["date"] = datetime.datetime.now()
        firestore.add_review(data, gym_id)
        #print("done for ", g)

        return redirect(url_for('.viewGym', gym_id=gym_id))

    return render_template('add_review.html', action='Add', gyms={}, gymName=gym_id)

@app.route('/gyms/add', methods=['GET', 'POST'])
def addGym():
    message = ""
    if request.method == 'POST':
        data = request.form.to_dict()
        gymName = data["name"]
        user = firestore.readGymUser(data["email"])
        if(user == None):
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
            
            #data["Sentiment Score"] = 0.875
            firestore.add_gym(data)
            firestore.add_gym_user(userDict)
            #session['user'] = 'gym'
            
            flag = firestore.add_extracted_gym_details(gymName)
            if flag==1:
                message = "Could not find gym!!"
                return render_template('add_gym.html', action='Add', gym={}, message=message)
            return redirect(url_for('.viewForGymUser', gym_id=gymName))
        else:
            message = "User Already Exists. Please Try to Login."

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
        data["Area"] = "Seattle"
        gym = firestore.updateGym(data, gym_id)
        status = send_emails(gym_id)
        print(status)
        return redirect(url_for('.viewForGymUser', gym_id=gym_id)) 

    return render_template('edit_gym.html', gym=gym, gym_id=gym_id, eventNum=len(gym["events"])+1)

def send_emails(gym_id):
    subscribers, parsed_url = firestore.getSubscribers(gym_id)
    msg = Message('Hello', sender = 'noreply.gymsearch@gmail.com', recipients = subscribers)
    # msg.body = "Hello User, Gym information is updated ! https://8080-cs-621499849372-default.cs-us-west1-olvl.cloudshell.dev/gyms/Spot%20Fitness%20and%20Spa"
    msg.body = "Hello Subscriber, " + gym_id + " gym's information has been updated! Check it out at "+ parsed_url
    mail.send(msg)
    return "Sent"

@app.route('/books/<book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    book = firestore.read(book_id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        # If an image was uploaded, update the data to point to the new image.
        image_url = upload_image_file(request.files.get('image'))

        if image_url:
            data['imageUrl'] = image_url

        book = firestore.update(data, book_id)

        return redirect(url_for('.view', book_id=book['id']))

    return render_template('form.html', action='Edit', book=book)



@app.route('/books/<book_id>/delete')
def delete(book_id):
    firestore.delete(book_id)
    return redirect(url_for('.list'))


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
