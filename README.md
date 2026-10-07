# Banco de Dados · Semana 10 · Governança de Dados

Prática guiada de **120 minutos** no Visual Studio Code. Não usa Neon.

## O que você vai construir
Você vai montar um mini fluxo de governança em sete checkpoints:

1. preparar o ambiente — 10 min;
2. gerar dados locais com falhas intencionais — 10 min;
3. diagnosticar qualidade — 20 min;
4. validar expectativas com Great Expectations — 20 min;
5. mascarar dados pessoais — 25 min;
6. criar catálogo e linhagem — 20 min;
7. gerar resumo e finalizar o caderno/PDF — 15 min.

**Total: 120 minutos.**

## Como começar no Windows PowerShell

Abra a pasta extraída no VS Code e use **Terminal → New Terminal**.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python 00_testar_ambiente.py
```

Se `python` não funcionar, tente `py` nos mesmos comandos.

> Se o PowerShell bloquear a ativação do ambiente virtual, você pode continuar usando `.venv\Scripts\python.exe` no lugar de `python`.

## Ordem dos scripts

```powershell
python 01_gerar_dados.py
python 02_diagnostico_qualidade.py
python 03_expectativas_gx.py
python 04_mascaramento_lgpd.py
python 05_catalogo_linhagem.py
python 06_resumo_entrega.py
```

## Great Expectations
O script 03 tenta executar **GX Core 1.x real**. Se o pacote não conseguir instalar ou inicializar no computador, o próprio script usa as mesmas regras em pandas e registra o motivo em `reports/gx_fallback_motivo.txt`. Assim a turma não perde a prática inteira por um problema de ambiente.

## Onde ficam os resultados
- `dados/`: CSVs brutos e a versão mascarada.
- `reports/`: diagnósticos, validações e páginas HTML para evidências.
- `governance/`: catálogo e linhagem em JSON.

## Entrega
Abra o **Caderno do Aluno**, responda às perguntas, adicione os prints em cada etapa e use **PDF** no final. O PDF deve conter as sete etapas, respostas e evidências.
