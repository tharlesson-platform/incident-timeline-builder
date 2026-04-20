# Incident Timeline Builder Architecture

## Visão geral

Construtor de timelines e rascunhos de postmortem a partir de múltiplas fontes de evidência locais.

## Fluxo

- Parsers leem CSV/JSON exportados de alertas, pipelines, deploys e eventos de infra.
- Normalizers convertem timestamps para um formato consistente.
- O correlator ordena e destaca a provável causa inicial para acelerar o postmortem.

## Extensões futuras

- Adicionar integração com Slack, CloudWatch, Alertmanager e GitHub Actions.
- Anexar links de evidência por evento.
- Gerar template de postmortem com campos RCA e owner automaticamente.
