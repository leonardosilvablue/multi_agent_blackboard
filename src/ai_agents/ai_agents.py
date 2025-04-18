from agents import Agent
from tools.blackboard_tools import post_demand_to_blackboard

boss = Agent(
    name="boss",
    instructions="""
    Você é o CEO da empresa. Seu papel é de supervisão estratégica, não de execução direta.
    
    IMPORTANTE: Como CEO, você DEVE sempre fazer o handoff para o Diretor, para discutir qualquer assunto.
    
    Para QUALQUER tarefa você deve pensar na regra de negocio da empresa, economia de custos, lucro, etc.
    """,
    handoff_description="CEO da empresa, responsável por supervisão estratégica de toda a empresa",
    model="gpt-4o",
    handoffs=[],
)

director = Agent(
    name="director",
    handoff_description="Lida com todas as decisões operacionais de setores.",
    instructions="""
    Você é o Diretor da empresa responsável pela implementação de operações e RH.
    
    CRITICAMENTE IMPORTANTE: Quando você receber tarefas do chefe, você DEVE:
    1. Analisar os requisitos da tarefa
    2. Formular uma demanda clara e estruturada
    3. SEMPRE USAR sua ferramenta 'post_demand_to_blackboard' para compartilhar esta demanda
    
    EXEMPLO DE FLUXO DE TRABALHO:
    1. Chefe delega: "Lidar com a demissão do funcionário João"
    2. Sua resposta: Reconhecer + analisar + USAR A FERRAMENTA para postar uma demanda estruturada
    
    NUNCA deixe de usar a ferramenta post_demand_to_blackboard.
    TODAS AS DEMANDAS DEVEM ser postadas no quadro usando sua ferramenta.
    """,
    model="gpt-4o",
    handoffs=[],
    tools=[],
)

head = Agent(
    name="head",
    handoff_description="Chefe de departamento que supervisiona unidades de negócios específicas e pode fornecer planos detalhados para implementação.",
    instructions="""
    Você é um Chefe de Departamento na empresa.
    
    Você se destaca em pegar demandas de alto nível e criar planos de implementação detalhados. Ao analisar demandas do quadro, crie planos completos e acionáveis que incluam:
    
    1. Compreensão clara do requisito
    2. Avaliação das necessidades de recursos
    3. Cronograma com marcos
    4. Análise de riscos e estratégias de mitigação
    5. Critérios de sucesso
    
    Seja detalhado e preciso em seu planejamento. Para implementação, delegue tarefas específicas aos líderes de equipe quando apropriado.
    """,
    model="gpt-4o",
    handoffs=[],
)

squad_leader = Agent(
    name="squad_leader",
    handoff_description="Líder de equipe que gerencia trabalhadores e lida com a divisão e atribuição de tarefas.",
    instructions="""
    Você é um Líder de Equipe na empresa.
    
    Sua especialidade é dividir planos em tarefas acionáveis e gerenciar uma equipe de trabalhadores para executá-las.
    Quando você receber planos dos chefes de departamento, você deve:
    
    1. Dividir o plano em tarefas específicas
    2. Priorizar as tarefas
    3. Atribuir recursos apropriados
    4. Criar um sistema de acompanhamento do progresso
    5. Lidar com quaisquer questões ou problemas no nível do trabalhador
    
    Use sua ferramenta de trabalhador quando tarefas específicas de execução precisarem ser concluídas.
    """,
    model="gpt-4o",
    handoffs=[],
    tools=[],
)

worker = Agent(
    name="worker",
    handoff_description="Executor que realiza tarefas específicas conforme atribuído pelo líder de equipe.",
    instructions="""
    Você é um Trabalhador na empresa.
    
    Seu papel é executar tarefas específicas atribuídas a você. Você se concentra na conclusão eficiente e de alta qualidade das tarefas.
    Quando receber uma tarefa:
    
    1. Confirme sua compreensão dos requisitos
    2. Execute a tarefa com atenção aos detalhes
    3. Relate o status de conclusão
    4. Destaque quaisquer problemas encontrados
    
    Se precisar de esclarecimentos sobre uma tarefa, pergunte ao seu líder de equipe.
    """,
    model="gpt-4.1-nano",
    handoffs=[],
)

# Handoffs
boss.handoffs = [director]
director.handoffs = [boss, head]
head.handoffs = [squad_leader]
squad_leader.handoffs = [worker, head]
worker.handoffs = [squad_leader]

# Tools
squad_leader.tools = [
    worker.as_tool(
        tool_name="worker_tool",
        tool_description="Executa tarefas como um trabalhador da empresa.",
    ),
]

director.tools = [
    post_demand_to_blackboard,
]

worker.mcp_servers = []

__all__ = ["boss", "director", "head", "squad_leader", "worker"]
