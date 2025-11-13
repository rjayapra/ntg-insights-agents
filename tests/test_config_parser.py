"""
Unit tests for config_parser module
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from ntg_insights_agents.config_parser import AgentConfigParser


@pytest.fixture
def valid_config():
    """Valid agent configuration"""
    return {
        'version': '1.0.0',
        'name': 'test-agent',
        'description': 'Test agent',
        'model': {
            'id': 'gpt-4o',
            'options': {
                'temperature': 0.7,
                'top_p': 0.9
            }
        },
        'instructions': 'You are a test agent',
        'metadata': {
            'authors': ['test-author'],
            'tags': ['test']
        },
        'tools': []
    }


@pytest.fixture
def valid_config_file(valid_config):
    """Create a temporary valid config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(valid_config, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def invalid_config_file():
    """Create a temporary invalid config file (missing required fields)"""
    invalid_config = {
        'version': '1.0.0',
        'name': 'test-agent'
        # Missing 'model' field
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(invalid_config, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


class TestAgentConfigParser:
    """Test cases for AgentConfigParser"""
    
    def test_parser_initialization(self, valid_config_file):
        """Test parser can be initialized with a file path"""
        parser = AgentConfigParser(valid_config_file)
        assert parser.config_path == Path(valid_config_file)
        assert parser.config is None
    
    def test_load_valid_config(self, valid_config_file):
        """Test loading a valid configuration file"""
        parser = AgentConfigParser(valid_config_file)
        config = parser.load()
        
        assert config is not None
        assert config['name'] == 'test-agent'
        assert config['model']['id'] == 'gpt-4o'
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises FileNotFoundError"""
        parser = AgentConfigParser('/nonexistent/file.yaml')
        
        with pytest.raises(FileNotFoundError):
            parser.load()
    
    def test_validate_valid_config(self, valid_config_file):
        """Test validation passes for valid configuration"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        assert parser.validate() is True
    
    def test_validate_missing_required_field(self, invalid_config_file):
        """Test validation fails when required fields are missing"""
        parser = AgentConfigParser(invalid_config_file)
        parser.load()
        
        with pytest.raises(ValueError, match="Missing required field: model"):
            parser.validate()
    
    def test_validate_before_load(self):
        """Test validation fails if config not loaded"""
        parser = AgentConfigParser('/some/path.yaml')
        
        with pytest.raises(ValueError, match="Configuration not loaded"):
            parser.validate()
    
    def test_get_agent_name(self, valid_config_file):
        """Test getting agent name from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        assert parser.get_agent_name() == 'test-agent'
    
    def test_get_model_id(self, valid_config_file):
        """Test getting model ID from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        assert parser.get_model_id() == 'gpt-4o'
    
    def test_get_instructions(self, valid_config_file):
        """Test getting instructions from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        assert parser.get_instructions() == 'You are a test agent'
    
    def test_get_model_options(self, valid_config_file):
        """Test getting model options from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        options = parser.get_model_options()
        assert options['temperature'] == 0.7
        assert options['top_p'] == 0.9
    
    def test_get_tools(self, valid_config_file):
        """Test getting tools from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        tools = parser.get_tools()
        assert tools == []
    
    def test_get_metadata(self, valid_config_file):
        """Test getting metadata from config"""
        parser = AgentConfigParser(valid_config_file)
        parser.load()
        
        metadata = parser.get_metadata()
        assert 'authors' in metadata
        assert 'test-author' in metadata['authors']
        assert 'test' in metadata['tags']
    
    def test_get_methods_before_load(self):
        """Test get methods fail if config not loaded"""
        parser = AgentConfigParser('/some/path.yaml')
        
        with pytest.raises(ValueError, match="Configuration not loaded"):
            parser.get_agent_name()
        
        with pytest.raises(ValueError, match="Configuration not loaded"):
            parser.get_model_id()
    
    def test_validate_invalid_model_structure(self):
        """Test validation fails for invalid model structure"""
        invalid_config = {
            'version': '1.0.0',
            'name': 'test-agent',
            'model': 'invalid-string-model'  # Should be dict
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            parser = AgentConfigParser(temp_path)
            parser.load()
            
            with pytest.raises(ValueError, match="'model' must be a dictionary"):
                parser.validate()
        finally:
            os.unlink(temp_path)
    
    def test_validate_missing_model_id(self):
        """Test validation fails when model.id is missing"""
        invalid_config = {
            'version': '1.0.0',
            'name': 'test-agent',
            'model': {
                'options': {'temperature': 0.7}
                # Missing 'id'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            parser = AgentConfigParser(temp_path)
            parser.load()
            
            with pytest.raises(ValueError, match="'model' must contain 'id' field"):
                parser.validate()
        finally:
            os.unlink(temp_path)
