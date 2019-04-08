def user(mongo, userName, passWord):
    for user in mongo.db.users.find({"username": userName, "password": passWord}):
        return user
