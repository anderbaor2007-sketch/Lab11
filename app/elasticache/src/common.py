"""Utilidades compartidas por las Lambdas del Lab 11 (ElastiCache)."""
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
    """Conexion reutilizable al cluster Valkey (TLS activado)."""
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
    """Tabla DynamoDB que actua como fuente de verdad."""
    global _tabla
    if _tabla is None:
        _tabla = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
    return _tabla


def flota():
    """Dataset compartido (shared/dataset/flota.json), empaquetado con la Lambda."""
    global _flota
    if _flota is None:
        ruta = os.path.join(os.path.dirname(__file__), "flota.json")
        with open(ruta, encoding="utf-8") as f:
            _flota = json.load(f)
    return _flota


def leer_tabla(equipo_id):
    """Ultima posicion de un equipo leyendo DynamoDB (Query, Limit=1)."""
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
    """Patron cache-aside. Devuelve (posicion, acierto, error_cache)."""
    clave = f"equipo:{equipo_id}:pos"
    if usar_cache:
        try:
            if fallo_simulado:
                raise redis.ConnectionError("fallo simulado del cache")
            pos = cache().hgetall(clave)
            if pos:
                return pos, True, False
        except redis.RedisError:
            # Si el cache falla, se sigue leyendo de DynamoDB: el sistema no cae.
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
