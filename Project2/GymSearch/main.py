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
from flask import request, url_for
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

# Configure logging
if not app.testing:
    logging.basicConfig(level=logging.INFO)
    client = google.cloud.logging.Client()
    # Attaches a Google Stackdriver logging handler to the root logger
    client.setup_logging()


@app.route('/')
def list():
    # start_after = request.args.get('start_after', None)
    books, last_title = firestore.list_details()

    return render_template('list.html', gymNames=books, last_title=last_title)


@app.route('/books/<book_id>')
def view(book_id):
    book = firestore.read(book_id)
    return render_template('view.html', book=book)

@app.route('/gyms/<gym_id>')
def viewGym(gym_id):
    gym = firestore.readGym(gym_id)
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType="All")

@app.route('/gyms/<gym_id>/<review_type>')
def filterGym(gym_id, review_type):
    gym = firestore.readGym(gym_id)
    gym['Reviews'] = firestore.getSpecificReviews(gym_id,review_type)
    return render_template('view_gym.html', gym=gym, gym_id=gym_id, reviewType=review_type)


@app.route('/gyms/add/<gym_id>', methods=['GET', 'POST'])
def add(gym_id):
    if request.method == 'POST':
        #print(request.form)
        data = request.form.to_dict(flat=True)
        data["date"] = datetime.datetime.now()
        firestore.add_review(data, gym_id)
        #print("done for ", g)

        return redirect(url_for('.viewGym', gym_id=gym_id))

    return render_template('form_gyms.html', action='Add', gyms={}, gymName=gym_id)

@app.route('/gyms/add', methods=['GET', 'POST'])
def addGym():
    if request.method == 'POST':
        #print(request.form)
        data = request.form.to_dict(flat=True)
        print(data)
        
        firestore.add_gym(data, data["name"])
        #print("done for ", g)

        #return redirect(url_for('.viewGym', gym_id=gym_id))

    return render_template('add_gym.html', action='Add', gym={})


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
