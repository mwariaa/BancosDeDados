from pathlib import Path
import hashlib
import os
import pandas as pd

Path("dados").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

clientes_path = Path("dados/clientes_raw.csv")
if not clientes_path.exists():
    print("Arquivo clientes_raw.csv não encontrado. Execute: python 01_gerar_dados.py")
    raise SystemExit(1)

df_raw = pd.read_csv(clientes_path)
salt = os.getenv("HASH_SALT", "salt_aula_semana10")

def hash_campo(valor):
    return hashlib.sha256(f"{salt}{valor}".encode("utf-8")).hexdigest()[:16]

def faixa_etaria(idade):
    try:
        idade = int(idade)
    except Exception:
        return "desconhecida"
    if idade < 0:
        return "invalida"
    if idade <= 24:
        return "18-24"
    if idade <= 34:
        return "25-34"
    if idade <= 44:
        return "35-44"
    if idade <= 59:
        return "45-59"
    return "60+"

df_silver = df_raw.copy()

# Supressão: removemos campos diretamente identificadores
colunas_removidas = [c for c in ["nome", "cpf", "telefone"] if c in df_silver.columns]
df_silver = df_silver.drop(columns=colunas_removidas)

# Hash com salt: mantém possibilidade de comparação sem expor e-mail real
df_silver["email_hash"] = df_silver["email"].astype(str).apply(hash_campo)
df_silver = df_silver.drop(columns=["email"])

# Generalização: idade exata vira faixa
df_silver["faixa_etaria"] = df_silver["idade"].apply(faixa_etaria)
df_silver = df_silver.drop(columns=["idade"])

df_silver.to_csv("dados/clientes_silver_mascarado.csv", index=False, encoding="utf-8")

amostra = pd.concat([
    df_raw.head(8).assign(versao="ANTES_RAW"),
    df_silver.head(8).assign(versao="DEPOIS_SILVER")
], ignore_index=True, sort=False)
amostra.to_html("reports/antes_depois_mascaramento.html", index=False)

resumo = pd.DataFrame([
    {"tecnica":"supressao", "aplicacao":"nome, cpf e telefone removidos", "objetivo":"reduzir exposição direta"},
    {"tecnica":"hash+salt", "aplicacao":"email -> email_hash", "objetivo":"manter chave de comparação sem mostrar e-mail"},
    {"tecnica":"generalizacao", "aplicacao":"idade -> faixa_etaria", "objetivo":"preservar análise sem idade exata"},
])
resumo.to_csv("reports/resumo_mascaramento.csv", index=False, encoding="utf-8")

print("=== Mascaramento LGPD aplicado ===")
print(f"Colunas removidas: {colunas_removidas}")
print("email -> email_hash")
print("idade -> faixa_etaria")
print("\nAntes (raw):")
print(df_raw[["cliente_id", "nome", "cpf", "email", "idade"]].head(5).to_string(index=False))
print("\nDepois (silver mascarado):")
print(df_silver[["cliente_id", "email_hash", "faixa_etaria", "cidade", "status_cliente"]].head(5).to_string(index=False))
print("\nArquivos gerados:")
print("- dados/clientes_silver_mascarado.csv")
print("- reports/antes_depois_mascaramento.html")
print("- reports/resumo_mascaramento.csv")
print("\nPróximo passo: python 05_catalogo_linhagem.py")
