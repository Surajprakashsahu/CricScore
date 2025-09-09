# Array of Python scripts to run
$scripts = @(
    "generateCommentry.py",
    "getSSimages.py",
    "getScoreSSimages.py",
    "image_infer_loop.py",
    "score_image_infer_loop.py"
)

# Get the current directory
$currentDir = Get-Location

# Activate virtual environment command
$venvActivate = ".\venv\Scripts\Activate.ps1"

foreach ($script in $scripts) {
    # Create a new PowerShell window for each script
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$currentDir'; & '$venvActivate'; python '$script'"
    )
    # Small delay to prevent all windows from stacking exactly on top of each other
    Start-Sleep -Milliseconds 500
}
