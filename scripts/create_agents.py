#!/usr/bin/env python3
"""
AI Foundry Agent Creation Script

This script reads agent configurations from the agents/agents.json file
and creates them in Azure AI Foundry using the Azure AI SDK.

The script:
- Loads agent definitions from agents.json
- Reads instructions from corresponding YAML files
- Uploads code interpreter files for agents that need them
- Creates agents with appropriate tools and configurations

Usage:
    python create_agents.py [--dry-run] [--force] [--agents-path agents]

Arguments:
    --dry-run: Show what would be created without actually creating
    --force: Overwrite existing agents with the same name
    --agents-path: Path to agents folder (default: agents)
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import yaml

# Add the backend directory to the Python path
#sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'backend'))

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
except ImportError as e:
    print(f"❌ Missing required Azure packages: {e}")
    print("Please install: pip install azure-ai-projects azure-identity azure-core")
    sys.exit(1)

def load_env_file(env_file: Optional[str] = None):
    """Load environment variables from a .env file"""
    possible_paths = []
    
    if env_file:
        possible_paths.append(Path(env_file))
    else:
        possible_paths.extend([
            Path.cwd() / '.env',
            Path.home() / '.env',
            Path(__file__).parent / '.env',
        ])
    
    for path in possible_paths:
        if path.exists():
            load_dotenv(dotenv_path=path)
            logger.info(f"✅ Loaded environment variables from: {path}")
            return
    
    logger.warning("⚠️ No .env file found in common locations")

def validate_environment() -> bool:
    """Validate that required environment variables are set"""
    logger.info("🔍 Validating environment variables...")
    
    required_vars = [
        "PROJECT_ENDPOINT",
        "AZURE_TENANT_ID"
    ]
    
    optional_vars = [       
    ]
    
    missing_required = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"  ✅ {var}")
        else:
            missing_required.append(var)
            logger.error(f"  ❌ {var} (required)")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"  ✅ {var} (optional)")
        else:
            logger.info(f"  ⚠️ {var} (optional - will use DefaultAzureCredential)")
    
    if missing_required:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these in your .env file or as environment variables")
        return False
    
    logger.info("✅ Environment validation passed")
    return True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    name: str
    description: str
    instructions: str
    model: str = "gpt-4o-mini"
    tools: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    coding_tools: bool = False
    coding_tool_resources: List[str] = field(default_factory=list)

class AIFoundryAgentCreator:
    """Creates agents in Azure AI Foundry"""
    
    def __init__(self, project_endpoint: str = None):
        """Initialize the agent creator"""
        self.project_endpoint = project_endpoint or os.getenv('PROJECT_ENDPOINT')
        if not self.project_endpoint:
            raise ValueError("PROJECT_ENDPOINT environment variable is required")
        
        # Initialize Azure AI Project client
        self.credential = DefaultAzureCredential()

        self.client = AIProjectClient(
                credential=self.credential,
                endpoint=self.project_endpoint
        )
        
        logger.info(f"Initialized AI Foundry client for: {self.project_endpoint}")
    
    def load_instructions_from_yaml(self, yaml_path: Path) -> Optional[str]:
        """Load instructions from a YAML agent configuration file"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                agent_yaml = yaml.safe_load(f)
                instructions = agent_yaml.get('instructions', '')
                
                # Handle both string and multi-line string instructions
                if isinstance(instructions, str):
                    return instructions.strip()
                elif isinstance(instructions, dict):
                    # Some YAML might have instructions as a dict
                    return str(instructions).strip()
                else:
                    logger.warning(f"Unexpected instructions format in {yaml_path}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to load instructions from {yaml_path}: {e}")
            return None
    
    def upload_file(self, file_path: Path) -> Optional[str]:
        """Upload a file to AI Foundry and return its file ID"""
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            logger.info(f"Uploading file: {file_path.name}")
            
            with open(file_path, 'rb') as f:
                uploaded_file = self.client.agents.upload_file_and_poll(
                    file=f,
                    purpose="assistants"
                )
            
            logger.info(f"✅ File uploaded successfully: {uploaded_file.id}")
            return uploaded_file.id
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    def load_agents_from_export(self, export_path: str = "agents") -> List[AgentConfig]:
        """Load agent configurations from agents.json file"""
        agents = []
        agents_folder_path = Path(export_path)
        agents_json_path = agents_folder_path / "agents.json"
        
        if not agents_json_path.exists():
            logger.error(f"agents.json not found at: {agents_json_path}")
            return agents
        
        try:
            with open(agents_json_path, 'r', encoding='utf-8') as f:
                agents_data = json.load(f)
            
            logger.info(f"Loading {len(agents_data.get('agents', []))} agent configurations...")
            
            for agent_def in agents_data.get('agents', []):
                name = agent_def.get('name')
                instruction_source = agent_def.get('instruction_source')
                
                if not name or not instruction_source:
                    logger.warning(f"Skipping agent with missing name or instruction_source")
                    continue
                
                # Load instructions from YAML file
                yaml_path = agents_folder_path / instruction_source
                instructions = self.load_instructions_from_yaml(yaml_path)
                
                if not instructions:
                    logger.error(f"Failed to load instructions for {name} from {instruction_source}")
                    continue
                
                # Build tools list
                tools = []
                coding_tool_resources = agent_def.get('coding_tool_resource', [])
                
                if agent_def.get('coding_tools', False):
                    # Add code interpreter tool
                    code_interpreter_tool = {
                        "type": "code_interpreter"
                    }
                    
                    # Upload files if specified
                    if coding_tool_resources:
                        file_ids = []
                        for resource_path in coding_tool_resources:
                            # Resolve path relative to agents folder
                            full_path = agents_folder_path / resource_path
                            file_id = self.upload_file(full_path)
                            if file_id:
                                file_ids.append(file_id)
                        
                        if file_ids:
                            code_interpreter_tool["file_ids"] = file_ids
                    
                    tools.append(code_interpreter_tool)
                
                agent_config = AgentConfig(
                    name=name,
                    description=agent_def.get('description', ''),
                    instructions=instructions,
                    model=agent_def.get('deployment_name', 'gpt-4o-mini'),
                    tools=tools,
                    coding_tools=agent_def.get('coding_tools', False),
                    coding_tool_resources=coding_tool_resources,
                    metadata={
                        'source': 'agents.json',
                        'instruction_source': instruction_source
                    }
                )
                
                agents.append(agent_config)
                logger.info(f"✅ Loaded agent config: {name} (tools: {len(tools)})")
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to load agents.json: {e}")
            return agents
    
    def create_agent(self, config: AgentConfig, force: bool = False) -> Optional[str]:
        """Create a single agent in AI Foundry"""
        try:
            # Check if agent already exists
            existing_agents = self.list_existing_agents()
            existing_names = [agent.get('name', '') for agent in existing_agents]
            
            if config.name in existing_names and not force:
                logger.warning(f"Agent '{config.name}' already exists. Use --force to overwrite.")
                return None
            
            # Prepare agent creation parameters
            agent_params = {
                "model": config.model,
                "name": config.name,
                "description": config.description,
                "instructions": config.instructions,
                "tools": config.tools or [],
                "metadata": config.metadata or {}
            }
            
            # Create the agent
            logger.info(f"Creating agent: {config.name}")
            agent = self.client.agents.create_agent(**agent_params)
            
            logger.info(f"✅ Successfully created agent: {config.name} (ID: {agent.id})")
            return agent.id
            
        except ResourceExistsError:
            logger.warning(f"Agent '{config.name}' already exists")
            return None
        except Exception as e:
            logger.error(f"Failed to create agent '{config.name}': {e}")
            return None
    
    def list_existing_agents(self) -> List[Dict]:
        """List existing agents in the AI Foundry project"""
        try:
            agents = self.client.agents.list_agents()
            return [agent.to_dict() for agent in agents]
        except Exception as e:
            logger.error(f"Failed to list existing agents: {e}")
            return []
    
    def create_all_agents(self, configs: List[AgentConfig], dry_run: bool = False, force: bool = False) -> Dict[str, str]:
        """Create all agents from configurations"""
        results = {}
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No agents will be created")
        
        logger.info(f"Processing {len(configs)} agent configurations...")
        
        for config in configs:
            if dry_run:
                logger.info(f"[DRY RUN] Would create agent: {config.name}")
                logger.info(f"  - Model: {config.model}")
                logger.info(f"  - Instructions length: {len(config.instructions)} characters")
                logger.info(f"  - Tools: {len(config.tools)}")
                logger.info(f"  - Coding tools: {config.coding_tools}")
                if config.coding_tool_resources:
                    logger.info(f"  - Resources: {', '.join(config.coding_tool_resources)}")
                results[config.name] = "dry-run"
            else:
                agent_id = self.create_agent(config, force=force)
                results[config.name] = agent_id
        
        return results

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Create AI agents in Azure AI Foundry from agents.json configuration"
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help="Show what would be created without actually creating"
    )
    parser.add_argument(
        '--force',
        action='store_true', 
        help="Overwrite existing agents with the same name"
    )
    parser.add_argument(
        '--agents-path',
        default='agents',
        help="Path to the agents directory containing agents.json (default: agents)"
    )
    parser.add_argument(
        '--project-endpoint',
        help="Azure AI Project endpoint (default: from PROJECT_ENDPOINT env var)"
    )
    parser.add_argument(
        '--env-file',
        help="Path to .env file (default: searches common locations)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("🤖 Starting AI Foundry Agent Creation")
        logger.info("=" * 50)
        
        # Load environment variables from .env file first
        load_env_file(args.env_file)
        
        # Validate environment variables
        if not validate_environment():
            logger.error("Environment validation failed. Please check your .env file.")
            sys.exit(1)
        
        # Initialize the agent creator
        creator = AIFoundryAgentCreator(project_endpoint=args.project_endpoint)
        
        # Load agent configurations
        logger.info(f"Loading agent configurations from: {args.agents_path}")
        configs = creator.load_agents_from_export(args.agents_path)
        
        if not configs:
            logger.error("No agent configurations found!")
            sys.exit(1)
        
        # Create agents
        results = creator.create_all_agents(
            configs=configs,
            dry_run=args.dry_run,
            force=args.force
        )
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("AGENT CREATION SUMMARY")
        logger.info("="*50)
        
        successful = 0
        failed = 0
        
        for name, result in results.items():
            if result and result != "dry-run":
                logger.info(f"✅ {name}: Created (ID: {result})")
                successful += 1
            elif result == "dry-run":
                logger.info(f"🔍 {name}: Dry run")
            else:
                logger.info(f"❌ {name}: Failed")
                failed += 1
        
        if not args.dry_run:
            logger.info(f"\nTotal: {successful} successful, {failed} failed")
        else:
            logger.info(f"\nDry run completed for {len(results)} agents")
        
        logger.info("="*50)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()