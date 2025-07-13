# tests/integration/test_orchestrator_integration.py
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, GenerationRequest
from genesis_core.config.project_config import ProjectConfig, StackConfig


@pytest.mark.asyncio
class TestOrchestratorIntegration:
    """Integration tests for orchestrator with real-like scenarios"""
    
    async def test_full_generation_workflow(self):
        """Test complete generation workflow end-to-end"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = CoreOrchestrator()
            
            # Mock MCPturbo with realistic responses
            orchestrator.mcp_protocol = AsyncMock()
            orchestrator.mcp_orchestrator = AsyncMock()
            orchestrator.agent_registry = AsyncMock()
            
            # Mock agent registry
            orchestrator.agent_registry.list_agents.return_value = [
                "architect_agent", "backend_agent", "frontend_agent", "devops_agent"
            ]
            
            # Mock workflow execution with realistic timing
            mock_result = AsyncMock()
            mock_result.success = True
            mock_result.generated_files = [
                "backend/app/main.py",
                "backend/requirements.txt", 
                "backend/Dockerfile",
                "frontend/app/page.tsx",
                "frontend/package.json",
                "frontend/Dockerfile",
                "docker-compose.yml",
                ".github/workflows/ci.yml"
            ]
            mock_result.metadata = {
                "tasks_completed": 6,
                "execution_time": 120.5,
                "agents_used": ["architect_agent", "backend_agent", "frontend_agent", "devops_agent"]
            }
            
            orchestrator.mcp_orchestrator.execute_workflow.return_value = mock_result
            
            await orchestrator.start()
            
            # Create generation request
            project_config = ProjectConfig(
                name="integration-test-app",
                description="Integration test application",
                template="saas-basic",
                components=["backend", "frontend"],
                features=["authentication", "billing"],
                stack=StackConfig(
                    backend="fastapi",
                    frontend="nextjs",
                    database="postgresql"
                )
            )
            
            request = GenerationRequest(
                project_config=project_config,
                output_path=temp_dir,
                metadata={"test_type": "integration"}
            )
            
            # Execute generation
            result = await orchestrator.execute_project_generation(request)
            
            # Verify result
            assert result.success
            assert result.workflow_id
            assert len(result.generated_files) == 8
            assert result.execution_time > 0
            
            # Verify workflow state
            workflow_status = orchestrator.get_workflow_status(result.workflow_id)
            assert workflow_status["status"] in ["completed", "running"]
            assert workflow_status["project_name"] == "integration-test-app"
            
            # Verify project state
            project_status = orchestrator.get_project_status(result.workflow_id)
            assert project_status["name"] == "integration-test-app"
            assert project_status["template"] == "saas-basic"
            assert len(project_status["components"]) == 2
            
            await orchestrator.stop()