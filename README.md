# genesis-core
genesis-core/
├── src/genesis_core/
│   ├── __init__.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── core_orchestrator.py    # Orquestador principal
│   │   ├── workflow_builder.py     # Constructor de workflows
│   │   └── task_coordinator.py     # Coordinador de tareas
│   ├── state/
│   │   ├── __init__.py
│   │   ├── project_state.py        # Estado del proyecto
│   │   ├── workflow_state.py       # Estado del workflow
│   │   └── persistence.py          # Persistencia de estado
│   ├── config/
│   │   ├── __init__.py
│   │   ├── project_config.py       # Configuración de proyecto
│   │   └── validation.py           # Validación de configuración
│   └── exceptions.py               # Excepciones específicas
├── tests/
├── docs/
├── pyproject.toml
├── README.md
├── ECOSYSTEM_DOCTRINE.md
└── .github/workflows/