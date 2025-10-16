from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import hashlib
import shutil
import os
from fastapi import FastAPI, UploadFile, Form
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles



from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
security = HTTPBasic()

# ✅ Allow frontend (Netlify) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ucc-campus-hostel.netlify.app"],  # your Netlify URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve image files
os.makedirs("backend/images", exist_ok=True)
app.mount("/images", StaticFiles(directory="backend/images"), name="images")


# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Create hostels table if not exists
conn = sqlite3.connect("backend/database.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS hostels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    owner_contact TEXT,
    image1 TEXT,
    image2 TEXT
)
""")
conn.commit()
conn.close()


@app.post("/hostels")
async def add_hostel(
    name: str = Form(...),
    contact: str = Form(...),
    image1: UploadFile = None,
    image2: UploadFile = None
):
    image1_path = f"uploads/{image1.filename}"
    image2_path = f"uploads/{image2.filename}"

    # Save uploaded images
    with open(image1_path, "wb") as buffer:
        shutil.copyfileobj(image1.file, buffer)
    with open(image2_path, "wb") as buffer:
        shutil.copyfileobj(image2.file, buffer)

    # Save data to database
    conn = sqlite3.connect("backend/database.db")
    c = conn.cursor()
    c.execute("INSERT INTO hostels (name, owner_contact, image1, image2) VALUES (?, ?, ?, ?)",
              (name, contact, image1_path, image2_path))
    conn.commit()
    conn.close()

    return {"message": "Hostel added successfully!"}


DB_PATH = "database.db"

# Create tables if not exist
conn = sqlite3.connect(DB_PATH)
conn.execute("""
CREATE TABLE IF NOT EXISTS hostels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image1 TEXT,
    image2 TEXT,
    contact TEXT
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
# Default admin user: admin / 12345
hashed_pw = hashlib.sha256("12345".encode()).hexdigest()
try:
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", hashed_pw))
except sqlite3.IntegrityError:
    pass
conn.commit()
conn.close()


# -------- API MODELS --------
class Hostel(BaseModel):
    name: str
    image1: str
    image2: str
    contact: str


# -------- HOSTEL ENDPOINTS --------
@app.get("/hostels")
def get_hostels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hostels")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "image1": r[2], "image2": r[3], "contact": r[4]}
        for r in rows
    ]


@app.post("/hostels")
async def add_hostel(
    name: str = Form(...),
    contact: str = Form(...),
    image1: UploadFile = None,
    image2: UploadFile = None
):
    img1_path, img2_path = None, None

    if image1:
        img1_path = f"images/{image1.filename}"
        with open(img1_path, "wb") as buffer:
            shutil.copyfileobj(image1.file, buffer)

    if image2:
        img2_path = f"images/{image2.filename}"
        with open(img2_path, "wb") as buffer:
            shutil.copyfileobj(image2.file, buffer)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO hostels (name, image1, image2, contact) VALUES (?, ?, ?, ?)",
                 (name, img1_path, img2_path, contact))
    conn.commit()
    conn.close()

    return {"message": "Hostel added successfully!"}


# -------- LOGIN ENDPOINT --------
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return JSONResponse({"message": "Invalid username"}, status_code=401)

    stored_password = result[0]
    hashed_input = hashlib.sha256(password.encode()).hexdigest()

    if hashed_input == stored_password:
        return {"message": "Login successful"}
    else:
        return JSONResponse({"message": "Incorrect password"}, status_code=401)


@app.get("/hostels")
def get_hostels():
    conn = sqlite3.connect("backend/database.db")
    c = conn.cursor()
    c.execute("SELECT name, image1, image2, owner_contact FROM hostels")
    hostels = c.fetchall()
    conn.close()
    return [{"name": h[0], "image1": h[1], "image2": h[2], "owner_contact": h[3]} for h in hostels]



