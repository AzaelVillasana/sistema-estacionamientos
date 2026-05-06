import pandas as pd
from datetime import datetime, timedelta
import re

eventos = []

def extraer_numero(valor):
    if pd.isna(valor):
        return 0
    numeros = re.findall(r'\d+', str(valor))
    return int(numeros[0]) if numeros else 0

def normalizar_hora(hora_str):
    if pd.isna(hora_str):
        return ""
    hora_str = str(hora_str).strip()

    for formato in ["%I:%M %p", "%H:%M"]:
        try:
            return datetime.strptime(hora_str, formato).strftime("%H:%M")
        except:
            continue
    return ""

def normalizar_fecha(fecha_str):
    try:
        return datetime.strptime(str(fecha_str).strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return ""

def cargar_eventos_google():
    global eventos

    url = "https://docs.google.com/spreadsheets/d/1Pfh5Ei76NE8VY5dT1jSk4a5sUqtrlK1TPSFSsgvoKZs/export?format=csv"

    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    eventos.clear()

    for _, row in df.iterrows():

        if pd.isna(row["Nombre del Evento"]):
            continue

        fecha = normalizar_fecha(row["Fecha del evento"])
        inicio = normalizar_hora(row["Hora del evento"])

        if fecha == "" or inicio == "":
            continue

        inicio_dt = datetime.strptime(inicio, "%H:%M")
        fin = (inicio_dt + timedelta(hours=1)).strftime("%H:%M")

        eventos.append({
            "estacionamiento": str(row["Estacionamiento Opción 2"]).replace("-", "").strip().upper(),
            "fecha": fecha,
            "inicio": inicio,
            "fin": fin,
            "asistentes": extraer_numero(row["Cajones solicitados"])
        })

    print(f"\n✅ {len(eventos)} eventos cargados\n")


def total_dia():
    fecha = normalizar_fecha(input("Fecha (DD/MM/YYYY): "))

    resultado = {}
    total_general = 0

    for e in eventos:
        if e["fecha"] == fecha:
            est = e["estacionamiento"]

            resultado[est] = resultado.get(est, 0) + e["asistentes"]
            total_general += e["asistentes"]

    print("\n📊 TOTAL GENERAL:", total_general)

    for est in sorted(resultado):
        print(f"{est}: {resultado[est]}")


def ocupacion_por_periodo():
    fecha = normalizar_fecha(input("Fecha (DD/MM/YYYY): "))

    resultado = {}
    total_m = total_t = 0

    for e in eventos:
        if e["fecha"] == fecha:
            est = e["estacionamiento"]

            if est not in resultado:
                resultado[est] = {"mañana": 0, "tarde": 0}

            inicio = datetime.strptime(e["inicio"], "%H:%M")

            if inicio.hour < 12:
                resultado[est]["mañana"] += e["asistentes"]
                total_m += e["asistentes"]
            else:
                resultado[est]["tarde"] += e["asistentes"]
                total_t += e["asistentes"]

    print("\n🌅 Mañana:", total_m, "| 🌇 Tarde:", total_t)

    for est in sorted(resultado):
        d = resultado[est]
        print(f"{est} → {d['mañana']} / {d['tarde']}")


def menu():
    while True:
        print("\n1. Cargar")
        print("2. Total día")
        print("3. Mañana/Tarde")
        print("4. Salir")

        op = input("Opción: ")

        if op == "1":
            cargar_eventos_google()
        elif op == "2":
            total_dia()
        elif op == "3":
            ocupacion_por_periodo()
        elif op == "4":
            break


if __name__ == "__main__":
    menu()