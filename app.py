import flask
from flask import Flask
from flask_socketio import SocketIO, emit, send
import firebase_admin
from firebase_admin import credentials, firestore, auth
import email_service
import time
import threading
import json
from flask_cors import CORS

import volunteer_event
import auth_service
import firestore_service

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

password_reset_datastore = {}

#----------------- Socket Events -----------------#

def student_listener_callback(doc_snapshot, changes, read_time):
    print("Student data changed")
    temp_student = []
    for doc in doc_snapshot:
        temp_student.append(doc.to_dict())
    socketio.emit('student_data', temp_student)
    
def volunteer_listener_callback(doc_snapshot, changes, read_time):
    print("Volunteer data changed")
    temp_volunteer = []
    for doc in doc_snapshot:
        temp_volunteer.append(doc.to_dict())
    socketio.emit('volunteer_data', json.dumps(temp_volunteer))

@socketio.on('listen_student')
def handle_connect():
    print("Client connected - student")
    send({'volunteer_data', "v1"})

@socketio.on('listen_volunteer')
def handle_connect():
    print("Client connected - volunteer")
    send({'student_data', "s2"})

student_listener_callback = db.collection('SCIE-Students').on_snapshot(student_listener_callback)
volunteer_listener_callback = db.collection('Volunteer').on_snapshot(volunteer_listener_callback)

@socketio.on('connect')
def handle_disconnect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    
#--------------- Socket Events Ends --------------#

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/signup', methods=['POST'])
def signup():
    data = flask.request.json
    email = data['email']
    password = data['password']
    if not email or not password:
        return 'Email and password are required', 400
    auth_service.create_user_with_email_and_password(email, password)
    return 'User created successfully', 200

@app.route('/signin', methods=['POST'])
def signin():
    data = flask.request.json
    email = data['email']
    password = data['password']
    try:
        response_data = auth_service.signIn_user_with_email_and_password(email, password)
        if 'error' in response_data:
            return flask.jsonify({"error": response_data['error']['message']}), 400
        id_token = response_data['idToken']
        uid = response_data['localId']
        return flask.jsonify({"idToken": id_token, "uid": uid}), 200
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 400
    
# tested
@app.route('/sendParticipateMessage', methods=['POST'])
def sendParticipateMessage():
    data = flask.request.json
    docId = data['docId']
    creatorId = data['creatorId']
    name = data['name']
    eventName = data['eventName']
    millisecondFromEpoch = data['millisecondFromEpoch']
    userId = data['userId']
    firestore_service.sendParticipateMessage(docId, creatorId, name, eventName, millisecondFromEpoch, userId)
    return 'Message sent successfully', 200

# tested
@app.route('/sendQuitMessage', methods=['POST'])
def sendQuitMessage():
    data = flask.request.json
    docId = data['docId']
    creatorId = data['creatorId']
    name = data['name']
    eventName = data['eventName']
    millisecondFromEpoch = data['millisecondFromEpoch']
    userId = data['userId']
    firestore_service.sendQuitMessage(docId, creatorId, name, eventName, millisecondFromEpoch, userId)
    return 'Message sent successfully', 200

# tested
@app.route('/participate', methods=['POST'])
def participate():
    data = flask.request.json
    docId = data['docId']
    uid = data['uid']
    millisecondSinceEpoch = data['millisecondSinceEpoch']
    volunteer = createVolunteerFromData(data)
    firestore_service.participate(docId, uid, millisecondSinceEpoch, volunteer)
    return 'Participation successful', 200

# tested
@app.route('/quitEvent', methods=['POST'])
def quitEvent():
    data = flask.request.json
    docId = data['docId']
    uid = data['uid']
    millisecondSinceEpoch = data['millisecondSinceEpoch']
    volunteer = createVolunteerFromData(data)
    firestore_service.quitEvent(docId, uid, millisecondSinceEpoch, volunteer)
    return 'Quit successful', 200

# tested
@app.route('/storeVolunteerEvent', methods=['POST'])
def storeVolunteerEvent():
    data = flask.request.json
    volunteer = createVolunteerFromData(data)
    firestore_service.storeVolunteerEvent(volunteer)
    return 'Event stored successfully', 200

# tested
@app.route('/updateVolunteerEvent', methods=['POST'])
def updateVolunteerEvent():
    data = flask.request.json
    docId = data['docId']
    volunteer = createVolunteerFromData(data)
    firestore_service.updateVolunteerEvent(docId, volunteer)
    return 'Event updated successfully', 200

# tested
@app.route('/ifStarred', methods=['POST'])
def ifStarred():
    data = flask.request.json
    docId = data['docId']
    uid = data['uid']
    return flask.jsonify({"ifStarred": firestore_service.ifStarred(docId, uid)}), 200

# tested
@app.route('/getVolunteerEvent', methods=['POST'])
def getVolunteerEvent():
    data = flask.request.json
    docId = data['docId']
    return flask.jsonify(firestore_service.getVolunteerEvent(docId)), 200

# tested
@app.route('/unStarVolunteerEventOnFirebase', methods=['POST'])
def unStarVolunteerEventOnFirebase():
    data = flask.request.json
    docId = data['docId']
    uid = data['uid']
    firestore_service.unStarVolunteerEventOnFirebase(docId, uid)
    return 'Event unstarred successfully', 200

# tested
@app.route('/starVolunteerEventOnFirebase', methods=['POST'])
def starVolunteerEventOnFirebase():
    data = flask.request.json
    docId = data['docId']
    uid = data['uid']
    firestore_service.starVolunteerEventOnFirebase(docId, uid)
    return 'Event starred successfully', 200

# tested
@app.route('/getUserInfo', methods=['POST'])
def getUserInfo():
    data = flask.request.json
    uid = data['uid']
    return flask.jsonify(firestore_service.getUserInfo(uid)), 200

# tested
@app.route('/getStudentInfo', methods=['POST'])
def getStudentInfo():
    data = flask.request.json
    docId = data['docId']
    return flask.jsonify(firestore_service.getStudentInfo(docId)), 200

# tested
@app.route('/setUserInfo', methods=['POST'])
def setUserInfo():
    data = flask.request.json
    uid = data['uid']
    userInfo = data['userInfo']
    firestore_service.setUserInfo(uid, userInfo)
    return 'User info set successfully', 200

# tested
@app.route('/ifStudentNumberUnique', methods=['POST'])
def ifStudentNumberUnique():
    data = flask.request.json
    studentNumber = int(data['studentNumber'])
    return flask.jsonify({"ifStudentNumberUnique": firestore_service.ifStudentNumberUnique(studentNumber)}), 200

# tested
@app.route('/recordApproveStudent', methods=['POST'])
def recordApproveStudent():
    data = flask.request.json
    approved = data['approved']
    participants = data['participants']
    docId = data['docId']
    firestore_service.recordApproveStudent(approved, participants, docId)
    return 'Approval recorded successfully', 200

# tested
@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    data = flask.request.json
    uid = data['uid']
    success = firestore_service.deleteAccount(uid)
    if (success):
        return 'Account deleted successfully', 200
    else:
        return 'Account deletion failed', 400

@app.route('/resetPassword', methods=['POST'])
def resetPassword():
    data = flask.request.json
    uid = data['uid']
    email = data['email']
    newPassword = data['newPassword']
    token = data['token']
    if(email not in password_reset_datastore):
        return 'Email does not exist in password reset datastore', 400
    if(password_reset_datastore[email] != token):
        return 'Invalid token', 400
    success: bool = auth_service.change_password(uid, newPassword)
    if(success):
        return 'Password reset successful', 200
    else:
        return 'Password reset failed', 400

@app.route('/sendPasswordResetEmail', methods=['POST'])
def sendPasswordResetEmail():
    email = flask.request.json['email']
    uid = firestore_service.getUidByEmail(email)
    if(uid == None):
        return 'Email does not exist', 400
    token = email_service.send_password_reset_email(email, uid)
    threading.Thread(target=add_token, args=(email, token, 600)).start()
    return 'Password reset email sent successfully', 200

@app.route("/verifyUserEmail", methods=['POST'])
def verifyUserEmail():
    email = flask.request.json['email']
    uid = firestore_service.getUidByEmail(email)
    success = email_service.verify_user_email(uid)
    if(success):
        return 'Email verified successfully', 200
    else:
        return 'Email verification failed', 400

def add_token(key: str, value: str, delay: int):
    password_reset_datastore[key] = value
    time.sleep(delay)
    password_reset_datastore.pop(key, None)

def createVolunteerFromData(data):
    return volunteer_event.VolunteerEvent(
        data["EventName"],
        data["Count"],
        data["Kind"],
        data["CsHours"],
        data["Time"],
        data["Location"],
        data["Details"],
        data["EventOfficer"],
        data["Spots"],
        data["Participants"],
        data["PhoneNumber"],
        data["Email"],
        data["Wechat"],
        data["CreatorUid"],
        data["Completed"]
    )
    
@app.route("/printData", methods=['POST'])
def printData():
    print(password_reset_datastore)
    return 'Data printed successfully', 200
   
@app.route('/sendTestEmail', methods=['POST']) 
def sendTestEmail():
    email = flask.request.json['email']
    print(email)
    email_service.send_test_email(email)
    return 'Test email sent successfully', 200
    
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)