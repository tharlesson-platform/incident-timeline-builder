# Examples

Os exemplos deste repositorio foram pensados para mostrar a consolidacao de eventos em formatos diferentes.

## Arquivos

- `events.json`
  - Lote de eventos estruturados em JSON.

- `events.csv`
  - Lote complementar em CSV para mostrar normalizacao e unificacao de fontes.

## Comando recomendado

```bash
incident-timeline-builder build --evidence-path examples --timezone UTC --output-dir artifacts/examples
```

## Saidas esperadas

- `timeline.json`
- `timeline.md`
- `timeline.html`
- `postmortem-draft.md`

## Ordem recomendada

1. Rode o exemplo em UTC
2. Rode o mesmo exemplo em `America/Sao_Paulo`
3. Compare a timeline e a normalizacao de tempo
