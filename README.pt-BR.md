# Cardume

**O Claude Code com um especialista para cada parte do trabalho.** O Cardume traz especialistas de
produto, arquitetura, design, frontend, backend, dados, plataforma, QA e segurança que o Claude aciona
sozinho, um processo do tamanho de cada tarefa e hooks que o modelo não consegue pular.

[English](README.md) · Português · a documentação detalhada em `docs/` está em inglês

[![Validate](https://github.com/jeffersonvalente/cardume/actions/workflows/validate.yml/badge.svg)](https://github.com/jeffersonvalente/cardume/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fjeffersonvalente%2Fcardume%2Fmain%2Fplugins%2Fcardume-core%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=informational)](docs/CHANGELOG.md)

## Instalar

No Claude Code:

```text
/plugin marketplace add jeffersonvalente/cardume
/plugin install cardume-all@cardume
```

Depois, uma vez em cada projeto:

```text
/cardume-core:setup
```

O setup mostra o diff e pergunta antes de gravar. Ele altera só um bloco marcado no `CLAUDE.md` e
acrescenta `.cardume/` ao `.gitignore`. Também sugere os plugins de stack e de navegação de
código (LSP) que combinam com o projeto. Depois disso, descreva a tarefa como sempre: *"adiciona
suporte a várias moedas nas faturas"*, *"o endpoint de pedidos dá 500 às vezes"*. O Cardume chama
você só quando a decisão é sua.

**Para o time todo**, commite isto como `.claude/settings.json` no repositório. Quem abrir o projeto
e confiar na pasta recebe o marketplace e os plugins, sem nenhum servidor para manter:

```json
{
  "extraKnownMarketplaces": {
    "cardume": {
      "source": { "source": "github", "repo": "jeffersonvalente/cardume" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "cardume-all@cardume": true }
}
```

Uma empresa pode ir além e exigir o Cardume em todas as máquinas pelas configurações gerenciadas (managed settings), sem que dê
para desligar. Veja [Use it with a team](docs/CONFIGURATION.md#use-it-with-a-team) (em inglês).

<p align="center"><img src="docs/assets/compare-feature.gif" width="900" alt="Gravação lado a lado do mesmo pedido em dois projetos idênticos: guardar clientes e faturas em SQLite e exportar CSV. À esquerda, o Claude Code puro já escreve o código e toma as decisões de design sozinho. À direita, com Cardume, o Claude anuncia Level 2 — feature, invoca a skill cardume-core:spec, pergunta sobre formato de dinheiro, dados e interface, escreve uma spec com requisitos numerados de R1 a R12, planeja um ADR e espera aprovação antes de codar."></p>

*Mesmo pedido, dois projetos idênticos, gravação real (acelerada). **Esquerda:** o Claude Code puro sai
codando e decide armazenamento, formato de dinheiro e interface sozinho. **Direita:** o Cardume classifica
como **nível 2**, invoca `cardume-core:spec`, pergunta as decisões que mudam o design, escreve uma spec
com requisitos numerados e espera sua aprovação antes de qualquer código.*

## O que dá para pedir

Descreva a tarefa como você falaria com um colega. O Claude escolhe o especialista; você nunca
precisa citar um agente. Uma amostra do que vai para onde:

| Você pede | Quem assume | O que você recebe |
| --- | --- | --- |
| "Vamos começar uma plataforma de agendamento para clínicas" | `product-manager` → `software-architect` | PRD e arquitetura aprovados por você; ADRs e lista de features |
| "Deixa a página de preços mais ousada" | `design-flow` | Direção visual, crítica e a página polida |
| "Cria o site da clínica" | `site-builder` + `design-flow` | Estrutura, conteúdo, design e passos de deploy |
| "Adiciona exportação de faturas com filtros" | `spec` → `backend-specialist`, `frontend-specialist` | Spec, tarefas, código e evidência de verificação |
| "O checkout dá 500 para alguns usuários" | `debugger` | Reprodução, causa raiz, correção e teste de regressão |
| "Por que a tabela gold perdeu linhas ontem?" | `data-engineer-gcp-bigquery` | Causa raiz pelo histórico de jobs e da tabela, com as queries que rodou |
| "Revisa o infra/main.tf antes de eu aplicar" | `iac-reviewer` | Achados por severidade, o que não deu para verificar, um veredito |
| "Os pods de produção ficam reiniciando" | `kubernetes-copilot` | Triagem só de leitura primeiro; pergunta antes de qualquer mudança |
| "Dá pra cortar 20% da conta de cloud?" | `finops-architect` | Quebra dos gastos, economias priorizadas com as contas, alertas de orçamento |
| "Revisão de segurança antes do lançamento" | `security-auditor` | Achados de OWASP, segredos e dependências, sem editar nada |
| "A fase 2 está pronta para aprovar?" | `qa-gatekeeper` | Relatório de gate feito com checagens reexecutadas, não com promessas |
| "Protótipo de um jogo de plataforma 2D na Godot" | `game-developer` | Setup da engine, game loop, game feel e performance |

O mapa completo está em [docs/CATALOG.md](docs/CATALOG.md) e na tabela
[`intelligent-routing`](plugins/cardume-core/skills/intelligent-routing/SKILL.md).

<p align="center"><img src="docs/assets/compare-iac-review.gif" width="900" alt="Gravação lado a lado: o mesmo arquivo Terraform, com bucket público, papel Owner e chave exportada, é enviado para revisão. À esquerda, o Claude Code puro revisa no chat. À direita, com Cardume, o Claude classifica como revisão só de leitura e encaminha ao agente cardume-platform:iac-reviewer, que devolve achados por severidade, o que não conseguiu verificar e as perguntas que bloqueiam a correção."></p>

*Mesmo arquivo Terraform, mesmo pedido. Os dois pegam o bucket público e o `roles/owner`. **Direita:** o
Cardume encaminha ao agente só de leitura `cardume-platform:iac-reviewer`, que também lista o que não
conseguiu verificar e as perguntas que bloqueiam a correção, e planeja uma mini-spec antes de mexer em IAM.*

## Por que é diferente

- **Um especialista para cada parte do trabalho.** 33 agentes cobrem produto, arquitetura, design,
  frontend, backend, dados, plataforma, QA, segurança e jogos. O Claude encaminha cada tarefa pela
  descrição dos agentes, usando a tabela
  [`intelligent-routing`](plugins/cardume-core/skills/intelligent-routing/SKILL.md) quando a escolha
  não é óbvia. Você nunca precisa citar um agente.
- **Quem garante é o harness, não o prompt.** Os hooks rodam fora do modelo: um modelo segue as
  instruções na maioria das vezes, um hook roda sempre, não importa o que o modelo decidiu.
  O [`stop_verify`](plugins/cardume-core/hooks/stop_verify.py) impede o fim do turno enquanto o scan
  de segurança ou o lint falham nos arquivos alterados no working tree do git.
  O [`guard_bash`](plugins/cardume-core/hooks/guard_bash.py) pergunta a você antes de
  `terraform apply`, `git push --force`, `DROP TABLE`, publicação de pacotes e outros comandos
  destrutivos ou públicos. O [`syntax_check`](plugins/cardume-core/hooks/syntax_check.py) devolve
  erros de sintaxe logo depois de cada edição.
- **Quem constrói não aprova.** A skill [`verify`](plugins/cardume-core/skills/verify/SKILL.md)
  roda num contexto novo, e o agente [`qa-gatekeeper`](plugins/cardume-core/agents/qa-gatekeeper.md)
  executa as checagens ele mesmo. Os dois só aceitam evidência: um comando com a saída, um teste, um
  arquivo. Um hook
  ([`restrict_verifier_writes`](plugins/cardume-core/hooks/restrict_verifier_writes.py)) impede o
  `qa-gatekeeper` de editar o código que ele julga.
- **Processo do tamanho da tarefa.** Todo pedido recebe um nível de 0 a 3. Um typo não gera
  documento; uma feature passa por spec → tasks → implement → verify → review; um produto novo passa
  por PRD → arquitetura → gate → release. O risco sobe o nível, e as decisões técnicas viram ADRs
  pelo caminho.
- **O comportamento é medido.** 40 casos de [`claude plugin eval`](docs/EVALS.md) conferem se as
  skills disparam quando devem, ficam quietas quando não devem e se as respostas atendem a uma
  rubrica escrita, com e sem o plugin.
- **Seus arquivos continuam seus.** O Cardume nunca escreve no `AGENTS.md`. No `CLAUDE.md`, só mexe
  dentro de um bloco marcado, depois de mostrar o diff, e com backup.
- **Sem telemetria.** Nenhum script envia dados de uso ou de sessão.

## Processo do tamanho da tarefa

| Você precisa de | Você recebe |
| --- | --- |
| **Nível 0** — um typo, um ajuste de texto, uma pergunta | A correção, direto. Sem documento. |
| **Nível 1** — um bug ou mudança pequena numa área | Uma mini-spec no PR: problema, 2–3 critérios de aceite, como foi verificado. Bug começa por um teste que falha. |
| **Nível 2** — uma feature, ou mudanças em várias áreas | `spec` → `tasks` → `implement` → `verify` → `review`, com a sua aprovação da spec e das tarefas. |
| **Nível 3** — um produto novo ou uma fase | PRD → arquitetura e ADRs → cada feature no nível 2 → gate com evidência → release. |

Autenticação, dinheiro, exclusão de dados, API pública e qualquer coisa irreversível começam no
nível 1 ou acima. Diga "faz direto" para pular o processo, ou "quero spec completa" para forçá-la.
Detalhes em [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) (em inglês).

## Como funciona

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/architecture-dark.svg">
  <img src="docs/assets/architecture-light.svg" width="900" alt="Arquitetura: o pedido é classificado num nível de trabalho de 0 a 3, encaminhado a agentes especialistas agrupados em sete plugins e conferido por um verificador separado que só aceita evidência antes de terminar. Os hooks rodam fora do modelo em edições, comandos de shell e fim do turno. Specs, tarefas, ADRs e relatórios de gate são escritos pelo caminho.">
</picture>

O nível decide quais documentos existem. O roteamento decide quem trabalha. Os hooks rodam quer o
modelo lembre das instruções ou não. O verificador parte dos critérios escritos, não do resumo de
quem construiu.

## O que vem dentro

33 agentes especialistas, 62 skills e 13 comandos manuais, em sete plugins. O `cardume-all` instala
todos; o `cardume-core` vem sempre junto.

| Plugin | Para |
| --- | --- |
| `cardume-core` | Fluxo de entrega (spec, tasks, verify, gate, release), hooks, roteamento, arquitetura, debug |
| `cardume-frontend` | Design de UI, sites, React/Next.js, mobile, performance, SEO, i18n |
| `cardume-backend` | APIs, bancos de dados, Node.js, Java/Spring, Rust, servidores MCP |
| `cardume-data` | BigQuery, lakehouse, Airflow, observabilidade de dados no GCP, revisão de PR de dados, auditoria de projetos de dados e IA |
| `cardume-platform` | Terraform, Kubernetes, CI/CD, observabilidade, FinOps, avaliação de cloud |
| `cardume-qa` | Testes, TDD, E2E com Playwright, auditoria de segurança, pentest |
| `cardume-games` | Desenvolvimento de jogos em várias engines |

A lista completa, com uma linha por item, está em [docs/CATALOG.md](docs/CATALOG.md).

## Evals

Cada plugin tem casos em `evals/` para o `claude plugin eval`. Um caso é um prompt realista mais
avaliadores: a skill certa carregou, o comando destrutivo ficou sem rodar, a resposta atende a uma
rubrica escrita avaliada por um modelo juiz. Cada caso roda com e sem o plugin, então a nota é uma
diferença, não um valor absoluto. Para os plugins que dependem do `cardume-core`, essa diferença é
core mais plugin contra o Claude puro.

```bash
cd plugins && claude plugin eval . --eval-dir cardume-qa/evals --scaffold --runs 3 --no-publish
```

O que eles não cobrem: os hooks (scripts determinísticos, não avaliados por modelo), projetos de
vários passos e edições num código real. A maioria dos casos só permite ferramentas de leitura.
Ainda não há taxas de aprovação publicadas. Um workflow de CI roda as suítes toda semana, com teto
de custo. Veja [docs/EVALS.md](docs/EVALS.md).

## Segurança e privacidade

<p align="center"><img src="docs/assets/compare-force-push.gif" width="900" alt="Gravação lado a lado: pedido de squash de dois commits e force push. À esquerda, o Claude Code puro faz o force push e reescreve o origin/main. À direita, com Cardume, o hook de guarda do cardume-core para o git push --force-with-lease e pede confirmação; o remote fica intacto."></p>

*Mesmo pedido. **Esquerda:** o Claude Code puro faz o force push e reescreve o `origin/main`.
**Direita:** o hook de guarda do Cardume (`[plugin:cardume-core]`) para o comando e pergunta antes.*

| Hook | Bloqueia ou pergunta |
| --- | --- |
| `guard_bash` | Pergunta antes de comandos destrutivos ou públicos: apply/destroy de infra, exclusões, `DROP`, force push, tags, releases, publicação de pacotes e imagens |
| `stop_verify` | Impede o fim do turno enquanto o scan de segurança ou o lint falham nos arquivos alterados; devolve a decisão a você depois de 3 tentativas |
| `syntax_check` | Devolve erros de sintaxe em arquivos `.py`, `.js`, `.sh` e `.json` logo depois de cada edição |
| `restrict_verifier_writes` | Limita o `qa-gatekeeper` a escrever relatórios e rodar comandos só de leitura |
| `spec_reminder` | Avisa uma vez (não bloqueia) quando uma mudança grande não tem spec, PRD nem ADR |
| `routing_reminder` | Lembra o Claude, antes de cada pedido, de dizer o nível e usar a skill ou o agente certo (não bloqueia) |

- **Sem telemetria.** Nenhum script envia dados de uso ou de sessão. Código só vai para outro agente
  se você optar por isso (veja o preview ao vivo abaixo).
- **Arquivos que ele nunca escreve:** `AGENTS.md`, a memória automática do Claude e qualquer parte
  do `CLAUDE.md` fora do bloco `<!-- cardume:start -->`. Instalar não escreve nada no seu
  projeto; os hooks guardam pequenos arquivos de estado em `.cardume/`, que o setup põe no `.gitignore`.
- **O preview ao vivo do design** escuta só em `127.0.0.1`, aceita só origens locais e exige um token
  por sessão. Mandar código para um agente separado é opcional.

Cada hook, exceto o limite do verificador, pode ser desligado por uma variável de ambiente. Veja
[docs/SAFETY.md](docs/SAFETY.md).

## Configuração

A maioria dos projetos não precisa de nada além do `/cardume-core:setup`. O `cardume-platform` pede
o repositório de módulos Terraform, o prefixo do bucket de state e a região padrão ao ser
habilitado. Chaves dos hooks, memória de agentes, atualizações e servidores MCP estão em
[docs/CONFIGURATION.md](docs/CONFIGURATION.md) e [docs/MCP_SETUP.md](docs/MCP_SETUP.md).

## Funciona com outras ferramentas

As skills seguem o padrão aberto [Agent Skills](https://agentskills.io) e podem ser instaladas no
Codex, Cursor, Gemini CLI e Copilot com `npx skills add jeffersonvalente/cardume` ou
`gh skill install`. Agentes, hooks e os comandos `cardume-*` são exclusivos do Claude Code. Veja
[docs/CONFIGURATION.md](docs/CONFIGURATION.md#other-tools-codex-cursor-gemini-cli-copilot).

## Contribuindo

Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para a estrutura, as convenções e as 19 checagens do
`scripts/validate.py`, e o [docs/CREATING_SKILLS.md](docs/CREATING_SKILLS.md) para escrever uma
skill. As mudanças ficam em [docs/CHANGELOG.md](docs/CHANGELOG.md).

## Licença e atribuições

O Cardume é distribuído sob a [licença MIT](LICENSE). Partes de terceiros mantêm as próprias licenças
e estão listadas em [NOTICE.md](NOTICE.md):

- **antigravity-kit / ag-kit** (MIT): base de vários agentes e skills, adaptados e estendidos;
- **Vercel** `agent-skills` e `web-interface-guidelines` (MIT): `react-best-practices`,
  `react-native-skills` e `web-design-guidelines`;
- **Impeccable**, de Paul Bakaus (Apache-2.0): base do fluxo `design-flow`.
