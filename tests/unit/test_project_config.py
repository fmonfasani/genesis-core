# tests/unit/test_core_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, GenerationRequest
from genesis_core.exceptions import CoreOrchestratorError


class TestCoreOrchestrator:
    """Test suite for CoreOrchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        orchestrator = CoreOrchestrator()
        
        assert not orchestrator.running
        assert len(orchestrator.active_workflows) == 0
        assert orchestrator.metrics["projects_created"] == 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_start_stop(self):
        """Test orchestrator start/stop lifecycle"""
        orchestrator = CoreOrchestrator()
        orchestrator.mcp_protocol = AsyncMock()
        
        await orchestrator.start()
        assert orchestrator.running
        orchestrator.mcp_protocol.start.assert_called_once()
        
        await orchestrator.stop()
        assert not orchestrator.running
        orchestrator.mcp_protocol.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_project_generation_success(self, orchestrator, sample_generation_request):
        """Test successful project generation"""
        # Mock MCPturbo workflow execution
        mock_result = AsyncMock()
        mock_result.success = True
        mock_result.generated_files = ["backend/main.py", "frontend/page.tsx"]
        mock_result.metadata = {"execution_time": 45.2}
        
        orchestrator.mcp_orchestrator.execute_workflow.return_value = mock_result
        orchestrator.agent_registry.list_agents.return_value = [
            "architect_agent", "backend_agent", "frontend_agent", "devops_agent"
        ]
        
        # Execute generation
        result = await orchestrator.execute_project_generation(sample_generation_request)
        
        # Assertions
        assert result.success
        assert result.project_path == sample_generation_request.output_path
        assert len(result.generated_files) == 2
        assert result.execution_time > 0
        
        # Verify workflow was created and executed
        orchestrator.mcp_orchestrator.execute_workflow.assert_called_once()
        
        # Verify metrics updated
        assert orchestrator.metrics["projects_created"] == 1
        assert orchestrator.metrics["workflows_executed"] == 1
    
    @pytest.mark.asyncio
    async def test_execute_project_generation_missing_agent(self, orchestrator, sample_generation_request):
        """Test generation fails when required agent is missing"""
        # Mock missing agent
        orchestrator.agent_registry.list_agents.return_value = ["architect_agent"]
        
        # Execute generation
        result = await orchestrator.execute_project_generation(sample_generation_request)
        
        # Should fail due to missing agents
        assert not result.success
        assert "Required agent not available" in result.error
    
    @pytest.mark.asyncio
    async def test_workflow_status_tracking(self, orchestrator, sample_generation_request):
        """Test workflow status is tracked correctly"""
        # Mock successful execution
        mock_result = AsyncMock()
        mock_result.success = True
        mock_result.generated_files = []
        mock_result.metadata = {}
        
        orchestrator.mcp_orchestrator.execute_workflow.return_value = mock_result
        orchestrator.agent_registry.list_agents.return_value = [
            "architect_agent", "backend_agent", "frontend_agent", "devops_agent"
        ]
        
        # Execute generation
        result = await orchestrator.execute_project_generation(sample_generation_request)
        workflow_id = result.workflow_id
        
        # Check workflow status
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None
        assert status["workflow_id"] == workflow_id
        assert status["project_name"] == sample_generation_request.project_config.name
    
    @pytest.mark.asyncio
    async def test_cancel_workflow(self, orchestrator):
        """Test workflow cancellation"""
        workflow_id = "test-workflow-123"
        orchestrator.active_workflows.add(workflow_id)
        orchestrator.mcp_orchestrator.cancel_workflow.return_value = True
        
        # Cancel workflow
        success = await orchestrator.cancel_workflow(workflow_id)
        
        assert success
        assert workflow_id not in orchestrator.active_workflows
        orchestrator.mcp_orchestrator.cancel_workflow.assert_called_once_with(workflow_id)


# tests/unit/test_project_config.py
import pytest
from pydantic import ValidationError

from genesis_core.config.project_config import ProjectConfig, StackConfig, ComponentType


class TestProjectConfig:
    """Test suite for ProjectConfig validation"""
    
    def test_valid_config_creation(self):
        """Test creating valid project config"""
        config = ProjectConfig(
            name="my-awesome-project",
            description="An awesome project",
            components=[ComponentType.BACKEND, ComponentType.FRONTEND],
            stack=StackConfig(backend="fastapi", frontend="nextjs")
        )
        
        assert config.name == "my-awesome-project"
        assert len(config.components) == 2
        assert config.stack.backend == "fastapi"
    
    def test_invalid_name_validation(self):
        """Test name validation fails for invalid names"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(name="invalid name with spaces!")
        
        assert "Name must be alphanumeric" in str(exc_info.value)
    
    def test_empty_components_validation(self):
        """Test validation fails for empty components"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(name="test", components=[])
        
        assert "At least one component is required" in str(exc_info.value)
    
    def test_stack_consistency_validation(self):
        """Test stack consistency validation"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(
                name="test",
                components=[ComponentType.BACKEND],
                stack=StackConfig(backend=None)  # Backend required but not specified
            )
        
        assert "Backend stack required" in str(exc_info.value)