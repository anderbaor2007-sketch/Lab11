import json
import os

import boto3
import redis
from boto3.dynamodb.conditions import Key

TTL = int(os.environ.get("CACHE_TTL_S", "10"))

_cache = None
_tabla = None
_flota = None


def cache():
    global _cache
    if _cache is None:
        _cache = redis.Redis(
            host=os.environ["CACHE_HOST"],
            port=6379,
            ssl=True,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
        )
    return _cache


def tabla():
    global _tabla
    if _tabla is None:
        _tabla = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
    return _tabla


def flota():
    global _flota
    if _flota is None:
        ruta = os.path.join(os.path.dirname(__file__), "flota.json")
        with open(ruta, encoding="utf-8") as f:
            _flota = json.load(f)
    return _flota


def leer_tabla(equipo_id):
    resp = tabla().query(
        KeyConditionExpression=Key("equipoId").eq(equipo_id),
        ScanIndexForward=False,
        Limit=1,
    )
    items = resp["Items"]
    if not items:
        return None
    return {k: str(v) for k, v in items[0].items()}


def leer_cache_aside(equipo_id, usar_cache=True, fallo_simulado=False):
    clave = f"equipo:{equipo_id}:pos"
    if usar_cache:
        try:
            if fallo_simulado:
                raise redis.ConnectionError("fallo simulado del cache")
            pos = cache().hgetall(clave)
            if pos:
                return pos, True, False
        except redis.RedisError:
            return leer_tabla(equipo_id), False, True

    pos = leer_tabla(equipo_id)
    if usar_cache and pos:
        try:
            p = cache().pipeline()
            p.hset(clave, mapping=pos)
            p.expire(clave, TTL)
            p.execute()
        except redis.RedisError:
            pass
    return pos, False, False
