# Uso: .\scripts\invocar.ps1 <funcion> '<json>' [archivo_salida]
# Ejemplo: .\scripts\invocar.ps1 poblador '{"equipos":1000}'
param(
    [Parameter(Mandatory = $true)][string]$Funcion,
    [string]$Payload = "{}",
    [string]$Salida = ""
)

$tmp = Join-Path $env:TEMP "lab11-payload.json"
[System.IO.File]::WriteAllText($tmp, $Payload)
if (-not $Salida) { $Salida = Join-Path $env:TEMP "lab11-$Funcion.json" }

aws lambda invoke `
    --function-name "lab11-$Funcion" `
    --payload "file://$tmp" `
    --cli-binary-format raw-in-base64-out `
    --profile lab11 --region us-east-2 `
    $Salida | Out-Null

Get-Content $Salida
