from pathlib import Path
import pandas as pd

Path("reports").mkdir(exist_ok=True)
clientes_path = Path("dados/clientes_raw.csv")
pedidos_path = Path("dados/pedidos_raw.csv")

if not clientes_path.exists() or not pedidos_path.exists():
    print("Arquivos não encontrados. Execute primeiro: python 01_gerar_dados.py")
    raise SystemExit(1)

clientes = pd.read_csv(clientes_path)
pedidos = pd.read_csv(pedidos_path)

print("=== Diagnóstico de Qualidade ===")

linhas = []

def add(dataset, dimensao, regra, falhas, total, risco):
    linhas.append({
        "dataset": dataset,
        "dimensao": dimensao,
        "regra": regra,
        "falhas": int(falhas),
        "total": int(total),
        "pct_falha": round((falhas / total * 100), 2) if total else 0,
        "risco": risco
    })

# Clientes
for col in ["nome", "cpf", "email", "cidade", "status_cliente"]:
    add("clientes", "Completude", f"{col} não pode ser nulo", clientes[col].isna().sum(), len(clientes), "cadastro incompleto")

add("clientes", "Unicidade", "CPF deve ser único", clientes.duplicated(subset=["cpf"]).sum(), len(clientes), "duplicidade de pessoa")
add("clientes", "Acurácia", "email deve conter @", (~clientes["email"].astype(str).str.contains("@", na=False)).sum(), len(clientes), "contato inválido")
datas = pd.to_datetime(clientes["data_nascimento"], errors="coerce")
add("clientes", "Temporalidade", "data_nascimento não pode ser futura", (datas > pd.Timestamp.today()).sum(), len(clientes), "idade/data impossível")
add("clientes", "Conformidade", "status_cliente em {ativo,inativo,bloqueado}", (~clientes["status_cliente"].isin(["ativo", "inativo", "bloqueado"])).sum(), len(clientes), "domínio fora do padrão")

# Pedidos
add("pedidos", "Completude", "cliente_id não pode ser nulo", pedidos["cliente_id"].isna().sum(), len(pedidos), "pedido sem cliente")
add("pedidos", "Acurácia", "total deve ser positivo", (pedidos["total"] <= 0).sum(), len(pedidos), "métrica financeira inválida")
add("pedidos", "Conformidade", "status em {criado,pago,entregue,cancelado}", (~pedidos["status"].isin(["criado", "pago", "entregue", "cancelado"])).sum(), len(pedidos), "status fora do padrão")
add("pedidos", "Temporalidade", "criado_em deve ser data válida", pd.to_datetime(pedidos["criado_em"], errors="coerce").isna().sum(), len(pedidos), "data inválida")

resumo = pd.DataFrame(linhas)
resumo.to_csv("reports/diagnostico_qualidade.csv", index=False, encoding="utf-8")
resumo.to_html("reports/diagnostico_qualidade.html", index=False)

print(resumo.to_string(index=False))
print("\nRelatórios gerados:")
print("- reports/diagnostico_qualidade.csv")
print("- reports/diagnostico_qualidade.html")
print("\nPróximo passo: python 03_expectativas_gx.py")
