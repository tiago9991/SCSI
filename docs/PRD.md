# PRD — SCSI: Sistema de Gestão para Corretora de Seguros Inteligente

> **Documento vivo.** Este PRD é o guia único de planejamento, arquitetura, desenvolvimento e deploy do projeto SCSI.
> **Stack-base:** Python > 3.13, Django > 6.0, PostgreSQL, Celery, RabbitMQ, Redis, LangChain > 1.0, LangGraph, OpenAI (GPT-5.5-mini), Docker, Docker Swarm, Traefik, Cloudflare, Let's Encrypt.
> **Convenções de idioma:** Código do projeto em **inglês**. Interface do usuário em **português brasileiro**.

---

## 1. Visão Geral

O **SCSI** (Sistema de Gestão para Corretora de Seguros Inteligente) é uma plataforma SaaS **multi-tenant compartilhada** voltada a corretoras de seguros de pequeno e médio porte. Ele centraliza, em uma única aplicação web, a gestão de:

- Clientes, seguradoras, ramos e coberturas.
- Propostas, apólices, itens cobertos, endossos e sinistros.
- Anexos privados, renovações e alertas.
- CRM com pipeline Kanban de negociações.
- Agentes, produtores, comissões e repasses.
- Relatórios em PDF/CSV e dashboard com métricas e insights.
- **Agentes de IA assistida** construídos com LangChain + LangGraph, com tools de acesso aos dados da corretora do usuário, sempre respeitando o isolamento multi-tenant.

O sistema roda em **Docker Swarm** sobre VPS Ubuntu, exposto pelo **Traefik** com TLS wildcard emitido via **Let's Encrypt DNS-01** sobre o domínio principal **scsi.digital**.

O SCSI permite que múltiplas corretoras utilizem a mesma aplicação, com isolamento lógico de dados, usuários, arquivos, permissões, clientes, propostas, apólices, sinistros, renovações, negociações, comissões, relatórios e agentes de IA.

---

## 2. Objetivos do Produto

1. **Centralizar** a operação da corretora em um único sistema moderno, fluido e responsivo.
2. **Garantir isolamento absoluto** entre corretoras (tenants) em arquitetura compartilhada, sem uso de schemas ou bancos separados.
3. **Automatizar fluxos** de propostas → apólices → itens cobertos → sinistros → renovações.
4. **Acelerar decisões** com agentes de IA que resumem clientes, apólices, sinistros, propostas e negociações, além de chat com sessões salvas e respostas em streaming Markdown.
5. **Padronizar relatórios** de carteira, comissões, sinistros e renovações em PDF e CSV.
6. **Oferecer CRM visual** com grid e Kanban arrastável, pipeline e etapas personalizáveis por corretora.
7. **Operar de forma resiliente** em produção, com healthchecks, restart policies, rollout sem downtime e rollback automático.
8. **Manter segurança de ponta a ponta**: arquivos privados protegidos, secrets não versionadas, TLS wildcard, isolamento de redes Docker.
9. **Servir como produto SaaS** com landing page pública, cadastro de corretora e plano `free` inicial (planos pagos fictícios/desabilitados).
10. **Ser diretamente utilizável** por desenvolvedores, arquitetos, DevOps e agentes de IA de programação como guia de implementação.

---

## 3. Público-Alvo

- **Corretoras de seguros de pequeno e médio porte** que precisam de um sistema unificado de gestão.
- **Corretores autônomos e equipes comerciais** que precisam de CRM, propostas e renovações organizadas.
- **Administradores de corretora** que precisam de dashboard, relatórios, comissões e repasses.
- **Agentes e produtores parceiros** que precisam visualizar suas comissões e repasses.
- **Equipas internas do SCSI** (operações/suporte) acessando via Django Admin com isolamento estrito por tenant.

---

## 4. Problemas que o Sistema Resolve

- Fragmentação de dados de clientes, apólices e sinistros entre planilhas e ferramentas dispersas.
- Falta de visão consolidada de carteira, comissões e renovações.
- Dificuldade de acompanhar negociações em pipeline visual.
- Risco operacional em renovações por ausência de alertas e status.
- Demora na leitura e interpretação de sinistros, apólices e propostas longas → **resumos com IA**.
- Falta de um assistente inteligente que responde com base nos dados da própria corretora.
- Dificuldade de geração de relatórios padronizados para gestão e auditoria.
- Exposição insegura de documentos sensíveis (propostas, apólices, sinistros).
- Custo e complexidade de infraestrutura para corretoras pequenas → SaaS multi-tenant.

---

## 5. Escopo do Produto

### 5.1 Funcionalidades em escopo

- Cadastro de corretora (tenant) durante criação de conta, com CNPJ e Razão Social obrigatórios.
- Landing page pública em `scsi.digital` com planos (apenas `free` habilitado).
- Autenticação por **email** usando sistema nativo do Django.
- Recuperação de senha por email (nativo do Django).
- Gestão de usuários, permissões e perfis vinculados à corretora.
- Clientes, seguradoras, ramos, coberturas, itens cobertos.
- Propostas, apólices, endossos, sinistros, anexos privados, renovações.
- Geração de apólice a partir de proposta (botão "gerar apólice").
- CRM com visualização **grid** e **Kanban** arrastável, pipeline e etapas personalizáveis.
- Agentes, produtores e comissões com cálculo de repasses.
- Dashboard com métricas, gráficos e funil de negociações.
- Relatórios em PDF (ReportLab/PyPDF) e CSV, com menu e tela dedicada.
- Inteligência Artificial:
  - Resumir cliente / apólice / sinistro / proposta / negociação.
  - Chat com IA, sessões salvas por usuário, streaming, resposta em Markdown.
- Tarefas assíncronas com Celery + RabbitMQ + Redis.
- Notificações internas ao finalizar tasks de IA.
- Django Admin completo, com filtros, buscas e respeito ao tenant.
- Documentação com MKDocs e suporte a Mermaid.
- Dados fake via Django command para demonstrações.
- Deploy local com Docker Compose.
- Deploy em produção com Docker Swarm + Traefik + TLS wildcard.
- Scripts de deploy e backup.

### 5.2 Stack em escopo

- Python > 3.13, Django > 6.0, um único `settings.py`.
- PostgreSQL, Celery, RabbitMQ, Redis.
- LangChain > 1.0, LangGraph, OpenAI GPT-5.5-mini.
- ReportLab, PyPDF.
- WhiteNoise para estáticos.
- dj-celery-panel para visualização de tasks no admin.
- django-environ para variáveis.
- MKDocs com Mermaid.
- Docker, Docker Compose, Docker Swarm, Traefik, Cloudflare, Let's Encrypt DNS-01.

---

## 6. Fora de Escopo Inicial

- **Sistema de pagamentos real** (planos pagos são fictícios; botões "em breve" desabilitados).
- **Apps mobile nativos** (web responsiva apenas).
- **Integrações com seguradoras via APIs externas** (cadastro manual de seguradoras).
- **Integração com órgãos reguladores** (SUSEP) por API.
- **Assinatura eletrônica** de propostas/apólices.
- **Bifurcação de schemas/bancos por tenant** (arquitetura é compartilhada).
- **Testes automatizados** (requisito explícito: não implementar testes).
- **SSO/SAML/OAuth externo** (login por email/senha nativo do Django).
- **WSGI/ASGI alternativos além do recomendado** (manter simples).
- **Integração com serviços de SMS/WhatsApp** (apenas email nativo do Django).
- **BI externo** (dashboard interno apenas).
- **Auditoria externa de compliance** (logs internos/admin apenas).

---

## 7. Personas e Perfis de Usuário

### 7.1 Personas

- **Owner/Admin da corretora**: responsável pela conta, gestor de usuários e configurações.
- **Gerente comercial**: acompanha pipeline, metas, comissões e relatórios.
- **Corretor/Produtor**: atende clientes, cria propostas, acompanha sinistros e renovações.
- **Agente parceiro**: pessoa ou empresa que vende para a corretora, recebe repasses.
- **Back-office**: cadastra apólices, endossos, anexos e controla_sinistros.
- **Operações SCSI (interno)**: acesso restrito via admin, sempre respeitando tenant.

### 7.2 Perfis no sistema (groups/permissões Django)

- `brokerage_admin` — Dono/Gerente/Administrador da corretora (acesso total dentro do tenant).
- `brokerage_agent` — Agente da corretora (acesso a seus produtores, comissões e negociações relacionadas).
- `brokerage_producer` — Produtor/corretor final (acesso a clientes, propostas, negociações e comissões próprias).
- `brokerage_backoffice` — Back-office (cadastros e anexos, sem acesso a comissões financeiras por padrão).
- `scsi_staff` — Equipe interna SCSI via Django Admin, **com escopo estrito por tenant**.

> Atribuição de permissões via `Group` e checagens customizadas por `brokerage` + `role`.

---

## 8. Visão Funcional do Sistema

A aplicação é organizada em **apps Django** na raiz do projeto. O app principal é `core` e o app de recursos compartilhados é `base`. Domínios de negócio ficam em apps separados.

### 8.1 Módulos funcionais

1. **Landing & Onboarding** — landing page, cadastro de corretora, escolha de plano.
2. **Identidade & Acesso** — usuários, login por email, recuperação de senha, permissões.
3. **Catálogo** — seguradoras, ramos, coberturas.
4. **Clientes** — cadastro completo e anexos.
5. **Propostas & Apólices** — propostas, geração de apólice, itens cobertos, endossos.
6. **Sinistros** — vinculados a apólice + item coberto, anexos.
7. **Anexos privados** — media protegida por tenant + permissão.
8. **Renovações** — controle de vencimentos e status.
9. **CRM** — negociações em grid e Kanban, pipeline personalizável.
10. **Agentes/Produtores/Comissões** — hierarquia comercial e repasses.
11. **Dashboard** — métricas, gráficos, funil.
12. **Relatórios** — PDF e CSV, menu dedicado.
13. **IA** — resumos e chat com tools de acesso ao tenant.
14. **Admin Django** — gestão total com filtros e buscas.
15. **Documentação** — MKDocs com Mermaid.

### 8.2 Jornadas principais

- **Onboarding**: landing → criar conta → cadastro de corretora (CNPJ + Razão Social) → plano `free` → usuário admin → dashboard.
- **Venda**: criar cliente → proposta → itens cobertos → aceitação → **gerar apólice** → apólice → endossos quando aplicável.
- **Sinistro**: apólice → item coberto → registrar sinistro → anexos → resumo com IA.
- **Renovação**: apólice próxima ao vencimento → renovação → status → relatórios/alertas.
- **CRM**: lead → negociação → etapa Kanban → proposta → apólice → comissão.
- **IA**: detalhe da entidade → "resumir com IA" → Celery → notificação → resumo salvo no campo da entidade.

---

## 9. Requisitos Funcionais

### 9.1 Identidade e Acesso

- **RF-ID-01** Cadastro, edição e desativação de usuários vinculados à corretora.
- **RF-ID-02** Login por **email** (não por username).
- **RF-ID-03** Logout, troca de senha e recuperação de senha por email (nativo Django).
- **RF-ID-04** Permissões por `Group` e checagens por `brokerage` + `role`.
- **RF-ID-05** Cada usuário pertence a exatamente uma corretora (`brokerage` FK).
- **RF-ID-06** Apenas usuários autenticados e vinculados a uma corretora acessam áreas internas.

### 9.2 Corretora (Tenant) e Onboarding

- **RF-BR-01** Cadastro de corretora durante criação de conta.
- **RF-BR-02** **CNPJ obrigatório** e **Razão Social obrigatória**; demais campos opcionais.
- **RF-BR-03** Escolha de plano na criação; apenas `free` disponível inicialmente.
- **RF-BR-04** Após cadastro, cria-se usuário admin vinculado à corretora.
- **RF-BR-05** Não há cadastro de usuário sem corretora.

### 9.3 Landing Page e Planos

- **RF-LP-01** Landing page principal na raiz (`scsi.digital`).
- **RF-LP-02** Apresenta o sistema e direciona para **criar conta** e **login**.
- **RF-LP-03** Planos exibidos são fictícios; apenas `free` habilitado.
- **RF-LP-04** Botões de planos pagos exibem **"em breve"** e ficam desabilitados.
- **RF-LP-05** Nenhuma integração com gateway de pagamentos.

### 9.4 Clientes

- **RF-CL-01** CRUD completo de clientes vinculado à corretora.
- **RF-CL-02** Cliente pode ter propostas, apólices, sinistros, anexos e negociações.
- **RF-CL-03** Tela de detalhe permite **resumir com IA**.
- **RF-CL-04** Listagens com filtros, busca e paginação.

### 9.5 Seguradoras e Ramos

- **RF-SR-01** CRUD de seguradoras por corretora.
- **RF-SR-02** CRUD de ramos de seguro (auto, residencial, vida, viagem, empresarial, frota, outros).
- **RF-SR-03** Seguradoras se relacionam com propostas, apólices e ramos quando aplicável.

### 9.6 Propostas e Apólices

- **RF-PP-01** CRUD de propostas vinculadas a cliente, seguradora, ramo e corretora.
- **RF-PP-02** CRUD de apólices.
- **RF-PP-03** Botão **"gerar apólice"** na proposta cria apólice automaticamente com base nos dados da proposta.
- **RF-PP-04** Propostas e apólices têm **itens cobertos** (1:N).
- **RF-PP-05** Proposta permite **resumir com IA**.
- **RF-PP-06** Apólice permite **resumir com IA**.

### 9.7 Itens Cobertos

- **RF-IC-01** Entidade de item coberto representa o objeto segurado.
- **RF-IC-02** Exemplos: automóvel, casa, frota, viagem, vida, item empresarial.
- **RF-IC-03** Relaciona-se com propostas e apólices.
- **RF-IC-04** Um sinistro sempre está em cima de um **item coberto por uma apólice**.

### 9.8 Sinistros

- **RF-SN-01** CRUD de sinistros.
- **RF-SN-02** Sinistro vinculado a uma **apólice** e a um **item coberto**.
- **RF-SN-03** Sinistro permite **anexos**.
- **RF-SN-04** Sinistro permite **resumir com IA**.

### 9.9 Anexos

- **RF-AN-01** Anexos em clientes, propostas, apólices e sinistros.
- **RF-AN-02** Diversos formatos aceitos (PDF, imagens, documentos comuns).
- **RF-AN-03** Arquivos **privados**: acesso somente por usuários autorizados da corretora correta.

### 9.10 Renovações

- **RF-RN-01** Gestão de renovações de seguros.
- **RF-RN-02** Controle de vencimentos e status.
- **RF-RN-03** Relatórios e alertas relacionados a renovações.

### 9.11 Endossos

- **RF-EN-01** CRUD de endossos.
- **RF-EN-02** Endossos relacionados a apólices.

### 9.12 CRM

- **RF-CRM-01** Painel CRM com visualização **grid** e **Kanban**.
- **RF-CRM-02** Pipeline Kanban **personalizável** por corretora.
- **RF-CRM-03** Etapas com nome e cores **personalizáveis**.
- **RF-CRM-04** Cards **arrastáveis** entre etapas.
- **RF-CRM-05** Negociações podem ser **resumidas com IA**.

### 9.13 Agentes, Produtores e Comissões

- **RF-AP-01** CRUD de agentes (pessoa ou empresa parceira).
- **RF-AP-02** CRUD de produtores (corretores finais).
- **RF-AP-03** Um agente pode ter vários produtores.
- **RF-AP-04** Um produtor pode trabalhar para um agente ou diretamente para a corretora.
- **RF-AP-05** Comissões da corretora, dos agentes e dos produtores.
- **RF-AP-06** Cálculo de repasses (corretora repassa parte a agentes/produtores).
- **RF-AP-07** Relatórios de comissões e repasses.

### 9.14 Dashboard

- **RF-DASH-01** Dashboard com visão geral e métricas da corretora.
- **RF-DASH-02** Métricas de carteira de clientes, seguros, seguradoras e valores.
- **RF-DASH-03** Insights e diversos gráficos.
- **RF-DASH-04** Gráfico de **funil de negociações/leads** com níveis.

### 9.15 Relatórios

- **RF-RP-01** Menu e tela dedicada a relatórios.
- **RF-RP-02** Exportação em **PDF** (ReportLab/PyPDF) e **CSV**.
- **RF-RP-03** Cobertura de clientes, seguros, seguradoras, apólices, propostas, sinistros, renovações, comissões e carteira.

### 9.16 Inteligência Artificial

- **RF-AI-01** Botão **"resumir com IA"** em: cliente, apólice, sinistro, proposta e negociação.
- **RF-AI-02** Ao clicar, dispara **task Celery** com agente LangChain + LangGraph.
- **RF-AI-03** O agente tem **tools** de acesso aos dados da corretora do usuário, sempre respeitando o tenant.
- **RF-AI-04** O agente gera resumo com insights, salvo em **campo de texto** da entidade.
- **RF-AI-05** Tela de **Chat com IA** no menu lateral.
- **RF-AI-06** Usuário pode criar sessões de chat, salvas por usuário.
- **RF-AI-07** Agente do chat tem tools de acesso à base da corretora.
- **RF-AI-08** Resposta com **streaming** e em **Markdown**.
- **RF-AI-09** Template renderiza Markdown em HTML de forma segura.
- **RF-AI-10** Modelo: **GPT-5.5-mini** via OpenAI.

### 9.17 Notificações Internas

- **RF-NT-01** Ao disparar task de IA, exibir **loading** no botão e aviso de que o usuário será notificado.
- **RF-NT-02** Ao finalizar a task, exibir **notificação na interface** para o usuário.

### 9.18 Admin Django

- **RF-AD-01** Admin permite gestão de todas as entidades.
- **RF-AD-02** Filtros e buscas em listagens.
- **RF-AD-03** Respeita tenant e permissões quando aplicável.

### 9.19 Documentação

- **RF-DC-01** Pasta `docs/` com toda a documentação.
- **RF-DC-02** MKDocs para servir a documentação.
- **RF-DC-03** Suporte a Mermaid.

### 9.20 Dados Fake

- **RF-FK-01** Django command para carga inicial de dados fake.
- **RF-FK-02** Cobre múltiplos cenários e use cases.
- **RF-FK-03** Usa diversas datas diferentes para demonstrações realistas.

---

## 10. Requisitos Não Funcionais

### 10.1 Responsividade

- **RNF-RP-01** Layout responsivo em todas as dimensões de tela.
- **RNF-RP-02** Componentes seguem o design system em `@design_system/design-system.html`.

### 10.2 Performance

- **RNF-PF-01** Nada pesado bloqueia request/response; processos longos vão para Celery.
- **RNF-PF-02** Uso de Redis como cache do app e result backend do Celery.
- **RNF-PF-03** Consultas com `select_related`/`prefetch_related` e índices apropriados.
- **RNF-PF-04** Paginação em listagens.

### 10.3 Segurança

- **RNF-SG-01** Não expor dados sensíveis.
- **RNF-SG-02** Rotas protegidas por autenticação e permissões.
- **RNF-SG-03** Filtros multi-tenant obrigatórios em queries sensíveis.
- **RNF-SG-04** Arquivos privados não expostos publicamente.
- **RNF-SG-05** Secrets de produção não versionados.
- **RNF-SG-06** `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')` em produção.
- **RNF-SG-07** Redirecionamento HTTP → HTTPS via Traefik.
- **RNF-SG-08** `SECURE_REDIRECT_EXEMPT` isenta `/health/` do redirect HTTPS.
- **RNF-SG-09** Traefik confia nas faixas de IP do Cloudflare em `forwardedHeaders trustedIPs`.

### 10.4 Deploy e Resiliência

- **RNF-DR-01** Todos os serviços com `restart_policy` (`condition: on-failure`, `delay`, `max_attempts`, `window`).
- **RNF-DR-02** Todos os serviços com `resources.limits` e `resources.reservations`.
- **RNF-DR-03** App com `update_config` (`order: start-first`, `failure_action: rollback`).
- **RNF-DR-04** Rollback automático em falha de healthcheck.
- **RNF-DR-05** Nenhum serviço em crash-loop por dependência não pronta (entrypoints `wait_for_db` + healthchecks).

### 10.5 Convenções de Código

- **RNF-CC-01** Python > 3.13, Django > 6.0.
- **RNF-CC-02** Um único `settings.py`.
- **RNF-CC-03** `.venv` na raiz do projeto para ambiente local.
- **RNF-CC-04** `requirements.txt` sempre atualizado na raiz.
- **RNF-CC-05** Código em **inglês**; UI em **português brasileiro**.
- **RNF-CC-06** `TIME_ZONE = 'America/Sao_Paulo'`.
- **RNF-CC-07** Variáveis via `.env` na raiz, importadas com `django-environ`.
- **RNF-CC-08** `.env` gitignored; `.env` de produção separado do de desenvolvimento.
- **RNF-CC-09** Listas separadas por vírgula (ex.: `ALLOWED_HOSTS`).
- **RNF-CC-10** Login por email; autenticação nativa do Django.
- **RNF-CC-11** Preferir recursos nativos do Django e **Class Based Views**.
- **RNF-CC-12** Sem testes automatizados.
- **RNF-CC-13** Código simples, legível, **PEP8** e **aspas simples**.
- **RNF-CC-14** Toda tabela/model com `created_at` e `updated_at`.
- **RNF-CC-15** Signals em `signals.py` dentro da app correspondente.

---

## 11. Arquitetura Técnica

### 11.1 Visão geral

```
[Cloudflare DNS] -> [Traefik (TLS wildcard)] -> [Django app (gunicorn/daphne)]
                                                         |
                       +---------------------------------+--------------------------------+
                       |                                 |                                |
            [PostgreSQL] (internal)         [Redis] (internal, cache+result)   [RabbitMQ] (internal, broker)
                                                         |
                                              [Celery worker + beat]
                                                         |
                                            [OpenAI via rede eress]
```

### 11.2 Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python > 3.13 |
| Framework web | Django > 6.0 (único `settings.py`) |
| Banco | PostgreSQL |
| Cache/Result backend | Redis |
| Broker | RabbitMQ |
| Tarefas assíncronas | Celery |
| IA | LangChain > 1.0 + LangGraph + OpenAI GPT-5.5-mini |
| Relatórios | ReportLab, PyPDF |
| Env | django-environ |
| Estáticos | WhiteNoise (`CompressedStaticFilesStorage`) |
| Admin tasks view | dj-celery-panel |
| Web server/LB | Traefik |
| DNS/TLS | Cloudflare + Let's Encrypt DNS-01 |
| Container local | Docker Compose |
| Container produção | Docker Swarm |
| Registry | GHCR (`ghcr.io/pycodebr/scsi_v1`) |
| Docs | MKDocs + Mermaid |

### 11.3 Serviços Docker obrigatórios

- `app` (Django)
- `db` (PostgreSQL)
- `celery_worker`
- `celery_beat`
- `rabbitmq`
- `redis`
- `traefik`

### 11.4 Entrypoints

- **app**: `wait_for_db` → `migrate` (com **advisory lock**) → `collectstatic --clear` → `runserver`/`gunicorn`.
- **celery_worker/celery_beat**: `wait_for_db` apenas. **Nunca** rodam migrations nem collectstatic.

### 11.5 Settings essenciais (resumo)

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` via `.env`.
- `DATABASES` via `.env`.
- `CACHES` (Redis) via `.env`.
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` via `.env`.
- `EMAIL_*` via `.env`.
- `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-5.5-mini` via `.env`.
- `SECURE_PROXY_SSL_HEADER`, `SECURE_REDIRECT_EXEMPT` em produção.
- `TIME_ZONE = 'America/Sao_Paulo'`.
- `LANGUAGE_CODE = 'pt-br'`.
- `AUTH_USER_MODEL = 'core.User'`.

---

## 12. Arquitetura Multi-Tenant Compartilhada

### 12.1 Princípios

- **Arquitetura compartilhada**: **não** usar schemas separados por tenant; **não** usar bancos separados.
- Isolamento via **campo-chave** (`brokerage_id` / `brokerage FK`) em todos os models de domínio.
- Filtros obrigatórios em queries, permissões e middlewares.

### 12.2 Implementação

- Toda entidade de negócio herda de uma `BaseTenantModel` em `base` com `brokerage = ForeignKey('core.Brokerage')`.
- **TenantMiddleware** resolve a corretora a partir do `request.user.brokerage` e a disponibiliza em `request.tenant`.
- **QuerySet** customizado (`TenantQuerySet`) filtra automaticamente por `brokerage` quando o tenant está no contexto.
- **Managers** (`TenantManager`) aplicam o filtro por padrão.
- **Permissões** (`DjangoModelPermissions` + checagens customizadas) validam que o objeto pertence à corretora do usuário.
- **Arquivos/media** são protegidos por view segura que valida `brokerage` + permissão.
- Usuários só veem dados da própria corretora — **jamais** de outra.

### 12.3 Admin multi-tenant

- `AdminSite` customizado sobrescreve `get_queryset` para filtrar por `request.user.brokerage`.
- `scsi_staff` com permissão especial pode ver dados de outras corretoras (apenas interno, auditado).

---

## 13. Segurança, Permissões e Isolamento de Dados

### 13.1 Autenticação

- Login por **email** (`AUTH_USER_MODEL = 'core.User'`, campo `USERNAME_FIELD = 'email'`).
- Senhas via sistema nativo do Django (`AbstractUser` adaptado).
- Recuperação de senha via email nativo do Django.

### 13.2 Autorização

- `Group` por perfil: `brokerage_admin`, `brokerage_agent`, `brokerage_producer`, `brokerage_backoffice`, `scsi_staff`.
- Permissões customizadas por model quando necessário.
- Mixins de views (CBV) para checar `brokerage` do objeto vs `brokerage` do usuário.

### 13.3 Isolamento

- `TenantMiddleware` + `TenantQuerySet` garantem escopo por corretora.
- Views que tratam objetos sempre chamam `get_object_or_404(Model.objects.for_tenant(request.tenant), pk=...)`.
- API de IA sempre recebe `tenant_id` do `request.user.brokerage`; tools nunca aceitam `brokerage_id` arbitrário do cliente.

### 13.4 HTTP/HTTPS

- TLS terminado no Traefik.
- `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')`.
- `SECURE_REDIRECT_EXEMPT = [r'^/health/?$']`.
- Traefik confia em IPs do Cloudflare (`forwardedHeaders.trustedIPs`).
- Traefik redireciona HTTP → HTTPS.

### 13.5 Secrets

- `.env` gitignored; produção e desenvolvimento separados.
- Em produção, preferir **Docker Secrets** para credenciais sensíveis (ex.: `CLOUDFLARE_DNS_API_TOKEN`, `POSTGRES_PASSWORD`, `SECRET_KEY`, `OPENAI_API_KEY`).
- Nenhum secret em texto puro em compose/stack versionados.
- `env_file` é lido diretamente pelo Docker (sem shell).
- Scripts que precisam ler `.env` usam **parser seguro de KEY=VALUE** (não `source` nem `.`).

### 13.6 Hardening adicional

- `DEBUG=False` em produção (validado pelo `deploy.sh`).
- `ALLOWED_HOSTS` com `localhost`/`127.0.0.1` para healthcheck interno.
- CSRF com `CSRF_TRUSTED_ORIGINS` em `https://` com wildcard de subdomínio.
- Headers de segurança: `SECURE_HSTS_SECONDS`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS = 'DENY'`.
- Arquivos estáticos servidos via WhiteNoise.

---

## 14. Proteção de Arquivos e Media Privada

### 14.1 Princípios

- Media **não** é exposta publicamente.
- Arquivos só podem ser acessados por usuários autenticados, da corretora correta e com permissão adequada.

### 14.2 Implementação

- `MEDIA_ROOT` em volume nomeado; `MEDIA_URL` aponta para rota interna (ex.: `/media/`).
- **`PrivateMediaView`** (CBV) verifica autenticação, `request.user.brokerage` e permissão antes de servir o arquivo.
- Serviço de arquivo via Django (não via Traefik diretamente) para permitir validação.
- Em produção, se necessário, `X-Accel-Redirect`/`X-Sendfile` pode ser usado para offload eficiente, mantendo a validação no Django.
- Tipos permitidos validados por extensão/MIME no upload.
- Tamanho máximo de upload configurável via `.env`.

### 14.3 Modelos de anexos

- `Attachment` genérico com `content_type` + `object_id` (GenericFK) **ou** FKs específicas por entidade — decisão de implementação respeitando `brokerage`.
- Cada anexo sempre carrega `brokerage` para filtro rápido.
- Validação: o `brokerage` do anexo deve coincidir com o `brokerage` do objeto pai.

---

## 15. Apps Django Recomendados

Apps na **raiz do projeto**. App principal = `core`. App de recursos compartilhados = `base`.

| App | Responsabilidade |
|---|---|
| `core` | App principal: projeto Django, `settings.py`, `urls.py`, `wsgi.py`/`asgi.py`, `User` customizado, `Brokerage`, `Plan`, middlewares de tenant, entrypoints. |
| `base` | Recursos compartilhados: `BaseTenantModel`, `TenantManager`/`TenantQuerySet`, mixins de views, helpers de permissão, form mixins, decorators, utils de Markdown seguro, utils de PDF/CSV. |
| `onboarding` | Landing page, cadastro de corretora, escolha de plano. |
| `clients` | Clientes e anexos de clientes. |
| `catalog` | Seguradoras, ramos, coberturas. |
| `proposals` | Propostas de seguro e itens cobertos de propostas. |
| `policies` | Apólices, itens cobertos de apólices, endossos, renovações. |
| `claims` | Sinistros e anexos de sinistros. |
| `attachments` | Lógica genérica de anexos privados (media segura). |
| `crm` | Negociações, pipeline, etapas, Kanban, grid. |
| `commercial` | Agentes, produtores, comissões e repasses. |
| `reports` | Geração de PDF/CSV e telas de relatórios. |
| `dashboard` | Dashboard, métricas, gráficos, funil. |
| `ai` | Agentes LangChain/LangGraph, tools, tasks Celery, chat, resumos. |
| `notifications` | Notificações internas na interface. |

> Cada app segue a convenção: `models.py`, `views.py`, `urls.py`, `admin.py`, `forms.py`, `signals.py` (quando aplicável), `services.py`, `migrations/`.

---

## 16. Modelagem Inicial de Domínio

> Convenção: toda tabela/model tem `created_at` e `updated_at`. Models de domínio herdam de `BaseTenantModel` (com `brokerage`). Nomes em inglês; labels/verbose em pt-br quando aplicável.

### 16.1 `core`

- **`Brokerage`** (tenant): `name`, `legal_name` (Razão Social, obrigatório), `cnpj` (obrigatório, único), `email`, `phone`, `address`, `plan` (FK para `Plan`), `created_at`, `updated_at`.
- **`Plan`**: `code` (`free`, `pro`, `business`...), `name`, `description`, `is_active`, `is_available` (apenas `free` = `True` inicialmente), `created_at`, `updated_at`.
- **`User`** (`AbstractUser` adaptado): `email` (único, `USERNAME_FIELD`), `brokerage` (FK), `role`/`groups`, `is_active`, `created_at`, `updated_at`. Sem `username`.

### 16.2 `base`

- **`BaseTenantModel`** (abstract): `brokerage` (FK), `created_at`, `updated_at`.
- **`TimeStampedModel`** (abstract): `created_at`, `updated_at` (para models não tenant, ex.: `Plan`).
- **`TenantQuerySet`** / **`TenantManager`**: filtros automáticos por `brokerage`.

### 16.3 `clients`

- **`Client`**: `brokerage`, `first_name`, `last_name`, `document` (CPF/CNPJ), `email`, `phone`, `birth_date`, `address`, `notes`, `ai_summary` (text, nullable), `created_at`, `updated_at`.

### 16.4 `catalog`

- **`InsuranceCompany`**: `brokerage`, `name`, `code`, `document`, `contact`, `created_at`, `updated_at`.
- **`Branch`**: `brokerage`, `name` (auto, residencial, vida, viagem, empresarial, frota, outros), `description`, `created_at`, `updated_at`.
- **`Coverage`**: `brokerage`, `branch` (FK), `name`, `description`, `created_at`, `updated_at`.

### 16.5 `proposals`

- **`Proposal`**: `brokerage`, `client` (FK), `insurance_company` (FK), `branch` (FK), `producer` (FK, nullable), `status`, `valid_until`, `premium`, `notes`, `ai_summary`, `created_at`, `updated_at`.
- **`ProposalCoveredItem`**: `brokerage`, `proposal` (FK), `kind` (auto, casa, frota, viagem, vida, empresarial), `description`, `value`, `attributes` (JSON), `created_at`, `updated_at`.

### 16.6 `policies`

- **`Policy`**: `brokerage`, `proposal` (FK, nullable), `client` (FK), `insurance_company` (FK), `branch` (FK), `number`, `start_date`, `end_date`, `premium`, `status`, `ai_summary`, `created_at`, `updated_at`.
- **`PolicyCoveredItem`**: `brokerage`, `policy` (FK), `kind`, `description`, `value`, `attributes` (JSON), `created_at`, `updated_at`.
- **`Endorsement`**: `brokerage`, `policy` (FK), `number`, `type`, `description`, `effective_date`, `created_at`, `updated_at`.
- **`Renewal`**: `brokerage`, `policy` (FK), `due_date`, `status`, `notes`, `created_at`, `updated_at`.

### 16.7 `claims`

- **`Claim`**: `brokerage`, `policy` (FK), `covered_item` (FK → `PolicyCoveredItem`), `client` (FK), `number`, `occurrence_date`, `description`, `status`, `amount`, `ai_summary`, `created_at`, `updated_at`.

### 16.8 `attachments`

- **`Attachment`**: `brokerage`, `content_type` (FK), `object_id`, `file` (FileField privada), `name`, `mime`, `size`, `created_at`, `updated_at`.
  - Sempre valida `brokerage` do objeto pai.

### 16.9 `crm`

- **`Pipeline`**: `brokerage`, `name`, `created_at`, `updated_at`.
- **`PipelineStage`**: `brokerage`, `pipeline` (FK), `name`, `color`, `order`, `created_at`, `updated_at`.
- **`Deal`**: `brokerage`, `client` (FK), `stage` (FK), `producer` (FK, nullable), `title`, `amount`, `expected_close_date`, `status`, `ai_summary`, `created_at`, `updated_at`.

### 16.10 `commercial`

- **`Agent`**: `brokerage`, `name`, `document`, `type` (person/company), `commission_percent`, `contact`, `created_at`, `updated_at`.
- **`Producer`**: `brokerage`, `agent` (FK, nullable), `name`, `document`, `commission_percent`, `contact`, `created_at`, `updated_at`.
- **`Commission`**: `brokerage`, `policy` (FK, nullable), `proposal` (FK, nullable), `amount`, `brokerage_share`, `agent_share`, `producer_share`, `created_at`, `updated_at`.

### 16.11 `ai`

- **`ChatSession`**: `brokerage`, `user` (FK), `title`, `created_at`, `updated_at`.
- **`ChatMessage`**: `session` (FK), `role` (user/assistant), `content` (Markdown), `created_at`, `updated_at`.
- **`AISummaryJob`** (controle de tasks): `brokerage`, `user` (FK), `content_type`, `object_id`, `status` (pending/running/done/failed), `result`, `created_at`, `updated_at`.

### 16.12 `notifications`

- **`Notification`**: `brokerage`, `user` (FK), `title`, `message`, `link`, `is_read`, `created_at`, `updated_at`.

---

## 17. Fluxos Principais do Sistema

### 17.1 Onboarding

1. Usuário acessa `scsi.digital`.
2. Clica em **Criar conta**.
3. Preenche dados da corretora (CNPJ + Razão Social obrigatórios) + dados do usuário admin.
4. Escolhe plano `free`.
5. Sistema cria `Brokerage` + `User` admin vinculado.
6. Redireciona para dashboard.

### 17.2 Venda (proposta → apólice)

1. Criar cliente.
2. Criar proposta vinculada a cliente, seguradora e ramo.
3. Adicionar **itens cobertos** à proposta.
4. Ao aceitar, clicar em **"gerar apólice"**.
5. Sistema cria `Policy` + copia `ProposalCoveredItem` → `PolicyCoveredItem`.
6. Apólice disponível para endossos, renovações e sinistros.

### 17.3 Sinistro

1. Selecionar apólice.
2. Selecionar **item coberto** da apólice.
3. Criar sinistro com dados da ocorrência.
4. Anexar documentos.
5. Opcionalmente **resumir com IA**.

### 17.4 Resumo com IA

1. Usuário abre detalhe da entidade.
2. Clica em **"Resumir com IA"**.
3. Frontend exibe loading no botão e aviso de notificação.
4. Backend dispara task Celery → agente LangChain/LangGraph → tools de leitura no tenant.
5. Resultado salvo em `ai_summary` da entidade.
6. Notificação interna criada para o usuário.
7. Interface atualiza/exibe o resumo.

### 17.5 Chat com IA

1. Usuário abre **Chat com IA** no menu lateral.
2. Cria/retoma sessão (`ChatSession`).
3. Envia mensagem → streaming → resposta em Markdown renderizada.
4. Agente usa tools de leitura no tenant para responder.

### 17.6 Renovação

1. Apólice próxima do vencimento.
2. Sistema lista em renovações com status.
3. Usuário atualiza status e gera relatório/alerta.

### 17.7 CRM Kanban

1. Usuário cria pipeline e etapas com cores.
2. Cria negociações (`Deal`) e arrasta entre etapas.
3. Resumo com IA disponível na negociação.

---

## 18. Dashboard e Métricas

### 18.1 Visão geral

- Dashboard único por corretora com cards de métricas, gráficos e insights.

### 18.2 Métricas

- Total de clientes (e evolução).
- Total de apólices vigentes e premium total.
- Propostas por status.
- Sinistros por status e valor médio.
- Renovações próximas (30/60/90 dias).
- Comissões totais e repasses.
- Seguradoras por volume de apólices.
- Ramos por distribuição.

### 18.3 Gráficos

- Barras/linhas de evolução de apólices e premium.
- Pizza de distribuição por ramo.
- Pizza de sinistros por status.
- **Funil de negociações/leads** com níveis (estágios do pipeline).

### 18.4 Insights

- Mini-textos/avisos: "X renovações nos próximos 30 dias", "Y sinistros abertos", "Z propostas sem follow-up há 7 dias".

---

## 19. CRM, Pipeline e Kanban

### 19.1 Pipeline

- Cada corretora tem um `Pipeline` com `PipelineStage`s.
- Etapas com **nome** e **cor** personalizáveis e ordenadas.
- Pipeline padrão sugerido: Lead → Contato → Proposta → Negociação → Fechado/Ganho, Fechado/Perdido.

### 19.2 Visualizações

- **Grid**: tabela com colunas principais, filtros e ordenação.
- **Kanban**: colunas por etapa, cards arrastáveis (drag-and-drop via JS), badge de valor, cliente e responsável.

### 19.3 Negociação (Deal)

- Campos: cliente, etapa, produtor, título, valor, data prevista de fechamento, status, resumo IA.
- Permite **resumir com IA**.
- Histórico de mudanças de etapa.

---

## 20. Propostas, Apólices, Itens Cobertos e Sinistros

### 20.1 Propostas

- CRUD completo.
- Status: rascunho, enviada, aceita, recusada, expirada.
- Itens cobertos (1:N).
- Anexos.
- Resumo IA.

### 20.2 Geração de apólice

- Botão **"Gerar apólice"** na proposta (status aceita).
- Cria `Policy` com dados da proposta + copia itens cobertos para `PolicyCoveredItem`.
- Define número de apólice (formato configurável por corretora).
- Mantém vínculo `proposal` na apólice.

### 20.3 Apólices

- CRUD completo.
- Itens cobertos (1:N).
- Endossos (1:N).
- Renovações (1:N).
- Resumo IA.

### 20.4 Itens cobertos

- Objeto segurado: auto, casa, frota, viagem, vida, empresarial.
- Atributos flexíveis em JSON (placa, endereço, lista de itens, destino, etc.).

### 20.5 Sinistros

- Sempre vinculado a `Policy` + `PolicyCoveredItem`.
- Status: aberto, em análise, aprovado, recusado, pago.
- Anexos.
- Resumo IA.

---

## 21. Agentes, Produtores e Comissões

### 21.1 Hierarquia

```
Brokerage
 ├── Agent (pessoa ou empresa parceira)
 │    ├── Producer (corretor final)
 ├── Producer (direto da corretora, sem agente)
```

### 21.2 Regras

- Agente: pessoa ou empresa que vende para a corretora.
- Produtor: corretor final, pode trabalhar para um agente ou diretamente para a corretora.
- Um agente pode ter vários produtores.
- Comissão é paga para a corretora; corretora repassa a agentes e produtores.

### 21.3 Comissões e repasses

- `Commission` registra valor total, `brokerage_share`, `agent_share`, `producer_share`.
- Cálculo automatizado a partir de percentuais configurados no agente/produtor/corretora.
- Relatórios por período, por agente, por produtor, por apólice.

---

## 22. Inteligência Artificial no Sistema

### 22.1 Stack de IA

- LangChain > 1.0 + LangGraph.
- Modelo: **GPT-5.5-mini** via OpenAI.
- Tools de leitura de dados por tenant.
- Tasks executadas em Celery (resumos) e streaming (chat).

### 22.2 Resumos com IA

- Entidades: `Client`, `Policy`, `Claim`, `Proposal`, `Deal`.
- Fluxo: botão → task Celery → agente com tools → resultado salvo em `ai_summary` → notificação.
- Tools sempre filtram por `request.user.brokerage` / `tenant_id` do contexto da task.
- Loading no botão + aviso ao usuário.

### 22.3 Chat com IA

- Menu lateral **Chat com IA**.
- Sessões salvas por usuário (`ChatSession` + `ChatMessage`).
- Tools de leitura no tenant.
- Streaming via SSE/WebSocket.
- Resposta em **Markdown**; template renderiza Markdown em HTML de forma segura (sanitização).
- Histórico persistido por sessão.

### 22.4 Segurança da IA

- Tools **nunca** aceitam `brokerage_id` arbitrário do cliente.
- O `tenant_id` é sempre derivado do usuário autenticado ou do contexto da task.
- Nenhum dado de outra corretora pode aparecer em respostas.
- Logs de uso de IA por usuário e corretora para auditoria.

---

## 23. Tarefas Assíncronas, Celery, RabbitMQ e Redis

### 23.1 Broker e result backend

- Broker: **RabbitMQ**.
- Result backend: **Redis**.
- Cache do app: **Redis**.

### 23.2 Tarefas

- `summarize_entity(content_type, object_id, tenant_id, user_id)` → IA resumos.
- `chat_stream(...)` → streaming de chat (quando aplicável via backend).
- Tarefas periódicas via **Celery Beat** (ex.: alertas de renovação, limpeza de jobs antigos).

### 23.3 Visualização

- **dj-celery-panel** no admin do Django para inspeção de tasks.

### 23.4 UX de tasks

- Botão com loading ao disparar.
- Aviso: "Você será notificado quando a análise ficar pronta."
- Notificação interna ao concluir.

### 23.5 Isolamento de redes

- `celery_worker` e `celery_beat` em `scsi_v1_internal` e `scsi_v1_egress` (egress para OpenAI).
- **Nunca** em `traefik_public`.

---

## 24. Relatórios, PDF e CSV

### 24.1 Stack

- **ReportLab** + **PyPDF** para PDF.
- CSV via `csv` nativo do Python/Django `StreamingHttpResponse`.

### 24.2 Tela

- Menu dedicado **Relatórios**.
- Tela dedicada com filtros por período, seguradora, ramo, produtor, status.

### 24.3 Relatórios

- Clientes (carteira).
- Seguros/Apólices (vigentes, vencidas, canceladas).
- Seguradoras (volume e premium).
- Propostas (conversão).
- Sinistros (status, valor médio, tempo médio).
- Renovações (próximos vencimentos, status).
- Comissões e repasses (por agente/produtor).
- Carteira consolidada.

### 24.4 Exportação

- Botões **PDF** e **CSV** em cada relatório.
- PDF com cabeçalho da corretora, filtros aplicados e rodapé com data/hora.
- CSV com cabeçalho de colunas e encoding UTF-8 com BOM para Excel-pt-br.

---

## 25. Landing Page, Cadastro e Planos

### 25.1 Landing page

- Rota raiz `/` em `scsi.digital`.
- Apresenta o sistema, benefícios e CTA para **Criar conta** e **Login**.
- Seção de planos.

### 25.2 Cadastro de corretora

- Formulário com: CNPJ (obrigatório), Razão Social (obrigatório), email, telefone, endereço (opcional) + dados do usuário admin.
- Validação de CNPJ único.
- Cria `Brokerage` + `User` admin + `Plan` `free`.

### 25.3 Planos

- Planos fictícios exibidos: `free`, `pro`, `business` (exemplo).
- Apenas `free` habilitado (`Plan.is_available=True`).
- Demais com botão **"em breve"** desabilitado.
- **Sem** integração com gateway de pagamentos.

---

## 26. Admin Django

### 26.1 Cobertura

- Gestão de todas as entidades do sistema.

### 26.2 Recursos

- Listas com **filtros** (`list_filter`) e **buscas** (`search_fields`).
- `raw_id_fields` / `autocomplete` para FKs grandes.
- `date_hierarchy` onde aplicável.
- `dj-celery-panel` para tasks.

### 26.3 Multi-tenant no admin

- `get_queryset(self, request)` filtra por `request.user.brokerage`.
- `scsi_staff` pode ver todos (superuser interno, auditado).
- `save_model` força `brokerage` do usuário quando aplicável.

---

## 27. Design System e UI/UX

### 27.1 Referência

- Design system em `@design_system/design-system.html`.
- Cores, componentes, tipografias e tokens **rigorosamente** seguidos.

### 27.2 Princípios

- Responsividade em todas as dimensões.
- Contraste adequado entre elementos, fontes e fundos.
- Feedback visual para ações assíncronas (loading, toasts, badges).
- Jornadas fluidas (onboarding, venda, sinistro, CRM, IA).

### 27.3 Componentes

- Tabelas com filtros/paginação.
- Formulários com validação inline.
- Kanban com drag-and-drop.
- Cards de métricas e gráficos.
- Modal/drawer para detalhes.
- Toasts/notificações internas.
- Botão "Resumir com IA" padronizado.

### 27.4 Markdown

- Renderização de Markdown em HTML de forma segura (sanitização) para respostas de IA e resumos.

---

## 28. Documentação com MKDocs

- Pasta `docs/` com toda a documentação (PRD, arquitetura, deploy, etc.).
- **MKDocs** para servir online.
- Suporte a **Mermaid** para diagramas.
- Mantida atualizada a cada entrega.

---

## 29. Dados Fake para Demonstração

- Django command: `python manage.py load_fake_data`.
- Cobre múltiplos cenários:
  - Múltiplas corretoras (para validar isolamento).
  - Clientes, seguradoras, ramos, propostas, apólices, sinistros, renovações, endossos.
  - Pipeline e negociações em várias etapas.
  - Agentes, produtores e comissões.
  - Datas variadas (passado, presente, futuro) para relatórios e renovações.
- Objetivo: demonstrações realistas sem dados reais.

---

## 30. Estrutura Recomendada de Pastas

```
SCSI/
├── .env                       # gitignored (desenvolvimento)
├── .env.example               # exemplo versionado
├── .gitignore
├── .venv/                     # ambiente virtual local
├── requirements.txt
├── manage.py
├── docker-compose.yml         # desenvolvimento local
├── docker-compose.prod.yml    # base para stack (referência)
├── stack.yml                  # Docker Swarm (produção)
├── Dockerfile
├── entrypoint.sh              # app: wait_for_db + migrate + collectstatic
├── entrypoint.celery.sh       # celery: wait_for_db apenas
├── mkdocs.yml
├── docs/
│   ├── PRD.md
│   ├── arquitetura.md
│   ├── deploy.md
│   └── ...
├── scripts/
│   ├── deploy.sh
│   └── backup.sh
├── design_system/
│   └── design-system.html
├── core/                      # app principal
│   ├── settings.py            # único settings
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── models.py              # User, Brokerage, Plan
│   ├── middlewares.py         # TenantMiddleware
│   ├── management/
│   │   └── commands/
│   │       ├── wait_for_db.py
│   │       └── load_fake_data.py
│   └── ...
├── base/                      # recursos compartilhados
│   ├── models.py              # BaseTenantModel, TimeStampedModel
│   ├── managers.py            # TenantManager, TenantQuerySet
│   ├── views.py               # mixins CBV
│   ├── permissions.py
│   ├── utils.py               # markdown seguro, pdf/csv helpers
│   └── ...
├── onboarding/
├── clients/
├── catalog/
├── proposals/
├── policies/
├── claims/
├── attachments/
├── crm/
├── commercial/
├── reports/
├── dashboard/
├── ai/
└── notifications/
```

---

## 31. Configuração Local com Docker Compose

### 31.1 Serviços locais

- `app` (Django)
- `db` (PostgreSQL)
- `celery_worker`
- `celery_beat`
- `rabbitmq`
- `redis`
- `traefik` (quando aplicável ao ambiente local)

### 31.2 Rede local

- Rede bridge única para desenvolvimento (simples).
- Em local, o Traefik é opcional; pode-se usar `runserver` direto.

### 31.3 `.env` de desenvolvimento

- Variáveis de DB, Redis, RabbitMQ, OpenAI, email, etc.
- `DEBUG=True` em desenvolvimento.

### 31.4 Comandos

```bash
# subir ambiente
docker compose up -d --build

# migrations (ou via entrypoint)
docker compose exec app python manage.py migrate

# dados fake
docker compose exec app python manage.py load_fake_data

# logs
docker compose logs -f app
docker compose logs -f celery_worker
```

---

## 32. Deploy em Produção com Docker Swarm

### 32.1 Princípios

- **Docker Swarm** em VPS Ubuntu.
- Imagem publicada no GHCR: `ghcr.io/pycodebr/scsi_v1`.
- `docker stack deploy --with-registry-auth`.
- Volumes nomeados: `postgres`, `redis`, `rabbitmq`, `media`, `staticfiles`, `letsencrypt`.
- Traefik em rede externa `traefik_public`.
- TLS wildcard via Let's Encrypt **DNS-01** com Cloudflare.

### 32.2 Serviços

- `app`, `db`, `celery_worker`, `celery_beat`, `rabbitmq`, `redis`, `traefik`.

### 32.3 Volumes

- `scsi_v1_postgres`
- `scsi_v1_redis`
- `scsi_v1_rabbitmq`
- `scsi_v1_media`
- `scsi_v1_staticfiles`
- `scsi_v1_letsencrypt`

### 32.4 Imagem

- Build local ou CI → `docker tag` → `docker push ghcr.io/pycodebr/scsi_v1:latest` (e tags de versão).
- Stack referencia `ghcr.io/pycodebr/scsi_v1:latest`.

### 32.5 Update/rollback

- `app`: `update_config.order = start-first`, `failure_action = rollback`.
- Healthcheck garante que a réplica nova fique saudável antes de derrubar a antiga.

---

## 33. Guia Completo de Deploy em VPS Ubuntu do Zero

> Substitua os placeholders `<...>` por valores reais. Nunca commit segredos.

### 33.1 Acessar a VPS

```bash
ssh root@<VPS_IP>
# ou usuário com sudo
ssh <user>@<VPS_IP>
```

### 33.2 Atualizar pacotes do Ubuntu

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release ufw fail2ban
```

### 33.3 Configurar firewall básico

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 33.4 Instalar Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 33.5 Habilitar e iniciar Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
docker --version
docker info
```

### 33.6 Fazer login no GHCR

```bash
echo "<GHCR_TOKEN>" | docker login ghcr.io -u <GHCR_USER> --password-stdin
```

### 33.7 Inicializar Docker Swarm

```bash
docker swarm init
```

### 33.8 Criar redes overlay

```bash
docker network create --driver overlay --attachable traefik_public
docker network create --driver overlay --internal scsi_v1_internal
docker network create --driver overlay scsi_v1_egress
```

### 33.9 Criar token de API no Cloudflare

- Painel Cloudflare → My Profile → API Tokens → Create Token.
- Permissão: **Zone > DNS > Edit**.
- Zona: **scsi.digital**.
- Copiar o token (placeholder: `<CLOUDFLARE_TOKEN>`).

### 33.10 Criar Docker Secrets

```bash
printf '<CLOUDFLARE_TOKEN>' | docker secret create CLOUDFLARE_DNS_API_TOKEN -
printf '<POSTGRES_PASSWORD>' | docker secret create POSTGRES_PASSWORD -
printf '<SECRET_KEY>'        | docker secret create SECRET_KEY -
printf '<OPENAI_API_KEY>'    | docker secret create OPENAI_API_KEY -
```

### 33.11 Criar demais secrets sensíveis

```bash
printf '<RABBITMQ_PASSWORD>' | docker secret create RABBITMQ_PASSWORD -
printf '<REDIS_PASSWORD>'    | docker secret create REDIS_PASSWORD -
# demais conforme necessário
```

### 33.12 Configurar `.env` de produção

```bash
sudo mkdir -p /opt/scsi
sudo nano /opt/scsi/.env
# cole as variáveis (sem segredos que viram secrets)
```

Exemplo de `.env` de produção (valores não secretos; sensíveis via Docker Secrets):

```env
DJANGO_SETTINGS_MODULE=core.settings
DEBUG=False
ALLOWED_HOSTS=scsi.digital,.scsi.digital,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://scsi.digital,https://*.scsi.digital
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# DB (valores não secretos; senha via secret)
POSTGRES_DB=scsi
POSTGRES_USER=scsi
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Cache/Broker
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=scsi

# OpenAI
OPENAI_MODEL=gpt-5.5-mini

# Email
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=...
```

### 33.13 Garantir DEBUG=False

- Validar no `.env`: `DEBUG=False`.

### 33.14 Configurar ALLOWED_HOSTS

```env
ALLOWED_HOSTS=scsi.digital,.scsi.digital,localhost,127.0.0.1
```

### 33.15 Configurar CSRF_TRUSTED_ORIGINS

```env
CSRF_TRUSTED_ORIGINS=https://scsi.digital,https://*.scsi.digital
```

### 33.16 Configurar Cloudflare

- DNS da zona `scsi.digital`:
  - `A`/`AAAA` `@` → `<VPS_IP>` (Proxied).
  - `A`/`AAAA` `*` → `<VPS_IP>` (Proxied) para wildcard.
- SSL/TLS: Full (Strict) ou Full.
- Origin Server Certificate opcional; o TLS é terminado no Traefik via Let's Encrypt.

### 33.17 Configurar Traefik com DNS-01

- Traefik exposto na `traefik_public`.
- `certificatesResolvers.le.acme.dnsChallenge.provider=cloudflare`.
- `CF_DNS_API_TOKEN_FILE=/run/secrets/CLOUDFLARE_DNS_API_TOKEN`.
- `acme.email=<ADMIN_EMAIL>`.
- `acme.storage=/letsencrypt/acme.json`.
- `acme.dnsChallenge.delayBeforeCheck=30` (ou similar).
- Wildcard: `*.scsi.digital` + `scsi.digital`.
- Redirecionar HTTP → HTTPS.
- `entryPoints.websecure.address=:443`, `entryPoints.web.address=:80`.
- `forwardedHeaders.trustedIPs` com faixas do Cloudflare.

### 33.18 Build e push da imagem

```bash
cd /opt/scsi
sudo git pull
sudo docker build -t ghcr.io/pycodebr/scsi_v1:latest .
sudo docker push ghcr.io/pycodebr/scsi_v1:latest
```

### 33.19 Deploy do stack

```bash
sudo docker stack deploy -c stack.yml --with-registry-auth scsi_v1
```

### 33.20 Verificar serviços

```bash
sudo docker service ls
sudo docker stack services scsi_v1
```

### 33.21 Verificar logs

```bash
sudo docker service logs scsi_v1_app --tail=100 -f
sudo docker service logs scsi_v1_celery_worker --tail=100 -f
sudo docker service logs scsi_v1_traefik --tail=100 -f
```

### 33.22 Verificar healthcheck do app

```bash
curl -fsS http://localhost/health/ && echo OK
# ou de fora (quando HTTPS já ativo):
curl -fsS https://scsi.digital/health/ && echo OK
```

### 33.23 Verificar emissão do certificado wildcard

```bash
sudo docker service logs scsi_v1_traefik 2>&1 | grep -i "acme\|certificate\|letsencrypt"
```

### 33.24 Validar HTTPS em scsi.digital

```bash
curl -I https://scsi.digital/
curl -I https://www.scsi.digital/
```

### 33.25 Usar `scripts/deploy.sh`

```bash
sudo bash scripts/deploy.sh
```

### 33.26 Usar `scripts/deploy.sh --skip-build`

```bash
sudo bash scripts/deploy.sh --skip-build
```

### 33.27 Usar `scripts/backup.sh`

```bash
sudo bash scripts/backup.sh
```

### 33.28 Restaurar backup (alto nível)

1. Parar serviços de app/celery (`docker service scale scsi_v1_app=0`).
2. Restaurar dump PostgreSQL com `pg_restore` a partir do arquivo de backup.
3. Restaurar pasta de media a partir do tarball de backup.
4. Reiniciar serviços (`docker service scale scsi_v1_app=1`).
5. Validar healthcheck e dados.

---

## 34. Scripts de Deploy e Backup

### 34.1 `scripts/deploy.sh`

Responsabilidades:

- Carregar `.env` com **parser seguro de KEY=VALUE** (sem `source`/`.`).
- Validar pré-condições.
- Validar que Swarm está ativo (`docker info` com `Swarm.active`).
- Validar que o secret `CLOUDFLARE_DNS_API_TOKEN` existe (`docker secret inspect`).
- Validar redes overlay `traefik_public` e `scsi_v1_egress` (`docker network inspect`).
- Validar `DEBUG=False`.
- Validar `localhost` em `ALLOWED_HOSTS`.
- `git pull`.
- Build da imagem (a menos que `--skip-build`).
- Push da imagem para `ghcr.io/pycodebr/scsi_v1`.
- `docker stack deploy -c stack.yml --with-registry-auth scsi_v1`.
- Forçar rollout de `app`, `celery_worker` e `celery_beat` (`docker service update --force`).
- Modo `--skip-build` para redeploy de configuração sem rebuild.

Fluxo de parser seguro (exemplo conceitual, sem `source`):

```bash
# Lê .env linha a linha, ignora comentários, faz export KEY=VALUE
set -a
while IFS='=' read -r key value; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  export "$key=$value"
done < /opt/scsi/.env
set +a
```

### 34.2 `scripts/backup.sh`

Responsabilidades:

- Backup do PostgreSQL via `pg_dump` (do container `db` ou via sidecar).
- Backup da media (tar do volume `scsi_v1_media`).
- Rotação por tempo (ex.: manter 7 diários, 4 semanais, 12 mensais).
- Adequado para cron (idempotente, com log e código de saída).
- Saída em `/opt/scsi/backups/` (ou volume dedicado).

---

## 35. Healthchecks, Rollout, Rollback e Resiliência

### 35.1 Endpoint `/health/`

- Rota: `/health/`.
- Retorna HTTP 200.
- **Não acessa banco.**
- **Não exige autenticação.**
- Usado pelo `HEALTHCHECK` do container e pelo Traefik.

### 35.2 Healthchecks por serviço

| Serviço | Healthcheck |
|---|---|
| `app` | `curl -fsS http://localhost/health/` |
| `db` | `pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"` |
| `redis` | `redis-cli ping` |
| `rabbitmq` | `rabbitmq-diagnostics check_port_connectivity` |
| `celery_worker` | `celery inspect ping` (ou check de processo) |
| `celery_beat` | check de processo |
| `traefik` | `traefik healthcheck --ping` |

- `start_period` adequado por serviço (ex.: `app=60s`, `db=30s`, `rabbitmq=40s`).

### 35.3 Ordem de subida

- Swarm ignora `depends_on` em runtime.
- Garantir ordem via **healthchecks** + `wait_for_db` nos entrypoints.

### 35.4 Restart policies

- `condition: on-failure`, `delay: 5s`, `max_attempts: 5`, `window: 120s` (ajustar por serviço).

### 35.5 Resource limits/reservations

- `resources.limits.cpus` / `memory` por serviço.
- `resources.reservations.cpus` / `memory` por serviço.
- Evitar starvation na VPS.

### 35.6 Update/rollback do app

- `update_config.order = start-first`.
- `update_config.failure_action = rollback`.
- Réplica nova saudável antes de derrubar a antiga.
- Rollback automático em falha de healthcheck.

---

## 36. Variáveis de Ambiente e Secrets

### 36.1 `.env` (desenvolvimento)

- Gitignored.
- Importado com `django-environ` no `settings.py`.
- Inclui: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASES`, `CACHES`, `CELERY_*`, `EMAIL_*`, `OPENAI_*`.

### 36.2 `.env` de produção

- Separado do de desenvolvimento.
- Em `/opt/scsi/.env` na VPS.
- Sensíveis preferencialmente como **Docker Secrets**.

### 36.3 Django Secret Keys

- `SECRET_KEY` via env ou Docker Secret (`SECRET_KEY_FILE`).
- `OPENAI_API_KEY` via env ou Docker Secret (`OPENAI_API_KEY_FILE`).
- `POSTGRES_PASSWORD` via Docker Secret (`POSTGRES_PASSWORD_FILE`).
- `CLOUDFLARE_DNS_API_TOKEN` via Docker Secret (`CF_DNS_API_TOKEN_FILE`).

### 36.4 Padrões de produção

```env
ALLOWED_HOSTS=scsi.digital,.scsi.digital,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://scsi.digital,https://*.scsi.digital
```

- Em `ALLOWED_HOSTS` apenas **hostname** (sem esquema).
- `localhost` e `127.0.0.1` obrigatórios para healthcheck interno.
- `CSRF_TRUSTED_ORIGINS` sempre com **https** + wildcard.

---

## 37. Critérios de Aceite

- [ ] Um usuário de uma corretora **não consegue acessar dados** de outra corretora (em listagens, detalhes, anexos e API de IA).
- [ ] Arquivos privados não são acessíveis sem autenticação e permissão.
- [ ] `/health/` retorna HTTP 200 **sem banco** e **sem autenticação**.
- [ ] App sobe em **Docker Compose** local com `docker compose up`.
- [ ] Stack sobe em **Docker Swarm** com `docker stack deploy --with-registry-auth`.
- [ ] Traefik emite **certificado wildcard** via DNS-01 para `*.scsi.digital` e `scsi.digital`.
- [ ] Celery processa tasks de IA **sem bloquear** a interface (loading + notificação).
- [ ] Redis funciona como cache e result backend.
- [ ] RabbitMQ funciona como broker.
- [ ] Proposta **gera apólice** corretamente com itens cobertos copiados.
- [ ] Sinistro está sempre ligado a **item coberto de uma apólice**.
- [ ] Chat de IA **respeita tenant** (tools nunca vazam dados de outra corretora).
- [ ] Respostas de IA em **Markdown** renderizadas com segurança.
- [ ] Relatórios exportam **PDF** e **CSV**.
- [ ] Dashboard exibe métricas, gráficos e **funil de negociações**.
- [ ] Deploy usa **Docker Secrets** e não expõe credenciais versionadas.
- [ ] `celery_worker` e `celery_beat` **não** estão em `traefik_public`.
- [ ] `db`, `redis`, `rabbitmq` apenas em `scsi_v1_internal`.
- [ ] `app` em `traefik_public` e `scsi_v1_internal`.
- [ ] `celery_worker`/`celery_beat` em `scsi_v1_internal` e `scsi_v1_egress`.
- [ ] Migrations rodando com **advisory lock** (uma réplica por vez).
- [ ] `collectstatic --clear` executado no entrypoint do app.
- [ ] Rollback automático ativado para o `app` (`start-first` + `failure_action: rollback`).
- [ ] Login por **email** funciona.
- [ ] Recuperação de senha por email funciona.
- [ ] Landing page exibe planos com apenas `free` habilitado e demais "em breve".
- [ ] Dados fake carregáveis via `python manage.py load_fake_data`.
- [ ] MKDocs serve a documentação com Mermaid.

---

## 38. Riscos Técnicos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Vazamento de dados entre tenants | Crítico | `BaseTenantModel` + `TenantQuerySet` + `TenantMiddleware` + checagens em views e tools de IA. |
| Arquivos media expostos publicamente | Alto | `PrivateMediaView` com validação de `brokerage` + permissão; nunca servir media via Traefik direto. |
| Migrations concorrentes em múltiplas réplicas | Alto | Advisory lock do PostgreSQL no entrypoint; apenas uma réplica migra por vez. |
| Conflitos de estáticos em redeploys | Médio | `collectstatic --clear` no entrypoint. |
| Crash-loop por dependência não pronta | Médio | `wait_for_db` + healthchecks + `start_period`. |
| Token Cloudflare vazado | Crítico | Docker Secret; `CF_DNS_API_TOKEN_FILE`; nunca em compose/`.env` versionado. |
| Respostas de IA inseguras (XSS via Markdown) | Alto | Sanitização no template; allowlist de tags/atributos. |
| Custos/limites de OpenAI | Médio | GPT-5.5-mini (custo baixo); cache de resumos; rate limit por usuário. |
| Sobrecarga da VPS | Alto | `resources.limits`/`reservations` em todos os serviços. |
| Downtime em deploy | Médio | `start-first` + `failure_action: rollback` + healthcheck. |
| Perda de dados | Crítico | `scripts/backup.sh` com rotação; volumes nomeados. |
| Cache stale | Baixo | Keys com prefixo por tenant; invalidação em signals relevantes. |
| Erro de CSRF em proxy | Médio | `CSRF_TRUSTED_ORIGINS` com https + wildcard; `SECURE_PROXY_SSL_HEADER`. |
| Loop de redirect HTTPS no `/health/` | Baixo | `SECURE_REDIRECT_EXEMPT = [r'^/health/?$']`. |

---

## 39. Sprints de Desenvolvimento

> Convenção: `- [ ]` para tarefas não concluídas. Atualize para `- [x]` ao concluir.

### Sprint 1 — Fundação do Projeto

- [x] Criar repositório do projeto SCSI.
- [x] Criar `.gitignore` (Python, Django, `.env`, `.venv`, `__pycache__`, media, staticfiles locais).
- [x] Criar `.env.example` versionado.
- [x] Criar `.venv` na raiz.
- [x] Criar `requirements.txt` na raiz (Django, django-environ, psycopg, celery, redis, rabbitmq, langchain, langgraph, openai, reportlab, pypdf, whitenoise, dj-celery-panel, mkdocs, etc.).
- [x] Criar `manage.py` na raiz.
- [x] Criar app `core` (projeto Django) com `settings.py` único, `urls.py`, `wsgi.py`, `asgi.py`.
- [x] Configurar `settings.py` com `django-environ`, `TIME_ZONE='America/Sao_Paulo'`, `LANGUAGE_CODE='pt-br'`.
- [x] Criar app `base` com `BaseTenantModel`, `TimeStampedModel`, `TenantManager`, `TenantQuerySet`.

### Sprint 2 — Docker Local

- [x] Criar `Dockerfile` (Python 3.13).
- [x] Criar `docker-compose.yml` com `app`, `db`, `celery_worker`, `celery_beat`, `rabbitmq`, `redis`, `traefik` (opcional local).
- [x] Criar `entrypoint.sh` (app: `wait_for_db` → `migrate` → `collectstatic --clear` → `runserver`).
- [x] Criar `entrypoint.celery.sh` (celery: `wait_for_db` apenas).
- [x] Criar management command `wait_for_db`.
- [x] Configurar volumes locais para postgres, redis, rabbitmq, media, staticfiles.
- [x] Validar `docker compose up` sobe tudo.

### Sprint 3 — Configuração Django

- [x] Configurar `DATABASES` via `.env`.
- [x] Configurar `CACHES` (Redis) via `.env`.
- [x] Configurar `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND` via `.env`.
- [x] Configurar `EMAIL_*` via `.env`.
- [x] Configurar `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` como listas por vírgula.
- [x] Configurar WhiteNoise (`CompressedStaticFilesStorage`).
- [x] Configurar `STATIC_ROOT` e `MEDIA_ROOT`.
- [x] Configurar `SECURE_PROXY_SSL_HEADER`, `SECURE_REDIRECT_EXEMPT` (condicional a produção).

### Sprint 4 — Usuário Customizado com Login por Email

- [x] Criar `core.User` (`AbstractUser` adaptado, `USERNAME_FIELD='email'`, sem `username`).
- [x] Configurar `AUTH_USER_MODEL='core.User'`.
- [x] Criar views/templates de login por email (CBV).
- [x] Criar logout.
- [x] Configurar recuperação de senha por email (nativo Django).
- [x] Criar middleware de tenant (`TenantMiddleware`).

### Sprint 5 — Multi-Tenant Base

- [ ] Criar `core.Brokerage` (CNPJ, Razão Social, etc.).
- [ ] Criar `core.Plan` (`free` disponível, demais `is_available=False`).
- [ ] Vincular `User.brokerage` FK.
- [ ] Implementar `BaseTenantModel` em `base`.
- [ ] Implementar `TenantQuerySet`/`TenantManager` filtrando por `brokerage`.
- [ ] Criar mixins de views CBV que filtram por `request.tenant`.

### Sprint 6 — Corretoras e Permissões

- [ ] Criar fluxo de cadastro de corretora (CNPJ + Razão Social obrigatórios).
- [ ] Criar `Group`s: `brokerage_admin`, `brokerage_agent`, `brokerage_producer`, `brokerage_backoffice`, `scsi_staff`.
- [ ] Criar permissões customizadas por model quando necessário.
- [ ] Criar landing page (raiz `/`) com CTA e planos.
- [ ] Habilitar apenas plano `free`; demais botões "em breve".
- [ ] Após cadastro, criar usuário admin vinculado à corretora.

### Sprint 7 — Clientes

- [ ] Criar app `clients` com `Client` (tenant).
- [ ] CRUD de clientes (CBV) com filtros e busca.
- [ ] Tela de detalhe do cliente.
- [ ] Placeholder para botão "Resumir com IA" (Sprint 23).
- [ ] Anexos de cliente (Sprint 14).

### Sprint 8 — Seguradoras e Ramos

- [ ] Criar app `catalog`.
- [ ] CRUD de `InsuranceCompany`.
- [ ] CRUD de `Branch` (auto, residencial, vida, viagem, empresarial, frota, outros).
- [ ] CRUD de `Coverage` por ramo.

### Sprint 9 — Itens Cobertos

- [ ] Criar `ProposalCoveredItem` e `PolicyCoveredItem` (ou model reutilizável conforme design).
- [ ] Campos: `kind`, `description`, `value`, `attributes` (JSON).
- [ ] Relacionar com propostas e apólices (1:N).

### Sprint 10 — Propostas

- [ ] Criar app `proposals` com `Proposal` (tenant).
- [ ] CRUD de propostas com cliente, seguradora, ramo, produtor.
- [ ] Itens cobertos 1:N na proposta.
- [ ] Status e validade.
- [ ] Anexos (Sprint 14).

### Sprint 11 — Apólices

- [ ] Criar app `policies` com `Policy` (tenant).
- [ ] CRUD de apólices com itens cobertos.
- [ ] Campos de número, vigência, premium, status.

### Sprint 12 — Geração de Apólice a partir da Proposta

- [ ] Botão "Gerar apólice" na proposta.
- [ ] Lógica de serviço que cria `Policy` + copia `ProposalCoveredItem` → `PolicyCoveredItem`.
- [ ] Mantém vínculo `proposal` na apólice.
- [ ] Testes manuais do fluxo.

### Sprint 13 — Sinistros

- [ ] Criar app `claims` com `Claim` (tenant).
- [ ] Sinistro vinculado a `Policy` + `PolicyCoveredItem`.
- [ ] CRUD com status e valor.
- [ ] Anexos (Sprint 14).

### Sprint 14 — Anexos Privados

- [ ] Criar app `attachments` com `Attachment` (tenant, GenericFK ou FKs).
- [ ] Upload validado por tipo/tamanho.
- [ ] `PrivateMediaView` para servir com validação de `brokerage` + permissão.
- [ ] Aplicar anexos em clientes, propostas, apólices e sinistros.

### Sprint 15 — CRM Grid

- [ ] Criar app `crm` com `Pipeline`, `PipelineStage`, `Deal`.
- [ ] Tela grid de negociações com filtros e ordenação.
- [ ] CRUD de negociações.

### Sprint 16 — CRM Kanban

- [ ] Tela Kanban com colunas por etapa.
- [ ] Cards arrastáveis (drag-and-drop).
- [ ] Cores personalizáveis por etapa.
- [ ] Nomes de etapas personalizáveis.
- [ ] Persistir mudança de etapa ao arrastar.

### Sprint 17 — Renovações

- [ ] Criar `Renewal` em `policies`.
- [ ] Controle de vencimentos e status.
- [ ] Alertas de renovações próximas (30/60/90 dias).
- [ ] Relatórios relacionados (Sprint 21).

### Sprint 18 — Endossos

- [ ] Criar `Endorsement` em `policies`.
- [ ] CRUD de endossos relacionados a apólices.
- [ ] Tipo, descrição e data de eficácia.

### Sprint 19 — Agentes e Produtores

- [ ] Criar app `commercial` com `Agent`, `Producer`.
- [ ] Um agente pode ter vários produtores.
- [ ] Produtor pode ser direto da corretora (sem agente).
- [ ] CRUDs completos.

### Sprint 20 — Comissões

- [ ] Criar `Commission` com `amount`, `brokerage_share`, `agent_share`, `producer_share`.
- [ ] Cálculo automatizado de repasses a partir de percentuais.
- [ ] Tela de comissões por período/agente/produtor.
- [ ] Relatórios de comissões (Sprint 21).

### Sprint 21 — Relatórios

- [ ] Criar app `reports`.
- [ ] Menu e tela dedicada a relatórios.
- [ ] Filtros por período, seguradora, ramo, produtor, status.
- [ ] Exportação **PDF** com ReportLab/PyPDF.
- [ ] Exportação **CSV** com `StreamingHttpResponse` (UTF-8 BOM).
- [ ] Relatórios: clientes, apólices, propostas, sinistros, renovações, comissões, carteira.

### Sprint 22 — Dashboard

- [ ] Criar app `dashboard`.
- [ ] Cards de métricas (clientes, apólices, premium, sinistros, renovações, comissões).
- [ ] Gráficos de evolução, distribuição por ramo, sinistros por status.
- [ ] Gráfico de **funil de negociações/leads** com níveis.
- [ ] Insights (textos curtos).

### Sprint 23 — IA para Resumos

- [ ] Criar app `ai`.
- [ ] Configurar LangChain + LangGraph + OpenAI GPT-5.5-mini via `.env`.
- [ ] Criar tools de leitura por tenant (sem `brokerage_id` do cliente).
- [ ] Criar task Celery `summarize_entity`.
- [ ] Botão "Resumir com IA" em cliente/apólice/sinistro/proposta/negociação.
- [ ] Salvar resultado em `ai_summary`.
- [ ] Loading no botão + aviso ao usuário.

### Sprint 24 — Chat com IA

- [ ] Criar `ChatSession` e `ChatMessage`.
- [ ] Tela de Chat no menu lateral.
- [ ] Streaming de resposta (SSE/WebSocket).
- [ ] Resposta em Markdown renderizada com segurança.
- [ ] Sessões salvas por usuário.
- [ ] Tools do chat respeitando tenant.

### Sprint 25 — Celery, RabbitMQ e Redis

- [ ] Configurar Celery app integrado ao Django.
- [ ] Configurar RabbitMQ como broker e Redis como result backend + cache.
- [ ] Configurar `dj-celery-panel` no admin.
- [ ] Configurar Celery Beat para tarefas periódicas (alertas de renovação, limpeza de jobs).

### Sprint 26 — Notificações Internas

- [ ] Criar app `notifications` com `Notification`.
- [ ] Criar notificação ao finalizar task de IA.
- [ ] Exibir notificações na interface (sino/toast).
- [ ] Marcar como lida.

### Sprint 27 — Dados Fake

- [ ] Criar management command `load_fake_data`.
- [ ] Gerar múltiplas corretoras para validar isolamento.
- [ ] Gerar clientes, propostas, apólices, sinistros, renovações, endossos.
- [ ] Gerar pipeline e negociações em várias etapas.
- [ ] Gerar agentes, produtores e comissões.
- [ ] Usar datas variadas (passado/presente/futuro).

### Sprint 28 — Admin Django

- [ ] Registrar todos os models no admin.
- [ ] `list_filter`, `search_fields`, `date_hierarchy`, `raw_id_fields`.
- [ ] `get_queryset` filtrando por `request.user.brokerage`.
- [ ] `save_model` forçando `brokerage` do usuário quando aplicável.
- [ ] Integrar `dj-celery-panel`.

### Sprint 29 — MKDocs

- [ ] Criar `docs/` com PRD e demais docs.
- [ ] Configurar `mkdocs.yml`.
- [ ] Habilitar Mermaid.
- [ ] Servir documentação local e/ou em subdomínio interno.

### Sprint 30 — Docker Swarm

- [ ] Criar `stack.yml` com todos os serviços.
- [ ] Configurar volumes nomeados.
- [ ] Configurar `restart_policy`, `resources`, `healthchecks`.
- [ ] Configurar `update_config` do app (`start-first`, `failure_action: rollback`).
- [ ] Validar `docker stack deploy --with-registry-auth`.

### Sprint 31 — Traefik e TLS Wildcard

- [ ] Configurar Traefik na rede `traefik_public`.
- [ ] Configurar Let's Encrypt DNS-01 com Cloudflare.
- [ ] Usar `CLOUDFLARE_DNS_API_TOKEN` como Docker Secret (`CF_DNS_API_TOKEN_FILE`).
- [ ] Emitir wildcard para `scsi.digital` e `*.scsi.digital`.
- [ ] Redirecionar HTTP → HTTPS.
- [ ] `forwardedHeaders.trustedIPs` do Cloudflare.

### Sprint 32 — Scripts de Deploy e Backup

- [ ] Criar `scripts/deploy.sh` (parser seguro, validações, build/push, stack deploy, rollout, `--skip-build`).
- [ ] Criar `scripts/backup.sh` (PostgreSQL + media, rotação por tempo, compatível com cron).

### Sprint 33 — Hardening e Revisão Final

- [ ] Validar `DEBUG=False` em produção.
- [ ] Validar `ALLOWED_HOSTS` com `localhost`/`127.0.0.1`.
- [ ] Validar `CSRF_TRUSTED_ORIGINS` com https + wildcard.
- [ ] Validar `SECURE_PROXY_SSL_HEADER`.
- [ ] Validar `SECURE_REDIRECT_EXEMPT` para `/health/`.
- [ ] Validar isolamento multi-tenant em todas as telas.
- [ ] Validar proteção de media privada.
- [ ] Validar secrets não versionados.
- [ ] Validar redes Docker conforme regras.
- [ ] Rodar `scripts/deploy.sh` e `scripts/backup.sh` em ambiente de homologação.
- [ ] Checklist final de qualidade (seção 40).

---

## 40. Checklist Final de Qualidade

- [ ] Python > 3.13 e Django > 6.0.
- [ ] Único `settings.py` em `core`.
- [ ] `.venv` na raiz; `requirements.txt` atualizado.
- [ ] `.env` gitignored; `.env` de produção separado.
- [ ] Variáveis via `django-environ` com listas por vírgula.
- [ ] Login por **email** (sem username).
- [ ] Recuperação de senha por email (nativo Django).
- [ ] `AUTH_USER_MODEL='core.User'`.
- [ ] `TIME_ZONE='America/Sao_Paulo'`, `LANGUAGE_CODE='pt-br'`.
- [ ] App principal `core` e app compartilhado `base` na raiz.
- [ ] Domínios separados em apps Django.
- [ ] Todo model com `created_at` e `updated_at`.
- [ ] Signals em `signals.py` dentro da app.
- [ ] Arquitetura multi-tenant compartilhada (sem schemas/bancos separados).
- [ ] `BaseTenantModel` + `TenantQuerySet` + `TenantMiddleware`.
- [ ] Arquivos media privados por view segura.
- [ ] Class Based Views preferidas.
- [ ] Recursos nativos do Django sempre que possível.
- [ ] Sem testes automatizados (conforme requisito).
- [ ] PEP8 e aspas simples.
- [ ] Celery + RabbitMQ (broker) + Redis (result backend + cache).
- [ ] `dj-celery-panel` no admin.
- [ ] Tarefas de IA não bloqueiam interface (loading + notificação).
- [ ] LangChain > 1.0 + LangGraph + OpenAI GPT-5.5-mini.
- [ ] Tools de IA sempre filtram por tenant (sem `brokerage_id` do cliente).
- [ ] Resumos salvos em campo `ai_summary`.
- [ ] Chat com sessões salvas por usuário.
- [ ] Streaming + Markdown sanitizado no chat.
- [ ] ReportLab/PyPDF para PDF; CSV nativo.
- [ ] Menu e tela dedicada a relatórios.
- [ ] Dashboard com métricas, gráficos e funil.
- [ ] CRM grid + Kanban arrastável, pipeline personalizável.
- [ ] Geração de apólice a partir da proposta.
- [ ] Sinistro sempre em item coberto de apólice.
- [ ] Anexos em clientes/propostas/apólices/sinistros.
- [ ] Endossos relacionados a apólices.
- [ ] Renovações com vencimento e status.
- [ ] Comissões com repasses (corretora/agente/produtor).
- [ ] Landing page com plano `free` habilitado e demais "em breve".
- [ ] Sem integração com pagamentos.
- [ ] Django Admin com filtros, buscas e respeito ao tenant.
- [ ] `docs/` com PRD e MKDocs + Mermaid.
- [ ] Command `load_fake_data` com cenários e datas variadas.
- [ ] Docker Compose local com todos os serviços.
- [ ] Docker Swarm em produção com volumes nomeados.
- [ ] Imagem em `ghcr.io/pycodebr/scsi_v1`.
- [ ] `docker stack deploy --with-registry-auth`.
- [ ] Rede `traefik_public` (external) — apenas `app` e `traefik`.
- [ ] Rede `scsi_v1_internal` (internal) — `db`, `redis`, `rabbitmq`, `celery_worker`, `celery_beat`, `app`.
- [ ] Rede `scsi_v1_egress` (overlay) — `celery_worker` e `celery_beat`.
- [ ] `celery_worker`/`celery_beat` **fora** de `traefik_public`.
- [ ] `db`/`redis`/`rabbitmq` **apenas** em `scsi_v1_internal`.
- [ ] TLS wildcard via Let's Encrypt DNS-01 com Cloudflare.
- [ ] `CLOUDFLARE_DNS_API_TOKEN` como Docker Secret; lido via `CF_DNS_API_TOKEN_FILE`.
- [ ] `/health/` retorna 200, sem banco, sem auth.
- [ ] Healthchecks em todos os serviços.
- [ ] Migrations com advisory lock no entrypoint do app.
- [ ] `collectstatic --clear` no entrypoint do app.
- [ ] Celery não roda migrations nem collectstatic.
- [ ] `restart_policy` em todos os serviços.
- [ ] `resources.limits`/`reservations` em todos os serviços.
- [ ] `update_config` do app com `start-first` e `failure_action: rollback`.
- [ ] `scripts/deploy.sh` com validações e `--skip-build`.
- [ ] `scripts/backup.sh` com rotação e compatível com cron.
- [ ] `ALLOWED_HOSTS=scsi.digital,.scsi.digital,localhost,127.0.0.1`.
- [ ] `CSRF_TRUSTED_ORIGINS=https://scsi.digital,https://*.scsi.digital`.
- [ ] `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')`.
- [ ] `SECURE_REDIRECT_EXEMPT` isenta `/health/`.
- [ ] Traefik confia nos IPs do Cloudflare (`forwardedHeaders.trustedIPs`).
- [ ] Nenhum secret versionado.
- [ ] UI em português brasileiro; código em inglês.
- [ ] Design system em `@design_system/design-system.html` respeitado.
