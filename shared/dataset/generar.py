import json
import os
import random

SEMILLA = 11
N_EQUIPOS = 1000
N_EMPRESAS = 20
LAT0, LNG0 = -8.1116, -79.0288

rng = random.Random(SEMILLA)
flota = []
for i in range(1, N_EQUIPOS + 1):
    flota.append(
        {
            "equipoId": f"EQ-{i:04d}",
            "empresaId": f"EMP-{(i - 1) % N_EMPRESAS + 1:02d}",
            "lat": round(LAT0 + rng.uniform(-0.15, 0.15), 6),
            "lng": round(LNG0 + rng.uniform(-0.15, 0.15), 6),
            "rpm": rng.randint(1500, 2200),
            "temperatura": rng.randint(75, 95),
        }
    )

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flota.json")
with open(ruta, "w", encoding="utf-8") as f:
    json.dump(flota, f, ensure_ascii=False, indent=1)
print(f"{len(flota)} equipos escritos en {ruta}")
