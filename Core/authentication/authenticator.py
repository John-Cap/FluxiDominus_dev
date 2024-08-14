
#Handles signing in and passwords, etc

import uuid

class UserBase:
    def __init__(self,user="",orgId="",role="") -> None:
        self.user=user
        self.orgId=orgId #Employee num
        self.role=role #Admin/scientist, etc
        self.sessionId=uuid.uuid4()

class User(UserBase):
    def __init__(self, user="", orgId="") -> None:
        super().__init__(user, orgId, "user")

class Administrator(UserBase):
    def __init__(self, user="", orgId="") -> None:
        super().__init__(user, orgId, "admin")
        
class AuthenticatorBase:
    def __init__(self,user=None) -> None:
        self.signedIn=False
        self.lastSignInAt=None
        self.sessionId=uuid.uuid4()
        self.user=user
        
    def isAdmin(self):
        if (self.user is None):
            return False
        return (self.user.role == "admin")
    
    def assignUser(self,user: User):
        if (self.user is None):
            self.user=user
        else:
            raise SystemExit(f"Error; Attempt to replace user {self.user.user} with {user.user}")
        
class Authenticator(AuthenticatorBase):
    def __init__(self, user=None) -> None:
        super().__init__(user)
        
if __name__ == "__main__":
    userGuy=User(user="WJ_Bonnet")
    imposter=User(user="Mr Imposter")
    adminGuy=Administrator(user="MR_Bones")
    
    auth_1=Authenticator(userGuy)
    auth_2=Authenticator(user=adminGuy)
    
    print(auth_1.isAdmin())
    print(auth_2.isAdmin())

    print(auth_1.sessionId)
    print(auth_2.sessionId)
    
    auth_1.assignUser(imposter)
    