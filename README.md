# Incident Timeline Builder

CLI para consolidar evidencias locais, montar timelines de incidentes, agrupar eventos automaticamente e gerar rascunhos de postmortem.

## O que o projeto entrega

- ingestao de evidencias genericas em `CSV` e `JSON`
- parsers dedicados para exports de `CloudWatch`, `Slack` e `GitHub Actions`
- normalizacao de timestamps com timezone real
- agrupamento automatico por incidente usando `incident_id`, tags, servico e proximidade temporal
- selecao do incidente principal para RCA e 5 Whys
- saidas em `timeline.json`, `timeline.md`, `timeline.html` e `postmortem-draft.md`

## Estrutura do projeto

```text
.
|-- cli/
|-- parsers/
|-- normalizers/
|-- correlators/
|-- reporters/
|-- examples/
|-- tests/
|-- docs/
|-- pyproject.toml
|-- Makefile
|-- .github/workflows/ci.yml
|-- README.md
```

## Instalacao

```bash
python -m pip install -e .[dev]
```

## Como executar

Exemplo principal com todos os conectores do roadmap:

```bash
incident-timeline-builder build --evidence-path examples/payments-incident --timezone UTC --output-dir artifacts/payments
```

Exemplo com multiplos incidentes no mesmo lote:

```bash
incident-timeline-builder build --evidence-path examples/multi-incident --timezone UTC --output-dir artifacts/multi
```

Exemplo consumindo bundle do `aws-sre-doctor`:

```bash
incident-timeline-builder build --evidence-path examples/aws-doctor-bundle --timezone UTC --output-dir artifacts/aws-doctor
```

Para diretórios aninhados:

```bash
incident-timeline-builder build --evidence-path ./incident-evidence --timezone America/Sao_Paulo --recursive
```

## Artefatos gerados

- `timeline.json`
  - report completo, incluindo eventos normalizados, incidentes agrupados e 5 Whys
- `timeline.md`
  - resumo legivel para revisão em pull request, issue ou wiki
- `timeline.html`
  - visualizacao HTML da timeline e dos incidentes agrupados
- `postmortem-draft.md`
  - template completo para RCA, impacto, fatores contribuintes e follow-ups

## Fontes suportadas

- `CSV` e `JSON` genericos
- `CloudWatch`
  - alarmes exportados em lote com `alarms`, `metric_alarms` ou listas de eventos
- `Slack`
  - arrays de mensagens ou objetos com `channel` e `messages`
- `GitHub Actions`
  - `workflow_runs` e listas de `jobs`
- `AWS SRE Doctor`
  - bundles com `diagnosis.json` e `bundle-manifest.json`

## Exemplos

- [examples/README.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/examples/README.md)
- [examples/payments-incident/README.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/examples/payments-incident/README.md)
- [examples/multi-incident/README.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/examples/multi-incident/README.md)

## Documentacao

- [docs/cli-reference.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/cli-reference.md)
- [docs/architecture.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/architecture.md)
- [docs/reproduction-guide.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/reproduction-guide.md)
- [docs/source-cloudwatch.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/source-cloudwatch.md)
- [docs/source-slack.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/source-slack.md)
- [docs/source-github-actions.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/source-github-actions.md)
- [docs/grouping-and-correlation.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/grouping-and-correlation.md)
- [docs/postmortem-template.md](C:/Users/tharl/OneDrive/Documentos/git/sre/incident-timeline-builder/docs/postmortem-template.md)

## Roadmap entregue nesta iteracao

- integracao com `CloudWatch`, `Slack` e `GitHub Actions` por meio de arquivos exportados
- template completo de postmortem
- agrupamento automatico por incidente e tags
- ingestao de bundle do `aws-sre-doctor` com fatos confirmados e hipoteses

## Licenca

Este projeto esta licenciado sob a Apache License 2.0. Consulte `LICENSE` para mais detalhes.

## Autor

**Tharlesson**  
GitHub: https://github.com/tharlesson


## CI isolado de validação

CI e guardrails preservam os gatilhos de pull request e fazem checkout explícito
do head (`pull_request.head.sha`, ou `github.sha` em push), sem persistir credenciais.
Checkout e setup-python estão fixados por SHA; cada job tem prazo de 20 minutos
e label exclusivo `incident-<job>-run-<run_id>`. CI mantém todos os pushes, incluindo
a branch piloto `fix/incident-isolated-python-ci`; guardrails acrescenta essa branch sem remover main/master.

O piloto usa Python 3.12 em runner Linux efêmero, sem configuração ou credenciais
AWS. Os testes locais são validados em container com rede desativada após instalar
as dependências, e a resolução Python atual é conferida por pip-audit. Isso não
autoriza chamadas cloud, adoção de forks, registro de runners ou execução em produção.
Admissão do SHA e política de contribuições externas são controladas separadamente
no host e não são implementadas nesta mudança. Para rollback, não publicar o delta
ou restaurar o workflow anteriormente revisado; não contornar os gates.
