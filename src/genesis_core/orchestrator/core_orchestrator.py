# src/genesis_core/orchestrator/core_orchestrator.py
"""
Core Orchestrator - CUMPLE ECOSYSTEM_DOCTRINE

MANDAMIENTOS CUMPLIDOS:
✅ No reimplementa lo que ya hace MCPturbo
✅ No habla directamente con el usuario final  
✅ Todo lo hace a través de agentes
✅ Nunca genera prompts directamente
✅ No genera código estático ni hardcodeado
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

# MANDAMIENTO: Usar exclusivamente primitivas de MCPturbo
from mcpturbo import protocol, orchestrator as mcp_orchestrator
from mcpturbo.agents import AgentRegistry
from mcpturbo.workflows import WorkflowDefinition, Task

from genesis_core.state.project_state import ProjectState
from genesis_core.state.workflow_state import WorkflowState
from genesis_core.config.project_config import ProjectConfig
from genesis_core.exceptions import CoreOrchestratorError


@dataclass
class GenerationRequest:
    """Request para generación de proyecto"""
    project_config: ProjectConfig
    output_path: str
    workflow_id: Optional[str] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Resultado de generación"""
    success: bool
    workflow_id: str
    project_path: Optional[str] = None
    generated_files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0


class CoreOrchestrator:
    """
    Orquestador Central de Genesis Core
    
    RESPONSABILIDADES (según DOCTRINE):
    - Coordinar workflows usando MCPturbo
    - Gestionar estado del proyecto
    - Validar configuraciones
    - Proveer interfaz limpia para consumidores externos
    
    NO HACE:
    - Comunicación directa con LLMs (eso es de MCPturbo)
    - Implementación de agentes (eso es de genesis-agents)
    - Generación de código (eso es de agentes especializados)
    - CLI o UI (eso es de genesis-cli)
    """
    
    def __init__(self):
        # MANDAMIENTO: Usar MCPturbo, no protocolo propio
        self.mcp_protocol = protocol
        self.mcp_orchestrator = mcp_orchestrator
        self.agent_registry = AgentRegistry()
        
        # Estado interno
        self.project_states: Dict[str, ProjectState] = {}
        self.workflow_states: Dict[str, WorkflowState] = {}
        
        # Control de ejecución
        self.running = False
        self.active_workflows: Set[str] = set()
        
        # Métricas
        self.metrics = {
            "projects_created": 0,
            "workflows_executed": 0,
            "average_execution_time": 0.0,
            "success_rate": 0.0
        }
    
    async def start(self):
        """Inicializar el orquestador"""
        if self.running:
            return
        
        # MANDAMIENTO: Delegar inicialización a MCPturbo
        await self.mcp_protocol.start()
        
        # Configurar handlers de eventos
        self._setup_event_handlers()
        
        self.running = True
    
    async def stop(self):
        """Detener el orquestador"""
        if not self.running:
            return
        
        # Cancelar workflows activos
        for workflow_id in list(self.active_workflows):
            await self.cancel_workflow(workflow_id)
        
        await self.mcp_protocol.stop()
        self.running = False
    
    def _setup_event_handlers(self):
        """Configurar handlers de eventos MCPturbo"""
        # MANDAMIENTO: Usar sistema de eventos de MCPturbo
        self.mcp_protocol.subscribe_to_broadcasts(
            "workflow.completed", self._handle_workflow_completed
        )
        self.mcp_protocol.subscribe_to_broadcasts(
            "workflow.failed", self._handle_workflow_failed
        )
        self.mcp_protocol.subscribe_to_broadcasts(
            "agent.registered", self._handle_agent_registered
        )
    
    async def execute_project_generation(
        self, request: GenerationRequest
    ) -> GenerationResult:
        """
        Ejecutar generación de proyecto completo
        
        INTERFAZ PRINCIPAL para consumidores externos (genesis-cli)
        """
        start_time = datetime.utcnow()
        workflow_id = request.workflow_id or str(uuid.uuid4())
        
        try:
            # Validar configuración
            await self._validate_generation_request(request)
            
            # Crear estado del proyecto
            project_state = ProjectState(
                name=request.project_config.name,
                template=request.project_config.template,
                config=request.project_config,
                output_path=request.output_path,
                created_at=start_time
            )
            self.project_states[workflow_id] = project_state
            
            # Construir workflow usando MCPturbo
            workflow_def = await self._build_generation_workflow(request)
            
            # Crear estado del workflow
            workflow_state = WorkflowState(
                workflow_id=workflow_id,
                definition=workflow_def,
                project_state=project_state,
                status="running",
                started_at=start_time
            )
            self.workflow_states[workflow_id] = workflow_state
            self.active_workflows.add(workflow_id)
            
            # MANDAMIENTO: Ejecutar usando MCPturbo orchestrator
            result = await self.mcp_orchestrator.execute_workflow(
                workflow_id, workflow_def
            )
            
            # Procesar resultado
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if result.success:
                self.metrics["projects_created"] += 1
                self.metrics["workflows_executed"] += 1
                
                return GenerationResult(
                    success=True,
                    workflow_id=workflow_id,
                    project_path=request.output_path,
                    generated_files=result.generated_files,
                    execution_time=execution_time,
                    metadata=result.metadata
                )
            else:
                return GenerationResult(
                    success=False,
                    workflow_id=workflow_id,
                    error=result.error,
                    execution_time=execution_time
                )
                
        except Exception as e:
            return GenerationResult(
                success=False,
                workflow_id=workflow_id,
                error=f"Error en orquestación: {str(e)}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
        finally:
            # Cleanup
            self.active_workflows.discard(workflow_id)
    
    async def _build_generation_workflow(
        self, request: GenerationRequest
    ) -> WorkflowDefinition:
        """
        Construir workflow de generación usando MCPturbo
        
        MANDAMIENTO: No implementar lógica de workflow propia
        """
        tasks = []
        
        # 1. Análisis de arquitectura
        tasks.append(Task(
            id="analyze_architecture",
            agent_id="architect_agent",
            action="analyze_requirements",
            params={
                "config": request.project_config.to_dict(),
                "output_path": request.output_path
            },
            dependencies=[]
        ))
        
        # 2. Diseño de arquitectura
        tasks.append(Task(
            id="design_architecture", 
            agent_id="architect_agent",
            action="design_architecture",
            params={
                "requirements": "{{analyze_architecture.result}}"
            },
            dependencies=["analyze_architecture"]
        ))
        
        # 3. Generación de backend
        if "backend" in request.project_config.components:
            tasks.append(Task(
                id="generate_backend",
                agent_id="backend_agent", 
                action="generate_backend",
                params={
                    "architecture": "{{design_architecture.result}}",
                    "output_path": f"{request.output_path}/backend"
                },
                dependencies=["design_architecture"]
            ))
        
        # 4. Generación de frontend  
        if "frontend" in request.project_config.components:
            tasks.append(Task(
                id="generate_frontend",
                agent_id="frontend_agent",
                action="generate_frontend", 
                params={
                    "architecture": "{{design_architecture.result}}",
                    "output_path": f"{request.output_path}/frontend"
                },
                dependencies=["design_architecture"]
            ))
        
        # 5. Configuración DevOps
        backend_deps = ["generate_backend"] if "backend" in request.project_config.components else []
        frontend_deps = ["generate_frontend"] if "frontend" in request.project_config.components else []
        
        tasks.append(Task(
            id="setup_devops",
            agent_id="devops_agent",
            action="setup_devops",
            params={
                "architecture": "{{design_architecture.result}}",
                "output_path": request.output_path
            },
            dependencies=["design_architecture"] + backend_deps + frontend_deps
        ))
        
        # MANDAMIENTO: Usar WorkflowDefinition de MCPturbo
        return WorkflowDefinition(
            id=request.workflow_id or str(uuid.uuid4()),
            name="project_generation",
            tasks=tasks,
            max_parallel_tasks=3,
            timeout=1800  # 30 minutos
        )
    
    async def _validate_generation_request(self, request: GenerationRequest):
        """Validar request de generación"""
        if not request.project_config.name:
            raise CoreOrchestratorError("Project name is required")
        
        if not request.output_path:
            raise CoreOrchestratorError("Output path is required")
        
        # Validar que agentes requeridos estén disponibles
        required_agents = ["architect_agent"]
        if "backend" in request.project_config.components:
            required_agents.append("backend_agent")
        if "frontend" in request.project_config.components:
            required_agents.append("frontend_agent")
        required_agents.append("devops_agent")
        
        available_agents = self.agent_registry.list_agents()
        for agent_id in required_agents:
            if agent_id not in available_agents:
                raise CoreOrchestratorError(f"Required agent not available: {agent_id}")
    
    # Event Handlers
    async def _handle_workflow_completed(self, event: Dict[str, Any]):
        """Manejar workflow completado"""
        workflow_id = event.get("workflow_id")
        if workflow_id in self.workflow_states:
            self.workflow_states[workflow_id].status = "completed"
            self.workflow_states[workflow_id].completed_at = datetime.utcnow()
    
    async def _handle_workflow_failed(self, event: Dict[str, Any]):
        """Manejar workflow fallido"""
        workflow_id = event.get("workflow_id")
        if workflow_id in self.workflow_states:
            self.workflow_states[workflow_id].status = "failed"
            self.workflow_states[workflow_id].completed_at = datetime.utcnow()
            self.workflow_states[workflow_id].error = event.get("error")
    
    async def _handle_agent_registered(self, event: Dict[str, Any]):
        """Manejar registro de agente"""
        agent_id = event.get("agent_id")
        # Log o métricas si es necesario
    
    # Métodos de consulta para consumidores externos
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de workflow"""
        if workflow_id not in self.workflow_states:
            return None
        
        state = self.workflow_states[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": state.status,
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "project_name": state.project_state.name,
            "progress": state.get_progress(),
            "error": state.error
        }
    
    def get_project_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado del proyecto"""
        if workflow_id not in self.project_states:
            return None
        
        state = self.project_states[workflow_id]
        return {
            "name": state.name,
            "template": state.template,
            "output_path": state.output_path,
            "created_at": state.created_at.isoformat(),
            "components": state.config.components,
            "features": state.config.features
        }
    
    def get_available_agents(self) -> List[str]:
        """Obtener agentes disponibles"""
        return self.agent_registry.list_agents()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del orquestador"""
        return {
            **self.metrics,
            "active_workflows": len(self.active_workflows),
            "total_workflows": len(self.workflow_states),
            "total_projects": len(self.project_states)
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancelar workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        # MANDAMIENTO: Usar cancelación de MCPturbo
        success = await self.mcp_orchestrator.cancel_workflow(workflow_id)
        
        if success and workflow_id in self.workflow_states:
            self.workflow_states[workflow_id].status = "cancelled"
            self.workflow_states[workflow_id].completed_at = datetime.utcnow()
        
        self.active_workflows.discard(workflow_id)
        return success