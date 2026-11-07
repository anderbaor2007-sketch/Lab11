"""Mide la latencia de lectura de la ultima posicion (p50, p95, p99).
modo = "cache" (cache-aside con Valkey) o "tabla" (DynamoDB directo)."""
import random
import time

from common import flota, leer_cache_aside, leer_tabla


def percentil(ordenados, p):
    return ordenados[min(len(ordenados) - 1, int(len(ordenados) * p / 100))]


def main(event, context):
    event = event or {}
    modo = event.get("modo", "cache")
    lecturas = int(event.get("lecturas", 1000))
    calentamiento = int(event.get("calentamiento", 100))
    rng = random.Random(int(event.get("semilla", 7)))
    ids = [rng.choice(flota())["equipoId"] for _ in range(calentamiento + lecturas)]

    def leer(equipo_id):
        if modo == "tabla":
            leer_tabla(equipo_id)
            return False
        _, acierto, _ = leer_cache_aside(equipo_id, True)
        return acierto

    for equipo_id in ids[:calentamiento]:
        leer(equipo_id)

    tiempos = []
    aciertos = 0
    for equipo_id in ids[calentamiento:]:
        t0 = time.perf_counter()
        acierto = leer(equipo_id)
        tiempos.append((time.perf_counter() - t0) * 1000)
        aciertos += 1 if acierto else 0

    tiempos.sort()
    return {
        "modo": modo,
        "lecturas": lecturas,
        "aciertos_cache": aciertos,
        "p50_ms": round(percentil(tiempos, 50), 3),
        "p95_ms": round(percentil(tiempos, 95), 3),
        "p99_ms": round(percentil(tiempos, 99), 3),
        "min_ms": round(tiempos[0], 3),
        "max_ms": round(tiempos[-1], 3),
        "media_ms": round(sum(tiempos) / len(tiempos), 3),
    }
