from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import upload

app = FastAPI()

# Allow frontend (port 5500) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.get("/")
def home():
    return {"message": "AI Resume Analyzer Backend Running"}