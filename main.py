

""" Only me and God know how this code still works """


from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
from random import choice
import secrets
import uvicorn
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

app = FastAPI()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    db = supabase.table("users")
except:
    print("i cant see the database dude")

async def read_motivaiton():
    try:
        with open("motivations.json","r", encoding="utf-8") as motivaitons:
            return json.load(motivaitons)
    except:
        return {"message": "sorry bro, no motivations here"}

async def get_current_user_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="my api is hungry, give it your token pls")
    try:
        token = str(authorization.split(" ")[1])
    except:
        raise HTTPException(status_code=401, detail="sorry, my api didnt like the token format. So, it refuses to eat")
    
    username = db.select("username").eq("token", token).execute()
    if not username.data[0]["username"]:
        raise HTTPException(status_code=401, detail="sorry, my api didnt recognize this token. So, it refuses to eat")
    return username.data[0]["username"]

async def rate_limit(user: str):
    now = datetime.now()

    window_raw = db.select("window_start").eq("username", user).execute()

    user_count = db.select("count").eq("username", user).execute()
    int_user_count = int(user_count.data[0].get('count', 0))

    if not window_raw.data:
        db.update({"window_start": now.isoformat()}).eq("username", user).execute()
        db.update({"count": 1}).eq("username", user).execute()
        return

    try:
        window_start = datetime.fromisoformat(window_raw.data)
    except:
        db.update({"window_start": now.isoformat()}).eq("username", user).execute()
        db.update({"count": 1}).eq("username", user).execute()
        return

    if (now - window_start).total_seconds() >= 60:
        int_count = 1
        window_start = now.isoformat()
    else:
        int_count = int_user_count + 1

    if int_count > 20:
        db.update({"count": int_count, "window_start": window_start}).eq("username", user).execute()
        raise HTTPException(
            status_code=429,
            detail="chilllll bro, you exceed the rate limit"
        )

    db.update({"count": int_count, "window_start": window_start}).eq("username", user).execute()

@app.post("/api/v1/get-token")
async def get_token(username: str):

    usernames = db.select("username").eq("username", username).execute()
    if usernames.data:
        raise HTTPException(status_code=400, detail="sorry bro, but this username has already taken. Be more faster next time.")

    user_token = secrets.token_hex(16)
    new_user_data = {
        "username": username,
        "token": user_token,
        "streak": 0,
        "last_streak_date": "none",
        "plan": [],
        "window_start": datetime.now().isoformat(),
        "count": 0,

    }
    db.insert(new_user_data).execute()
    return {"message": "here is your token sir", "token": user_token}

@app.post("/api/v1/new-study-plan")
async def study_plan(hours: int, subject: str, difficulty: str = None, break_time: int = None,user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    if difficulty == None and break_time == None:
        raise HTTPException(status_code=422, detail="my api wants a difficulty or a break time, you cant leave both of them empty")
    if difficulty and break_time:
        raise HTTPException(status_code=400, detail="my api doesnt want both of difficulty and break time at the same time, leave one empty please")
    
    if difficulty == None:
        difficulty_none = True
    else:
        difficulty_none = False

    if difficulty_none == False:
        if difficulty.lower() == "easy":
            break_time = 15
        elif difficulty.lower() == "medium":
            break_time = 10
        elif difficulty.lower() == "hard":
            break_time = 5
        else:
            raise HTTPException(status_code=400, detail="my api wants a parameter from the document")

    plan = []
    for a in range(hours):
        plan.append({
            "study hour": 1,
            "study": f"study or practice {subject}",
            "break minutes": break_time
        })
    db.update({"plan": plan}).eq("username", user).execute()
    
    if break_time >= 15:
        difficulty = "Easy"
    elif break_time <= 15 and break_time >= 10:
        difficulty = "Medium"
    elif break_time <= 10 and break_time >= 5:
        difficulty = "Hard"
    elif break_time < 5:
        difficulty = "Hardcore"

    streak = db.select("streak").eq("username", user).execute()
    if streak.data[0]["streak"] >= 1:
        return {"user": user,
            "message": f"hey, i see that youre on a streak! keep it on fire baby!!!!!",    
            "difficulty": difficulty,
            "plan": plan}
    
    
    return {"user": user,
            "difficulty": difficulty,
            "plan": plan}

@app.get("/api/v1/get-study-plan")
async def get_study_plan(user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    current_plan = db.select("plan").eq("username", user).execute()
    if current_plan.data[0]["plan"] == []:
        return {"message": "you dont have a plan bro.. NOW GO AND GET A STUDY PLAN!!!", "plan": []}
    return {"message": "here is current plan sir", "plan": current_plan.data[0]["plan"]}

@app.post("/api/v1/reset-study-plan")
async def reset_study_plan(user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    current_plan = db.select("plan").eq("username", user).execute()
    if current_plan.data[0]["plan"] == []:
        return {"message": "bro, you dont have a study plan already. GO GET A STUDY PLAN"}
    else:
        db.update({"plan": []}).eq("username", user).execute()
        return {"message": "your study plan succesfully reseted.. NOW GET A NEW STUDY PLAN YOU COUCH POTATO"}


@app.post("/api/v1/update-streak")
async def update_streak(user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    today = str(date.today())
    last_streak_date_db = db.select("last_streak_date").eq("username", user).execute()
    streak_db = db.select("streak").eq("username", user).execute()

    if last_streak_date_db.data[0]["last_streak_date"] == "none":
        db.update({"last_streak_date": today, "streak": streak_db.data[0]["streak"] + 1}).eq("username", user).execute()
        return{"message": "your streak is succesfully increased!", "streak": streak_db.data[0]["streak"]}
    
    last_streak_day = date.fromisoformat(last_streak_date_db.data[0]["last_streak_date"])

    if last_streak_date_db.data[0]["last_streak_date"] == today:
        raise HTTPException(status_code=400, detail="hey, my api says you already updated your streak today")
    
    today = date.today()
    if (today - last_streak_day).days >= 2:
        db.update({"last_streak_date": today.isoformat(), "streak": 1}).eq("username", user).execute()
        return {"message": "sorry bro, but you miss your streak", "current streak": streak_db.data[0]["streak"]}

    db.update({"streak": streak_db.data[0]["streak"] + 1, "last_streak_date": today.isoformat()}).eq("username", user).execute()
    streak_db = db.select("streak").eq("username", user).execute()

    return{"message": "your streak is succesfully increased!", "streak": streak_db.data[0]["streak"] + 1}

@app.get("/api/v1/motivation")
async def motivation(user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    motivations = await read_motivaiton()
    motivation_sentence = choice(motivations["motivations"])
    return {"motivation": f"{user}, {motivation_sentence}"}

@app.get("/api/v1/me")
async def show_me(user: str = Depends(get_current_user_token)):
    await rate_limit(user)
    users_all_data = db.select("*").eq("username", user).execute()
    return {f"{user}": users_all_data.data[0]}
    
    

if __name__ == "__main__":
    uvicorn.run(app)