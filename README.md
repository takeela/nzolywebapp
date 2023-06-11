## Prerequisite
- Install Flask 
- Install mysql-connector-python

## How to run the application
- python app.py
- Open a browser, type http://localhost:5000

## Routes 
- Note: http://localhost:5000 will be replaced by ${host} in the following content. 
### GET ${host}/
- By default, the index url is pointing to member list page

### GET ${host}/listmembers
- This function is to display a list of members. Since it is retrieving data from MySql database, it is using GET method. 

### GET ${host}/member
- This function is to display the details of a member. From the list member page, there is a hyper link for each member, which is passing the member id as a query parameter to this url. 

### POST ${host}/member
- This function is to create a new member. POST method is used to create a new record in database. 

### POST ${host}/member/{memberId}
- This function is to update an existing member. Member Id is passed in the path. 

### GET ${host}/{memberID}/event
- This route is accessible in member list page for each member. It's fetching the upcoming and previous events for a member. 


### GET ${host}/listevents
- This function is to display a list of events. Since it is retrieving data from MySql database, it is using GET method.

### GET ${host}/report/medal
- This function is to deplay medal report. It's using "left join" in Sql query to join multiple tables to fetch required info. In the html template, it uses the if statement based on 'Position' to decide which medal an athelete got. 

### GET ${host}/report/athlete
- This function is to display athlete report. It's using "left join" in Sql query to join multiple tables to fetch required info. In this function, it rebuids the response grouping it by event name. Moreover, the athletes are ordered by 'LastName', then by 'FirstName'.

### GET ${host}/admin
- This function is to show a page to add/update members and events. Since those functions should only be available in this page. A variable called isAdmin is declared. In the template, it's checking isAdmin to decide whether some buttons can be showed. 

### GET ${host}/listresults
- This route is accessible from stage list page. It will show the result for each stage. 

### GET ${host}/result
- This route is to provide a form to add/update a result of a stage. 

### POST ${host}/result
- This route is to add a result of a stage. 

### POST ${host}/result/{resultId}
- This route is to update an existing result.