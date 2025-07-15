from fastapi import APIRouter,Response,Request,status
from pymongo.errors import ConnectionFailure,OperationFailure,DuplicateKeyError
from Auth.models import *
from Auth.utils import *

auth_router = APIRouter()

@auth_router.post('/auth/register',summary="Register and user and return JWT Tokens")
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

@auth_router.post('/auth/login',description='Login a user and return JWT Tokens',summary="Login a user and return JWT Tokens")
async def login(user:LoginReqModel,response:Response,request:Request) -> Response:
    try:
        db = request.app.database
        user = await get_user(db, user.email)
        if not user or not verify_password(user["password"], user.password):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Invalid credentials"}
        access_token = create_access_token(str(user["_id"]), expires_delta=1)
        refresh_token = create_refresh_token(str(user["_id"]), expires_delta=10)
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
        
auth_router.get('/auth/refresh',description='Refresh the access token using the refresh token',summary="Refresh the access token")
async def refresh_token(request: Request, response: Response):
    try:
        # Get the refresh token from the request
        refresh_token = request.headers.get("Authorization")
        if not refresh_token:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Missing refresh token or token is blocked"}
        # Verify the refresh token
        user_id = await verify_refresh_token(refresh_token)
        if not user_id:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return {"message": "Invalid refresh token"}
        # Create new access token
        access_token = await create_access_token(user_id)
        refresh_token = await create_refresh_token(user_id)
        # Return the new tokens
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "message": f"An unexpected error occurred: {str(e)}"
        }