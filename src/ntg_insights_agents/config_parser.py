"""
YAML configuration parser for AI Foundry agents
"""

import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path


class AgentConfigParser:
    """Parser for AI Foundry agent YAML configurations"""
    
    def __init__(self, config_path: str):
        """
        Initialize the parser with a YAML configuration file path
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: Optional[Dict[str, Any]] = None
        
    def load(self) -> Dict[str, Any]:
        """
        Load and parse the YAML configuration file
        
        Returns:
            Dictionary containing the parsed configuration
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        return self.config
    
    def validate(self) -> bool:
        """
        Validate the loaded configuration
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if self.config is None:
            raise ValueError("Configuration not loaded. Call load() first.")
        
        required_fields = ['version', 'name', 'model']
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate model configuration
        if 'model' in self.config:
            model_config = self.config['model']
            if not isinstance(model_config, dict):
                raise ValueError("'model' must be a dictionary")
            if 'id' not in model_config:
                raise ValueError("'model' must contain 'id' field")
        
        return True
    
    def get_agent_name(self) -> str:
        """Get the agent name from configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('name', '')
    
    def get_model_id(self) -> str:
        """Get the model ID from configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('model', {}).get('id', '')
    
    def get_instructions(self) -> str:
        """Get the agent instructions from configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('instructions', '')
    
    def get_model_options(self) -> Dict[str, Any]:
        """Get the model options from configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('model', {}).get('options', {})
    
    def get_tools(self) -> List[Any]:
        """Get the tools configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('tools', [])
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the metadata from configuration"""
        if self.config is None:
            raise ValueError("Configuration not loaded")
        return self.config.get('metadata', {})
