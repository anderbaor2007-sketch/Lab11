import time
from decimal import Decimal

from common import TTL, cache, flota, tabla


def main(event, context):
    event = event or {}
    cuantos = int(event.get("equipos", 1000))
    ttl = int(event.get("ttl", TTL))
    a_cache = not event.get("solo_tabla", False)
    a_tabla = not event.get("solo_cache", False)
    ts = int(time.time())
    equipos = flota()[:cuantos]
    t0 = time.perf_counter()

    if a_tabla:
        with tabla().batch_writer() as lote:
            for e in equipos:
                lote.put_item(
                    Item={
                        "equipoId": e["equipoId"],
                        "timestamp": ts,
                        "empresaId": e["empresaId"],
                        "lat": Decimal(str(e["lat"])),
                        "lng": Decimal(str(e["lng"])),
                        "rpm": e["rpm"],
                        "temperatura": e["temperatura"],
                    }
                )

    if a_cache:
        r = cache()
        for i in range(0, len(equipos), 200):
            p = r.pipeline()
            for e in equipos[i : i + 200]:
                clave = f"equipo:{e['equipoId']}:pos"
                p.hset(
                    clave,
                    mapping={
                        "empresaId": e["empresaId"],
                        "lat": e["lat"],
                        "lng": e["lng"],
                        "rpm": e["rpm"],
                        "temperatura": e["temperatura"],
                        "timestamp": ts,
                    },
                )
                p.expire(clave, ttl)
                p.geoadd("flota:geo", (e["lng"], e["lat"], e["equipoId"]))
                p.sadd(f"empresa:{e['empresaId']}:equipos", e["equipoId"])
            p.execute()

    return {
        "equipos": len(equipos),
        "escribio_cache": a_cache,
        "escribio_tabla": a_tabla,
        "ttl_s": ttl,
        "ms": round((time.perf_counter() - t0) * 1000, 1),
    }
