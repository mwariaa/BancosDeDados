from pathlib import Path
import json
from datetime import datetime
import pandas as pd

Path("governance").mkdir(exist_ok=True)

clientes_silver = Path("dados/clientes_silver_mascarado.csv")
diagnostico = Path("reports/diagnostico_qualidade.csv")
expectativas = Path("reports/expectativas_resultado.csv")
if not clientes_silver.exists():
    print("Arquivo mascarado não encontrado. Execute: python 04_mascaramento_lgpd.py")
    raise SystemExit(1)

df = pd.read_csv(clientes_silver)

catalogo = {
    "gerado_em": datetime.now().isoformat(),
    "datasets": [
        {
            "nome": "dados/clientes_raw.csv",
            "descricao": "Cadastro bruto de clientes com dados pessoais e problemas intencionais para diagnóstico.",
            "owner": "disciplina-banco-dados",
            "formato": "csv",
            "sensibilidade": "dados_pessoais_restrito",
            "frequencia_atualizacao": "gerado sob demanda na prática",
            "colunas": [
                {"nome": "cliente_id", "tipo": "inteiro", "lgpd": False, "descricao": "Identificador técnico do cliente"},
                {"nome": "nome", "tipo": "texto", "lgpd": True, "descricao": "Nome completo"},
                {"nome": "cpf", "tipo": "texto", "lgpd": True, "descricao": "Documento pessoal"},
                {"nome": "email", "tipo": "texto", "lgpd": True, "descricao": "Contato pessoal"},
                {"nome": "telefone", "tipo": "texto", "lgpd": True, "descricao": "Contato pessoal"}
            ]
        },
        {
            "nome": "dados/clientes_silver_mascarado.csv",
            "descricao": "Versão governada para análise: sem nome, CPF e telefone; e-mail hasheado; idade generalizada.",
            "owner": "disciplina-banco-dados",
            "formato": "csv",
            "sensibilidade": "interno_anonimizado_parcial",
            "frequencia_atualizacao": "gerado após mascaramento",
            "colunas": [
                {"nome": c, "tipo": str(df[c].dtype), "lgpd": c in ["email_hash"], "descricao": "Coluna resultante do pipeline de mascaramento"} for c in df.columns
            ]
        }
    ]
}

linhagem = [
    {
        "ts": datetime.now().isoformat(),
        "entrada": "script 01",
        "saida": "dados/clientes_raw.csv",
        "transformacoes": ["geração local de dados com problemas controlados para aprendizagem"]
    },
    {
        "ts": datetime.now().isoformat(),
        "entrada": "dados/clientes_raw.csv",
        "saida": "reports/diagnostico_qualidade.csv",
        "transformacoes": ["cálculo de nulos", "duplicatas", "e-mails inválidos", "datas futuras", "domínios fora do padrão"]
    },
    {
        "ts": datetime.now().isoformat(),
        "entrada": "dados/clientes_raw.csv",
        "saida": "dados/clientes_silver_mascarado.csv",
        "transformacoes": ["supressão de nome/cpf/telefone", "hash+salt do email", "idade para faixa_etaria"]
    },
    {
        "ts": datetime.now().isoformat(),
        "entrada": "dados/clientes_silver_mascarado.csv",
        "saida": "governance/catalog.json",
        "transformacoes": ["documentação de metadados", "classificação de sensibilidade", "descrição de colunas"]
    }
]

with open("governance/catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalogo, f, ensure_ascii=False, indent=2)

with open("governance/lineage_log.json", "w", encoding="utf-8") as f:
    json.dump(linhagem, f, ensure_ascii=False, indent=2)

print("=== Catálogo e linhagem gerados ===")
print("governance/catalog.json")
print("governance/lineage_log.json")
print("\nDatasets no catálogo:")
for ds in catalogo["datasets"]:
    print(f"- {ds['nome']} | sensibilidade: {ds['sensibilidade']}")

print("\nPróximo passo: python 06_resumo_entrega.py")
