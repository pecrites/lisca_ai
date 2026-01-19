import sqlite3

def get_db():
    return sqlite3.connect("lisca.db")

def init_db():
    db = get_db()
    c = db.cursor()

    # UTILISATEURS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # DOSSIERS PATIENTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        age INTEGER,
        cancer TEXT,
        situation_sociale TEXT,
        urgence INTEGER,
        statut TEXT,
        cree_par TEXT
    )
    """)

    # DÉPISTAGE
    c.execute("""
    CREATE TABLE IF NOT EXISTS depistage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        type TEXT,
        resultat TEXT,
        medecin TEXT,
        date TEXT
    )
    """)

    # AUDIT
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utilisateur TEXT,
        action TEXT,
        date TEXT
    )
    """)

    db.commit()
    db.close()
