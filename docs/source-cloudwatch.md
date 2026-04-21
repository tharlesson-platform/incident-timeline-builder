# CloudWatch

## Formato suportado

O parser aceita:

- objetos com `alarms`
- objetos com `metric_alarms`
- listas de alarmes

## Campos reconhecidos

- `AlarmName`
- `NewStateValue`
- `StateUpdatedTimestamp`
- `NewStateReason`
- `Dimensions`
- `incident_id`
- `tags`

## Exemplo

```json
{
  "alarms": [
    {
      "AlarmName": "payments-api-5xx-rate",
      "NewStateValue": "ALARM",
      "StateUpdatedTimestamp": "2026-04-20T10:03:00+00:00",
      "NewStateReason": "5XXError exceeded threshold on ALB"
    }
  ]
}
```

## Resultado esperado

- `source=cloudwatch`
- `type=alert`
- severidade derivada do estado do alarme
- tag `customer-impact` inferida para alarmes de erro, disponibilidade ou latencia
