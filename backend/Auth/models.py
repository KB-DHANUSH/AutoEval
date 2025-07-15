from pydantic import BaseModel

class AuthResModel(BaseModel):
    """
    Model for authentication response containing access and refresh tokens.
    """
    ACCESS_TOKEN : str
    REFRESH_TOKEN : str
    
    model_config = {
        "json_schema_extra":{
            "examples" : [
                {
                    "REFRESH_TOKEN" : "dsgnksdnbngq",
                    "ACCESS_TOKEN" :"angknjbknbebnqebn"
                }
            ]
        }
    }
    
class RegisterReqModel(BaseModel):
    """
    Model for user registration request containing username, email, and password.
    """
    username :str
    email :str
    password:str
    model_config = {
        "json_schema_extra":{
            "examples" : [
                {
                    "username": "John Doe",
                    "email": "johndoe@example.com",
                    "password": "password123"
                }
            ]
        }
    }
    
class LoginReqModel(BaseModel):
    """
    Model for user login request containing email and password.
    """
    email :str
    password:str
    model_config = {
        "json_schema_extra":{
            "examples" : [
                {
                    "email": "johndoe@example.com",
                    "password": "password123"
                }
            ]
        }
    }