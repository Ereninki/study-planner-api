# Study Planner API

![Atl Text](https://camo.githubusercontent.com/97e7bdfc7ec056444bb02b36ef391a76512b4ddfa38e34bb655de710078cce01/68747470733a2f2f6861636b6174696d652e6861636b636c75622e636f6d2f6170692f76312f62616467652f55304153435537504341572f4572656e696e6b692f73747564792d706c616e6e65722d617069)

This is an API that i made for [Raspapi](https://raspapi.hackclub.com/) event, its a **FastAPI** based study planning system with **streak tracking, motivation system with a rate limiting**

## Features

- bearer token based authentication
- auto-generated study plans
- daily streak system
- motivation generator
- rate limiting system
- JSON based database (no sql required)

  ***

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Supabase

  ***

## Usage

The base is **/api/v1/** and the first thing you need to do is getting a token.
You can get a token by "https://study-planner-api-nu.vercel.app/api/v1/get-token?username=<YOUR_USERNAME>" and it will create a primary memory in a**database** and give you a token, please save that token.

This API using authorization so you need to use **Authorization** and select the type **Bearer Token** and paste the token that you saved, then you start to using the API.

---

## Documentation

**URL:** `/api/v1/get-token`
**Method:** `POST`
**Necessary Query Parameter:** `username(string)`
**Usage:** `Giving you a token for you to save your study informations.`
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/get-token?username=ereninki`

---

**URL:** `/api/v1/new-study-plan`  
<br>**Method:** `POST`  
<br>**Necessary Query Parameter:** `hours(int), subject(string)`  
<br>**Not Necessary but you need to use one of them but not both of them:** `difficulty(string (easy, medium or hard only)), break_time(int)`  
<br>**Usage:** `Making you a study plan for the subject you choose and the difficulty query is for deciding the break time, if you have a break time in your mind just use break time and not use difficulty.`  
<br>**Example:** `https://study-planner-api-nu.vercel.app/api/v1/new-study-plan?hours=5&subject="math"&difficulty="easy` or `https://study-planner-api-nu.vercel.app/api/v1/new-study-plan?hours=8&subject="science"&break_time=3`

---

**URL:** `/api/v1/get-study-plan`  
**Method:** `GET`  
**Usage:** `Showing your current plan and not require any query parameters.`  
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/get-study-plan`

---

**URL:** `/api/v1/reset-study-plan`  
**Method:** `POST`  
**Usage:** `Resetting your plan and not reqiure any query parameters either.`  
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/reset-study-plan`

---

**URL:** `/api/v1/update-streak`  
**Method:** `POST`  
**Usage:** `Updating your streak if its the new day and not require any query parameters either.`  
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/update-streak`

---

**URL:** `/api/v1/motivation`  
**Method:** `GET`  
**Usage:** `Giving you motivation words and not require any query parameters either.`  
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/motivation`

---

**URL:** `/api/v1/me`  
**Method:** `GET`  
**Usage:** `Showing you every detail about you and not reqiure any query paramaters`  
**Example:** `https://study-planner-api-nu.vercel.app/api/v1/me`
