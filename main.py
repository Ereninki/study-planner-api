from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from random import choice
import secrets
import uvicorn
import json

app = FastAPI()
db_file_name = "database.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_db():
    try:
        with open(db_file_name, "r") as db:
            return json.load(db)
    except:
        return {"message": "i dunno why but i cant see database file"}
def write_db(data):
    try:
        with open(db_file_name, "w") as db:
            json.dump(data, db, indent=2)
    except:
        return {"message": "i dunno why but i cant write to database file"}
def read_motivaiton():
    try:
        with open("motivations.json","r", encoding="utf-8") as motivaitons:
            return json.load(motivaitons)
    except:
        return {"message": "sorry bro, no motivations here"}

def get_current_user_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="my  api is hungry, give it your token pls")
    db=read_db()

    try:
        token = str(authorization.split(" ")[1])
    except:
        raise HTTPException(status_code=401, detail="sorry, my api didnt like the token format. So, it refuses to eat")
    
    for username, data in db["users"].items():
        if data["token"] == token:
            return username
    
    raise HTTPException(status_code=401, detail="sorry, my api didnt recognize this token. So, it refuses to eat")

def rate_limit(user: str):
    db = read_db()
    now = datetime.now()

    db["users"][user]

    rate_limit = db["users"][user].get("rate_limit", {})

    window_raw = rate_limit.get("window_start")

    if not window_raw:
        rate_limit["window_start"] = now.isoformat()
        rate_limit["count"] = 1
        write_db(db)
        return

    try:
        window_start = datetime.fromisoformat(window_raw)
    except:
        rate_limit["window_start"] = now.isoformat()
        rate_limit["count"] = 1
        write_db(db)
        return

    if (now - window_start).total_seconds() >= 60:
        rate_limit["window_start"] = now.isoformat()
        rate_limit["count"] = 1
    else:
        rate_limit["count"] += 1

    if rate_limit["count"] > 20:
        write_db(db)
        raise HTTPException(
            status_code=429,
            detail="chilllll bro, you exceed the rate limit"
        )

    write_db(db)

@app.get("/api/v1/get-token")
def get_token(username: str):
    db = read_db()

    if username in db["users"]:
        raise HTTPException(status_code=400, detail="sorry bro, but this username has already taken. Be more faster next time.")

    user_token = secrets.token_hex(16)
    db["users"][username] = {
        "token": user_token,
        "streak": 0,
        "last_streak_day": "none",
        "plan": [],
        "rate_limit": {
            "window_start": datetime.now().isoformat(),
            "count": 0
        }
    }
    write_db(db)
    return {"message": "here is your token sir", "token": user_token}

@app.get("/api/v1/new-study-plan")
def study_plan(hours: int, subject: str, difficulty: str = None, break_time: int = None,user: str = Depends(get_current_user_token)):
    rate_limit(user)
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

    db = read_db()
    plan = []
    for a in range(hours):
        plan.append({
            "study hour": 1,
            "study": f"study or practice {subject}",
            "break minutes": break_time
        })
    db["users"][user]["plan"] = plan
    write_db(db)

    db = read_db()
    
    if break_time >= 15:
        difficulty = "Easy"
    elif break_time <= 15 and break_time >= 10:
        difficulty = "Medium"
    elif break_time <= 10 and break_time >= 5:
        difficulty = "Hard"
    elif break_time < 5:
        difficulty = "Hardcore"

    if db["users"][user]["streak"] >= 1:
        return {"user": user,
            "message": f"hey, i see that youre on a streak! keep it on fire baby!!!!!",    
            "difficulty": difficulty,
            "plan": plan}
    
    return {"user": user,
            "difficulty": difficulty,
            "plan": plan}

@app.get("/api/v1/get-study-plan")
def get_study_plan(user: str = Depends(get_current_user_token)):
    rate_limit(user)
    db = read_db()
    if db["users"][user]["plan"] == []:
        return {"message": "you dont have a plan bro.. NOW GO AND GET A STUDY PLAN!!!", "plan": []}
    return {"message": "here is current plan sir", "plan": db["users"][user]["plan"]}

@app.post("/api/v1/reset-study-plan")
def reset_study_plan(user: str = Depends(get_current_user_token)):
    rate_limit(user)
    db = read_db()
    if db["users"][user]["plan"] == []:
        return {"message": "bro, you dont have a study plan already. GO GET A STUDY PLAN"}
    else:
        db["users"][user]["plan"] = []
        return {"message": "your study plan succesfully reseted.. NOW GET A NEW STUDY PLAN YOU COUCH POTATO"}


@app.post("/api/v1/update-streak")
def update_streak(user: str = Depends(get_current_user_token)):
    rate_limit(user)
    db = read_db()
    today = str(date.today())

    if db["users"][user]["last_streak_date"] == "none":
        db["users"][user]["last_streak_date"] = today
        db["users"][user]["streak"] += 1
        write_db(db)
        return{"message": "your streak is succesfully increased!", "streak": db["users"][user]["streak"]}
    
    last_streak_day = date.fromisoformat(db["users"][user]["last_streak_date"])

    if db["users"][user]["last_streak_date"] == today:
        raise HTTPException(status_code=400, detail="hey, my api says you already updated your streak today")
    
    today = date.today()
    if (today - last_streak_day).days >= 2:
        db["users"][user]["last_streak_date"] = today.isoformat()
        db["users"][user]["streak"] = 1
        write_db(db)
        return {"message": "sorry bro, but you miss your streak", "current streak": db["users"][user]["streak"]}

    db["users"][user]["streak"] += 1
    db["users"][user]["last_streak_date"] = today.isoformat()

    write_db(db)

    return{"message": "your streak is succesfully increased!", "streak": db["users"][user]["streak"]}

@app.get("/api/v1/motivation")
def motivation(user: str = Depends(get_current_user_token)):
    rate_limit(user)
    motivations = read_motivaiton()
    motivation_sentence = choice(motivations["motivations"])
    return {"motivation": f"{user}, {motivation_sentence}"}

@app.get("/api/v1/me")
def show_me(user: str = Depends(get_current_user_token)):
    rate_limit(user)
    db = read_db()
    return {f"{user}": db["users"][user]}
    
    

if __name__ == "__main__":
    uvicorn.run(app)