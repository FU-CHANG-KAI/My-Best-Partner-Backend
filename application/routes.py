from application import app, db, models, api, moment
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for
from application.models import Activity, User, Application
from datetime import datetime
import shortuuid
from flask_restplus import Resource
from urllib.parse import unquote
from functools import wraps
import time
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


@api.route("/login")
class Login(Resource):
    def get(self):
            email               = request.form.get('Email')
            password            = request.form.get('Password')

            user                = User.objects(email=email).first()
            if user and user.get_password(password):
                return jsonify('{}, You are successfully logged in!, cheers'.format(user.username)) 
            else:
                return jsonify("Sorry, something went wrong")

# User registration
# user_id is generated automatically
@api.route('/register')
class Register(Resource):
    def post(self):
            user_id             = User.objects.count()
            user_id += 1

            username            = request.form.get('Username') 
            email               = request.form.get('Email')
            password            = request.form.get('Password')
            
            user = User.objects(email=email).first()
            if user:
                raise ValidationError("Email is already in use. Pick another one.")

            user = User(user_id=user_id, email=email, username=username)    
            user.set_password(password)
            user.save()
            return jsonify('{}, you are Successfully registered'.format(user.username)) 
    

# User establish or edit their individual profile
@api.route('/profile/<idx>') 
class Profile(Resource): 
    def get(self, idx):
        user_id             = idx
        user                = User.objects(user_id=user_id).first()

        username            = user.username
        email               = user.email
        sex                 = user.sex
        hobbies             = user.hobbies
        skills              = user.skills

        profileInfo = {
            'Username'      : username,
            'E-mail'        : email,
            'Sex'           : sex,
            'Hobbies'       : hobbies,
            'skills'        : skills
        }

        return jsonify(profileInfo) 

    # Revise the user's profile
    def put(self,idx):
        user_id             = idx

        username            = request.form.get('Username')
        sex                 = request.form.get('sex')
        hobbies             = request.form.get('hobbies')
        skills              = request.form.get('skills')

        user                =  User.objects(user_id=user_id)
        user.update(username=username, sex=sex, hobbies=hobbies,skills=skills)

        return jsonify("the profile is successfully edited")


#Search activities by leader name or activity name(by startswith)
@api.route('/homepage')
class Homepage(Resource):
    def get(self):
        serachByLeader      = request.form.get("leader")
        serachByActivity    = request.form.get("activity") 
        searchString        = request.form.get("search") 

        if serachByLeader:
            activities      = Activity.objects(leader_name__startswith=searchString)
            #return jsonify(activities)
            return jsonify(activities)
        
        if serachByActivity:
            activities      = Activity.objects(activity_name__startswith=searchString)

            return jsonify(activities)

        return jsonify(Activity.objects.all())

#Leader create a new activity
@api.route('/build/<idx>')
class Build(Resource):
    def post(self, idx): 
        # activity_id is useful when all the activiteis to be shown ==>To be confirm
        use_id = idx
        user = User.objects(use_id=use_id).first()

        leader_id = user.user_id

        activities = Activity.objects.all()
        n = len(activities)
        activity_id = 0
        if n != 0:
            activity_id = activities[n-1].activity_id
            activity_id += 1

        activity_name       = request.form.get("activity")
        start_date_str      = request.form.get("start")
        skills              = request.form.get("skills")
        genre               = request.form.get("genre")
        description         = request.form.get("description")

        start_date_datetime = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')

        #check if there is the same activity name 
        isPresent = Activity.objects(activity_name = activity_name).first()
        if isPresent:
            return jsonify("Please select another name")

        activity = Activity(leader_id=leader_id, 
        activity_id=activity_id, activity_name=activity_name, leader_name=username, 
        open_date=datetime.utcnow(), start_date=start_date_datetime , 
        genre=genre, skills=skills, description=description)
        activity.save()
        return (jsonify("Successfully build a new activity"))

# Detail for one activity
# 1. Utilize user_id & activity_id to decide wether the user 
# is authorized to update and delete the activity 
# 2. applicant apply this activity
@api.route('/detail/<idx>/<idx1>')  # idx = use_id, idx1 = activity_id
class Detail(Resource):
    # GET ACTIVITY
    def get(self, idx, idx1):
        return jsonify(Activity.objects(activity_id=idx1))

    # PUT-update activity
    def put(self, idx, idx1):
        use_id                = idx
        activity_id           = int(idx1)
        activity = Activity.objects(activity_id = activity_id).first()
        if activity.leader_name == use_id:
            activity_id       = idx1
            activity_name     = request.form.get("activity")
            start_date_str    = request.form.get("start")
            skills            = request.form.get("skills")
            genre             = request.form.get("genre")
            description       = request.form.get("description")

            if not start_date_str:
                Activity.objects(activity_id=activity_id).update(activity_name=activity_name, 
                genre=genre, skills=skills, description=description)

                return jsonify(Activity.objects(activity_id=activity_id))

            start_date_datetime = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
            Activity.objects(activity_id=activity_id).update(activity_name=activity_name, start_date=start_date_datetime , 
            genre=genre, skills=skills, description=description)

            return add_cors(jsonify(Activity.objects(activity_id=activity_id)))
        return jsonify("You do not have the authority")

    # DELETE-delete activity
    def delete(self, idx, idx1):
        leader_id             = idx
        activity_id           = idx1
        activity = Activity.objects(activity_id = activity_id).first()
       
        if activity.leader_id == leader_id:
            Activity.objects(activity_id=activity_id).delete()
            return jsonify("The activity is deleted")
        return jsonify("You do not have authority")

    # POST-apply activity
    def post(self, idx, idx1): # Apply a new activity
        applicant_id          = idx     
        activity_id           = idx1
        
        # Search if the applicanttion has already existed in 
        #  MongoDB collection 'Application'
        applications_exist = Application.objects(applicant_id=applicant_id)
        for application_exist in applications_exist:
            if application_exist.activity_id == activity_id:
                return jsonify("You already applied",400)
        
        # Obtain applicant's information from collection 'User'
        user                  = User.objects(use_id=applicant_id).first()
        applicant_name        = user.username

        # Obtain activity information from collection 'Activity'
        activity              = Activity.objects(activity_id=activity_id).first()
        activity_name         = activity.activity_name

        apply_id = Application.objects.count()
        apply_id += 1 
        application = Application(apply_id=apply_id, applicant_id=applicant_id, applicant_name=applicant_name,
        activity_id=activity_id, activity_name=activity_name, status=0)
        application.save()
        return jsonify("Successfully apply", 200)

#  A Dashboard shows the activities the user created and attended
@api.route('/overview/<idx>')
class Overview(Resource):
    # The activities the user created
    def get(self, idx):  # idx = user_id
        user_id = idx
        activities=Activity.objects(leader_id=user_id).all()
        create_activities          = []

        if activities:
            for activity in activities:

                activity_name      = activity.activity_name
                applications       = Application.objects(activity_name=activity_name).all()
                application_list_zero = []
                application_list_one  = []
                for application in applications:
                    if application.status   == 0:
                            application_list_zero.append(application.applicant_id)
                    elif application.status == 1:
                            application_list_one.append(application.applicant_id)
                activity_id        = activity.activity_id
                activity_name      = activity.activity_name
                open_date          = activity.open_date
                genre              = activity.genre

                # '0': the application has not been decided by the leader
                # '1': the application is successful 
                create_activity_dict = {
                    "Project_Name"       : activity_name,
                    "Deadline"           : open_date,
                    "Major"              : genre,
                    "0"                  : application_list_zero,
                    "1"                  : application_list_one
                }   

                create_activities.append(create_activity_dict)
            return jsonify(create_activities, 200)

        return add_cors(jsonify("You do not have any created acticities", 400))

    def post(self, idx):
        # The activities the user attended
        user_id = idx  # idx = user_id
        applications=Application.objects(applicant_id=user_id)
        apply_activities       = []

        if applications:
            for application in applications:
                activity_id         = application.activity_id
                activity_id         = activity_id
                status              = application.status

                activity            = Activity.objects(activity_id=activity_id).first()

                activity_name       = activity.activity_name
                open_date           = activity.open_date
                genre               = activity.genre
                leader_name         = activity.leader_name

                open_date_local     = time.local(open_date)
                format_time         = time.strftime("%Y-%m-%d %H:%M:%S", open_date_local) 

                apply_activity_dict = {
                    "Project_Name"       : activity_name,
                    "Deadline"           : open_date,
                    "Deadline"           : format_time,
                    "Major"              : genre,
                    "Leader"             : leader_name,
                    "Application Status" : status
                }

                apply_activities.append(apply_activity_dict)

            return jsonify(apply_activities, 200)

        return jsonify("You don't have any applied acticities", 400)

    def put(self, idx):
        accept                      = request.form.get("accept")
        reject                      = request.form.get("reject")
        applicant_name              = request.form.get("applicant")
        activity_name               = request.form.get("project")
        activity_name               = activity_name

        if accept:
            application             = Application.objects(activity_name=activity_name).first()
            application.update(status=1)
            
            return jsonify("The applicant successfully attend your activity",200)

        elif reject:
            activity                = Application.objects(activity_name=activity_name).first()
            activity.update(status=-1)
            
            return jsonify("The applicant fails to attend your activity",200)