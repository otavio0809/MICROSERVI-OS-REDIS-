Caso 14 - Microserviço de Cache com Redis

Projeto desenvolvido para a disciplina de Testes e Qualidade de Software. O sistema consiste em uma API construída com FastAPI que utiliza Redis para armazenamento em cache, com foco na melhoria de desempenho e na validação da aplicação por meio de testes automatizados.

Funcionalidades Implementadas

Aula 1 - Estrutura Inicial e Testes Unitários

Desenvolvimento da API utilizando FastAPI.
Implementação de endpoints para consulta de preços e limpeza de cache.
Tratamento e validação de dados.
Criação de testes unitários com Pytest para validar as funções de serialização e desserialização utilizadas no cache.

Aula 2 - Testes de Integração e Tratamento de Falhas

Integração da aplicação com Redis executando em container Docker.
Implementação de testes de integração para validar o fluxo de cache:

Cache Miss: consulta ao serviço externo e armazenamento no cache.
Cache Hit: recuperação dos dados diretamente do Redis.
Implementação de testes para cenários de falha, verificando o comportamento da API quando o serviço externo está indisponível.

Execução do Projeto: Iniciar o Redis, Instalar as dependências: pip install -r requirements.txt


Executar a aplicação:
uvicorn app.main:app --reload

Executar os testes:
pytest


Estrutura de Testes

Testes unitários: validação das funções auxiliares relacionadas ao cache.
Testes de integração: validação da comunicação entre a API e o Redis.
Testes de falha: validação do comportamento da aplicação diante da indisponibilidade de serviços externos.
