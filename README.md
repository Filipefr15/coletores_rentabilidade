# 📈 Coletores de Rentabilidade

Automação em Python que coleta diariamente/mensalmente os principais índices financeiros do mercado brasileiro e internacional e os persiste em um banco PostgreSQL, substituindo a consulta manual em múltiplos sites por um processo automatizado.

## Sobre o projeto

Cada índice tem um "coletor" dedicado, responsável por abrir a página de origem via Selenium, extrair a tabela de dados, tratar/normalizar os valores e gravar (com upsert) em uma tabela própria no banco. O `runner.py` orquestra a execução de todos os coletores para uma ou mais datas.

### Índices coletados

| Índice | Fonte | Script |
| --- | --- | --- |
| SELIC | Banco Central (BCB) | `selic_collector.py` |
| IPCA | IPEA Data | `ipca_collector.py` |
| IBOVESPA (histórico) | Investing.com | `ibov_collector.py` |
| IMA, IDkA, IRF-M | ANBIMA | `ima_idka_collector.py` |
| Índices de renda variável (IBOVESPA, SMLL, IBRX50, ICON, VALE3, PETR4, BDRX) | InfoMoney | `rv_index_collector.py` |
| Câmbio (Dólar PTAX) | IPEA Data | `tx_cambio_collector.py` |
| S&P 500 | Yahoo Finance | `sEp_500_collector.py` |

## Tecnologias

- Python
- Selenium (automação web / scraping)
- PostgreSQL + psycopg2
- pandas
- Docker

## Estrutura do projeto

```
├── src/                    # Scripts de coleta usados em produção (runner.py, Docker)
│   ├── segmentacao/         # Utilitário compartilhado de inicialização do WebDriver
│   └── *_collector.py       # Um coletor por índice/fonte
├── notebooks/               # Notebooks de exploração e apresentação dos dados
├── data/                    # Amostras de dados já coletados (CSV)
├── Dockerfile
└── requirements.txt
```

## Como usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e preencha com os dados do seu banco PostgreSQL:
   ```bash
   cp .env.example .env
   ```
3. Ajuste as datas desejadas em `src/runner.py` e execute:
   ```bash
   cd src
   python runner.py
   ```

### Com Docker

```bash
docker build -t coletores-rentabilidade .
docker run --env-file .env coletores-rentabilidade
```

## Notebooks

A pasta `notebooks/` contém as versões exploratórias de cada coletor (usadas durante o desenvolvimento) e uma apresentação com a análise dos dados de SELIC/IPCA coletados.

---

### 🤖 Coletores de Rentabilidade

Automação desenvolvida para coletar periodicamente os principais índices financeiros do mercado brasileiro e internacional (SELIC, IPCA, IBOVESPA, câmbio, S&P 500, entre outros).

O programa substituiu a consulta manual em múltiplos sites por um processo automatizado, centralizando os dados em um único banco PostgreSQL.

**Tecnologias:** Python, Selenium e automação web.

**Código:** `[ADICIONAR LINK DO REPOSITÓRIO OU DEMONSTRAÇÃO]`
