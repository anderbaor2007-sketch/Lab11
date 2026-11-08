import json
import random
import time

random.seed(42)  

NUM_EQUIPOS = 1000
NUM_EMPRESAS = 20
EVENTOS_POR_EQUIPO = 10  


LAT_BASE = -8.1116
LNG_BASE = -79.0287

def generar():
    eventos = []
    ahora = int(time.time())

    for i in range(1, NUM_EQUIPOS + 1):
        equipo_id = f"EQ-{i:04d}"
        empresa_id = f"EMP-{((i - 1) % NUM_EMPRESAS) + 1:03d}"

        for j in range(EVENTOS_POR_EQUIPO):
            ts = ahora - (EVENTOS_POR_EQUIPO - j) * 10  
            evento = {
                "equipoId": equipo_id,
                "empresaId": empresa_id,
                "lat": round(LAT_BASE + random.uniform(-0.05, 0.05), 6),
                "lng": round(LNG_BASE + random.uniform(-0.05, 0.05), 6),
                "rpm": random.randint(800, 3000),
                "temperatura": round(random.uniform(60, 110), 1),
                "ts": ts,
            }
            eventos.append(evento)

    return eventos

if __name__ == "__main__":
    datos = generar()
    print(f"Generados {len(datos)} eventos para {NUM_EQUIPOS} equipos")

   
    lote_size = 25
    lotes = [datos[i:i+lote_size] for i in range(0, len(datos), lote_size)]

    with open("eventos.json", "w") as f:
        json.dump(lotes, f)

    print(f"Guardados en {len(lotes)} lotes de hasta {lote_size} eventos")
    print(f"Archivo: eventos.json")