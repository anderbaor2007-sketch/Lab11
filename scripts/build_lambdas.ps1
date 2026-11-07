# Arma app\elasticache\build con el codigo, flota.json y la libreria redis.
# Terraform empaqueta esa carpeta en el zip de las Lambdas.
$raiz  = Split-Path $PSScriptRoot -Parent
$src   = Join-Path $raiz "app\elasticache\src"
$build = Join-Path $raiz "app\elasticache\build"

if (Test-Path $build) { Remove-Item $build -Recurse -Force }
New-Item -ItemType Directory $build | Out-Null

Copy-Item "$src\*.py" $build
Copy-Item (Join-Path $raiz "shared\dataset\flota.json") $build
python -m pip install redis --target $build --quiet --upgrade

Write-Host "Build listo en $build"
