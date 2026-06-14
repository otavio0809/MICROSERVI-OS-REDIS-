Case 14: Microserviço de Cache (Redis)- Adaptado a situação de previsão metereologica. 

Projeto desenvolvido para a disciplina de Testes e Qualidade de Software. O sistema consiste em um microserviço construído com FastAPI que implementa uma camada de cache utilizando Redis para otimizar consultas de dados meteorológicos (previsão do tempo), focado em eficiência de desempenho e validação rigorosa por meio de testes automatizados (Unitários, Integração, E2E e Mutação).

Funcionalidades Implementadas

Aula 1 - Estrutura Inicial e Testes Unitários

API FastAPI: Criação do endpoint principal /clima/{cidade} para consulta de condições meteorológicas e do endpoint /cache/clear para gerenciamento e invalidação do cache.

Tratamento de Dados: Funções auxiliares em app/utils.py para serialização e desserialização de payloads.

Testes Unitários (test_unitario.py): Validação estrita das funções de conversão com Pytest, garantindo resiliência contra tipos de dados inválidos antes de interagir com o cache.

Aula 2 - Testes de Integração e Tratamento de Falhas

Integração com Redis: Arquitetura preparada para rodar com Redis via container Docker ou simulada em memória via fakeredis para isolamento de testes.

Testes de Integração (test_integ.py): Validação do ciclo lógico do cache:

Cache Miss: Quando o dado não está no Redis, o sistema consulta de forma segura o serviço meteorológico externo e armazena o resultado.

Cache Hit: Consultas subsequentes recuperam os dados instantaneamente do Redis, poupando chamadas externas.

Tratamento de Falhas: Teste de comportamento resiliente (retorno HTTP 502) simulando a indisponibilidade total do provedor meteorológico externo.

Entrega Aula 3 — Testes E2E e Análise de Mutação

Testes End-to-End (test_e2e.py): Simulação completa da jornada do usuário: fluxo de primeira consulta (miss), segunda consulta imediata (hit), limpeza manual do cache via requisição POST e verificação do retorno ao estado original (miss).

Cenário de Mutação Analisado

Para avaliar a sensibilidade e a qualidade da nossa suíte de testes, simulamos a introdução de um bug (mutante) no arquivo app/main.py. Alteramos o parâmetro de expiração do cache no método cliente_redis.setex(chave_cache, 10, ...) mudando o tempo de vida (TTL) de 10 para 0 segundos.

Impacto do Mutante: A API continuou respondendo sem estourar exceções de código, mas o mecanismo de persistência temporária foi quebrado. Todas as requisições resultavam obrigatoriamente em Cache Miss (cached: False).

Relatório de Impacto e Resolução: O teste End-to-End (test_e2e.py) capturou a mutação imediatamente. A asserção assert dados_2["cached"] is True falhou na segunda chamada do teste, pois o mutante impediu o dado de estar disponível no Redis.

Resultado: O mutante foi detectado e eliminado com sucesso, comprovando a alta cobertura e confiabilidade dos testes desenvolvidos.