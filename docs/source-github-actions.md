# GitHub Actions

## Formato suportado

O parser aceita:

- objetos com `workflow_runs`
- objetos com `jobs`
- listas equivalentes

## Campos reconhecidos

- `name`
- `status`
- `conclusion`
- `run_started_at`
- `updated_at`
- `html_url`
- `service`
- `environment`

## Exemplo

```json
{
  "workflow_runs": [
    {
      "name": "Deploy payments-api to prod",
      "conclusion": "success",
      "run_started_at": "2026-04-20T09:58:00+00:00",
      "updated_at": "2026-04-20T10:00:30+00:00"
    }
  ]
}
```

## Resultado esperado

- `source=github-actions`
- `type=deploy` quando o nome do workflow contem `deploy`
- `type=pipeline` nos demais casos
- severidade inferida a partir de `status` e `conclusion`
