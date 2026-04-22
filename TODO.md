# TODO

## Multi-country download

Implementar funções para descarregar dados de múltiplos países de uma só vez.

### Requisitos

- Aceitar uma lista de países (ou `"all"` para todos)
- Reutilizar a mesma sessão HTTP autenticada para todas as transferências (HMD/HFD)
- Adicionar coluna `country` ao DataFrame resultante para identificar a origem
- Suportar paralelismo opcional com `concurrent.futures` para acelerar downloads
- Devolver um único DataFrame concatenado ou um `dict[str, DataFrame]` (opção do utilizador)
- Tratar erros por país sem abortar os restantes (continuar e reportar falhas no fim)

### API proposta

```python
# HMD — retorna DataFrame único com coluna 'country'
df = pyhmfd.read_hmd_web_multi(
    countries=["AUS", "USA", "FRATNP"],
    item="Mx_1x1",
    workers=4,          # downloads paralelos
    on_error="warn",    # ou "raise" para abortar
)

# HFD — idem
df = pyhmfd.read_hfd_web_multi(
    countries=["USA", "SWE", "JPN"],
    item="asfrRR",
    workers=4,
)

# Todos os países disponíveis
df = pyhmfd.read_hmd_web_multi(countries="all", item="Mx_1x1")
```

### Implementação

- [ ] `pyhmfd/multi.py` — lógica de paralelismo e agregação
- [ ] `read_hmd_web_multi()` — wrapper HMD
- [ ] `read_hfd_web_multi()` — wrapper HFD
- [ ] Testes com mock de múltiplos países
- [ ] Exportar funções no `__init__.py`
- [ ] Atualizar README com exemplos
