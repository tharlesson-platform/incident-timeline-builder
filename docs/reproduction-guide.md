# Guia de reproducao

Este guia ajuda a validar as funcionalidades entregues no roadmap.

## Pre-requisitos

- Python 3.11+
- dependencias instaladas com `python -m pip install -e .[dev]`

## Passo 1: incidente unico com todas as fontes

```bash
incident-timeline-builder build --evidence-path examples/payments-incident --timezone UTC --output-dir artifacts/payments
```

Revise:

- `artifacts/payments/timeline.json`
- `artifacts/payments/timeline.md`
- `artifacts/payments/timeline.html`
- `artifacts/payments/postmortem-draft.md`

## Passo 2: validar timezone local

```bash
incident-timeline-builder build --evidence-path examples/payments-incident --timezone America/Sao_Paulo --output-dir artifacts/payments-br
```

Valide:

- offsets com `-03:00`
- mesma ordenacao logica da timeline
- postmortem com a mesma hipotese causal

## Passo 3: validar agrupamento automatico

```bash
incident-timeline-builder build --evidence-path examples/multi-incident --timezone UTC --output-dir artifacts/multi
```

Valide:

- dois ou mais incidentes em `timeline.json`
- `primary_incident_id` apontando para o cluster mais relevante
- eventos de `catalog-api` e `checkout-api` em grupos separados

## Erros comuns

- apontar `--evidence-path` para `examples/` sem `--recursive` e esperar leitura dos subdiretorios
- comparar horarios sem considerar o timezone solicitado
- misturar exportacoes de incidentes diferentes no mesmo diretorio sem tags de servico
