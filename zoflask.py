from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
CORS(app)

app.config['MONGO_DBNAME'] = 'Zomato'
app.config['MONGO_URI'] = 'mongodb+srv://tmxsmoke:aminocentesis@cluster0.zmgremb.mongodb.net/Zomato?retryWrites=true&w=majority'
mongo = PyMongo(app)

@app.route("/")
def welcome():
    return "Welcome to home page"


@app.route("/addDish", methods=["POST"])
def adddish():
    if request.method == 'POST':
        collection = mongo.db['dish']
        data = request.get_json()
        inserted_document = collection.insert_one(data)
        return jsonify("Dish has been added successfully")


@app.route("/menu", methods=["GET"])
def showmenu():
    if request.method == "GET":
        collection = mongo.db['dish']
        data = list(collection.find())
        print(data)
        for item in data:
            item['_id'] = str(item['_id'])
        
        return jsonify(data)

    
@app.route("/delete/<string:Id>", methods=["DELETE"])
def deleteDish(Id):
    collection = mongo.db.dish
    result = collection.delete_one({"_id": ObjectId(Id)})
    
    if result.deleted_count > 0:
        return jsonify("Dish has been removed successfully")
    
    return jsonify("Dish not found")



@app.route("/updateDish/<string:id>", methods=["PATCH"])
def updateDish(id):
    if request.method == "PATCH":
        data = request.get_json()
        collection = mongo.db['dish']
        filter_query = {'_id': ObjectId(id)}
        update_query = {'$set': {'Quantity': data['Quantity'], 'Name': data['Name'],"Price":data["Price"],"Img":data["Img"]}}
        result = collection.update_one(filter_query, update_query)

        if result.matched_count > 0:
            return jsonify("Successfully updated the quantity and name")

        return jsonify("Id not found")


@app.route("/order",methods=["POST"])
def oderDish():
    if request.method == "POST":
        data = request.get_json()
        collection = mongo.db['dish']
        collection2=mongo.db["order"]
        dish = mongo.db["dish"].find_one({"Name": data["food"]})
        if dish:
            dish["Quantity"] -= data["Quantity"]
            data["Price"] = dish["Price"] * data["Quantity"]
            data["status"] = "received"
            collection2.insert_one(data)
            return jsonify("Order Created Successfully")

        return jsonify("food not found")


@app.route("/allorder", methods=["GET"])
def getOrder():
    collection = mongo.db.order
    data = list(collection.find())
    print(data)
    for item in data:
            item['_id'] = str(item['_id'])
        
    return jsonify(data)


@app.route("/showlogin", methods=["GET"])
def getOrder1():
    collection = mongo.db.login
    logins = collection.find()
    return jsonify([login for login in logins])


@app.route("/login", methods=["POST"])
def getlogin():
    logindata = request.get_json()
    collection = mongo.db.login

    login = collection.find_one({"email": logindata["email"], "password": logindata["password"]})
    if login:
        return jsonify("Login Successful", logindata)

    return jsonify("Wrong Credentials", "")


@app.route("/Signup", methods=["POST"])
def getSignup():
    Signup = request.get_json()
    collection = mongo.db.login

    existing_user = collection.find_one({"email": Signup["email"]})
    if existing_user:
        return jsonify("Email already exists")

    collection.insert_one(Signup)
    return jsonify("Successfully Created Account")


@app.route("/updateOrder/<name>", methods=["PATCH"])
def UpdateOrder(name):
    collection = mongo.db.order
    order = collection.find_one({"Name": name})

    if order:
        if order["status"] == "received":
            order["status"] = "preparing"
            collection.update_one({"Name": name}, {"$set": {"status": "preparing"}})
            return jsonify("Order Status changed successfully: Preparing")
        elif order["status"] == "preparing":
            order["status"] = "ready for pickup"
            collection.update_one({"Name": name}, {"$set": {"status": "ready for pickup"}})
            return jsonify("Order Status changed successfully: Ready for Pickup")
        elif order["status"] == "ready for pickup":
            order["status"] = "delivered"
            collection.update_one({"Name": name}, {"$set": {"status": "delivered"}})
            return jsonify("Order Status changed successfully: Delivered")
        else:
            return jsonify("Order already delivered")

    return jsonify("Order with this name doesn't exist")







if __name__ == '__main__':
    app.run(port=8080)
