from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# =====================================================
# APP INIT
# =====================================================
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lisca.db")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# =====================================================
# UTILISATEURS (AUTH SIMPLE – STABLE)
# =====================================================
USERS = {
    "social_aminata": {"role": "assistant_social", "password": "SocialLisca2026"},
    "secretaire_lisca": {"role": "secretaire", "password": "SecLisca2026"},
    "sg_lisca": {"role": "sg", "password": "SgLisca2026"},
    "presidente_lisca": {"role": "presidente", "password": "PrLisca2026"},
    "medecin_lisca": {"role": "medecin", "password": "MedLisca2026"},
}

# =====================================================
# EMAIL CONFIG (YAHOO)
# =====================================================
EMAIL_EXPEDITEUR = "moubarak1994@yahoo.fr"
EMAIL_PASSWORD = "kilfojnaujqgbaex"   # ⚠️ mot de passe d’application
EMAIL_ASSISTANT_SOCIAL = "ibrahim.madougou@yahoo.fr"

def envoyer_email(destinataire, sujet, message):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_EXPEDITEUR
        msg["To"] = destinataire
        msg["Subject"] = sujet
        msg.set_content(message)

        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(EMAIL_EXPEDITEUR, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("Erreur email :", e)

# =====================================================
# DATABASE
# =====================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        age INTEGER,
        type_cancer TEXT,
        situation_sociale TEXT,
        urgent TEXT,
        statut TEXT DEFAULT 'EN_ATTENTE',
        created_by TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS depistages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        type_depistage TEXT,
        resultat TEXT,
        medecin TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS partenariats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        type TEXT,
        contact TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rendez_vous (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT,
        date TEXT,
        acteur TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =====================================================
# LOGIN
# =====================================================
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = USERS.get(username)
    if user and user["password"] == password:
        return RedirectResponse(f"/{user['role']}?user={username}", status_code=302)
    return RedirectResponse("/", status_code=302)

# =====================================================
# ASSISTANT SOCIAL
# =====================================================
@app.get("/assistant_social", response_class=HTMLResponse)
def assistant_social(request: Request, user: str):
    return templates.TemplateResponse("assistant_social.html", {"request": request, "user": user})

@app.post("/assistant_social/ajouter")
def ajouter_dossier(
    user: str = Form(...),
    nom: str = Form(...),
    age: int = Form(...),
    type_cancer: str = Form(...),
    situation_sociale: str = Form(...),
    urgent: str = Form(...)
):
    conn = get_db()
    conn.execute("""
        INSERT INTO dossiers VALUES (NULL,?,?,?,?,?,'EN_ATTENTE',?,?)
    """, (
        nom, age, type_cancer, situation_sociale, urgent,
        user, datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/assistant_social/historique?user={user}", 302)

@app.get("/assistant_social/historique", response_class=HTMLResponse)
def historique_social(request: Request, user: str):
    conn = get_db()
    dossiers = conn.execute(
        "SELECT * FROM dossiers WHERE created_by=? ORDER BY id DESC",
        (user,)
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(
        "assistant_social_historique.html",
        {"request": request, "user": user, "dossiers": dossiers}
    )

# =====================================================
# SECRETAIRE
# =====================================================
@app.get("/secretaire", response_class=HTMLResponse)
def secretaire(request: Request, user: str):
    conn = get_db()
    dossiers = conn.execute(
        "SELECT * FROM dossiers WHERE statut='VALIDE' ORDER BY id DESC"
    ).fetchall()
    rdv = conn.execute(
        "SELECT * FROM rendez_vous ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(
        "secretaire.html",
        {"request": request, "user": user, "dossiers": dossiers, "rdv": rdv}
    )

@app.post("/secretaire/rdv")
def ajouter_rdv(titre: str = Form(...), date: str = Form(...), user: str = Form(...)):
    conn = get_db()
    conn.execute(
        "INSERT INTO rendez_vous VALUES (NULL,?,?,?)",
        (titre, date, user)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/secretaire?user={user}", 302)

# =====================================================
# MEDECIN
# =====================================================
@app.get("/medecin", response_class=HTMLResponse)
def medecin(request: Request, user: str):
    conn = get_db()
    depistages = conn.execute(
        "SELECT * FROM depistages WHERE medecin=? ORDER BY id DESC",
        (user,)
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(
        "medecin.html",
        {"request": request, "user": user, "depistages": depistages}
    )

@app.post("/medecin/ajouter")
def ajouter_depistage(
    patient: str = Form(...),
    type_depistage: str = Form(...),
    resultat: str = Form(...),
    user: str = Form(...)
):
    conn = get_db()
    conn.execute("""
        INSERT INTO depistages VALUES (NULL,?,?,?,?,?)
    """, (
        patient, type_depistage, resultat, user,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/medecin?user={user}", 302)

# =====================================================
# SG
# =====================================================
@app.get("/sg", response_class=HTMLResponse)
def sg(request: Request, user: str):
    conn = get_db()
    data = {
        "dossiers": conn.execute("SELECT * FROM dossiers ORDER BY id DESC").fetchall(),
        "depistages": conn.execute("SELECT * FROM depistages ORDER BY id DESC").fetchall(),
        "partenariats": conn.execute("SELECT * FROM partenariats ORDER BY id DESC").fetchall(),
        "rdv": conn.execute("SELECT * FROM rendez_vous ORDER BY date DESC").fetchall()
    }
    conn.close()
    return templates.TemplateResponse("sg.html", {"request": request, "user": user, **data})

@app.post("/sg/statut")
def changer_statut(dossier_id: int = Form(...), statut: str = Form(...), user: str = Form(...)):
    conn = get_db()

    dossier = conn.execute(
        "SELECT * FROM dossiers WHERE id=?",
        (dossier_id,)
    ).fetchone()

    conn.execute(
        "UPDATE dossiers SET statut=? WHERE id=?",
        (statut, dossier_id)
    )
    conn.commit()
    conn.close()

    if dossier:
        envoyer_email(
            EMAIL_ASSISTANT_SOCIAL,
            "Décision LISCA – Dossier patient",
            f"Le dossier du patient {dossier['nom']} a été {statut}."
        )

    return RedirectResponse(f"/sg?user={user}", 302)

@app.post("/sg/partenariat")
def ajouter_partenariat(
    nom: str = Form(...),
    type: str = Form(...),
    contact: str = Form(...),
    user: str = Form(...)
):
    conn = get_db()
    conn.execute(
        "INSERT INTO partenariats VALUES (NULL,?,?,?,?)",
        (nom, type, contact, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/sg?user={user}", 302)

# =====================================================
# PRESIDENTE
# =====================================================
@app.get("/presidente", response_class=HTMLResponse)
def presidente(request: Request, user: str):
    conn = get_db()
    data = {
        "dossiers": conn.execute("SELECT * FROM dossiers ORDER BY id DESC").fetchall(),
        "depistages": conn.execute("SELECT * FROM depistages ORDER BY id DESC").fetchall(),
        "partenariats": conn.execute("SELECT * FROM partenariats ORDER BY id DESC").fetchall(),
        "rdv": conn.execute("SELECT * FROM rendez_vous ORDER BY date DESC").fetchall()
    }
    conn.close()
    return templates.TemplateResponse("presidente.html", {"request": request, "user": user, **data})

# =====================================================
# API SYNC – TEMPS RÉEL
# =====================================================
@app.get("/api/sync")
def api_sync():
    conn = get_db()
    data = {
        "dossiers": [dict(r) for r in conn.execute("SELECT * FROM dossiers ORDER BY id DESC")],
        "partenariats": [dict(r) for r in conn.execute("SELECT * FROM partenariats ORDER BY id DESC")]
    }
    conn.close()
    return JSONResponse(content=data)

# =====================================================
# PDF GLOBAL
# =====================================================
@app.get("/rapport/pdf")
def rapport_pdf():
    path = os.path.join(BASE_DIR, "rapport_lisca.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    c.drawString(40, 800, "RAPPORT GLOBAL LISCA")
    y = 760

    conn = get_db()
    for d in conn.execute("SELECT nom, statut FROM dossiers"):
        c.drawString(40, y, f"{d['nom']} – {d['statut']}")
        y -= 14
    conn.close()

    c.save()
    return FileResponse(path, filename="rapport_lisca.pdf")
