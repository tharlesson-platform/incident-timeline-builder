# Examples

Os exemplos agora cobrem o roadmap entregue:

- `payments-incident/`
  - incidente unico com evidencias de CloudWatch, Slack, GitHub Actions e eventos genericos
- `multi-incident/`
  - duas janelas de incidente no mesmo lote para validar agrupamento automatico por tags e proximidade temporal

## Comandos recomendados

```bash
incident-timeline-builder build --evidence-path examples/payments-incident --timezone UTC --output-dir artifacts/payments
incident-timeline-builder build --evidence-path examples/multi-incident --timezone UTC --output-dir artifacts/multi
```

## O que cada exemplo valida

- `payments-incident`
  - parsers dedicados de CloudWatch, Slack e GitHub Actions
  - consolidacao de timeline
  - template completo de postmortem

- `multi-incident`
  - agrupamento automatico por tags e servico
  - eleicao do incidente principal para RCA
  - manutencao de multiplos clusters no mesmo report
