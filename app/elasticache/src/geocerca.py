import time

from common import cache


def main(event, context):
    event = event or {}
    lat = float(event.get("lat", -8.1116))
    lng = float(event.get("lng", -79.0288))
    km = float(event.get("km", 5))

    t0 = time.perf_counter()
    res = cache().geosearch(
        "flota:geo",
        longitude=lng,
        latitude=lat,
        radius=km,
        unit="km",
        withdist=True,
        sort="ASC",
    )
    ms = (time.perf_counter() - t0) * 1000

    return {
        "centro": [lat, lng],
        "radio_km": km,
        "encontrados": len(res),
        "ms": round(ms, 3),
        "mas_cercanos": [[m, round(float(d), 3)] for m, d in res[:5]],
    }
