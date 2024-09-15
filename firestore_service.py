import app
import volunteer_event
from firebase_admin import firestore, auth

studentCollection = "SCIE-Students"
volunteerCollection = "Volunteer"

def sendParticipateMessage(
        docId: str, # participant event's docId
        creatorId: str, # creator of the event
        name: str, # name of the student
        eventName: str, # name of the event
        millisecondFromEpoch: int, # time of participation
        userId: str # id of the student
    ) -> None:
    app.db.collection(studentCollection).document(creatorId).collection("Messages").add({
        "title": f"{name} joined {eventName}",
        "docId": docId,
        "time": millisecondFromEpoch,
        "studentId": userId,
    })
    
def sendQuitMessage(
        docId: str, # participant event's docId
        creatorId: str, # creator of the event
        name: str, # name of the student
        eventName: str, # name of the event
        millisecondFromEpoch: int, # time of participation
        userId: str # id of the student
    ) -> None:
    app.db.collection(studentCollection).document(creatorId).collection("Messages").add({
        "title": f"{name} quit {eventName}",
        "docId": docId,
        "time": millisecondFromEpoch,
        "studentId": userId,
    })
    
#TODO -> need to add to box in the client side
def participate(
        docId: str, # participant event's docId
        uid: str,
        millisecondSinceEpoch: int, # time of participation
        volunteer: volunteer_event.VolunteerEvent,
    ):
    app.db.collection(volunteerCollection).document(docId).update({
        "Participants": firestore.ArrayUnion([uid])},
    )
    studentInfo = getStudentInfo(uid)
    if (studentInfo == None): return
    sendParticipateMessage(
        docId,
        volunteer.creatorUid,
        studentInfo["username"],
        volunteer.eventName,
        millisecondSinceEpoch,
        uid
    )
    
#TODO -> need to remove from box in the client side
def quitEvent(
        docId: str, # participant event's docId
        uid: str,
        millisecondSinceEpoch: int, # time of participation
        volunteer: volunteer_event.VolunteerEvent,
    ):
    app.db.collection(volunteerCollection).document(docId).update({
        "Participants": firestore.ArrayRemove([uid])},
    )
    studentInfo = getStudentInfo(uid)
    if (studentInfo == None): return
    sendQuitMessage(
        docId,
        volunteer.creatorUid,
        studentInfo["username"],
        volunteer.eventName,
        millisecondSinceEpoch,
        uid
    )
    
def storeVolunteerEvent(volunteer: volunteer_event.VolunteerEvent) -> None:
    app.db.collection(volunteerCollection).add(volunteer.toMap())

def updateVolunteerEvent(docId: str, volunteer: volunteer_event.VolunteerEvent) -> None:
    app.db.collection(volunteerCollection).document(docId).update(volunteer.toMap())
    
def ifStarred(docId: str, uid: str) -> bool:
    return docId in app.db.collection(studentCollection).document(uid).get().to_dict()["starred"]

def getVolunteerEvent(docId: str) -> dict:
    return app.db.collection(volunteerCollection).document(docId).get().to_dict()

def unStarVolunteerEventOnFirebase(docId: str, uid: str) -> None:
    app.db.collection(studentCollection).document(uid).update({
        "starred": firestore.ArrayRemove([docId])},
    )

def starVolunteerEventOnFirebase(docId: str, uid: str) -> None:
    app.db.collection(studentCollection).document(uid).update({
        "starred": firestore.ArrayUnion([docId])},
    )

def getUserInfo(uid: str) -> dict:
    return app.db.collection(studentCollection).document(uid).get().to_dict()

def getStudentInfo(docId: str) -> dict:
    try:
        return app.db.collection(studentCollection).document(docId).get().to_dict()
    except:
        return None

def setUserInfo(uid: str, userInfo: dict) -> bool:
    try:
        app.db.collection(studentCollection).document(uid).set(userInfo, merge=True)
        return True
    except:
        return False

def ifStudentNumberUnique(studentNumber: int) -> bool:
    return len(app.db.collection(studentCollection).where("studentNumber", "==", studentNumber).get()) == 0

def recordApproveStudent(
        approved: list[bool],
        participants: list[str],
        docId: str,
    ):
    approvedStudents: list[str] = []
    disapprovedStudents: list[str] = []
    for i in range(len(participants)):
        if (approved[i]):
            approvedStudents.append(participants[i])
        else:
            disapprovedStudents.append(participants[i])
    batch = app.db.batch()
    batch.update(
        app.db.collection(volunteerCollection).document(docId),
        {"Completed": approvedStudents}
    )
    for i in range(len(approvedStudents)):
        batch.update(
            app.db.collection(studentCollection).document(approvedStudents[i]),
            {"completed": firestore.ArrayUnion([docId])}
        )
    for i in range(len(disapprovedStudents)):
        batch.update(
            app.db.collection(studentCollection).document(disapprovedStudents[i]),
            {"disapproved": firestore.ArrayUnion([docId])}
        )
    batch.commit()
    
def deleteAccount(
        uid: str
    ) -> bool:
    try:
        docs = app.db.collection(studentCollection).document(uid).collection("Messages").get()
        for doc in docs:
            app.db.collection(studentCollection).document(uid).collection("Messages").document(doc.id).delete()
        app.db.collection(studentCollection).document(uid).delete()
        auth.delete_user(uid)
        return True
    except:
        return False
    
def getUidByEmail(email: str) -> str:
    docs = app.db.collection(studentCollection).where("email", "==", email).get()
    if(len(docs) == 0 or len(docs) > 1): return None
    for doc in docs:
        return doc.id

#TODO try catch decorator
