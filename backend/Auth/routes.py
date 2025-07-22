from fastapi import APIRouter,Response,Request,status
from pymongo.errors import ConnectionFailure,OperationFailure,DuplicateKeyError
from jwt import DecodeError
from Auth.models import *
from Auth.utils import *

auth_router = APIRouter()

@auth_router.post('/register',summary="Register and user and return JWT Tokens")
async def register(user:RegisterReqModel,response:Response,request:Request) -> Response:
    try:
        resp = await request.app.database["Users"].insert_one({
            "username": user.username,
            "email": user.email,
            "password": await get_hashed_password(user.password)
        })
        access_token = await create_access_token(str(resp.inserted_id),expires_delta=1)
        refresh_token = await create_refresh_token(str(resp.inserted_id),expires_delta=10)
    except ConnectionFailure as err:
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message" : "Something went wrong with the connection to database"
        }
    except OperationFailure as err:
        print("OperationFailure:", err.code, err.details)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Insert operation failed"}


    except DuplicateKeyError as err:
        response.status_code=status.HTTP_406_NOT_ACCEPTABLE
        return{
            "message" : "It Already Exists"
        }
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message":f"I don't know: {str(e)}"
        }
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@auth_router.post('/login',description='Login a user and return JWT Tokens',summary="Login a user and return JWT Tokens")
async def login(user:LoginReqModel,response:Response,request:Request) -> Response:
    try:
        db = request.app.database
        user_db = await get_user(db, user.email)
        if not user_db or not await verify_password(user.password, user_db["password"]):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Invalid credentials"}
        access_token = await create_access_token(str(user_db["_id"]), expires_delta=1)
        refresh_token = await create_refresh_token(str(user_db["_id"]), expires_delta=10)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    except ConnectionFailure:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "Something went wrong with the connection to database"
        }
    except OperationFailure:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": "Operation failed"
        }
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": f"An unexpected error occurred: {str(e)}"
        }
        
@auth_router.get("/refresh", summary="Refresh access token")
async def refresh_token(request: Request, response: Response):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Missing or malformed Authorization header"}

    token = auth.split(" ", 1)[1]

    if token.count(".") != 2:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Malformed JWT token"}

    try:
        user_id = await verify_refresh_token(token)
        if not user_id:
            raise ValueError("invalid token")
    except DecodeError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid JWT token"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Unexpected error: {str(e)}"}

    access = await create_access_token(user_id)
    refresh = await create_refresh_token(user_id)
    return {"access_token": access, "refresh_token": refresh}
