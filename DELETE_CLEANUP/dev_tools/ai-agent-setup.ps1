# AI Agent Automation Script for CIAF
# PowerShell script to automate common AI agent workflows

param(
    [Parameter(Position=0)]
    [string]$Action = "help",
    
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [string]$Environment = "development"
)

# Color output functions
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Header { param($Message) Write-Host "`n🔷 $Message" -ForegroundColor Blue }

# Configuration
$PYTHON_EXE = "D:/python312/python.exe"
$WORKSPACE_ROOT = $PSScriptRoot
$CIAF_MODULE = "ciaf"

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    # Check Python
    if (!(Test-Path $PYTHON_EXE)) {
        Write-Error "Python not found at $PYTHON_EXE"
        return $false
    }
    Write-Success "Python found: $PYTHON_EXE"
    
    # Check CIAF module
    $ciafExists = Test-Path (Join-Path $WORKSPACE_ROOT $CIAF_MODULE)
    if (!$ciafExists) {
        Write-Error "CIAF module not found in workspace"
        return $false
    }
    Write-Success "CIAF module found"
    
    return $true
}

function Install-Dependencies {
    Write-Header "Installing Dependencies"
    
    try {
        # Install main dependencies
        & $PYTHON_EXE -m pip install -e .
        if ($LASTEXITCODE -ne 0) { throw "Failed to install main dependencies" }
        Write-Success "Main dependencies installed"
        
        # Install development dependencies
        & $PYTHON_EXE -m pip install -r requirements-dev.txt
        if ($LASTEXITCODE -ne 0) { throw "Failed to install dev dependencies" }
        Write-Success "Development dependencies installed"
        
        # Install pre-commit hooks
        & $PYTHON_EXE -m pip install pre-commit
        pre-commit install
        Write-Success "Pre-commit hooks installed"
        
    } catch {
        Write-Error "Dependency installation failed: $_"
        return $false
    }
    
    return $true
}

function Run-QualityChecks {
    Write-Header "Running Quality Checks"
    
    try {
        # Type checking with MyPy
        Write-Info "Running MyPy type checking..."
        & $PYTHON_EXE -m mypy $CIAF_MODULE --ignore-missing-imports
        if ($LASTEXITCODE -eq 0) { Write-Success "MyPy checks passed" }
        else { Write-Warning "MyPy found issues" }
        
        # Security scanning with Bandit
        Write-Info "Running Bandit security scan..."
        & $PYTHON_EXE -m bandit -r $CIAF_MODULE -f json -o security-report.json
        if ($LASTEXITCODE -eq 0) { Write-Success "Security scan passed" }
        else { Write-Warning "Security scan found issues" }
        
        # Code formatting check
        Write-Info "Checking code formatting..."
        & $PYTHON_EXE -m black $CIAF_MODULE --check
        if ($LASTEXITCODE -eq 0) { Write-Success "Code formatting is correct" }
        else { 
            Write-Warning "Code formatting issues found"
            if ($Force) {
                Write-Info "Auto-fixing formatting..."
                & $PYTHON_EXE -m black $CIAF_MODULE
                & $PYTHON_EXE -m isort $CIAF_MODULE
                Write-Success "Code formatted"
            }
        }
        
        return $true
    } catch {
        Write-Error "Quality checks failed: $_"
        return $false
    }
}

function Run-Tests {
    param([string]$TestType = "all")
    
    Write-Header "Running Tests ($TestType)"
    
    try {
        switch ($TestType) {
            "unit" {
                & $PYTHON_EXE -m pytest tests/ -m "unit" -v --tb=short
            }
            "integration" {
                & $PYTHON_EXE -m pytest tests/ -m "integration" -v --tb=short
            }
            "compliance" {
                & $PYTHON_EXE -m pytest tests/ -m "compliance" -v --tb=short
            }
            "security" {
                & $PYTHON_EXE -m pytest tests/ -m "security" -v --tb=short
            }
            "all" {
                & $PYTHON_EXE -m pytest tests/ -v --tb=short --cov=$CIAF_MODULE --cov-report=html --cov-report=term
            }
            default {
                Write-Error "Unknown test type: $TestType"
                return $false
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Tests passed"
            return $true
        } else {
            Write-Error "Tests failed"
            return $false
        }
    } catch {
        Write-Error "Test execution failed: $_"
        return $false
    }
}

function Run-Demos {
    param([string]$DemoType = "all")
    
    Write-Header "Running Demos ($DemoType)"
    
    $demos = @{
        "healthcare" = "examples/golden_paths/healthcare_samd_demo.py"
        "banking" = "examples/golden_paths/banking_sr11_7_demo.py"
        "government" = "examples/golden_paths/government_omb_m24_10_demo.py"
        "citation" = "examples/citation_anchor_demo.py"
    }
    
    try {
        if ($DemoType -eq "all") {
            foreach ($demo in $demos.GetEnumerator()) {
                Write-Info "Running $($demo.Key) demo..."
                & $PYTHON_EXE $demo.Value
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "$($demo.Key) demo completed"
                } else {
                    Write-Warning "$($demo.Key) demo had issues"
                }
            }
        } elseif ($demos.ContainsKey($DemoType)) {
            Write-Info "Running $DemoType demo..."
            & $PYTHON_EXE $demos[$DemoType]
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$DemoType demo completed"
            } else {
                Write-Error "$DemoType demo failed"
                return $false
            }
        } else {
            Write-Error "Unknown demo type: $DemoType. Available: $($demos.Keys -join ', ')"
            return $false
        }
        
        return $true
    } catch {
        Write-Error "Demo execution failed: $_"
        return $false
    }
}

function Validate-Frameworks {
    Write-Header "Validating CIAF Frameworks"
    
    try {
        # Validate frameworks
        Write-Info "Validating compliance frameworks..."
        & $PYTHON_EXE scripts/validate_frameworks.py
        if ($LASTEXITCODE -eq 0) { Write-Success "Framework validation passed" }
        else { Write-Error "Framework validation failed"; return $false }
        
        # Validate regulatory mappings
        Write-Info "Validating regulatory mappings..."
        & $PYTHON_EXE scripts/validate_regulatory_mappings.py
        if ($LASTEXITCODE -eq 0) { Write-Success "Regulatory mapping validation passed" }
        else { Write-Error "Regulatory mapping validation failed"; return $false }
        
        return $true
    } catch {
        Write-Error "Framework validation failed: $_"
        return $false
    }
}

function Generate-InvestorPackage {
    Write-Header "Generating Investor Package"
    
    try {
        # Create investor package directory
        $packageDir = Join-Path $WORKSPACE_ROOT "investor_package"
        if (!(Test-Path $packageDir)) {
            New-Item -ItemType Directory -Path $packageDir | Out-Null
        }
        
        # Run benchmarks
        Write-Info "Running ROI benchmarks..."
        & $PYTHON_EXE benchmarks/audit-time/ciaf_roi_analysis.py
        
        # Copy key files
        Copy-Item "README.md" $packageDir
        Copy-Item "Docs/compliance_cross_walk.csv" $packageDir -ErrorAction SilentlyContinue
        Copy-Item "ciaf_roi_analysis_data.json" $packageDir -ErrorAction SilentlyContinue
        
        # Generate receipts if they don't exist
        if (Test-Path "examples/receipts") {
            Copy-Item "examples/receipts" $packageDir -Recurse -ErrorAction SilentlyContinue
        }
        
        Write-Success "Investor package generated in $packageDir"
        return $true
    } catch {
        Write-Error "Investor package generation failed: $_"
        return $false
    }
}

function Start-DocumentationServer {
    Write-Header "Starting Documentation Server"
    
    try {
        Write-Info "Starting HTTP server on port 8000..."
        Write-Info "Documentation will be available at http://localhost:8000"
        Write-Info "Press Ctrl+C to stop the server"
        
        Set-Location (Join-Path $WORKSPACE_ROOT "Docs")
        & $PYTHON_EXE -m http.server 8000
    } catch {
        Write-Error "Failed to start documentation server: $_"
    } finally {
        Set-Location $WORKSPACE_ROOT
    }
}

function Clean-Workspace {
    Write-Header "Cleaning Workspace"
    
    try {
        # Remove Python cache files
        Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force
        
        # Remove test artifacts
        Remove-Item -Path ".coverage", "htmlcov", ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
        
        # Remove build artifacts
        Remove-Item -Path "build", "dist", "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
        
        # Remove reports
        Remove-Item -Path "security-report.json", "validation_report.json", "framework_validation_report.json" -Force -ErrorAction SilentlyContinue
        
        # Remove LaTeX artifacts
        Get-ChildItem -Path . -Recurse -Include "*.aux", "*.log", "*.out", "*.toc", "*.synctex.gz", "*.fdb_latexmk", "*.fls" | Remove-Item -Force
        
        Write-Success "Workspace cleaned"
    } catch {
        Write-Error "Workspace cleaning failed: $_"
    }
}

function Run-AIAgentWorkflow {
    Write-Header "Running Complete AI Agent Workflow"
    
    $success = $true
    
    # Step 1: Check prerequisites
    if (!(Test-Prerequisites)) { return $false }
    
    # Step 2: Install dependencies (if forced or missing)
    if ($Force -or !(Test-Path "htmlcov")) {
        if (!(Install-Dependencies)) { $success = $false }
    }
    
    # Step 3: Validate frameworks
    if (!(Validate-Frameworks)) { $success = $false }
    
    # Step 4: Run quality checks
    if (!(Run-QualityChecks)) { $success = $false }
    
    # Step 5: Run tests
    if (!(Run-Tests)) { $success = $false }
    
    # Step 6: Run demos
    if (!(Run-Demos)) { $success = $false }
    
    if ($success) {
        Write-Success "AI Agent Workflow completed successfully!"
        Write-Info "Next steps:"
        Write-Info "  • Run 'Generate-InvestorPackage' for due diligence materials"
        Write-Info "  • Run 'Start-DocumentationServer' to browse documentation"
        Write-Info "  • Use VS Code tasks for ongoing development"
    } else {
        Write-Error "AI Agent Workflow completed with errors"
    }
    
    return $success
}

function Show-Help {
    Write-Host @"
🤖 CIAF AI Agent Automation Script

Usage: .\ai-agent-setup.ps1 [Action] [-Force] [-Environment <env>]

Available Actions:
  help                 - Show this help message
  install             - Install all dependencies
  test [type]         - Run tests (unit, integration, compliance, security, all)
  demo [type]         - Run demos (healthcare, banking, government, citation, all)
  quality             - Run code quality checks
  validate            - Validate CIAF frameworks and mappings
  clean               - Clean workspace artifacts
  docs                - Start documentation server
  investor            - Generate investor package
  workflow            - Run complete AI agent workflow
  
Examples:
  .\ai-agent-setup.ps1 install
  .\ai-agent-setup.ps1 test unit
  .\ai-agent-setup.ps1 demo healthcare
  .\ai-agent-setup.ps1 workflow -Force
  .\ai-agent-setup.ps1 quality
  
Options:
  -Force              - Force reinstallation/recreation
  -Environment        - Set environment (development, testing, production)
  
"@ -ForegroundColor White
}

# Main execution logic
switch ($Action.ToLower()) {
    "install" { Install-Dependencies }
    "test" { Run-Tests $args[0] }
    "demo" { Run-Demos $args[0] }
    "quality" { Run-QualityChecks }
    "validate" { Validate-Frameworks }
    "clean" { Clean-Workspace }
    "docs" { Start-DocumentationServer }
    "investor" { Generate-InvestorPackage }
    "workflow" { Run-AIAgentWorkflow }
    "help" { Show-Help }
    default { 
        Write-Error "Unknown action: $Action"
        Show-Help
        exit 1
    }
}