import pandas as pd
from datetime import datetime, timedelta
import re
import tkinter as tk
from tkinter import messagebox

eventos = []

# 🔢 Extraer número
def extraer_numero(valor):
    if pd.isna(valor):
        return 0
    numeros = re.findall(r'\d+', str(valor))
    return int(numeros[0]) if numeros else 0


# 🕒 Normalizar hora
def normalizar_hora(hora_str):
    if pd.isna(hora_str):
        return ""

    hora_str = str(hora_str).strip()
    formatos = ["%I:%M %p", "%H:%M"]

    for formato in formatos:
        try:
            return datetime.strptime(hora_str, formato).strftime("%H:%M")
        except:
            continue

    return ""


# 📥 Cargar datos
def cargar_eventos():
    global eventos

    url = "https://docs.google.com/spreadsheets/d/1Pfh5Ei76NE8VY5dT1jSk4a5sUqtrlK1TPSFSsgvoKZs/export?format=csv"

    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()

        eventos.clear()

        for _, row in df.iterrows():

            if pd.isna(row["Nombre del evento"]):
                continue

            inicio = normalizar_hora(row["Hora Inicio"])
            fin = normalizar_hora(row["Hora Fin"])

            if inicio == "":
                continue

            if fin == "":
                inicio_dt = datetime.strptime(inicio, "%H:%M")
                fin_dt = inicio_dt + timedelta(hours=1)
                fin = fin_dt.strftime("%H:%M")

            evento = {
                "estacionamiento": str(row["Estacionamiento"]).strip().lower(),
                "fecha": str(row["Fecha Inicio"]).strip(),
                "inicio": inicio,
                "fin": fin,
                "asistentes_num": extraer_numero(row["No. de Asistentes"])
            }

            eventos.append(evento)

        resultado.set(f"✅ {len(eventos)} eventos cargados")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# 🔍 Consulta por hora
def consultar_ocupacion():
    est = entrada_est.get().strip().lower()
    fecha = entrada_fecha.get().strip()
    hora_input = entrada_hora.get().strip()

    hora = normalizar_hora(hora_input)

    if hora == "":
        messagebox.showerror("Error", "Hora inválida")
        return

    hora_consulta = datetime.strptime(hora, "%H:%M")

    ocupados = 0

    for e in eventos:
        if e["estacionamiento"] == est and e["fecha"] == fecha:
            inicio = datetime.strptime(e["inicio"], "%H:%M")
            fin = datetime.strptime(e["fin"], "%H:%M")

            if inicio <= hora_consulta < fin:
                ocupados += e["asistentes_num"]

    resultado.set(f"🚗 Ocupados: {ocupados}")


# 📊 Total del día
def total_dia():
    est = entrada_est.get().strip().lower()
    fecha = entrada_fecha.get().strip()

    total = 0

    for e in eventos:
        if e["estacionamiento"] == est and e["fecha"] == fecha:
            total += e["asistentes_num"]

    resultado.set(f"📊 Total del día: {total}")


# 🖥️ INTERFAZ PRO
ventana = tk.Tk()
ventana.title("Sistema de Estacionamientos")
ventana.geometry("420x420")
ventana.configure(bg="#f4f6f7")

# Título
tk.Label(
    ventana,
    text="Sistema de Estacionamientos",
    font=("Arial", 16, "bold"),
    bg="#f4f6f7"
).pack(pady=10)

# Frame principal
frame = tk.Frame(ventana, bg="#f4f6f7")
frame.pack(pady=10)

# Campos
def crear_input(texto):
    tk.Label(frame, text=texto, bg="#f4f6f7", font=("Arial", 10, "bold")).pack(anchor="w")
    entry = tk.Entry(frame, width=30)
    entry.pack(pady=5)
    return entry

entrada_est = crear_input("Estacionamiento")
entrada_fecha = crear_input("Fecha (DD/MM/YYYY)")
entrada_hora = crear_input("Hora (HH:MM o AM/PM)")

# Botones
def boton(texto, comando, color):
    return tk.Button(
        ventana,
        text=texto,
        command=comando,
        width=25,
        bg=color,
        fg="white",
        font=("Arial", 10, "bold")
    )

boton("Cargar Datos", cargar_eventos, "#2e86c1").pack(pady=5)
boton("Consultar Ocupación", consultar_ocupacion, "#28b463").pack(pady=5)
boton("Total del Día", total_dia, "#f39c12").pack(pady=5)

# Resultado
resultado = tk.StringVar()
tk.Label(
    ventana,
    textvariable=resultado,
    font=("Arial", 14, "bold"),
    bg="#f4f6f7",
    fg="#2c3e50"
).pack(pady=20)

ventana.mainloop()