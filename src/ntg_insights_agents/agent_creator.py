"""
Agent creator for Azure AI Foundry
"""

import os
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


class AgentCreator:
    """Creates AI Foundry agents from configuration"""
    
    def __init__(self, 
                 project_endpoint: Optional[str] = None,
                 subscription_id: Optional[str] = None,
                 resource_group: Optional[str] = None,
                 project_name: Optional[str] = None):
        """
        Initialize the agent creator
        
        Args:
            project_endpoint: Azure AI Foundry project endpoint URL
            subscription_id: Azure subscription ID
            resource_group: Azure resource group name
            project_name: Azure AI Foundry project name
        """
        self.project_endpoint = project_endpoint or os.getenv('AZURE_AI_PROJECT_ENDPOINT')
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = resource_group or os.getenv('AZURE_RESOURCE_GROUP')
        self.project_name = project_name or os.getenv('AZURE_AI_PROJECT_NAME')
        
        # Initialize credential
        self.credential = DefaultAzureCredential()
        
        # Initialize client if project endpoint is provided
        self.client: Optional[AIProjectClient] = None
        if self.project_endpoint:
            self.client = AIProjectClient.from_connection_string(
                credential=self.credential,
                conn_str=self.project_endpoint
            )
    
    def create_agent(self, 
                     name: str,
                     model: str,
                     instructions: str = "",
                     tools: list = None,
                     metadata: Dict[str, Any] = None,
                     **kwargs) -> Any:
        """
        Create an AI Foundry agent
        
        Args:
            name: Name of the agent
            model: Model deployment name or ID
            instructions: System instructions for the agent
            tools: List of tools to attach to the agent
            metadata: Additional metadata for the agent
            **kwargs: Additional agent configuration options
            
        Returns:
            Created Agent object
            
        Raises:
            ValueError: If client is not initialized
            Exception: If agent creation fails
        """
        if self.client is None:
            raise ValueError(
                "AI Project client not initialized. "
                "Please provide project_endpoint or set AZURE_AI_PROJECT_ENDPOINT environment variable."
            )
        
        try:
            # Prepare agent configuration
            agent_config = {
                "model": model,
                "name": name,
                "instructions": instructions,
            }
            
            # Add tools if provided
            if tools:
                agent_config["tools"] = tools
            
            # Add metadata if provided
            if metadata:
                agent_config["metadata"] = metadata
            
            # Add any additional configuration
            agent_config.update(kwargs)
            
            # Create the agent
            agent = self.client.agents.create_agent(**agent_config)
            
            return agent
            
        except Exception as e:
            raise Exception(f"Failed to create agent: {str(e)}")
    
    def create_agent_from_config(self, config: Dict[str, Any]) -> Any:
        """
        Create an agent from a parsed configuration dictionary
        
        Args:
            config: Dictionary containing agent configuration
            
        Returns:
            Created Agent object
        """
        # Extract configuration
        name = config.get('name', 'Unnamed Agent')
        model = config.get('model', {}).get('id', '')
        instructions = config.get('instructions', '')
        tools = config.get('tools', [])
        metadata = config.get('metadata', {})
        
        # Get model options
        model_options = config.get('model', {}).get('options', {})
        
        # Create agent with configuration
        return self.create_agent(
            name=name,
            model=model,
            instructions=instructions,
            tools=tools,
            metadata=metadata,
            **model_options
        )
    
    def list_agents(self) -> list:
        """
        List all agents in the project
        
        Returns:
            List of agents
            
        Raises:
            ValueError: If client is not initialized
        """
        if self.client is None:
            raise ValueError("AI Project client not initialized")
        
        try:
            agents = self.client.agents.list_agents()
            return list(agents)
        except Exception as e:
            raise Exception(f"Failed to list agents: {str(e)}")
    
    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent by ID
        
        Args:
            agent_id: ID of the agent to delete
            
        Raises:
            ValueError: If client is not initialized
        """
        if self.client is None:
            raise ValueError("AI Project client not initialized")
        
        try:
            self.client.agents.delete_agent(agent_id)
        except Exception as e:
            raise Exception(f"Failed to delete agent: {str(e)}")
