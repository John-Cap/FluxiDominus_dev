
#Handles signing in and passwords, etc

import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import binascii
import uuid

from Core.Data.database import MySQLDatabase
from Core.UI.brokers_and_topics import MqttTopics

class UserBase:
    def __init__(self,user="",orgId="",role="") -> None:
        self.user=user
        self.orgId=orgId #Employee num
        self.role=role #Admin/user, etc
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
        self.mqttService=None
        
        #Encryption
        self.key='6d7933326c656e67746873757065727365637265746e6f6f6e656b6e6f777331'
        self.iv='313662797465736c6f6e676976313233'
            
        self.db=MySQLDatabase( #TODO - Hardcoded default
            host="146.64.91.174",
            port=3306,
            user="pharma",
            password="pharma",
            database="pharma"
        )

    def decryptString(self,encData):
        keyBytes = binascii.unhexlify(self.key)  # Na hex
        ivBytes = binascii.unhexlify(self.iv)    # Na hex

        encBytes = base64.b64decode(encData)  # Decode Base64 data

        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)

        decryptedData = unpad(cipher.decrypt(encBytes), AES.block_size)

        return decryptedData.decode('utf-8')

    def signIn(self,orgId,password):
        det=self.loginDetFromDb(orgId)
        passwordCorrect=det[7]
        #decrypted=self.decryptString(passwordCorrect)
        print(passwordCorrect + " " + password)
        if not self.signedIn and passwordCorrect == password:
            self.signedIn=True
            _report=json.dumps({"LoginPageWidget":{"authenticated":True}})
            self.mqttService.client.publish(_report,MqttTopics.getUiTopic("LoginPageWidget"),qos=2)
            print('Signed in report: '+str(_report))
        else:
            print("Wrong password!")
                
    def isAdmin(self):
        if (self.user is None):
            return False
        return (self.user.role == "admin")
    
    def assignUser(self,user: User):
        if (self.user is None):
            self.user=user
        else:
            raise SystemExit(f"Error; Attempt to replace user {self.user.user} with {user.user}")

    def loginDetFromDb(self,orgId):
        if not self.db.connected:
            self.db.connect()
        return self.db.fetchRecordByColumnValue("users","orgId",orgId)

class Authenticator(AuthenticatorBase):
    def __init__(self, user=None) -> None:
        super().__init__(user)
        
if __name__ == "__main__":
    encData = 'DYWV/12CYFuKsHxa//eJ4g==' #Hello world
    
    decrypted_string = Authenticator().decryptString(encData)
    print(f'Decrypted: {decrypted_string}')

    userGuy=User(user="Wessel Bonnet",orgId="309930")
    imposter=User(user="Mr Imposter")
    adminGuy=Administrator(user="MR_Bones")
    
    auth_1=Authenticator(userGuy)
    auth_2=Authenticator(user=adminGuy)
    
    print(auth_1.isAdmin())
    print(auth_2.isAdmin())

    print(auth_1.sessionId)
    print(auth_2.sessionId)
    
    print(auth_1.loginDetFromDb(adminGuy.orgId))