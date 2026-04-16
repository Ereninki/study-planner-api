# Study Planner API

This is an API that i made for [Raspapi](https://raspapi.hackclub.com/) event, its a **FastAPI** based study planning system with streak tracking, motivation system and a rate limiting

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
- JSON

  ***

## Usage

You can see [documents here](https://study-planner-api-nu.vercel.app/redoc)

The base is **/api/v1/** and the first thing you need to do use getting a token.
You can get a token by [https://study-planner-api-nu.vercel.app/api/v1/get-token?username=<YOUR_USERNAME>]() and it will create a primary memory in **database.json** and give you a token, please save that token.

If you are using Postman, click on **"Authorization"** tab, then set the type **"Bearer Token"** and put the token that you saved and you can start using the API.
