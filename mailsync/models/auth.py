from mailsync.models.base import BaseModel
from mailsync.models.sqlite import user_table
from hashlib import sha1

class UserModel(BaseModel):
    
    def __init__(self):
        super(UserModel, self).__init__()
        
        self.collection = user_table

    def get_sha1(self, password):
        return sha1(password).hexdigest()

    def create_user(self, userdata):
        userdata["password"] = self.get_sha1(userdata["password"])

        self.collection.insert(userdata["username"], userdata["password"])

    def check_user(self, userdata):
        userdata["password"] = self.get_sha1(userdata["password"])
        
        return self.collection.find_user(userdata["username"], userdata["password"])

    def update_password(self, userdata, new_password):
        new_password = self.get_sha1(new_password)
        
        self.collection.update_password(userdata["username"], new_password)

    def count_users(self):
        return self.collection.users_count() 

    def username_exists(self, username):
        return self.collection.find_user_by_username(username)

user_model = UserModel()