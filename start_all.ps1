# Array of Python scripts to run for HTML-based cricket data processing
$scripts = @(
    "generateCommentry.py",
    "getCommentaryHTML.py",
    "getScoreHTML.py",
    "commentary_data_processor.py",
    "score_data_processor.py",
    "playCommentaryFiles.py"
)

# Get the current directory
$currentDir = Get-Location

# Activate virtual environment command
$venvActivate = ".\crickScore_venv\bin\activate"

Write-Host "Starting all HTML-based cricket data processing scripts..."

foreach ($script in $scripts) {
    if (Test-Path $script) {
        # Create a new PowerShell window for each script
        Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "Set-Location '$currentDir'; & '$venvActivate'; python '$script'"
        )
        Write-Host "Started $script"
        # Small delay to prevent all windows from stacking exactly on top of each other
        Start-Sleep -Milliseconds 500
    } else {
        Write-Host "Warning: $script not found"
    }
}
