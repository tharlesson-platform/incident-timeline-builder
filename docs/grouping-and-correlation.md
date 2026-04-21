# Grouping And Correlation

## Como o agrupamento funciona

O correlator tenta esta ordem:

1. usar `incident_id` explicito
2. agrupar por mesmo servico
3. agrupar por tags significativas compartilhadas
4. respeitar uma janela de proximidade temporal

## Tags significativas

O algoritmo ignora tags genericas como:

- `deploy`
- `rollback`
- `cloudwatch`
- `slack`
- `github-actions`
- `customer-impact`

Isso evita que todo o lote caia no mesmo grupo apenas por compartilhar uma tag operacional.

## Eleicao do incidente principal

O incidente principal e o cluster com melhor combinacao de:

- quantidade de eventos com `customer-impact`
- severidade maxima
- quantidade total de eventos

Esse cluster alimenta a analise de 5 Whys e o `postmortem-draft.md`.
