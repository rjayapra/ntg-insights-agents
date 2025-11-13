# PowerShell Script to Create AI Foundry Agents
# Usage: .\create_agents.ps1 [-DryRun] [-Force] [-AgentsPath "agents"] [-Verbose]

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Verbose,
    [string]$AgentsPath = "agents"
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🤖 AI Foundry Agent Creation Script" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required but not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
$venvPath = ".\.venv"
if (Test-Path $venvPath) {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "⚠️ No virtual environment found at $venvPath" -ForegroundColor Yellow
    Write-Host "� Creating virtual environment..." -ForegroundColor Blue
    
    try {
        python -m venv $venvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            Write-Host "Please create one manually with: python -m venv .venv" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "❌ Exception creating virtual environment: $_" -ForegroundColor Red
        Write-Host "Please create one manually with: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
}

# Activate virtual environment
if (Test-Path "$venvPath\Scripts\Activate.ps1") {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
    & "$venvPath\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️ Could not find activation script" -ForegroundColor Yellow
}

# Check if required packages are installed
Write-Host "🔍 Checking required packages..." -ForegroundColor Blue

$requiredPackages = @(
    "azure-ai-projects",
    "azure-identity", 
    "azure-core",
    "python-dotenv",
    "pyyaml"
)

$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        $result = pip show $package 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $package" -ForegroundColor Green
        } else {
            $missingPackages += $package
            Write-Host "  ❌ $package (missing)" -ForegroundColor Red
        }
    } catch {
        $missingPackages += $package
        Write-Host "  ❌ $package (missing)" -ForegroundColor Red
    }
}

# Install missing packages
if ($missingPackages.Count -gt 0) {
    Write-Host "📦 Installing missing packages..." -ForegroundColor Blue
    foreach ($package in $missingPackages) {
        Write-Host "  Installing $package..." -ForegroundColor Yellow
        try {
            pip install $package
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ $package installed successfully" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Failed to install $package" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ❌ Exception installing $package`: $_" -ForegroundColor Red
        }
    }
}

# Check environment variables
Write-Host "🔍 Checking environment variables..." -ForegroundColor Blue

$requiredEnvVars = @(
    "PROJECT_ENDPOINT",
    "AZURE_TENANT_ID"
)

$missingEnvVars = @()

foreach ($envVar in $requiredEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($envVar)
    if ($value) {
        Write-Host "  ✅ $envVar" -ForegroundColor Green
    } else {
        $missingEnvVars += $envVar
        Write-Host "  ❌ $envVar (missing)" -ForegroundColor Red
    }
}

# Load from .env file if environment variables are missing
if ($missingEnvVars.Count -gt 0) {
    $envFiles = @(".env", "src\backend\.env")
    
    foreach ($envFile in $envFiles) {
        if (Test-Path $envFile) {
            Write-Host "📄 Loading environment variables from $envFile..." -ForegroundColor Blue
            
            Get-Content $envFile | ForEach-Object {
                if ($_ -match '^([^#][^=]*?)=(.*)$') {
                    $name = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    
                    # Remove quotes if present
                    if ($value -match '^"(.*)"$') {
                        $value = $matches[1]
                    }
                    
                    if ($name -in $requiredEnvVars) {
                        [Environment]::SetEnvironmentVariable($name, $value, "Process")
                        Write-Host "  ✅ Loaded $name" -ForegroundColor Green
                    }
                }
            }
            break
        }
    }
}

# Final check for required environment variables
$stillMissingEnvVars = @()
foreach ($envVar in $requiredEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($envVar)
    if (-not $value) {
        $stillMissingEnvVars += $envVar
    }
}

if ($stillMissingEnvVars.Count -gt 0) {
    Write-Host "❌ Missing required environment variables:" -ForegroundColor Red
    foreach ($envVar in $stillMissingEnvVars) {
        Write-Host "  - $envVar" -ForegroundColor Red
    }
    Write-Host "Please set these variables or update your .env file" -ForegroundColor Yellow
    exit 1
}

# Check if agents directory exists
if (-not (Test-Path $AgentsPath)) {
    Write-Host "❌ Agents directory not found: $AgentsPath" -ForegroundColor Red
    Write-Host "Please ensure the agents directory exists with agents.json" -ForegroundColor Yellow
    exit 1
}

$agentsJsonPath = Join-Path $AgentsPath "agents.json"
if (-not (Test-Path $agentsJsonPath)) {
    Write-Host "❌ agents.json not found: $agentsJsonPath" -ForegroundColor Red
    exit 1
}

# Read and display agent count
try {
    $agentsJson = Get-Content $agentsJsonPath -Raw | ConvertFrom-Json
    $agentCount = $agentsJson.agents.Count
    Write-Host "📊 Found $agentCount agent configurations in agents.json" -ForegroundColor Blue
    
    # Display agent names
    Write-Host "`nAgents to be created:" -ForegroundColor Cyan
    foreach ($agent in $agentsJson.agents) {
        $toolInfo = if ($agent.coding_tools) { " (with code interpreter)" } else { "" }
        Write-Host "  • $($agent.name)$toolInfo" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Could not parse agents.json: $_" -ForegroundColor Yellow
}

# Build Python command arguments
$pythonArgs = @("create_agents.py")

if ($DryRun) {
    $pythonArgs += "--dry-run"
    Write-Host "`n🔍 Running in DRY RUN mode" -ForegroundColor Yellow
}

if ($Force) {
    $pythonArgs += "--force"
    Write-Host "⚠️ Force mode enabled - will overwrite existing agents" -ForegroundColor Yellow
}

if ($Verbose) {
    $pythonArgs += "--verbose"
}

$pythonArgs += "--agents-path", $AgentsPath

# Run the Python script
Write-Host "`n🚀 Executing agent creation script..." -ForegroundColor Blue
Write-Host "Command: python $($pythonArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
    & python @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Agent creation script completed successfully" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Agent creation script failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "`n❌ Exception running agent creation script: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 Script execution completed!" -ForegroundColor Green
Write-Host "Check the output above for detailed results." -ForegroundColor Blue