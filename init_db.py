import sqlite3

conn = sqlite3.connect("aprendikids.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    texto TEXT NOT NULL,
    respuesta_a INTEGER,
    likes INTEGER DEFAULT 0,
    fecha TEXT,
    FOREIGN KEY (respuesta_a) REFERENCES comentarios (id)
)
""")

conn.commit()
conn.close()

print("✅ Base de datos inicializada.")
