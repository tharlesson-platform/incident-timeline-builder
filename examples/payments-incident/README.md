# Payments Incident

Scenario de checkout com degradacao apos deploy em producao.

## Arquivos

- `events.csv`
  - eventos genericos de infra, validacao e deploy
- `events.json`
  - evidencia complementar local
- `cloudwatch-alarms.json`
  - alarmes e sinais de customer impact
- `slack-incident.json`
  - trilha de ChatOps do incidente
- `github-actions-runs.json`
  - workflow run e rollback do deploy

## Resultado esperado

- um incidente principal relacionado a `payments-api`
- causa provavel associada a deploy ou mudanca de infra proxima do impacto
- postmortem com follow-ups e snapshot de 5 Whys
