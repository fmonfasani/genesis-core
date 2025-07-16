<!-- ECOSYSTEM_DOCTRINE: genesis-core -->
# 🧠 Ecosystem Doctrine — Genesis-Core (Orquestador Central)

Este repositorio forma parte del ecosistema **Genesis Engine**.  
Su rol es el de **orquestador central que coordina la generación de proyectos full-stack**.

## 🧠 Rol Declarado

- Tipo: **Orquestador Central**
- Nombre: `genesis-core`
- Dominio: Coordinación de generación de software
- Función: Orquestar workflows de generación usando MCPturbo

## 🔒 Mandamientos del Proyecto

### 1. **No reimplementarás lo que ya hace MCPturbo**
Genesis-Core debe usar exclusivamente las primitivas de MCPturbo.  
No debe definir su propio protocolo, lógica de reintentos ni workflows paralelos.

### 2. **No generarás código directamente**
NO contiene generadores, templates, ni lógica de creación de archivos.  
Solo coordina agentes externos que generan código.

### 3. **No implementarás lógica de agentes específicos**
NO debe contener lógica de FastAPI, Next.js, Docker, etc.  
Solo coordina agentes especializados de otros repositorios.

### 4. **No hablarás directamente con el usuario final**
Genesis-Core **no tiene CLI propia ni interfaz gráfica**.  
Recibe instrucciones de genesis-cli y ejecuta.

### 5. **Solo orquestarás y coordinarás**
Tu única responsabilidad es coordinar workflows usando MCPturbo.  
Gestionar estado del proyecto y validar configuraciones.

### 6. **No contendrás templates**
Los templates están en genesis-templates.  
Solo referencias y coordinas su uso.

### 7. **Serás agnóstico al dominio específico**
NO conoces de SaaS, e-commerce, ni dominios específicos.  
Solo coordinas la generación según configuración recibida.

---

## 🧩 Interfaz esperada por consumidores

Los consumidores externos (como genesis-cli) deben usar:

- `GenesisOrchestrator.execute_project_generation(request)`
- `ProjectConfig` para configuración
- `GenerationResult` para resultados
- `ProjectState` para estado del proyecto

---

## 📦 Separación de capas (importante)

| Capa | Puede importar desde | No puede importar desde |
|------|----------------------|--------------------------|
| genesis-core | mcpturbo | genesis-cli, genesis-backend, genesis-frontend, genesis-devops, genesis-ai |
| genesis-cli | genesis-core | mcpturbo directamente |
| genesis-agents | mcpturbo | genesis-core |

---

## 🤖 AI Agents, please read:

Este repositorio es el cerebro coordinador del ecosistema.

Si estás revisando código, escribiendo tests o generando lógica nueva:
- ❌ No implementes generación de código directa.
- ❌ No crees templates o lógica de agentes específicos.
- ❌ No implementes protocolo de comunicación propio.
- ✅ Usa MCPturbo para toda la coordinación.
- ✅ Mantén la lógica de orquestación pura y agnóstica.

Toda excepción debe documentarse en `DOCTRINE_CHANGE_REQUEST.md`.

---

## 📎 Referencias

- MCPturbo Core → [https://github.com/fmonfasani/mcpturbo](https://github.com/fmonfasani/mcpturbo)
- Genesis CLI → [https://github.com/fmonfasani/genesis-cli](https://github.com/fmonfasani/genesis-cli)
