# Guia de reproducao

Este guia ajuda novos colaboradores a gerar uma timeline completa sem precisar descobrir manualmente quais tipos de arquivo o repositorio aceita.

## Pre-requisitos

- Python 3.11+
- dependencias instaladas com `python -m pip install -e .[dev]`

## Primeira execucao recomendada

```bash
incident-timeline-builder build --evidence-path examples --timezone UTC --output-dir artifacts/utc
```

Depois revise:

- `artifacts/utc/timeline.json`
- `artifacts/utc/timeline.md`
- `artifacts/utc/timeline.html`
- `artifacts/utc/postmortem-draft.md`

## Segunda execucao recomendada

```bash
incident-timeline-builder build --evidence-path examples --timezone America/Sao_Paulo --output-dir artifacts/br
```

Esse passo ajuda a validar a normalizacao de timezone, que costuma ser ponto de dor em postmortems.

## O que revisar

- ordenacao cronologica
- agrupamento dos eventos
- causa provavel sugerida
- proximos passos

## Erros comuns

- Misturar diretorios com eventos nao relacionados.
- Rodar sem revisar timezone e depois comparar horarios incorretamente.
- Esperar enriquecimento automatico de fontes externas que ainda nao estao conectadas.

## Fluxo recomendado para onboarding

1. Rodar com timezone UTC
2. Rodar com timezone local
3. Comparar a timeline
4. Criar um diretorio proprio em `examples/` para um incidente simulado do time
