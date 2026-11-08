import os
import json
import time
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
TTL_DAYS = int(os.environ.get("TTL_DAYS", "7"))


def main(event, context):
    """
    Recibe una lista de eventos de telemetría y los escribe en DynamoDB.
    Cada evento: equipoId, empresaId, lat, lng, rpm, temperatura, ts
    """
    eventos = event.get("eventos", [])
    escritos = 0
    errores = 0

    with table.batch_writer() as batch:
        for ev in eventos:
            try:
                ahora = int(time.time())
                item = {
                    "equipoId": ev["equipoId"],
                    "timestamp": int(ev.get("timestamp", ev.get("ts", 0))),
                    "empresaId": ev["empresaId"],
                    "lat": Decimal(str(ev["lat"])),
                    "lng": Decimal(str(ev["lng"])),
                    "rpm": int(ev.get("rpm", 0)),
                    "temperatura": Decimal(str(ev.get("temperatura", 0))),
                    "expiracion": ahora + (TTL_DAYS * 86400),
                }
                batch.put_item(Item=item)
                escritos += 1
            except Exception as e:
                errores += 1
                print(f"Error escribiendo {ev.get('equipoId')}: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "escritos": escritos,
            "errores": errores,
            "total": len(eventos)
        })
    }