import os
import json
import time
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
GSI_NAME = "empresa-timestamp-index"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def ultima_posicion(equipo_id):
    """Consulta la última posición de un equipo (Query con Limit=1, orden descendente)."""
    t0 = time.perf_counter()
    resp = table.query(
        KeyConditionExpression=Key("equipoId").eq(equipo_id),
        ScanIndexForward=False,  # más reciente primero
        Limit=1,
    )
    latencia_ms = round((time.perf_counter() - t0) * 1000, 2)
    items = resp.get("Items", [])
    return {
        "equipo": equipo_id,
        "posicion": items[0] if items else None,
        "latencia_ms": latencia_ms,
    }


def ruta(equipo_id, desde_ts, hasta_ts):
    """Consulta la ruta de un equipo en un rango de tiempo."""
    t0 = time.perf_counter()
    resp = table.query(
        KeyConditionExpression=Key("equipoId").eq(equipo_id)
        & Key("timestamp").between(int(desde_ts), int(hasta_ts)),
        ScanIndexForward=True,
    )
    latencia_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "equipo": equipo_id,
        "puntos": len(resp["Items"]),
        "latencia_ms": latencia_ms,
        "datos": resp["Items"][:5],  # solo primeros 5 para no saturar la salida
    }


def flota_empresa(empresa_id, desde_ts):
    """Consulta la flota reciente de una empresa usando el GSI."""
    t0 = time.perf_counter()
    resp = table.query(
        IndexName=GSI_NAME,
        KeyConditionExpression=Key("empresaId").eq(empresa_id)
        & Key("timestamp").gte(int(desde_ts)),
        ScanIndexForward=False,
    )
    latencia_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "empresa": empresa_id,
        "registros": len(resp["Items"]),
        "latencia_ms": latencia_ms,
        "muestra": resp["Items"][:3],
    }


def main(event, context):
    operacion = event.get("operacion", "ultima_posicion")

    if operacion == "ultima_posicion":
        resultado = ultima_posicion(event["equipoId"])
    elif operacion == "ruta":
        resultado = ruta(event["equipoId"], event["desde"], event["hasta"])
    elif operacion == "flota_empresa":
        resultado = flota_empresa(event["empresaId"], event["desde"])
    else:
        return {"statusCode": 400, "body": f"Operación desconocida: {operacion}"}

    return {
        "statusCode": 200,
        "body": json.dumps(resultado, cls=DecimalEncoder),
    }