from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta"

# -------------------------
# Rutas de actividades
# -------------------------
@app.route("/actividad/<materia>")
def materia(materia):
    videos_dict = {
        "matematicas": [
            "https://www.youtube.com/embed/oexd_Dfic_Q?si=aBygywLiU8qIPWcf",
            "https://www.youtube.com/embed/42vjqtleG9E?si=-8xrkubl7HlYor4_"
        ],
        "español": [
            "https://www.youtube.com/embed/HjOOGujV-LU?si=sO0HFVX4fhQRS4E2",
            "https://www.youtube.com/embed/bO23pUTXyA4?si=wlLJ-S_WOUAw-Zcf",
            "https://www.youtube.com/embed/TTCVAWc7qXw?si=X9H8nxLgg0Hpj7gV",
            "https://www.youtube.com/embed/PD6uRb4Mm1o?si=ULxr24mjgljdz-kA",
            "https://www.youtube.com/embed/JiXVHYCrrn4?si=-Tl6k00XGUVxkKZZ",
            "https://www.youtube.com/embed/djE0VGtaLTI?si=XYGD_jYgtgtCPiaH",
            "https://www.youtube.com/embed/I4I-yYFX--I?si=b-zo1FJp8kJFv6Kr",
            "https://www.youtube.com/embed/hzYl-zbKqcs?si=Lt6DmxyAnG33iYdB",
            "https://www.youtube.com/embed/e8K_X4v8vAU?si=Kii1XUKYboOMQXfn",
            "https://www.youtube.com/embed/CrX12Y--gFY?si=ADqPaHmx3kfbLrEk",
            "https://www.youtube.com/embed/Gm0VKgmz__E?si=sFQeNNJpuaiFPVAC",
            "https://www.youtube.com/embed/OJZ1ztPLklA?si=wMqGLhLzzKVU-Sfv",
            "https://www.youtube.com/embed/hK6lx6POg7E?si=b5DFS3x3whKx7ugT"
        ],
        "sociales": [
            "https://www.youtube.com/embed/t-DffdVdjEg?si=2MumAiOcNloWmtH9",
            "https://www.youtube.com/embed/-O1OqlqBFRc?si=txWD3XcPa1vACdAO",
            "https://www.youtube.com/embed/1Yn2qcgm7fw?si=yLxUkJyVuxrIe-PW"
        ],
        "ingles": [
            "https://www.youtube.com/embed/K0aKVqSUD6w?si=LWvNLsm9mhg1jigy",
            "https://www.youtube.com/embed/NgxYGqosslM?si=HqcXfJxa3qm8KDOu",
            "https://www.youtube.com/embed/4W2MBnAVMmI?si=990fX7-oYrSDKY_R",
            "https://www.youtube.com/embed/qH0qgFxD6iU?si=pGEhj894MdgxbQj2",
            "https://www.youtube.com/embed/oR7S6eeNLMg?si=0cRmctheXNM4a-C5",
            "https://www.youtube.com/embed/ygWDpMJEePg?si=umbeqbzd5r7xDVDn",
            "https://www.youtube.com/embed/Q2RgGtY8joM?si=2or2bBJ4YM1XQwrs",
            "https://www.youtube.com/embed/vd--4rLgY1Y?si=92dCsvpU9vhmzgZJ",
            "https://www.youtube.com/embed/FLKJkA9Mzh8?si=lDmcXCIMGpdN8R3r",
            "https://www.youtube.com/embed/9WsUQZT9hMQ?si=3VAK5pm9wG9lRDRc"
        ],
        "naturales": [
            "https://www.youtube.com/embed/X1sQg4nxEe8?si=Ikrf8KZEuZ3Ou0Ik"
        ],
        "otros": []
    }

    videos = videos_dict.get(materia.lower())
    if videos is None:
        return "Materia no encontrada", 404

    return render_template("materia.html", videos=videos, materia=materia)

# -------------------------
# Admin
# -------------------------
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# -------------------------
# La base de datos
# -------------------------
def init_db():
    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()

    # Progreso
    c.execute("""
        CREATE TABLE IF NOT EXISTS progreso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            fecha TEXT NOT NULL,
            comentario TEXT
        )
    """)

    # Comentarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            texto TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            respuesta_a INTEGER,
            fecha TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Ejecutar al iniciar
init_db()


# -------------------------
# Comentarios
# -------------------------
@app.route("/comentario", methods=["GET", "POST"])
def comentario():
    conn = sqlite3.connect("aprendikids.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "Anónimo")
        texto = request.form["texto"]
        respuesta_a = request.form.get("respuesta_a")
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO comentarios (nombre, texto, respuesta_a, fecha)
            VALUES (?, ?, ?, ?)
        """, (nombre, texto, respuesta_a if respuesta_a else None, fecha))
        conn.commit()
        conn.close()
        flash("✅ Comentario agregado.", "success")
        return redirect(url_for("comentario"))

    # Comentarios principales
    c.execute("SELECT id, nombre, texto, likes, fecha FROM comentarios WHERE respuesta_a IS NULL ORDER BY id DESC")
    comentarios = c.fetchall()

    # Respuestas organizadas
    respuestas_dict = {}
    c.execute("SELECT id, nombre, texto, likes, fecha, respuesta_a FROM comentarios WHERE respuesta_a IS NOT NULL")
    for r in c.fetchall():
        if r["respuesta_a"] not in respuestas_dict:
            respuestas_dict[r["respuesta_a"]] = []
        respuestas_dict[r["respuesta_a"]].append(r)

    conn.close()
    return render_template("comentario.html", comentarios=comentarios, respuestas_dict=respuestas_dict)

# Ruta para dar me gusta
@app.route("/like/<int:id>", methods=["POST"])
def like(id):
    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()
    c.execute("UPDATE comentarios SET likes = likes + 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("comentario"))

# -------------------------
# Rutas normales
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/acerca")
def acerca():
    return render_template("acerca.html")

# -------------------------
# Contacto
# -------------------------
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        telefono = request.form.get("telefono", "")
        mensaje = request.form["mensaje"]

        destinatario = "tucorreo@gmail.com"
        remitente = "tucorreo@gmail.com"
        password = "tu_contraseña_o_clave_app"

        asunto = f"Nuevo mensaje de contacto - {nombre}"
        cuerpo = f"""
        Nombre: {nombre}
        Email: {email}
        Teléfono: {telefono}
        Mensaje:
        {mensaje}
        """

        try:
            msg = MIMEMultipart()
            msg["From"] = remitente
            msg["To"] = destinatario
            msg["Subject"] = asunto
            msg.attach(MIMEText(cuerpo, "plain"))

            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.sendmail(remitente, destinatario, msg.as_string())
            servidor.quit()

            flash("✅ Tu mensaje ha sido enviado con éxito.", "success")
        except Exception as e:
            flash(f"❌ Error al enviar el mensaje: {e}", "danger")

        return redirect(url_for("contacto"))

    return render_template("contacto.html")

# -------------------------
# Progreso
# -------------------------
@app.route("/progreso", methods=["GET", "POST"])
def progreso():
    if request.method == "POST":
        email = request.form["email"]
        comentario = request.form.get("comentario", "")

        try:
            conn = sqlite3.connect("aprendikids.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO progreso (email, fecha, comentario) 
                VALUES (?, ?, ?)
            """, (email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), comentario))
            conn.commit()
            conn.close()
            flash("✅ Tu progreso ha sido guardado con éxito.", "success")
        except sqlite3.IntegrityError:
            flash("⚠️ Este correo ya está registrado.", "warning")

        return redirect(url_for("progreso"))

    return render_template("progreso.html")

# -------------------------
# Login de Admin
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        if usuario == ADMIN_USER and clave == ADMIN_PASS:
            session["admin"] = True
            flash("✅ Bienvenido al panel de administración.", "success")
            return redirect(url_for("admin"))
        else:
            flash("❌ Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("👋 Has cerrado sesión.", "info")
    return redirect(url_for("login"))

# -------------------------
# Panel Admin (protegido)
# -------------------------
@app.route("/admin")
def admin():
    if "admin" not in session:
        flash("⚠️ Debes iniciar sesión para acceder al panel.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()
    c.execute("SELECT email, fecha FROM progreso")
    usuarios = c.fetchall()
    conn.close()
    return render_template("admin.html", usuarios=usuarios)

@app.route("/admin/delete/<email>", methods=["POST"])
def delete_user(email):
    if "admin" not in session:
        flash("⚠️ Debes iniciar sesión para acceder al panel.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()
    c.execute("DELETE FROM progreso WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    flash(f"🗑️ El usuario {email} ha sido eliminado.", "info")
    return redirect(url_for("admin"))

# -------------------------
# Panel Admin - Comentarios
# -------------------------
@app.route("/admin/comentarios")
def admin_comentarios():
    if "admin" not in session:
        flash("⚠️ Debes iniciar sesión para acceder al panel.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()
    c.execute("SELECT id, nombre, texto, likes, fecha FROM comentarios ORDER BY id DESC")
    comentarios = c.fetchall()
    conn.close()

    return render_template("admin_comentario.html", comentarios=comentarios)

@app.route("/admin/comentarios/delete/<int:id>", methods=["POST"])
def delete_comentario(id):
    if "admin" not in session:
        flash("⚠️ Debes iniciar sesión para acceder al panel.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("aprendikids.db")
    c = conn.cursor()
    c.execute("DELETE FROM comentarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("🗑️ Comentario eliminado con éxito.", "info")
    return redirect(url_for("admin_comentarios"))

# -------------------------
# Helper
# -------------------------
def get_db():
    conn = sqlite3.connect("aprendikids.db")
    conn.row_factory = sqlite3.Row  # <- claves por nombre
    return conn

if __name__ == "__main__":
    app.run(debug=True)
