from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Cookie, FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
from db import add_user, create_all, drop_all, get_user
from schemas import UserMod
from jwt import encode


def create_token():
    payload ={
        "sub": str("212323"),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return encode(payload, "AHGchgsqdfdfvashgasdhadasasfasfsdfs21343245342t45eyg54dr2dfre5r54rfcweg56r", algorithm="HS256")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("dropping all tables")
    await drop_all()
    print("creating all tables")
    await create_all()
    yield
 


app = FastAPI(lifespan=lifespan)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/reg")
async def regist(data: UserMod, response: Response):
    result = await add_user(data)
    if result:
        token = create_token()
        response.set_cookie("access_token", token)
        return{"Status":"Ok"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")



@app.post("/log")
async def login(data: UserMod, response: Response):
    result = await get_user(data)
    if result:
        token = create_token()
        response.set_cookie("access_token", token)
        return{"Status":"Ok"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")


@app.post("/Qr")
async def generate_qr(text: str,response2: Response,  access_token: str | None = Cookie(None)):

    if not access_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Не найден токен авторизации в cookies"}
        )

    qr_api_url = "https://api.qrserver.com/v1/create-qr-code/"
    query_params = {
        "size": "250x250",
        "data": text
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(qr_api_url, params=query_params)
            

            response.raise_for_status()
            
        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Сторонний сервис QR-кодов вернул ошибку"
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Не удалось связаться с сервисом QR-кодов"
            )
    from io import BytesIO
    return StreamingResponse(BytesIO(response.content), media_type="image/png")









