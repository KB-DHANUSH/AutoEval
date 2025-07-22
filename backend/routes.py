from fastapi import APIRouter,Request,Response

router = APIRouter(prefix='/api')

@router.get('/')
async def root():
    return{
        "message":"Welcome to AutoCorrector!"
    }