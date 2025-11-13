# ntg-insights-agents
Repo to setup required agents for insights project

## Overview
This repository contains configurations and scripts to create AI agents in Azure AI Foundry for the NTG Insights project.

## Project Structure
```
ntg-insights-agents/
├── agents/                 # Agent configurations
│   ├── agents.json        # Main agent definitions
│   └── *.yaml             # Individual agent instruction files
├── tools/                 # Resources for code interpreter agents
│   ├── *.csv             # CSV data files
│   └── *.json            # JSON data files
├── scripts/
│   ├── create_agents.py   # Python script to create agents
│   ├── create_agents.ps1  # PowerShell wrapper script (Windows)
│   └── create_agents.sh   # Bash wrapper script (Linux/Mac)
└── requirements.txt       # Python dependencies
```

## Setup

### Prerequisites
- Python 3.8+
- Azure AI Foundry project
- Azure subscription with appropriate permissions

### Installation

**Option 1: Automated Setup (Recommended)**

The wrapper scripts will automatically:
- **Create a virtual environment (`.venv`) if it doesn't exist**
- Activate the virtual environment
- Install all required dependencies
- Validate environment variables
- Run the agent creation script

**Windows (PowerShell):**
```powershell
cd scripts
.\create_agents.ps1
```

**Linux/Mac (Bash):**
```bash
cd scripts
chmod +x create_agents.sh  # Make executable (first time only)
./create_agents.sh
```

**Option 2: Manual Setup**

If you prefer to set up manually or need more control:

1. Create and activate virtual environment:
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the root directory with:
```
PROJECT_ENDPOINT=https://your-project.api.azureml.ms
AZURE_TENANT_ID=your-tenant-id
```

## Agent Definitions

Agents are defined in `agents/agents.json`. Each agent has:
- `name`: Agent display name
- `instruction_source`: YAML file containing the agent's instructions
- `deployment_name`: Model to use (e.g., "gpt-4.1")
- `description`: Agent description
- `coding_tools`: Whether to enable code interpreter
- `coding_tool_resource`: (Optional) Files to upload for code interpreter

### Current Agents
1. **Insights_Index_Agent** - Retrieves reference materials
2. **Insights_Lesson_Plan_Agent** - Generates lesson plans
3. **Insights_Orchestrator_Agent** - Synthesizes outputs from other agents
4. **Insights_QSP_CI_Agent_CSV** - Processes QSP data from CSV (with code interpreter)
5. **Insights_QSP_CI_Agent_JSON** - Processes QSP data from JSON (with code interpreter)
6. **Insights_QSP_Fabric_Agent** - Semantic navigation of QSP data
7. **Insights_Reference_Agent** - Validates reference documents

## Usage

### Quick Start with Wrapper Scripts (Recommended)

The easiest way to create agents is using the provided wrapper scripts that handle all setup automatically.

**Windows (PowerShell):**
```powershell
cd scripts

# Basic usage - creates all agents
.\create_agents.ps1

# Dry run - preview without creating
.\create_agents.ps1 -DryRun

# Force overwrite existing agents
.\create_agents.ps1 -Force

# Verbose output
.\create_agents.ps1 -Verbose

# Custom agents path
.\create_agents.ps1 -AgentsPath "..\agents"

# Combined options
.\create_agents.ps1 -DryRun -Verbose
```

**Linux/Mac (Bash):**
```bash
cd scripts

# Make executable (first time only)
chmod +x create_agents.sh

# Basic usage - creates all agents
./create_agents.sh

# Dry run - preview without creating
./create_agents.sh --dry-run

# Force overwrite existing agents
./create_agents.sh --force

# Verbose output
./create_agents.sh --verbose

# Custom agents path
./create_agents.sh --agents-path ../agents

# Combined options
./create_agents.sh --dry-run --verbose
```

### Direct Python Script Usage

You can also run the Python script directly if you've manually set up your environment:

Basic usage:
```bash
python scripts/create_agents.py
```

Dry run (preview without creating):
```bash
python scripts/create_agents.py --dry-run
```

Force overwrite existing agents:
```bash
python scripts/create_agents.py --force
```

Custom agents path:
```bash
python scripts/create_agents.py --agents-path /path/to/agents
```

Verbose output:
```bash
python scripts/create_agents.py --verbose
```

### Command-Line Options

**PowerShell Script (`create_agents.ps1`):**
- `-DryRun`: Preview what will be created without making changes
- `-Force`: Overwrite existing agents with the same name
- `-Verbose`: Enable verbose logging
- `-AgentsPath <path>`: Path to agents directory (default: agents)

**Bash Script (`create_agents.sh`):**
- `--dry-run`: Preview what will be created without making changes
- `--force`: Overwrite existing agents with the same name
- `--verbose`: Enable verbose logging
- `--agents-path <path>`: Path to agents directory (default: agents)
- `-h, --help`: Show help message

**Python Script (`create_agents.py`):**
- `--dry-run`: Preview what will be created without making changes
- `--force`: Overwrite existing agents with the same name
- `--agents-path`: Path to agents directory (default: agents)
- `--project-endpoint`: Azure AI Project endpoint (overrides env var)
- `--env-file`: Path to .env file
- `--verbose`, `-v`: Enable verbose logging

## How It Works

1. **Load Configuration**: Reads `agents/agents.json` for agent definitions
2. **Extract Instructions**: Parses YAML files to get agent instructions
3. **Upload Resources**: For agents with `coding_tools: true`, uploads specified files
4. **Create Agents**: Creates agents in AI Foundry with:
   - Model configuration
   - Instructions
   - Tools (code interpreter with files if specified)
   - Metadata

## Adding New Agents

1. Create a YAML file in `agents/` with the agent's instructions:
```yaml
version: 1.0.0
name: My_New_Agent
model:
  id: gpt-4.1
instructions: |
  Your detailed agent instructions here...
```

2. Add an entry to `agents/agents.json`:
```json
{
  "name": "My_New_Agent",
  "instruction_source": "My_New_Agent.yaml",
  "deployment_name": "gpt-4.1",
  "description": "Description of what the agent does",
  "coding_tools": false
}
```

3. For agents needing code interpreter with files:
```json
{
  "name": "My_Data_Agent",
  "instruction_source": "My_Data_Agent.yaml",
  "deployment_name": "gpt-4.1",
  "description": "Processes data files",
  "coding_tools": true,
  "coding_tool_resource": [
    "../tools/my_data.csv"
  ]
}
```

4. Run the creation script:
```bash
# Using wrapper scripts (recommended)
# Windows
.\scripts\create_agents.ps1 -Verbose

# Linux/Mac
./scripts/create_agents.sh --verbose

# Or using Python directly
python scripts/create_agents.py --verbose
```

## Troubleshooting

### Virtual Environment Issues
- The scripts **automatically create** a `.venv` directory if it doesn't exist
- **Windows**: If you get execution policy errors, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Linux/Mac**: If script isn't executable, run: `chmod +x scripts/create_agents.sh`
- If automatic venv creation fails, create manually: `python -m venv .venv` then rerun the script

### Authentication Issues
- Ensure you're logged in to Azure CLI: `az login`
- Verify your tenant ID is correct
- Check that you have permissions to create agents in the AI Foundry project

### File Upload Issues
- Verify file paths are correct relative to the agents folder
- Check file sizes (there may be limits)
- Ensure files exist in the specified locations

### YAML Parsing Issues
- Validate YAML syntax using a YAML validator
- Ensure the `instructions` field exists in the YAML file
- Check for proper indentation

