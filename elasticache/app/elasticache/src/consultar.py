import time

from common import flota, leer_cache_aside


def main(event, context):
    event = event or {}
    ids = event.get("equipos")
    if not ids:
        n = int(event.get("n", 200))
        ids = [e["equipoId"] for e in flota()[:n]]
    usar_cache = not event.get("sin_cache", False)
    fallo = bool(event.get("simular_fallo_cache", False))

    aciertos = 0
    errores_cache = 0
    t0 = time.perf_counter()
    for equipo_id in ids:
        _, acierto, error = leer_cache_aside(equipo_id, usar_cache, fallo)
        aciertos += 1 if acierto else 0
        errores_cache += 1 if error else 0
    ms = (time.perf_counter() - t0) * 1000

    return {
        "equipos": len(ids),
        "aciertos_cache": aciertos,
        "lecturas_a_dynamodb": len(ids) - aciertos,
        "errores_cache": errores_cache,
        "modo": "cache-aside" if usar_cache else "solo-dynamodb",
        "ms_total": round(ms, 2),
    }
