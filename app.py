from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor(dictionary=True)
    return dbconn

@app.route("/")
def home():
    return listmembers()

@app.route("/listmembers")
def listmembers():
    connection = getCursor()
    connection.execute("SELECT m.*, t.TeamName FROM members m left join teams t on m.TeamID = t.TeamID;")
    memberList = connection.fetchall()
    # print(memberList)
    return render_template("memberlist.html", memberlist = memberList)    


@app.route("/listevents")
def listevents():
    connection = getCursor()
    connection.execute("SELECT e.*, t.TeamName FROM events e left join teams t on e.NZTeam = t.TeamID;")
    eventList = connection.fetchall()
    return render_template("eventlist.html", eventlist = eventList)

@app.route("/admin")
def admin():    
    queryParameters = request.args
    memberName = queryParameters.get("member_query")
    eventName = queryParameters.get("event_query")
    sql = "SELECT m.*, t.TeamName FROM members m left join teams t on m.TeamID = t.TeamID"    
    if memberName != "" and memberName is not None:
        sql = sql + " where m.FirstName like '%" + memberName + "%' or m.LastName like '%"+ memberName +"%'"
    connection = getCursor()
    connection.execute(sql)    
    memberList = connection.fetchall()    

    eventSql = "SELECT e.*, t.TeamName FROM events e left join teams t on e.NZTeam = t.TeamID"    
    if eventName != "" and eventName is not None:
        eventSql = eventSql + " where e.EventName like '%" + eventName + "%'"
    connection.execute(eventSql)
    eventList = connection.fetchall()
    print(eventList)

    return render_template("admin.html", memberlist = memberList, eventlist = eventList, isAdmin = True)    

@app.route("/member", methods=['GET'])
def memberPage():    
    queryParameters = request.args
    memberId = queryParameters.get("id")
    member = None
    if memberId is not None:
        member = getMember(memberId)
    teams = listteams()
    return render_template("member.html", memberId = memberId, member = member, teams = teams, isAdmin = True)    

@app.route("/member", methods=['POST'])
def addMember():    
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName') 
    teamId = request.form.get('teamId')    
    city = request.form.get('city')
    birthdate = request.form.get('dob')
    data = (firstName, lastName, teamId, city, birthdate)   
    connection = getCursor()    
    connection.execute("insert into members(FirstName, LastName, TeamID, City, Birthdate) \
                       VALUES(%s, %s, %s, %s, %s)", data)    
    return admin()

@app.route("/member/<int:id>", methods=['POST'])
def updateMember(id):
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName') 
    teamId = request.form.get('teamId')
    city = request.form.get('city')
    birthdate = request.form.get('dob')
    data = (firstName, lastName, teamId, city, birthdate, id)   
    connection = getCursor()    
    connection.execute("update members set FirstName=%s, LastName=%s, \
                        TeamID=%s, City =%s, Birthdate=%s \
                        where MemberId=%s", data)        
    return admin()

@app.route("/event", methods=['GET'])
def eventPage():    
    queryParameters = request.args
    eventId = queryParameters.get("id")
    event = None
    if eventId is not None:
        event = getEvent(eventId)
    teams = listteams()
    return render_template("event.html", eventId = eventId, event = event, teams = teams, isAdmin = True)

@app.route("/event", methods=['POST'])
def addEvent():    
    eventName = request.form.get('eventName')
    sport = request.form.get('sport') 
    nzTeam = request.form.get('nzTeam')
    data = (eventName, sport, nzTeam)  
    connection = getCursor()    
    connection.execute("insert into events(EventName, Sport, NZTeam) VALUES(%s, %s, %s)", data)    
    return admin()

@app.route("/event/<int:id>", methods=['POST'])
def updateEvent(id):
    eventName = request.form.get('eventName')
    sport = request.form.get('sport') 
    nzTeam = request.form.get('nzTeam')
    data = (eventName, sport, nzTeam, id)
    connection = getCursor()    
    connection.execute("update events set EventName=%s, Sport=%s, NZTeam=%s WHERE EventID=%s", data)        
    return admin()

@app.route("/stages", methods=['GET'])
def liststages():    
    queryParameters = request.args
    eventId = queryParameters.get("eventId")
    event = getEvent(eventId)
    stages = getStages(eventId)       
    return render_template("eventstages.html", event = event,stages = stages, isAdmin = True)

@app.route("/stage", methods=['GET'])
def stagePage():    
    queryParameters = request.args
    eventId = queryParameters.get("eventId") 
    stageId = queryParameters.get("id") 
    stage = None
    if stageId is not None:
        stage = getStage(stageId)
    return render_template("eventstage.html", eventId = eventId, stage=stage, isAdmin = True)    

@app.route("/stage", methods=['POST'])
def addStage():    
    stageName = request.form.get('stageName')
    eventId = request.form.get('eventId') 
    location = request.form.get('location')
    stageDate = request.form.get('stageDate')
    qualifying = request.form.get('qualifying')
    if qualifying is None:
        qualifying = 0    
    pointsToQualify = request.form.get('pointsToQualify')
    if qualifying == 0:
        pointsToQualify = None
    data = (stageName, eventId, location, stageDate,qualifying, pointsToQualify)  
    connection = getCursor()    
    connection.execute("insert into event_stage(StageName, EventID, Location, StageDate, Qualifying, PointsToQualify) \
                        VALUES(%s, %s, %s,%s, %s, %s)", data)    
    return admin()

@app.route("/stage/<int:id>", methods=['POST'])
def updateStage(id):
    stageName = request.form.get('stageName')
    eventId = request.form.get('eventId') 
    location = request.form.get('location')
    stageDate = request.form.get('stageDate')
    qualifying = request.form.get('qualifying')
    if qualifying is None:
        qualifying = 0  
    pointsToQualify = request.form.get('pointsToQualify')
    if qualifying == 0:
        pointsToQualify = None
    data = (stageName, eventId, location, stageDate,qualifying, pointsToQualify, id)
    connection = getCursor()    
    connection.execute("update event_stage set StageName=%s, EventID=%s, Location=%s, \
                        StageDate=%s, Qualifying=%s, PointsToQualify=%s \
                        WHERE StageId=%s", data)        
    return admin()

@app.route("/listresults", methods=['GET'])
def listresults():    
    queryParameters = request.args    
    stageId = queryParameters.get("id") 
    stage = None
    if stageId is not None:
        stage = getStage(stageId)
    results = resultList(stageId)
    return render_template("stageresults.html", stage=stage, results=results, isAdmin = True)

@app.route("/result", methods=['GET'])
def getresult():    
    queryParameters = request.args    
    resultId = queryParameters.get("id") 
    stageId = queryParameters.get("stageId") 
    result = None
    if resultId is not None:    
        result = getResult(resultId)   
    stage = getStage(stageId) 
    members = listMembersByStageId(stageId)    
    return render_template("stageresult.html", result=result, stageId=stageId,stage=stage, members=members, isAdmin = True)

@app.route("/result", methods=['POST'])
def addResult():            
    stageId = request.form.get('stageId')
    memberId = request.form.get('memberId')
    points = request.form.get('points') 
    position = request.form.get('position')    
   
    data = (stageId, memberId, points, position)  
    connection = getCursor()    
    connection.execute("insert into event_stage_results(StageID, MemberID, PointsScored, Position) \
                        VALUES(%s, %s, %s,%s)", data)    
    return admin()

@app.route("/result/<int:id>", methods=['POST'])
def updateResult(id):                        
    memberId = request.form.get('memberId')
    points = request.form.get('points') 
    position = request.form.get('position')    
   
    data = (memberId, points, position, id)
    connection = getCursor()    
    connection.execute("update event_stage_results set MemberID=%s, PointsScored=%s, Position=%s \
                       WHERE ResultID=%s", data) 
    return admin()

@app.route("/report/medal")
def medalReport():
    connection = getCursor()   
    connection.execute("select * from event_stage es \
                       left join event_stage_results r on es.StageID = r.StageID \
                       left join events e on es.EventID = e.EventID \
                       left join members m on r.MemberID = m.MemberID \
                       where es.StageName = 'Final' and r.Position > 0")
    reports = connection.fetchall()
    return render_template("medalreport.html", reports = reports, isAdmin=True)


@app.route("/report/athlete")
def athleteReport():
    connection = getCursor()   
    connection.execute("select * from members m \
                        left join teams t on m.TeamID = t.TeamID \
                        order by t.TeamName, m.LastName, m.FirstName")
    reports = connection.fetchall()    
    athleteReports = {}
    # build a new dictionary with key (eventName) and value (a list of members)
    for report in reports:         
        teamMember = {"FirstName": report['FirstName'], "LastName": report['LastName']}  
        # if a key does not exist, create a new               
        if report['TeamName'] not in athleteReports:
            athleteReports[report['TeamName']] = [teamMember]
        else:
            athleteReports[report['TeamName']].append(teamMember)
    print(athleteReports)
    return render_template("athletereport.html", athleteReports = athleteReports, isAdmin=True)

@app.route("/<int:id>/event")
def eventsByMemberId(id):    
    connection = getCursor()   
    connection.execute("select * from event_stage_results r \
                        left join members m on r.MemberID = m.MemberID \
                        left join event_stage es on es.StageID = r.StageID \
                        left join events e on e.EventID = es.EventID \
                        where r.MemberID=%s and es.StageDate >= DATE(NOW())", (id,))  
    upcomingEvents = connection.fetchall()
    connection.execute("select * from event_stage_results r \
                        left join members m on r.MemberID = m.MemberID \
                        left join event_stage es on es.StageID = r.StageID \
                        left join events e on e.EventID = es.EventID \
                        where r.MemberID=%s and es.StageDate < DATE(NOW())", (id,))  
    previousResults = connection.fetchall()
    connection.execute("select * from members where MemberID=%s", (id,))
    member = connection.fetchone()
    return render_template("eventresult.html", upcomingEvents = upcomingEvents,
                           previousResults = previousResults, member = member)


def listteams():
    connection = getCursor()   
    connection.execute("select * from teams")  
    teams = connection.fetchall()
    return teams

def getMember(id):
    connection = getCursor()   
    connection.execute("select * from members where MemberID=%s", (id,))  
    member = connection.fetchone()
    return member

def listMembersByStageId(id):
    connection = getCursor()   
    connection.execute("select m.* from members m \
                       left join events e on e.NZTeam = m.TeamID \
                       left join event_stage es on es.EventID = e.EventID \
                       where es.StageID=%s", (id,))  
    members = connection.fetchall()
    return members

def getEvent(id):
    connection = getCursor()   
    connection.execute("select * from events where EventID=%s", (id,))  
    event = connection.fetchone()
    return event

def getStages(eventId):
    connection = getCursor()   
    connection.execute("select * from event_stage where EventID=%s", (eventId,))  
    stages = connection.fetchall()
    return stages

def getStage(id):
    connection = getCursor()   
    connection.execute("select * from event_stage where StageID=%s", (id,))  
    stage = connection.fetchone()
    return stage

def resultList(id):
    connection = getCursor()   
    connection.execute("select * from event_stage_results r \
                       left join event_stage s on r.StageID = s.StageID \
                       where r.StageID=%s", (id,))  
    results = connection.fetchall()
    return results

def getResult(id):
    connection = getCursor()   
    connection.execute("select * from event_stage_results where ResultID=%s", (id,))  
    result = connection.fetchone()
    return result

if __name__ == '__main__':
    app.run()