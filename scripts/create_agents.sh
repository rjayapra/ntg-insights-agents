#!/bin/bash
# Bash Script to Create AI Foundry Agents
# Usage: ./create_agents.sh [--dry-run] [--force] [--agents-path agents] [--verbose]

set -e  # Exit on any error

# Default values
DRY_RUN=false
FORCE=false
VERBOSE=false
AGENTS_PATH="agents"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --agents-path)
            AGENTS_PATH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--force] [--agents-path PATH] [--verbose]"
            echo "  --dry-run       Show what would be created without actually creating"
            echo "  --force         Overwrite existing agents with the same name"
            echo "  --agents-path   Path to agents directory (default: agents)"
            echo "  --verbose       Enable verbose logging"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🤖 AI Foundry Agent Creation Script${NC}"
echo -e "${CYAN}===================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python is required but not found in PATH${NC}"
    echo -e "${YELLOW}Please install Python and ensure it's in your PATH${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}✅ Python detected: $PYTHON_VERSION${NC}"

# Check if virtual environment exists
VENV_PATH="./.venv"
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
else
    echo -e "${YELLOW}⚠️ No virtual environment found at $VENV_PATH${NC}"
    echo -e "${BLUE}� Creating virtual environment...${NC}"
    
    if $PYTHON_CMD -m venv "$VENV_PATH"; then
        echo -e "${GREEN}✅ Virtual environment created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        echo -e "${YELLOW}Please create one manually with: $PYTHON_CMD -m venv .venv${NC}"
        exit 1
    fi
fi

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
    source "$VENV_PATH/bin/activate"
else
    echo -e "${YELLOW}⚠️ Could not find activation script${NC}"
fi

# Check if required packages are installed
echo -e "${BLUE}🔍 Checking required packages...${NC}"

REQUIRED_PACKAGES=("azure-ai-projects" "azure-identity" "azure-core" "python-dotenv" "pyyaml")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if pip show "$package" &> /dev/null; then
        echo -e "  ${GREEN}✅ $package${NC}"
    else
        MISSING_PACKAGES+=("$package")
        echo -e "  ${RED}❌ $package (missing)${NC}"
    fi
done

# Install missing packages
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${BLUE}📦 Installing missing packages...${NC}"
    for package in "${MISSING_PACKAGES[@]}"; do
        echo -e "  ${YELLOW}Installing $package...${NC}"
        if pip install "$package"; then
            echo -e "  ${GREEN}✅ $package installed successfully${NC}"
        else
            echo -e "  ${RED}❌ Failed to install $package${NC}"
        fi
    done
fi

# Check environment variables
echo -e "${BLUE}🔍 Checking environment variables...${NC}"

REQUIRED_ENV_VARS=("PROJECT_ENDPOINT" "AZURE_TENANT_ID")
MISSING_ENV_VARS=()

for env_var in "${REQUIRED_ENV_VARS[@]}"; do
    if [ -n "${!env_var}" ]; then
        echo -e "  ${GREEN}✅ $env_var${NC}"
    else
        MISSING_ENV_VARS+=("$env_var")
        echo -e "  ${RED}❌ $env_var (missing)${NC}"
    fi
done

# Load from .env file if environment variables are missing
if [ ${#MISSING_ENV_VARS[@]} -gt 0 ]; then
    ENV_FILES=(".env" "src/backend/.env")
    
    for env_file in "${ENV_FILES[@]}"; do
        if [ -f "$env_file" ]; then
            echo -e "${BLUE}📄 Loading environment variables from $env_file...${NC}"
            
            # Export variables from .env file
            export $(grep -v '^#' "$env_file" | xargs -d '\n')
            
            # Check again
            for env_var in "${REQUIRED_ENV_VARS[@]}"; do
                if [ -n "${!env_var}" ]; then
                    echo -e "  ${GREEN}✅ Loaded $env_var${NC}"
                fi
            done
            break
        fi
    done
fi

# Final check for required environment variables
STILL_MISSING_ENV_VARS=()
for env_var in "${REQUIRED_ENV_VARS[@]}"; do
    if [ -z "${!env_var}" ]; then
        STILL_MISSING_ENV_VARS+=("$env_var")
    fi
done

if [ ${#STILL_MISSING_ENV_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    for env_var in "${STILL_MISSING_ENV_VARS[@]}"; do
        echo -e "  ${RED}- $env_var${NC}"
    done
    echo -e "${YELLOW}Please set these variables or update your .env file${NC}"
    exit 1
fi

# Check if agents directory exists
if [ ! -d "$AGENTS_PATH" ]; then
    echo -e "${RED}❌ Agents directory not found: $AGENTS_PATH${NC}"
    echo -e "${YELLOW}Please ensure the agents directory exists with agents.json${NC}"
    exit 1
fi

AGENTS_JSON_PATH="$AGENTS_PATH/agents.json"
if [ ! -f "$AGENTS_JSON_PATH" ]; then
    echo -e "${RED}❌ agents.json not found: $AGENTS_JSON_PATH${NC}"
    exit 1
fi

# Read and display agent count
if command -v jq &> /dev/null; then
    AGENT_COUNT=$(jq '.agents | length' "$AGENTS_JSON_PATH")
    echo -e "${BLUE}📊 Found $AGENT_COUNT agent configurations in agents.json${NC}"
    
    # Display agent names
    echo -e "\n${CYAN}Agents to be created:${NC}"
    jq -r '.agents[] | "  • \(.name)\(if .coding_tools then " (with code interpreter)" else "" end)"' "$AGENTS_JSON_PATH"
else
    echo -e "${BLUE}📊 Found agents.json${NC}"
    echo -e "${YELLOW}⚠️ Install 'jq' to see agent details${NC}"
fi

# Build Python command arguments
PYTHON_ARGS=("create_agents.py")

if [ "$DRY_RUN" = true ]; then
    PYTHON_ARGS+=("--dry-run")
    echo -e "\n${YELLOW}🔍 Running in DRY RUN mode${NC}"
fi

if [ "$FORCE" = true ]; then
    PYTHON_ARGS+=("--force")
    echo -e "${YELLOW}⚠️ Force mode enabled - will overwrite existing agents${NC}"
fi

if [ "$VERBOSE" = true ]; then
    PYTHON_ARGS+=("--verbose")
fi

PYTHON_ARGS+=("--agents-path" "$AGENTS_PATH")

# Run the Python script
echo -e "\n${BLUE}🚀 Executing agent creation script...${NC}"
echo -e "${CYAN}Command: $PYTHON_CMD ${PYTHON_ARGS[*]}${NC}"
echo ""

if $PYTHON_CMD "${PYTHON_ARGS[@]}"; then
    echo -e "\n${GREEN}✅ Agent creation script completed successfully${NC}"
else
    echo -e "${RED}❌ Agent creation script failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Script execution completed!${NC}"
echo -e "${BLUE}Check the output above for detailed results.${NC}"