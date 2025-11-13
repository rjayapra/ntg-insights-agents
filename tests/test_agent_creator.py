"""
Unit tests for agent_creator module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from ntg_insights_agents.agent_creator import AgentCreator


@pytest.fixture
def mock_agent():
    """Mock Agent object"""
    agent = Mock()
    agent.id = 'agent-123'
    agent.name = 'test-agent'
    agent.model = 'gpt-4o'
    return agent


@pytest.fixture
def agent_config():
    """Sample agent configuration"""
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


class TestAgentCreator:
    """Test cases for AgentCreator"""
    
    def test_initialization_with_endpoint(self):
        """Test creator initialization with project endpoint"""
        endpoint = "https://test.endpoint.com"
        
        with patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'), \
             patch('ntg_insights_agents.agent_creator.AIProjectClient'):
            creator = AgentCreator(project_endpoint=endpoint)
            
            assert creator.project_endpoint == endpoint
    
    def test_initialization_with_env_vars(self):
        """Test creator initialization using environment variables"""
        with patch.dict('os.environ', {
            'AZURE_AI_PROJECT_ENDPOINT': 'https://env.endpoint.com',
            'AZURE_SUBSCRIPTION_ID': 'sub-123',
            'AZURE_RESOURCE_GROUP': 'rg-test',
            'AZURE_AI_PROJECT_NAME': 'project-test'
        }), \
             patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'), \
             patch('ntg_insights_agents.agent_creator.AIProjectClient'):
            creator = AgentCreator()
            
            assert creator.project_endpoint == 'https://env.endpoint.com'
            assert creator.subscription_id == 'sub-123'
            assert creator.resource_group == 'rg-test'
            assert creator.project_name == 'project-test'
    
    def test_initialization_without_endpoint(self):
        """Test creator initialization without endpoint"""
        with patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'):
            creator = AgentCreator()
            
            assert creator.client is None
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_create_agent(self, mock_cred, mock_client_class, mock_agent):
        """Test creating an agent"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.agents.create_agent.return_value = mock_agent
        mock_client_class.from_connection_string.return_value = mock_client
        
        # Create agent
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        agent = creator.create_agent(
            name='test-agent',
            model='gpt-4o',
            instructions='Test instructions'
        )
        
        # Verify
        assert agent.id == 'agent-123'
        assert agent.name == 'test-agent'
        mock_client.agents.create_agent.assert_called_once()
    
    def test_create_agent_without_client(self):
        """Test creating an agent without initialized client"""
        with patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'):
            creator = AgentCreator()
            
            with pytest.raises(ValueError, match="AI Project client not initialized"):
                creator.create_agent(
                    name='test-agent',
                    model='gpt-4o'
                )
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_create_agent_with_tools(self, mock_cred, mock_client_class, mock_agent):
        """Test creating an agent with tools"""
        mock_client = MagicMock()
        mock_client.agents.create_agent.return_value = mock_agent
        mock_client_class.from_connection_string.return_value = mock_client
        
        tools = [{'type': 'function', 'name': 'test_tool'}]
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        agent = creator.create_agent(
            name='test-agent',
            model='gpt-4o',
            tools=tools
        )
        
        assert agent is not None
        call_args = mock_client.agents.create_agent.call_args
        assert 'tools' in call_args.kwargs
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_create_agent_with_metadata(self, mock_cred, mock_client_class, mock_agent):
        """Test creating an agent with metadata"""
        mock_client = MagicMock()
        mock_client.agents.create_agent.return_value = mock_agent
        mock_client_class.from_connection_string.return_value = mock_client
        
        metadata = {'authors': ['test'], 'tags': ['tag1']}
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        agent = creator.create_agent(
            name='test-agent',
            model='gpt-4o',
            metadata=metadata
        )
        
        assert agent is not None
        call_args = mock_client.agents.create_agent.call_args
        assert 'metadata' in call_args.kwargs
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_create_agent_from_config(self, mock_cred, mock_client_class, mock_agent, agent_config):
        """Test creating an agent from configuration dictionary"""
        mock_client = MagicMock()
        mock_client.agents.create_agent.return_value = mock_agent
        mock_client_class.from_connection_string.return_value = mock_client
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        agent = creator.create_agent_from_config(agent_config)
        
        assert agent.id == 'agent-123'
        assert agent.name == 'test-agent'
        mock_client.agents.create_agent.assert_called_once()
        
        # Check that model options were passed
        call_args = mock_client.agents.create_agent.call_args
        assert call_args.kwargs['name'] == 'test-agent'
        assert call_args.kwargs['model'] == 'gpt-4o'
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_list_agents(self, mock_cred, mock_client_class):
        """Test listing agents"""
        mock_agent1 = Mock()
        mock_agent1.name = 'agent1'
        mock_agent2 = Mock()
        mock_agent2.name = 'agent2'
        
        mock_client = MagicMock()
        mock_client.agents.list_agents.return_value = [mock_agent1, mock_agent2]
        mock_client_class.from_connection_string.return_value = mock_client
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        agents = creator.list_agents()
        
        assert len(agents) == 2
        assert agents[0].name == 'agent1'
        assert agents[1].name == 'agent2'
    
    def test_list_agents_without_client(self):
        """Test listing agents without initialized client"""
        with patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'):
            creator = AgentCreator()
            
            with pytest.raises(ValueError, match="AI Project client not initialized"):
                creator.list_agents()
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_delete_agent(self, mock_cred, mock_client_class):
        """Test deleting an agent"""
        mock_client = MagicMock()
        mock_client_class.from_connection_string.return_value = mock_client
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        creator.delete_agent('agent-123')
        
        mock_client.agents.delete_agent.assert_called_once_with('agent-123')
    
    def test_delete_agent_without_client(self):
        """Test deleting an agent without initialized client"""
        with patch('ntg_insights_agents.agent_creator.DefaultAzureCredential'):
            creator = AgentCreator()
            
            with pytest.raises(ValueError, match="AI Project client not initialized"):
                creator.delete_agent('agent-123')
    
    @patch('ntg_insights_agents.agent_creator.AIProjectClient')
    @patch('ntg_insights_agents.agent_creator.DefaultAzureCredential')
    def test_create_agent_failure(self, mock_cred, mock_client_class):
        """Test handling agent creation failure"""
        mock_client = MagicMock()
        mock_client.agents.create_agent.side_effect = Exception("API Error")
        mock_client_class.from_connection_string.return_value = mock_client
        
        creator = AgentCreator(project_endpoint="https://test.endpoint.com")
        
        with pytest.raises(Exception, match="Failed to create agent"):
            creator.create_agent(name='test-agent', model='gpt-4o')
