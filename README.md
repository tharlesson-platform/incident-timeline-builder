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

## Licenca

Este projeto esta licenciado sob a Apache License 2.0. Consulte `LICENSE` para mais detalhes.

## Autor

**Tharlesson**  
GitHub: https://github.com/tharlesson
