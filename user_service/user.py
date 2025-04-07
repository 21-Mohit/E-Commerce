class User:

    def __init__(self, username,password) -> None:
        self.username = username
        self.password = password
        
    @staticmethod   
    def is_authenticated(self):
        return True
    
    @staticmethod
    def is_active(self):
        return True
    
    @staticmethod
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.username
    
    def check_password(self,password):
        return password == self.password