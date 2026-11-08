# Lab 11 · Amazon ElastiCache vs Amazon DynamoDB (TerraFleet, Grupo 11)

Curso: Infraestructura como Código (UPAO). Todo se despliega con **Terraform** en **us-east-2 (Ohio)**, sin clics en consola.
Este repositorio contiene la parte de **ElastiCache** (Fabrizzio Gutierrez). La parte de DynamoDB la desarrolla Jimmy en su propio stack y su propia cuenta.

## Qué problema resuelve cada servicio

| | Amazon ElastiCache (Valkey 8.0) | Amazon DynamoDB |
|---|---|---|
| Problema | Leer rápido y a gran frecuencia la última posición de la flota, y buscar equipos por cercanía | Guardar la telemetría de forma durable y escalable (fuente de verdad) |
| Modelo | En memoria: Hash con TTL, GEO, Set | Tabla clave-valor (PK equipoId, SK timestamp) |
| Durabilidad | Sin respaldo a propósito (`snapshot_retention_limit = 0`): se pierde si caen los nodos | Durable, replicada en varias zonas |

## Arquitectura de este stack (ElastiCache)

Diagrama: `docs/diagrama-elasticache.png` (fuente editable: `docs/diagrama-elasticache.drawio`).

- VPC `10.11.0.0/16` con 2 subredes privadas (us-east-2a/b), sin NAT y con un endpoint de tipo gateway hacia DynamoDB.
- Clúster `lab11-terrafleet`: Valkey 8.0, 1 primario + 1 réplica en zonas distintas, failover automático, Multi-AZ, cifrado en reposo y en tránsito, `cache.t4g.micro`, política `allkeys-lru`.
- 4 Lambdas dentro de la VPC (consumidores), cada una con su rol IAM de mínimo privilegio:
  - `lab11-poblador`: carga 1000 equipos en DynamoDB y en la caché.
  - `lab11-consultar`: lectura con patrón cache-aside (caché primero, DynamoDB si falla).
  - `lab11-geocerca`: búsqueda por radio con `GEOSEARCH`.
  - `lab11-benchmark`: mide latencias p50/p95/p99 en modo `cache` o `tabla`.
- Tabla fuente `lab11-telemetria-fuente` (DynamoDB, bajo demanda): es la fuente de verdad de este stack. No es el stack de DynamoDB de Jimmy.

Dataset: 1000 equipos (`EQ-0001`..`EQ-1000`) de 20 empresas, coordenadas alrededor de Trujillo, generado con semilla fija (`shared/dataset/generar.py`, `flota.json`).

## Cómo reproducirlo

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_lambdas.ps1
cd infra\elasticache
terraform init
terraform apply
cd ..\..
```

Invocar una Lambda con AWS CLI (perfil `lab11`, región `us-east-2`):

```powershell
Set-Content payload.json '{"equipos":1000,"ttl":900}' -Encoding ascii
aws lambda invoke --function-name lab11-poblador --payload file://payload.json --cli-binary-format raw-in-base64-out --profile lab11 --region us-east-2 salida.json
```

El mismo patrón sirve para `lab11-consultar`, `lab11-geocerca` y `lab11-benchmark` con sus propios payloads (por ejemplo `{"modo":"cache","lecturas":1000}`).

Métricas de CloudWatch antes de destruir:

```powershell
aws cloudwatch get-metric-statistics --namespace AWS/ElastiCache --metric-name CacheHits --dimensions Name=CacheClusterId,Value=lab11-terrafleet-002 --start-time <inicio UTC> --end-time <fin UTC> --period 60 --statistics Sum --profile lab11 --region us-east-2
```

Destruir:

```powershell
cd infra\elasticache
terraform destroy
```

Las credenciales viven solo en el perfil local de AWS CLI (`lab11`). No hay claves en el repositorio.

## Resultados medidos (ElastiCache)

Todas las mediciones se hicieron desde una Lambda dentro de la VPC (512 MB), con lecturas secuenciales de un solo hilo.

### E1 · Latencia de lectura (1000 lecturas, 100 de calentamiento)

| Métrica | ElastiCache | DynamoDB (tabla fuente de este stack) | Ventaja |
|---|---|---|---|
| p50 | 1,257 ms | 4,971 ms | 4,0x |
| p95 | 2,067 ms | 15,685 ms | 7,6x |
| p99 | 5,642 ms | 16,695 ms | 3,0x |
| Media | 1,430 ms | 7,838 ms | 5,5x |

Evidencia: `results/e1-cache.json`, `results/e1-tabla.json`.

### E2 · Aciertos y TTL (TTL = 10 s, 200 lecturas por ronda)

| Ronda | Aciertos de caché | Lecturas a DynamoDB | Tiempo |
|---|---|---|---|
| 1 (caché fría) | 0 | 200 | 2037 ms |
| 2 (inmediata) | 200 | 0 | 233 ms |
| 3 (inmediata) | 200 | 0 | 242 ms |
| 4 (tras esperar 15 s) | 0 | 200 | 1988 ms |

Esto muestra el **mecanismo** (el TTL expira los datos y las lecturas vuelven a DynamoDB). No es una tasa de aciertos de producción: esa depende de cuántas veces se relee un dato antes de que expire. Evidencia: `evidencias/elasticache/e2-*.json`.

### E3 · Failover y pérdida de datos

| Prueba | Resultado |
|---|---|
| Failover forzado (`test-failover`) | El primario pasó de `-001` (us-east-2b) a `-002` (us-east-2a) entre los 14 s y los 20 s (muestreo cada ~6 s). Sin intervención manual |
| Datos tras el failover (200 equipos) | 200 aciertos, 0 lecturas a DynamoDB: sin pérdida en la muestra |
| Reinicio de ambos nodos | Volvieron a `available` a los 460 s (~7,7 min) |
| Datos tras reiniciar ambos | 0 aciertos, 200 lecturas a DynamoDB, 0 errores: la caché quedó vacía y la aplicación siguió respondiendo desde DynamoDB (2772 ms vs 237 ms con caché llena) |

No se midió el comportamiento de la aplicación *durante* los 7,7 minutos del reinicio, solo antes y después. Evidencia: `evidencias/elasticache/e3-*`.

### E5 · Búsqueda geográfica

`GEOSEARCH` a 5 km del centro de Trujillo (-8,1116; -79,0288): **76 equipos**, el más cercano a 475 m.
Tiempo: 87,7 ms en la primera llamada (arranque en frío de la Lambda y handshake TLS) y **2,37 ms** con la función caliente. DynamoDB no ofrece esta consulta de forma nativa. Evidencia: `results/e5-geocerca*.json`.

### E6 · Aprovisionamiento y configuración

| Dato | Valor |
|---|---|
| Creación de la base (VPC, clúster, tabla; 13 recursos) | 9 min 46 s (el clúster tarda ~9 min 33 s) |
| Despliegue de las 4 Lambdas con roles (15 recursos) | 3 min 45 s |
| Reinicio de ambos nodos | 7 min 40 s |
| Tamaño de la configuración de Terraform | 303 líneas en 8 archivos `.tf` |

Evidencia: `evidencias/elasticache/apply.log`, `apply-lambdas.log`, `e3-reinicio.log`.

### Métricas de CloudWatch

Exportadas con `aws cloudwatch get-metric-statistics` a `evidencias/elasticache/cloudwatch/`. Coinciden con lo medido por los scripts (por ejemplo, 600 fallos en el nodo `-002` y 1302 aciertos en el `-001`), con una excepción: CloudWatch no registró los 200 aciertos de la consulta inmediatamente posterior al failover. La evidencia de esa consulta es su propio resultado (`e3-tras-failover.json`).

## Comparación final ElastiCache vs DynamoDB

Las columnas de DynamoDB (Jimmy) se completan con las mediciones de su stack.

| Criterio | ElastiCache | DynamoDB (Jimmy) |
|---|---|---|
| Latencia de lectura p50 / p95 / p99 | 1,257 / 2,067 / 5,642 ms | por medir |
| Tiempo de creación del recurso principal | ~9 min 33 s | por medir |
| Tiempo para escalar | por medir | por medir |
| Disponibilidad ante caída de nodo | Failover en menos de 20 s, sin pérdida en la muestra | por medir |
| Durabilidad | Sin respaldo (pierde datos al reiniciar todos los nodos) | por medir |
| Consulta por radio | Nativa (`GEOSEARCH`, 2,37 ms) | por medir |
| Costo | 2 nodos `cache.t4g.micro` facturados por hora mientras existan | por medir |
| Tamaño de la configuración Terraform | 303 líneas | por medir |

## Estructura del repositorio

```
app/elasticache/src/      código de las Lambdas (Python)
infra/elasticache/        Terraform (red, caché, tabla fuente, IAM, Lambdas)
scripts/                  empaquetado de las Lambdas
shared/dataset/           dataset común (flota.json) y su generador
results/                  resultados de los experimentos
evidencias/elasticache/   logs, JSON de cada prueba, métricas y capturas
docs/                     diagramas
```

## Limitaciones

- Una sola cuenta y región por integrante, con instancias pequeñas (`cache.t4g.micro`); los números sirven para comparar, no para dimensionar producción.
- Lecturas secuenciales de un solo hilo, sin pruebas de carga concurrente.
- El primer experimento de cada función incluye arranque en frío; se reporta aparte cuando aplica.
- La tabla de DynamoDB de este stack es una fuente mínima para la caché. La evaluación de DynamoDB como base principal está en el stack de Jimmy.
