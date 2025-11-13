# Quick Start Guide

This guide will help you get started with creating AI Foundry agents using this tool.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Azure AI Foundry Project**: Create a project at https://ai.azure.com
3. **Python 3.8+**: Make sure Python is installed on your system

## Installation

### 1. Clone and Install

```bash
git clone https://github.com/rjayapra/ntg-insights-agents.git
cd ntg-insights-agents
pip install -e .
```

### 2. Set Up Azure Authentication

```bash
# Login to Azure CLI
az login

# Verify your login
az account show
```

### 3. Configure Your Project

```bash
# Create configuration file
ntg-agent init

# Edit .env file with your project details
# Get your project endpoint from Azure AI Foundry portal
```

## Basic Usage

### Validate a Configuration

Before creating an agent, validate your YAML configuration:

```bash
ntg-agent validate examples/simple-chatbot.yaml
```

### Create an Agent

Create an agent from a YAML configuration:

```bash
# Set your project endpoint
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.eastus.api.azureml.ms"

# Create the agent
ntg-agent create examples/simple-chatbot.yaml
```

### List Your Agents

See all agents in your project:

```bash
ntg-agent list-agents
```

### Delete an Agent

Remove an agent by its ID:

```bash
ntg-agent delete <agent-id>
```

## Creating Your Own Agent

### 1. Create a YAML Configuration File

Create a file `my-agent.yaml`:

```yaml
version: 1.0.0
name: my-custom-agent
description: My custom AI agent
id: ''
metadata:
  authors:
    - Your Name
  tags:
    - custom
model:
  id: 'gpt-4o'
  options:
    temperature: 0.7
    top_p: 0.95
instructions: |
  You are a helpful AI assistant specialized in [your domain].
  
  Your responsibilities include:
  - Task 1
  - Task 2
  - Task 3
tools: []
```

### 2. Validate Your Configuration

```bash
ntg-agent validate my-agent.yaml
```

### 3. Create the Agent

```bash
ntg-agent create my-agent.yaml
```

## Using as a Python Library

You can also use this tool as a Python library in your own scripts:

```python
from ntg_insights_agents.config_parser import AgentConfigParser
from ntg_insights_agents.agent_creator import AgentCreator

# Parse configuration
parser = AgentConfigParser('my-agent.yaml')
config = parser.load()
parser.validate()

# Create agent
creator = AgentCreator(project_endpoint='your-endpoint')
agent = creator.create_agent_from_config(config)

print(f"✓ Agent created: {agent.name} (ID: {agent.id})")
```

## Common Issues

### Authentication Failed

If you see authentication errors:

1. Make sure you're logged in: `az login`
2. Check your subscription is active
3. Verify you have access to the AI Foundry project

### Model Not Found

If the agent creation fails with "model not found":

1. Go to your AI Foundry project in the portal
2. Navigate to "Models + endpoints"
3. Check which models are deployed
4. Update your YAML with the correct model deployment name

### Invalid Configuration

If validation fails:

1. Check that all required fields are present: `version`, `name`, `model`
2. Verify `model.id` is specified
3. Make sure your YAML syntax is valid

## Next Steps

- Explore the example configurations in the `examples/` directory
- Read the full README for more details
- Check out the Azure AI Foundry documentation: https://learn.microsoft.com/en-us/azure/ai-foundry/

## Getting Help

- Check the troubleshooting section in README.md
- Open an issue on GitHub
- Contact the NTG Insights Team
