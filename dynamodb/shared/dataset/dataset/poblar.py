# shared/dataset/poblar.py
import json
import boto3

lambda_client = boto3.client("lambda", region_name="us-east-2")

with open("eventos.json", "r") as f:
    lotes = json.load(f)

total_eventos = sum(len(l) for l in lotes)
print(f"Total eventos: {total_eventos} en {len(lotes)} lotes")

escritos = 0
errores = 0

for i, lote in enumerate(lotes):
    payload = json.dumps({"eventos": lote})
    resp = lambda_client.invoke(
        FunctionName="lab11-dynamo-procesar-telemetria",
        Payload=payload.encode()
    )
    body = json.loads(resp["Payload"].read())
    result = json.loads(body.get("body", "{}"))
    escritos += result.get("escritos", 0)
    errores += result.get("errores", 0)
    if (i + 1) % 100 == 0:
        print(f"  Lotes: {i+1}/{len(lotes)}...")

print(f"Completado: {escritos} escritos, {errores} errores en {len(lotes)} lotes")