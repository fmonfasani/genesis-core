# tests/conftest.py
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator
from genesis_core.config.project_config import ProjectConfig, StackConfig


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def orchestrator():
    """Create a test orchestrator instance."""
    orchestrator = CoreOrchestrator()
    
    # Mock MCPturbo dependencies
    orchestrator.mcp_protocol = AsyncMock()
    orchestrator.mcp_orchestrator = AsyncMock()
    orchestrator.agent_registry = Mock()
    
    await orchestrator.start()
    yield orchestrator
    await orchestrator.stop()


@pytest.fixture
def sample_project_config():
    """Sample project configuration for testing."""
    return ProjectConfig(
        name="test-project",
        description="Test project for unit testing",
        template="saas-basic",
        components=["backend", "frontend"],
        features=["authentication", "billing"],
        stack=StackConfig(
            backend="fastapi",
            frontend="nextjs",
            database="postgresql"
        )
    )


@pytest.fixture
def sample_generation_request(sample_project_config):
    """Sample generation request."""
    from genesis_core.orchestrator.core_orchestrator import GenerationRequest
    
    return GenerationRequest(
        project_config=sample_project_config,
        output_path="/tmp/test-projects",
        metadata={"test": True}
    )