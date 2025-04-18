# Multi-Agent Blackboard System

Sistema de gerenciamento de processos usando agentes de IA e quadro negro (blackboard) para coordenação.

## Descrição

Este sistema implementa um modelo de agentes de IA que trabalham em conjunto para processar demandas e tarefas. O sistema utiliza um quadro negro (blackboard) como meio de comunicação entre os agentes.

## Agentes

- **Boss**: Agente responsável por receber e delegar tarefas iniciais
- **Director**: Gerencia as operações e RH
- **Head**: Analisa demandas e cria planos estruturados
- **Squad Leader**: Divide planos em tarefas acionáveis
- **Worker**: Executa tarefas específicas

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

1. Inicie o sistema:
   ```bash
   python src/main.py
   ```

2. Comandos disponíveis:
   - Digite uma tarefa para processar
   - Digite 'view' para ver o conteúdo do quadro negro
   - Digite 'help' para ver os comandos disponíveis
   - Digite 'exit' ou pressione Ctrl+C para sair

## Exemplos

Para iniciar um processo de contratação:
```
Enter a task: quero contratar o bryan soares
```

## Logs

Os logs do sistema são salvos em `agent_system.log` e podem ser usados para monitorar o fluxo de processamento das tarefas.
