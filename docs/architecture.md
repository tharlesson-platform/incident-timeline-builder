# Architecture

## Visao geral

O `incident-timeline-builder` transforma evidencias locais em um report unico:

1. `parsers/`
   - identifica e converte arquivos `CSV` e `JSON` em eventos normalizados
   - reconhece formatos dedicados de CloudWatch, Slack e GitHub Actions
2. `normalizers/`
   - converte timestamps para o timezone solicitado
3. `correlators/`
   - agrupa eventos em incidentes usando `incident_id`, servico, tags e proximidade temporal
   - escolhe o incidente principal
   - gera resumo e 5 Whys
4. `reporters/`
   - renderiza timeline em JSON, Markdown e HTML
   - monta `postmortem-draft.md`

## Decisoes principais

- integracoes sao baseadas em arquivos exportados e nao em chamadas online
- agrupamento automatico funciona mesmo sem `incident_id` explicito
- o postmortem e gerado a partir do incidente principal, sem perder os outros clusters no report

## Modelo de evento interno

Cada evidencia e convertida para este shape logico:

```json
{
  "timestamp": "2026-04-20T07:03:00-03:00",
  "type": "alert",
  "severity": "critical",
  "source": "cloudwatch",
  "message": "payments-api-5xx-rate: 5XXError exceeded threshold on ALB",
  "tags": ["payments", "customer-impact", "cloudwatch"],
  "incident_id": "payments-apr20",
  "owner": "sre-oncall",
  "service": "payments-api",
  "link": null,
  "metadata": {}
}
```

## Evolucao futura opcional

- links profundos de evidencia por evento
- export adicional para CSV
- heuristicas avancadas de correlacao com score configuravel
