from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import sqlite3, hashlib, shutil, os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ucc-campus-hostel.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("images", exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")

DB_PATH = "database.db"

# Initialize database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS hostels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT,
    image1 TEXT,
    image2 TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)""")

# Create default admin
hashed_pw = hashlib.sha256("12345".encode()).hexdigest()
try:
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", hashed_pw))
except sqlite3.IntegrityError:
    pass

conn.commit()
conn.close()

@app.post("/hostels")
async def add_hostel(
    name: str = Form(...),
    contact: str = Form(...),
    image1: UploadFile = None,
    image2: UploadFile = None
):
    img1_path = f"images/{image1.filename}" if image1 else None
    img2_path = f"images/{image2.filename}" if image2 else None

    if image1:
        with open(img1_path, "wb") as f:
            shutil.copyfileobj(image1.file, f)
    if image2:
        with open(img2_path, "wb") as f:
            shutil.copyfileobj(image2.file, f)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO hostels (name, contact, image1, image2) VALUES (?, ?, ?, ?)",
                 (name, contact, img1_path, img2_path))
    conn.commit()
    conn.close()
    return {"message": "Hostel added successfully"}

@app.get("/hostels")
def get_hostels():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, contact, image1, image2 FROM hostels")
    rows = c.fetchall()
    conn.close()
    return [{"name": r[0], "contact": r[1], "image1": r[2], "image2": r[3]} for r in rows]

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return JSONResponse({"message": "Invalid username"}, status_code=401)

    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    if hashed_input == row[0]:
        return {"message": "Login successful"}
    else:
        return JSONResponse({"message": "Incorrect password"}, status_code=401)










