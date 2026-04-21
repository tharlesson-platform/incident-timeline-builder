# Incident Timeline Builder

CLI para consolidar evidências, montar timelines de incidentes e gerar rascunho de postmortem.

## Problema que resolve

- Durante incidentes, eventos relevantes ficam espalhados entre alertas, deploys, pipelines e logs exportados.
- Montar timeline manual consome tempo e costuma atrasar postmortems.
- A ferramenta ordena evidências, sugere causa provável, gera análise de 5 Whys e produz material pronto para revisão.

## Arquitetura

- Parsers modulares para JSON/CSV locais.
- Normalização de timestamps para uma linha do tempo coerente.
- Correlator simples que destaca evento crítico mais provável e próximos passos.

## Estrutura do projeto

```text
.
|-- cli/
|-- parsers/
|-- normalizers/
|-- correlators/
|-- reporters/
|-- examples/
|-- tests/
|-- docs/
|-- pyproject.toml
|-- Makefile
|-- .github/workflows/ci.yml
|-- README.md
|-- LICENSE
|-- NOTICE
```

## Como executar

```bash
python -m pip install -e .[dev]
incident-timeline-builder build --evidence-path examples --timezone UTC
```

## Reproducao guiada

- Primeiro passo:
  - `incident-timeline-builder build --evidence-path examples --timezone UTC --output-dir artifacts/utc`
- Segundo passo:
  - `incident-timeline-builder build --evidence-path examples --timezone America/Sao_Paulo --output-dir artifacts/br`
- Para reproducao mais assertiva:
  - consulte `examples/README.md`
  - siga `docs/reproduction-guide.md`

## Exemplos reais

- `incident-timeline-builder build --evidence-path examples --timezone UTC`
- `incident-timeline-builder build --evidence-path ./incident-2026-04-20 --timezone America/Sao_Paulo`
- `incident-timeline-builder build --evidence-path examples --timezone America/Sao_Paulo --output-dir artifacts/br`

## Como isso ajuda SREs no dia a dia

- Reduz tempo para fechar timeline e iniciar o postmortem.
- Ajuda a juntar sinais de fontes heterogêneas com ordenação consistente.
- Estrutura um primeiro rascunho dos 5 porquês para acelerar RCA colaborativa.
- Cria base objetiva para RCA, comunicação e aprendizado.

## Roadmap

- Integração com CloudWatch, Slack e GitHub Actions.
- Template completo de postmortem.
- Agrupamento automático por incidente e tags.

## Licença

Este projeto está licenciado sob a Apache License 2.0. Consulte o arquivo `LICENSE` para mais detalhes.

## Atribuição

Este projeto foi desenvolvido e publicado por **Tharlesson**.
Caso você utilize este material como base em ambientes internos, estudos, adaptações ou redistribuições, preserve os créditos de autoria e os avisos de licença aplicáveis.

## Créditos e Uso

Este repositório foi criado com foco em automação, padronização operacional e melhoria da rotina de profissionais de SRE, DevOps, Cloud e Plataforma.

Você pode:
- estudar
- reutilizar
- adaptar
- evoluir este projeto dentro do seu contexto

Ao reutilizar ou derivar este material:
- mantenha os avisos de licença
- preserve os créditos de autoria quando aplicável
- documente alterações relevantes feitas sobre a base original

## Autor

**Tharlesson**  
GitHub: https://github.com/tharlesson
