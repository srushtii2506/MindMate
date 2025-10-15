from fastapi import FastAPI, Form, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import secrets
import re

from database import engine, SessionLocal, Base, User, Feedback, Exercise, Diet, Video, StressResult, Admin

# ------------------- Initialize -------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow CORS (frontend → backend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Dependency -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- Token Stores -------------------
user_tokens = {}   # {token: email}
admin_tokens = {}  # {token: admin_id}

# ------------------- Root -------------------
@app.get("/")
def root():
    return {"message": "✅ MindMate backend is running!"}

# ------------------- Tables -------------------
@app.get("/tables")
def show_tables():
    query = text("SELECT name FROM sqlite_master WHERE type='table';")
    with engine.connect() as connection:
        result = connection.execute(query)
        tables = [row[0] for row in result]
    return {"tables": tables}

# ------------------- User Auth -------------------
def require_user(token: str = Header(None)):
    if not token or token not in user_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    return user_tokens[token]

# ------------------- Admin Auth -------------------
def require_admin(token: str = Header(None), db: Session = Depends(get_db)):
    # Allow hardcoded "admin" token for admin dashboard access
    if token == "admin":
        # Create a temporary admin object for the hardcoded token
        class TempAdmin:
            def __init__(self):
                self.id = 1
                self.username = "admin"
                self.is_active = 1
        return TempAdmin()

    if not token or token not in admin_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized admin")
    admin_id = admin_tokens[token]
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == 1).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin account inactive or not found")
    return admin

# ------------------- Stress Detection -------------------
class StressInput(BaseModel):
    user: str
    bp: str
    sleep: float
    resp: float
    heart: float

def parse_blood_pressure(bp_str):
    try:
        systolic, diastolic = map(int, bp_str.split('/'))
        return systolic, diastolic
    except:
        try:
            systolic = int(bp_str)
            return systolic, 0
        except:
            return 120, 80

def get_hypertension_stage(systolic, diastolic):
    if systolic >= 180 or diastolic >= 120:
        return "Hypertensive Crisis", "DANGER"
    elif systolic >= 160 or diastolic >= 100:
        return "Stage 2 Hypertension", "HIGH"
    elif systolic >= 140 or diastolic >= 90:
        return "Stage 1 Hypertension", "MEDIUM"
    elif systolic >= 130 or diastolic >= 80:
        return "Elevated", "LOW"
    else:
        return "Normal", "NORMAL"

def get_medical_advice(systolic, diastolic, sleep, resp, heart):
    bp_stage, bp_risk = get_hypertension_stage(systolic, diastolic)
    advice_parts = []
    warnings = []
    tips = []

    if bp_risk == "DANGER":
        warnings.append("HYPERTENSIVE CRISIS: Seek immediate medical attention!")
        advice_parts.append("Go to emergency room immediately.")
    elif bp_risk == "HIGH":
        warnings.append("Stage 2 Hypertension detected")
        advice_parts.append("Consult doctor within 1 week.")
    elif bp_risk == "MEDIUM":
        warnings.append("Stage 1 Hypertension detected")
        advice_parts.append("Schedule doctor appointment within 1 month.")
    elif bp_risk == "LOW":
        advice_parts.append("BP slightly elevated. Monitor regularly.")
    else:
        advice_parts.append("Blood pressure is normal.")

    # Sleep Advice
    if sleep < 5:
        advice_parts.append(f"CRITICAL: Only {sleep} hours of sleep. Aim for 7-9 hours nightly.")
    elif sleep < 7:
        advice_parts.append(f"Sleep duration is low ({sleep} hours). Try to get 7-9 hours.")
    else:
        advice_parts.append(f"Good sleep duration ({sleep} hours).")

    # Heart Rate Advice
    if heart > 100:
        advice_parts.append(f"Heart rate is elevated ({heart} bpm).")
    elif heart < 60:
        advice_parts.append(f"Heart rate is low ({heart} bpm).")
    else:
        advice_parts.append(f"Heart rate is normal ({heart} bpm).")

    # Respiration Advice
    if resp > 20:
        advice_parts.append(f"Respiration rate is high ({resp} breaths/min).")
    elif resp < 12:
        advice_parts.append(f"Respiration rate is low ({resp} breaths/min).")
    else:
        advice_parts.append(f"Respiration rate is normal ({resp} breaths/min).")

    return {
        "warnings": warnings,
        "analysis": advice_parts,
        "tips": tips,
        "bp_stage": bp_stage,
        "bp_risk": bp_risk
    }

@app.post("/stress")
def stress_detect(input: StressInput, db: Session = Depends(get_db)):
    try:
        user_email = input.user if input.user and input.user != "undefined" else "guest@example.com"
        if not (0 < input.sleep <= 24) or not (0 < input.resp <= 60) or not (0 < input.heart <= 300):
            raise ValueError("Invalid numeric input")
        systolic, diastolic = parse_blood_pressure(input.bp)
        if not (50 <= systolic <= 300) or not (30 <= diastolic <= 200):
            raise ValueError("Invalid blood pressure range")

        medical_data = get_medical_advice(systolic, diastolic, input.sleep, input.resp, input.heart)

        score = 0
        if input.sleep < 5: score += 4
        elif input.sleep < 7: score += 2
        if input.heart > 100: score += 3
        elif input.heart < 60: score += 2
        if input.resp > 20: score += 2
        elif input.resp < 12: score += 2

        if score >= 8:
            stress_level = "HIGH"; stress_advice = "HIGH STRESS: Multiple health concerns detected."
        elif score >= 5:
            stress_level = "MEDIUM"; stress_advice = "MODERATE STRESS: Several vital signs need attention."
        elif score >= 2:
            stress_level = "LOW"; stress_advice = "MILD STRESS: Some vital signs could be improved."
        else:
            stress_level = "OPTIMAL"; stress_advice = "EXCELLENT: All vital signs are healthy."

        full_advice = f"{stress_advice}\n\nBlood Pressure Stage: {medical_data['bp_stage']}\n"
        if medical_data["warnings"]: full_advice += "WARNINGS:\n" + "\n".join(medical_data["warnings"]) + "\n"
        full_advice += "ANALYSIS:\n" + "\n".join(medical_data["analysis"]) + "\n"

        result = StressResult(user=user_email, sleep=input.sleep, bp=f"{systolic}/{diastolic}",
                              resp=input.resp, heart=input.heart, stress_level=stress_level, advice=full_advice)
        db.add(result)
        db.commit()
        db.refresh(result)

        return {"id": result.id, "stress_level": stress_level, "advice": full_advice,
                "timestamp": result.timestamp, "bp_stage": medical_data["bp_stage"],
                "systolic": systolic, "diastolic": diastolic}

    except Exception as e:
        return {"stress_level": "MEDIUM", "advice": f"Error: {str(e)}", "timestamp": None}

@app.get("/stress/history")
def stress_history(user: str, db: Session = Depends(get_db)):
    if user == "undefined" or not user:
        return []
    results = db.query(StressResult).filter(StressResult.user == user).order_by(StressResult.timestamp.desc()).all()
    return [{"id": r.id, "sleep": r.sleep, "bp": r.bp, "resp": r.resp,
             "heart": r.heart, "stress_level": r.stress_level, "advice": r.advice,
             "timestamp": r.timestamp} for r in results]

@app.delete("/stress/history/delete/{id}")
def delete_stress_history(id: int, db: Session = Depends(get_db)):
    record = db.query(StressResult).filter(StressResult.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Stress history record not found")
    db.delete(record)
    db.commit()
    return {"message": "Stress history record deleted successfully"}

# ------------------- Feedback -------------------
@app.post("/feedback")
def add_feedback(name: str = Form(...), country: str = Form(...),
                 message: str = Form(...), rating: int = Form(...),
                 db: Session = Depends(get_db)):
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    fb = Feedback(name=name, country=country, message=message, rating=rating)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"message": "Feedback submitted successfully", "id": fb.id}

@app.get("/feedback")
def get_feedback(db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).order_by(Feedback.id.desc()).all()
    return [{"id": f.id, "name": f.name, "country": f.country, "message": f.message, "rating": f.rating}
            for f in feedbacks]

# ------------------- User Endpoints -------------------
@app.post("/register")
def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if not re.match(r"^[\w\.-]+@gmail\.com$", email):
        raise HTTPException(status_code=400, detail="Email must be @gmail.com")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="User exists")
    db.add(User(email=email, password=password))
    db.commit()
    token = secrets.token_hex(16)
    user_tokens[token] = email
    return {"message": f"User {email} registered", "token": token}

@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = secrets.token_hex(16)
    user_tokens[token] = email
    return {"message": f"User {email} logged in", "token": token}

@app.post("/logout")
def logout(token: str = Header(None)):
    if token in user_tokens: del user_tokens[token]
    return {"message": "User logged out"}

# ------------------- Admin Auth -------------------
@app.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Try to find admin by email or username
    admin = db.query(Admin).filter(
        ((Admin.email == username) | (Admin.username == username)),
        Admin.is_active == 1
    ).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    # Check password manually
    if admin.password != password:
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    token = secrets.token_hex(16)
    admin_tokens[token] = admin.id
    return {"message": f"Admin {admin.email} logged in", "token": token,
            "admin_id": admin.id, "username": admin.email}

@app.post("/admin/logout")
def admin_logout(token: str = Header(None)):
    if token in admin_tokens: del admin_tokens[token]
    return {"message": "Admin logged out"}

# ------------------- Admin CRUD Endpoints -------------------
# Users
@app.get("/admin/users")
def admin_get_users(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email} for u in users]

@app.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

# Feedback
@app.get("/admin/feedbacks")
def admin_get_feedbacks(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    feedbacks = db.query(Feedback).all()
    return [{"id": f.id, "name": f.name, "country": f.country, "message": f.message, "rating": f.rating} for f in feedbacks]

@app.delete("/admin/feedbacks/{fid}")
def admin_delete_feedback(fid: int, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    fb = db.query(Feedback).filter(Feedback.id == fid).first()
    if not fb: raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(fb)
    db.commit()
    return {"message": "Feedback deleted"}

# ------------------- Analytics -------------------
@app.get("/admin/analytics/users")
def admin_user_stats(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    users_count = db.query(User).count()
    feedback_count = db.query(Feedback).count()
    stress_count = db.query(StressResult).count()
    return {"users": users_count, "feedbacks": feedback_count, "stress_entries": stress_count}

# ------------------- Run Server -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
