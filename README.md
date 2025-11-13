# NTG Insights Agents

A Python-based tool to create and manage Azure AI Foundry agents using YAML configuration files.

## Overview

This project provides a command-line interface (CLI) and Python library to:
- Create AI Foundry agents from YAML configurations exported from Azure AI Foundry
- Validate agent configurations before deployment
- List and manage existing agents in your Azure AI Foundry project
- Support for all AI Foundry agent features including model options, tools, and metadata

## Features

- ✅ Parse and validate Azure AI Foundry agent YAML configurations
- ✅ Create agents programmatically using Azure AI SDK
- ✅ Command-line interface for easy agent management
- ✅ Support for model configuration (temperature, top_p, etc.)
- ✅ Support for agent metadata (authors, tags)
- ✅ Example configurations for common use cases
- ✅ Environment-based configuration support

## Installation

### Prerequisites

- Python 3.8 or higher
- Azure subscription with AI Foundry project
- Azure CLI (for authentication)

### Install from source

```bash
# Clone the repository
git clone https://github.com/rjayapra/ntg-insights-agents.git
cd ntg-insights-agents

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Configuration

### Azure Authentication

This tool uses Azure's `DefaultAzureCredential` for authentication. You can authenticate using:

1. **Azure CLI** (recommended for development):
   ```bash
   az login
   ```

2. **Environment Variables**:
   ```bash
   export AZURE_TENANT_ID="your-tenant-id"
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"
   ```

3. **Managed Identity** (for production deployments)

### Project Configuration

Set up your Azure AI Foundry project connection:

```bash
# Create a .env file
ntg-agent init

# Edit .env and add your project details
AZURE_AI_PROJECT_ENDPOINT=your_project_endpoint_here
AZURE_SUBSCRIPTION_ID=your_subscription_id_here
AZURE_RESOURCE_GROUP=your_resource_group_here
AZURE_AI_PROJECT_NAME=your_project_name_here
```

## Usage

### Command-Line Interface

#### Initialize Configuration

Create example configuration files and .env template:

```bash
ntg-agent init
```

#### Validate Agent Configuration

Validate a YAML configuration without creating an agent:

```bash
ntg-agent validate examples/simple-chatbot.yaml
```

#### Create an Agent

Create an agent from a YAML configuration:

```bash
ntg-agent create examples/insights-data-analyst.yaml --endpoint "your-endpoint-url"
```

Or with environment variable:

```bash
export AZURE_AI_PROJECT_ENDPOINT="your-endpoint-url"
ntg-agent create examples/insights-data-analyst.yaml
```

#### List Agents

List all agents in your project:

```bash
ntg-agent list-agents --endpoint "your-endpoint-url"
```

#### Delete an Agent

Delete an agent by ID:

```bash
ntg-agent delete agent-id-here --endpoint "your-endpoint-url"
```

### Python Library Usage

```python
from ntg_insights_agents.config_parser import AgentConfigParser
from ntg_insights_agents.agent_creator import AgentCreator

# Parse configuration
parser = AgentConfigParser('examples/simple-chatbot.yaml')
config = parser.load()
parser.validate()

# Create agent
creator = AgentCreator(project_endpoint='your-endpoint')
agent = creator.create_agent_from_config(config)

print(f"Created agent: {agent.name} (ID: {agent.id})")
```

## YAML Configuration Format

The tool supports the Azure AI Foundry agent YAML format:

```yaml
# yaml-language-server: $schema=https://aka.ms/ai-foundry-vsc/agent/1.0.0
version: 1.0.0
name: my-agent
description: Description of the agent
id: ''
metadata:
  authors:
    - author1
    - author2
  tags:
    - tag1
    - tag2
model:
  id: 'gpt-4o'
  options:
    temperature: 1
    top_p: 1
instructions: |
  Your agent instructions here.
  These define the agent's behavior and personality.
tools: []
```

### Configuration Fields

- **version**: Schema version (currently 1.0.0)
- **name**: Agent name (required)
- **description**: Brief description of the agent
- **id**: Agent ID (auto-generated when created)
- **metadata**: 
  - **authors**: List of agent authors
  - **tags**: List of tags for categorization
- **model**: Model configuration (required)
  - **id**: Model deployment name (e.g., 'gpt-4o', 'gpt-35-turbo')
  - **options**: Model parameters
    - **temperature**: Controls randomness (0-2)
    - **top_p**: Controls diversity (0-1)
- **instructions**: System prompt defining agent behavior (required)
- **tools**: List of tools/functions the agent can use

## Examples

The `examples/` directory contains sample agent configurations:

1. **insights-data-analyst.yaml** - Data analysis specialist
2. **code-review-assistant.yaml** - Code review expert
3. **simple-chatbot.yaml** - Basic conversational agent

Try them out:

```bash
ntg-agent validate examples/insights-data-analyst.yaml
ntg-agent create examples/code-review-assistant.yaml
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=ntg_insights_agents tests/
```

### Project Structure

```
ntg-insights-agents/
├── src/
│   └── ntg_insights_agents/
│       ├── __init__.py
│       ├── config_parser.py    # YAML configuration parser
│       ├── agent_creator.py    # Azure AI Foundry agent creator
│       └── cli.py              # Command-line interface
├── examples/                    # Example agent configurations
├── tests/                       # Unit tests
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Ensure you're logged in: `az login`
2. Verify your Azure subscription is active
3. Check that you have necessary permissions on the AI Foundry project

### Configuration Validation Errors

Common validation errors:

- **Missing required field**: Ensure `version`, `name`, and `model` are present
- **Invalid model config**: Check that `model.id` is specified
- **YAML syntax error**: Validate YAML syntax using a YAML validator

### Agent Creation Failures

If agent creation fails:

1. Verify your project endpoint URL is correct
2. Ensure the model deployment exists in your project
3. Check that you have permissions to create agents

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the NTG Insights Team

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Foundry VS Code Extension](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/vs-code-agents)
- [Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects)
