# src/genesis_core/config/project_config.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ComponentType(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGING = "messaging"


class TemplateType(str, Enum):
    SAAS_BASIC = "saas-basic"
    MICROSERVICES = "microservices" 
    AI_READY = "ai-ready"
    E_COMMERCE = "e-commerce"
    BLOG_CMS = "blog-cms"


class FeatureType(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BILLING = "billing"
    NOTIFICATIONS = "notifications"
    FILE_UPLOAD = "file_upload"
    SEARCH = "search"
    ANALYTICS = "analytics"
    ADMIN_PANEL = "admin_panel"
    AI_CHAT = "ai_chat"
    MONITORING = "monitoring"


class StackConfig(BaseModel):
    """Configuración de stack tecnológico"""
    backend: Optional[str] = "fastapi"
    frontend: Optional[str] = "nextjs"
    database: Optional[str] = "postgresql"
    cache: Optional[str] = "redis"
    messaging: Optional[str] = None


class ProjectConfig(BaseModel):
    """
    Configuración completa del proyecto
    
    Validación centralizada de toda la configuración del proyecto
    """
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    template: TemplateType = TemplateType.SAAS_BASIC
    
    # Componentes a generar
    components: List[ComponentType] = Field(
        default=[ComponentType.BACKEND, ComponentType.FRONTEND]
    )
    
    # Features a incluir
    features: List[FeatureType] = Field(default=[])
    
    # Stack tecnológico
    stack: StackConfig = Field(default_factory=StackConfig)
    
    # Configuraciones específicas
    deployment: Dict[str, Any] = Field(default_factory=dict)
    integrations: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata adicional
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        """Validar nombre del proyecto"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Name must be alphanumeric with hyphens or underscores")
        return v.lower()
    
    @validator('components')
    def validate_components(cls, v):
        """Validar componentes"""
        if not v:
            raise ValueError("At least one component is required")
        return v
    
    @validator('stack')
    def validate_stack_consistency(cls, v, values):
        """Validar consistencia del stack"""
        components = values.get('components', [])
        
        if ComponentType.BACKEND in components and not v.backend:
            raise ValueError("Backend stack required when backend component selected")
        
        if ComponentType.FRONTEND in components and not v.frontend:
            raise ValueError("Frontend stack required when frontend component selected")
        
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        """Crear desde diccionario"""
        return cls(**data)