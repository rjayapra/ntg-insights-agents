"""
Command-line interface for NTG Insights Agents
"""

import click
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from .config_parser import AgentConfigParser
from .agent_creator import AgentCreator


# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    NTG Insights Agents - Create AI Foundry agents from YAML configurations
    """
    pass


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--endpoint', '-e', help='Azure AI Project endpoint URL', 
              envvar='AZURE_AI_PROJECT_ENDPOINT')
@click.option('--validate-only', '-v', is_flag=True, 
              help='Only validate the configuration without creating the agent')
def create(config_file, endpoint, validate_only):
    """
    Create an AI Foundry agent from a YAML configuration file
    
    CONFIG_FILE: Path to the YAML configuration file
    """
    try:
        # Parse configuration
        click.echo(f"Loading configuration from: {config_file}")
        parser = AgentConfigParser(config_file)
        config = parser.load()
        
        # Validate configuration
        click.echo("Validating configuration...")
        parser.validate()
        click.echo("✓ Configuration is valid")
        
        # Display configuration details
        click.echo(f"\nAgent Details:")
        click.echo(f"  Name: {parser.get_agent_name()}")
        click.echo(f"  Model: {parser.get_model_id()}")
        click.echo(f"  Instructions: {parser.get_instructions()[:100]}...")
        
        if validate_only:
            click.echo("\n✓ Validation complete (dry run)")
            return
        
        # Check for endpoint
        if not endpoint:
            click.echo("\n✗ Error: Azure AI Project endpoint is required", err=True)
            click.echo("  Set AZURE_AI_PROJECT_ENDPOINT environment variable or use --endpoint option", err=True)
            sys.exit(1)
        
        # Create agent
        click.echo("\nCreating agent...")
        creator = AgentCreator(project_endpoint=endpoint)
        agent = creator.create_agent_from_config(config)
        
        click.echo(f"✓ Agent created successfully!")
        click.echo(f"  Agent ID: {agent.id}")
        click.echo(f"  Agent Name: {agent.name}")
        
    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"✗ Validation Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate(config_file):
    """
    Validate a YAML configuration file without creating an agent
    
    CONFIG_FILE: Path to the YAML configuration file
    """
    try:
        click.echo(f"Loading configuration from: {config_file}")
        parser = AgentConfigParser(config_file)
        config = parser.load()
        
        click.echo("Validating configuration...")
        parser.validate()
        
        click.echo("\n✓ Configuration is valid")
        click.echo(f"\nAgent Details:")
        click.echo(f"  Name: {parser.get_agent_name()}")
        click.echo(f"  Model: {parser.get_model_id()}")
        if parser.get_instructions():
            click.echo(f"  Instructions: {parser.get_instructions()[:100]}...")
        
        metadata = parser.get_metadata()
        if metadata:
            click.echo(f"  Metadata:")
            if 'authors' in metadata:
                click.echo(f"    Authors: {', '.join(metadata['authors'])}")
            if 'tags' in metadata:
                click.echo(f"    Tags: {', '.join(metadata['tags'])}")
        
    except FileNotFoundError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"✗ Validation Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--endpoint', '-e', help='Azure AI Project endpoint URL',
              envvar='AZURE_AI_PROJECT_ENDPOINT')
def list_agents(endpoint):
    """
    List all agents in the Azure AI Foundry project
    """
    try:
        if not endpoint:
            click.echo("✗ Error: Azure AI Project endpoint is required", err=True)
            click.echo("  Set AZURE_AI_PROJECT_ENDPOINT environment variable or use --endpoint option", err=True)
            sys.exit(1)
        
        creator = AgentCreator(project_endpoint=endpoint)
        agents = creator.list_agents()
        
        if not agents:
            click.echo("No agents found in the project")
            return
        
        click.echo(f"Found {len(agents)} agent(s):\n")
        for agent in agents:
            click.echo(f"  • {agent.name}")
            click.echo(f"    ID: {agent.id}")
            click.echo(f"    Model: {agent.model}")
            click.echo()
            
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('agent_id')
@click.option('--endpoint', '-e', help='Azure AI Project endpoint URL',
              envvar='AZURE_AI_PROJECT_ENDPOINT')
@click.confirmation_option(prompt='Are you sure you want to delete this agent?')
def delete(agent_id, endpoint):
    """
    Delete an agent by ID
    
    AGENT_ID: ID of the agent to delete
    """
    try:
        if not endpoint:
            click.echo("✗ Error: Azure AI Project endpoint is required", err=True)
            click.echo("  Set AZURE_AI_PROJECT_ENDPOINT environment variable or use --endpoint option", err=True)
            sys.exit(1)
        
        creator = AgentCreator(project_endpoint=endpoint)
        creator.delete_agent(agent_id)
        
        click.echo(f"✓ Agent {agent_id} deleted successfully")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def init():
    """
    Create a sample .env file and example agent configuration
    """
    env_content = """# Azure AI Foundry Configuration
AZURE_AI_PROJECT_ENDPOINT=your_project_endpoint_here
AZURE_SUBSCRIPTION_ID=your_subscription_id_here
AZURE_RESOURCE_GROUP=your_resource_group_here
AZURE_AI_PROJECT_NAME=your_project_name_here
"""
    
    env_path = Path('.env')
    if env_path.exists():
        click.echo("✗ .env file already exists", err=True)
    else:
        with open(env_path, 'w') as f:
            f.write(env_content)
        click.echo("✓ Created .env file")
        click.echo("  Please edit .env and add your Azure AI Foundry credentials")
    
    # Create example directory if it doesn't exist
    example_dir = Path('examples')
    example_dir.mkdir(exist_ok=True)
    
    # Create example configuration
    example_config = """# yaml-language-server: $schema=https://aka.ms/ai-foundry-vsc/agent/1.0.0
version: 1.0.0
name: example-agent
description: An example AI Foundry agent
id: ''
metadata:
  authors:
    - Your Name
  tags:
    - example
    - demo
model:
  id: 'gpt-4o'
  options:
    temperature: 1
    top_p: 1
instructions: |
  You are a helpful AI assistant. Your role is to assist users with their questions
  and provide accurate, helpful information.
tools: []
"""
    
    example_path = example_dir / 'example-agent.yaml'
    if example_path.exists():
        click.echo("✗ Example configuration already exists at examples/example-agent.yaml", err=True)
    else:
        with open(example_path, 'w') as f:
            f.write(example_config)
        click.echo("✓ Created example configuration at examples/example-agent.yaml")


if __name__ == '__main__':
    main()
