from pymongo import *
from flask import *
from flask_restful import *
from wtforms import *
from flask_jwt_extended import *
from bson.objectid import *

## -- DATA BASE -- ##
client = MongoClient(host="localhost", post= 27017)
db = client["sanjesh"]
users = db["users"]
scoreGuide = db["scoreGuide"]
scoreGuide.insert_many(
    {"code": 1, "message":"+1"},
    {"code": 2, "message":"+2"},
)
## -- VALIDATION PART -- ##
class Login_Validation(Form):
    name = StringField("name", validators=[validators.DataRequired(), validators.length(min=4)])
    email = EmailField("email", validators=[validators.DataRequired()])
    password = StringField("password", validators=[validators.DataRequired(), validators.length(min=8, max=32)])
    number = IntegerField("number", validators=[validators.DataRequired(), validators.length(min=11, max=11)])
class Score_Validation(Form):
    number = IntegerField("number", validators=[validators.DataRequired(), validators.length(min=11, max=11)]) 
    code = IntegerField("code", validators=[validators.DataRequired(), validators.length(min=1, max=2)])
## -- LOGIN PART -- ##
class JWT_Reqirements(Resource):
    def post(self):
        userValidator = Login_Validation(request.form)
        if userValidator.validate():
            userData = request.form.to_dict()
            user = users.find_one(userData)
            if  not user is None:
                claim = {"role": user["role"]}
                token = create_access_token(identity=user["number"], additional_claims=claim), 200
                return{"status":"ok", "message":"login successfully", "token":token}
            else:
                return{"status":"error", "message":"user was not found"},404
        else:
            return{"status":"error", "message": userValidator.errors},400

## -- USER PART -- ##
class Users_Functions(Resource):
    
    def post(self, id=None):
        userValidator = Login_Validation(request.form)
        userData = request.form.to_dict()
        if userValidator.validate():
            
            if users.count_documents({}) == 0:
                userData["role"] == "admin"
            else:
                userData["role"] == "user"
                userData["score"] == 0
            
            if users.find_one({"number":userData["number"]}) is None:
                users.insert_one(userData)
                return{"status":"ok", "message":"you account was created successfully"},200
            else:
                return{"status":"error", "messasge":"this number already exists."},403
            
        else:
            return{"status":"error", "message":userValidator.errors()},400
        
    @jwt_required()   
    def put(self, id=None):
        role = get_jwt()["role"]
        number = get_jwt_identity()
        if not id is None:
            if role == "admin":
                data = request.form.to_dict()
                user = users.update_one({"_id":ObjectId(id)}, {"$set":data})
                return{"status":"ok", "message":"user is updated."},200
            else:
                return{"status":"error", "message":"access denied."},403
        else:
            userValidator = Login_Validation(request.form)
            if userValidator.validate():
                userData = request.form.to_dict()
                update = users.update_one({"number":number}, {"$set":userData})
                if update.modified_count > 0 :
                    return{"status":"ok", "message":"User is updated."},200
                else:
                    return{"status":"error", "message":"an error happened try again later."}
            else:
                return{"status":"error", "message":userValidator.errors},403
            
    
    @jwt_required()
    def get(self, id=None):
        role = get_jwt()["role"]
        if role == "admin":
            if not id is None:
                user = users.find_one({"_id":ObjectId(id)}, {"password" : 0 })
                if user == 0:
                    return{"status":"error", "message":"user wasnt found"},404
                user["_id"] == str(user["_id"])
                return{"status":"ok", "user": user},200
            else:
                Users = list(users.find({"password":0}))
                for user in Users:
                    user["_id"] == str(user["_id"])
                return{"status":"ok", "users":Users},200
        else:
            return{"status":"ok", "message":"access denied."}
    
    @jwt_required()
    def delete(self, id=None):
        role = get_jwt()["number"]
        number = get_jwt_identity()
        if not id is None:
            if role == "admin":
                user = users.delete_one({"id":ObjectId(id)})
                return{"status":"ok", "message":"user is deleted."},200
            else:
                return{"status":"error", "message":"access denied"},403
        else:
            user = users.delete_one({"number":number})
            if user.deleted_count > 0:
                return{"status":"ok", "message":"user is deleted."},200
            else:
                return{"status":"error", "message":"an error happened try again."}

## -- SCORE PANEL -- ##
class Submit_Score(Resource):
    @jwt_required()
    def post(self):
        role = get_jwt()["role"]
        if role == "admin":
            inputValidator = Score_Validation(request.form)
            if inputValidator.validate():
                scoreData = request.form
                code = scoreData["code"]
                number = scoreData["number"]
                user = users.find_one({"number":number})
                if code == 1:
                    user["score"] += 1
                    return{"status":"ok", "message":"the student's score has grown."},200
                elif code == 2:
                    user["score"] -= 1
                    return{"status":"ok", "message":"the student's score has fallen."},200
                else:
                    return{"status":"error", "message":"the code you inserted is not defined."}, 404
            else:
                return{"status":"error", "message":inputValidator.errors}
        else:
            return{"status":"error", "message":"access denied"},403
        
## -- MAIN PART -- ##
def main():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] == "QSTPT"
    jwt = JWTManager(app)
    api = Api(app)
    api.add_resource(Users_Functions(), "/user", "/user/<string:id>")
    api.add_resource(JWT_Reqirements(), "/login")
    app.run(debug=True)
if __name__ == "__main__":
    main()