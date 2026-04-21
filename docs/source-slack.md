# Slack

## Formato suportado

O parser aceita:

- arrays de mensagens
- objetos com `channel` e `messages`

## Campos reconhecidos

- `ts`
- `text`
- `user`
- `service`
- `incident_id`
- `tags`

## Exemplo

```json
{
  "channel": "inc-payments-apr20",
  "messages": [
    {
      "ts": "1776688990.000000",
      "text": "Seeing customer impact on checkout, 5xx is climbing fast."
    }
  ]
}
```

## Resultado esperado

- `source=slack`
- `type=chatops`
- severidade inferida a partir do texto
- tags adicionais para `deploy`, `rollback` e `customer-impact`
