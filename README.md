# Multi-Agent Blackboard System with AutoGen

Sistema de gerenciamento de processos usando agentes de IA com AutoGen e quadro negro (blackboard) para coordenação.

## Descrição

Este sistema implementa um modelo de agentes de IA que trabalham em conjunto para processar demandas e tarefas. O sistema utiliza:

- **AutoGen**: Framework para criação de agentes LLM colaborativos
- **Blackboard**: Padrão de design para comunicação entre agentes
- **FastAPI**: Para exposição de endpoints de API

## Agentes

- **Boss**: Agente responsável por receber e delegar tarefas iniciais
- **Director**: Gerencia as operações e RH
- **Head**: Analisa demandas e cria planos estruturados
- **Squad Leader**: Divide planos em tarefas acionáveis
- **Worker**: Executa tarefas específicas

## Arquitetura AutoGen

O sistema foi implementado usando AutoGen, que oferece:

- **AssistantAgent**: Implementação de agentes independentes
- **RoundRobinGroupChat**: Coordenação de conversas entre agentes
- **FunctionTool**: Ferramentas especializadas para os agentes usarem

## Requisitos

- Python 3.12+
- OpenAI API Key

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure sua API Key:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env e adicione sua OpenAI API Key
   ```

## Uso

### CLI Mode

1. Inicie o sistema via linha de comando:
   ```bash
   python src/main.py
   ```

2. Digite uma tarefa para processar, e o sistema usará o fluxo de agentes do AutoGen para processá-la.

### API Mode

1. Inicie o servidor API:
   ```bash
   python src/server.py
   ```

2. A API estará disponível em `http://localhost:8000`

#### Endpoints

- **POST /api/v1/demands**
  ```json
  {
    "demand": "quero contratar o bryan soares",
    "priority": "normal",
    "department": "RH"
  }
  ```

- **GET /api/v1/demands/{task_id}/status**
  - Retorna o status de uma demanda específica

- **GET /api/v1/health**
  - Verifica a saúde do sistema

#### Exemplo de uso com curl

```bash
# Criar uma nova demanda
curl -X POST http://localhost:8000/api/v1/demands \
  -H "Content-Type: application/json" \
  -d '{"demand": "quero contratar o bryan soares"}'

# Verificar status de uma demanda
curl http://localhost:8000/api/v1/demands/1234abcd/status
```

## Exemplos

Para iniciar um processo de contratação:
```
Enter a task: quero contratar o bryan soares
```

## Logs

Os logs do sistema são salvos em `agent_system.log` e podem ser usados para monitorar o fluxo de processamento das tarefas.
