# CLI Reference

## Comando `build`

```bash
incident-timeline-builder build --evidence-path <path> --timezone <iana-tz> [--output-dir <dir>] [--recursive] [--title <name>]
```

### Opcoes

- `--evidence-path`
  - arquivo ou diretório com evidencias
- `--timezone`
  - timezone IANA do report final, como `UTC` ou `America/Sao_Paulo`
- `--output-dir`
  - pasta de saida. Default: `artifacts`
- `--recursive`
  - percorre subdiretorios para coletar evidencias
- `--title`
  - substitui o titulo padrao do report

## Comando `version`

```bash
incident-timeline-builder version
```
