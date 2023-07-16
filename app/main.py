import os

from fastapi import Cookie, FastAPI, Form, Request, Response, templating, UploadFile, File
from jose import jwt
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

app = FastAPI()
templates = templating.Jinja2Templates("templates")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ваше решение сюда
@app.get("/flowers")
def get_flowers(request: Request):
    return templates.TemplateResponse("flowers/index.html", {"request": request, "flowers": flowers_repository.get_all()})

@app.post("/flowers")
def create_flowers(request: Request, name: str = Form(), count: int = Form(), cost: int = Form()):
    tmp = Flower(name=name, count=count, cost=cost)

    flowers_repository.save(tmp)
    return RedirectResponse("/flowers", status_code=303)


@app.post("/cart/items")
def cart_items(response: Response,request: Request, flower_id: str = Form()):
    existing_cookie = request.cookies.get("flower_ids")
    if existing_cookie:
        # Append new flower ID to the existing cookie value
        cookie_value = existing_cookie + "," + str(flower_id)
    else:
        # Create a new cookie value if no existing cookie is found
        cookie_value = str(flower_id)
    flowers_repository.minus_flower(int(flower_id))
    response = RedirectResponse("/flowers", status_code=303)
    response.set_cookie(key="flower_ids", value=cookie_value)
    return response

@app.get("/cart/items")
def get_cart_items(request: Request):
    cookie_list = request.cookies.get('flower_ids')
    token = request.cookies.get('token')
    flowers = []
    flower_ids = cookie_list.split(",") if cookie_list else []

    for flower in flower_ids:
        get_flower = flowers_repository.get_one(int(flower))
        if get_flower:
            flowers.append(get_flower)
    print(flowers)
    total_cost = sum(flower.cost for flower in flowers) if flowers else 0
    return templates.TemplateResponse("cart/index.html", {"request": request, "flowers": flowers, "total_cost": total_cost, "token": token})


@app.get("/signup")
def signup_form(request: Request):
    return templates.TemplateResponse("users/signup.html", {"request": request})

@app.post("/signup")
async def signup(email: str = Form(), full_name: str = Form(), password: str = Form(), photo: UploadFile = File()):
    photo_directory = "static/photos"

    os.makedirs(photo_directory, exist_ok=True)  # Create the "photos" directory if it doesn't exist

    photo_path = os.path.join(photo_directory, photo.filename)
    with open(photo_path, "wb") as f:
        f.write(await photo.read())
    photo_path = photo_path[7:]
    user = User(email=email, full_name=full_name, password=password, photo=photo_path)
    users_repository.save(user)
    return RedirectResponse("/login", status_code=303)

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})



def encodeJWT(user_id: str) -> str:
    payload = {"user_id": user_id,}
    token = jwt.encode(payload, "lluna", "HS256")
    return token

def decodeJWT(token:str) -> int:
    data = jwt.decode(token, "lluna", "HS256")
    return data["user_id"]

@app.post("/login")
def login(request:Request, response:Response, email: str = Form(), password: str = Form()):
    user = users_repository.get_by_email(email)
    if user:
        if user.password == password:
            response = RedirectResponse("/profile", status_code=303)
            token = encodeJWT(user.id)
            response.set_cookie("token", token)
            return response
    else:
        return RedirectResponse("/signup", status_code=303)
    return Response("Password exist")


@app.get("/profile")
def get_profile(request:Request, token: str = Cookie()):
    user_id = decodeJWT(token)
    user = users_repository.get_by_id(user_id)

    return templates.TemplateResponse("users/profile.html", {"request":request, "user":user})

@app.post("/purchased")
def purchase(request: Request, response: Response, token: str = Cookie()):
    user_id = decodeJWT(token)
    cookie_list = request.cookies.get('flower_ids')
    flower_ids = cookie_list.split(",") if cookie_list else []
    for flower_id in flower_ids:
        purchase_temp = Purchase(user_id, int(flower_id))
        purchases_repository.save(purchase_temp)
    return RedirectResponse("/purchased", status_code=303)

@app.get("/purchased")
def get_all_purchased(request: Request,token: str = Cookie()):
    user_id = decodeJWT(token)
    purchases = purchases_repository.get_all_purchases_by_user_id(user_id)
    flowers = []
    for purchase in purchases:
        flowers.append(flowers_repository.get_one(purchase.flower_id))
    return templates.TemplateResponse("purchases/index.html", {"request":request, "flowers": flowers})





# конец решения
