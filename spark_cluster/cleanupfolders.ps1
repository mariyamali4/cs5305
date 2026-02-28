# Remove Spark and Ivy related folders
$foldersToDelete = @(
    "spark-home",
    "spark-events",
    "worker-data",
    "workder-logs",
    "warehouse",
    ".ivy2"
)

foreach ($folder in $foldersToDelete) {
    $path = Join-Path -Path $PSScriptRoot -ChildPath $folder
    
    if (Test-Path -Path $path) {
        Remove-Item -Path $path -Recurse -Force
        Write-Host "Deleted: $path"
    } else {
        Write-Host "Not found: $path"
    }
}