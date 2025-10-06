import sqlite3
from datetime import datetime

conn = sqlite3.connect("aprendikids.db")
c = conn.cursor()

comentarios = [
    ("Carlos", "Me encantó la página, muy divertida 😍", None, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("María", "Sería genial agregar más juegos educativos 🎮", None, 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("Luis", "¡Gracias por esta herramienta, mis hijos la disfrutan mucho! 👏", None, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
]

c.executemany("""
    INSERT INTO comentarios (nombre, texto, respuesta_a, likes, fecha)
    VALUES (?, ?, ?, ?, ?)
""", comentarios)

conn.commit()
conn.close()

print("✅ Comentarios de prueba insertados.")
