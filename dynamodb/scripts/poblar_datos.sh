#!/bin/bash
set -e

LAMBDA_NAME="lab11-dynamo-procesar-telemetria"
REGION="us-east-2"
ARCHIVO_DATOS="../../shared/dataset/eventos.json"
EVIDENCIAS="../../evidencias/dynamodb"

echo "=== Poblando tabla DynamoDB: $(date) ==="


TOTAL_LOTES=$(python3 -c "import json; datos=json.load(open('$ARCHIVO_DATOS')); print(len(datos))")
echo "Total de lotes a enviar: $TOTAL_LOTES"

ESCRITOS=0
ERRORES=0

for i in $(seq 0 $(($TOTAL_LOTES - 1))); do
    # Extraer el lote i del JSON
    PAYLOAD=$(python3 -c "
import json
datos = json.load(open('$ARCHIVO_DATOS'))
lote = datos[$i]
print(json.dumps({'eventos': lote}))
")

    # Invocar la Lambda
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_NAME" \
        --region "$REGION" \
        --payload "$PAYLOAD" \
        --cli-binary-format raw-in-base64-out \
        /tmp/response_$i.json 2>&1)

    BODY=$(cat /tmp/response_$i.json | python3 -c "import sys,json; r=json.load(sys.stdin); b=json.loads(r.get('body','{}')); print(b.get('escritos',0))")
    ESCRITOS=$(($ESCRITOS + $BODY))

    # Progreso cada 50 lotes
    if [ $(( ($i + 1) % 50 )) -eq 0 ]; then
        echo "  Lote $((i+1))/$TOTAL_LOTES — escritos hasta ahora: $ESCRITOS"
    fi
done

echo ""
echo "=== Resultado final ==="
echo "  Eventos escritos: $ESCRITOS"
echo "  Fecha: $(date)"
echo ""


echo "Verificando con Scan count..."
aws dynamodb scan \
    --table-name lab11-telemetria \
    --region "$REGION" \
    --select COUNT \
    --output json | tee "$EVIDENCIAS/scan-count.json"

echo "=== Población completada: $(date) ==="