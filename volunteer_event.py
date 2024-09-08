class VolunteerEvent:
    
    def __init__(
            self,
            eventName: str,
            count: int,
            kind: list[str],
            csHours: float,
            time: int, # millisecond from epoch,
            location: str,
            details: str,
            eventOfficer: str,
            spots: int,
            participants: list[str], # list of participants's user id
            phoneNumber: str,
            email: str,
            wechat: str,
            creatorUid: str,
            completed: list[str] # list of completed users's user id
        ) -> None:
        self.eventName = eventName
        self.count = count
        self.kind = kind
        self.csHours = csHours
        self.time = time
        self.location = location
        self.details = details
        self.eventOfficer = eventOfficer
        self.spots = spots
        self.participants = participants
        self.phoneNumber = phoneNumber
        self.email = email
        self.wechat = wechat
        self.creatorUid = creatorUid
        self.completed = completed
        
    def toMap(self):
        return {
            "EventName": self.eventName,
            "Count": self.count,
            "Kind": self.kind,
            "CsHours": self.csHours,
            "Time": self.time,
            "Location": self.location,
            "Details": self.details,
            "EventOfficer": self.eventOfficer,
            "Spots": self.spots,
            "Participants": self.participants,
            "PhoneNumber": self.phoneNumber,
            "Email": self.email,
            "Wechat": self.wechat,
            "CreatorUid": self.creatorUid,
            "Completed": self.completed,
        }