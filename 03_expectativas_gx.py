from pathlib import Path
import json
import pandas as pd

Path("reports").mkdir(exist_ok=True)
clientes_path = Path("dados/clientes_raw.csv")
pedidos_path = Path("dados/pedidos_raw.csv")
if not clientes_path.exists() or not pedidos_path.exists():
    print("Arquivos não encontrados. Execute primeiro: python 01_gerar_dados.py")
    raise SystemExit(1)

clientes = pd.read_csv(clientes_path)
pedidos = pd.read_csv(pedidos_path)

# As mesmas regras existem em dois formatos:
# 1) Expectações GX reais, quando Great Expectations está disponível.
# 2) Fallback em pandas, para a aula não parar se a instalação do GX falhar.
regras = [
    {"dataset":"clientes", "coluna":"cliente_id", "regra":"nao_nulo", "descricao":"cliente_id não pode ser nulo"},
    {"dataset":"clientes", "coluna":"cpf", "regra":"unico", "descricao":"cpf deve ser único"},
    {"dataset":"clientes", "coluna":"email", "regra":"regex", "valor":r".+@.+", "descricao":"email deve conter @"},
    {"dataset":"clientes", "coluna":"status_cliente", "regra":"em_conjunto", "valor":["ativo","inativo","bloqueado"], "descricao":"status_cliente deve estar no conjunto permitido"},
    {"dataset":"pedidos", "coluna":"pedido_id", "regra":"unico", "descricao":"pedido_id deve ser único"},
    {"dataset":"pedidos", "coluna":"cliente_id", "regra":"nao_nulo", "descricao":"cliente_id não pode ser nulo"},
    {"dataset":"pedidos", "coluna":"total", "regra":"maior_que", "valor":0, "descricao":"total deve ser positivo"},
    {"dataset":"pedidos", "coluna":"status", "regra":"em_conjunto", "valor":["criado","pago","entregue","cancelado"], "descricao":"status deve estar no conjunto permitido"},
]


def validar_pandas(df, r):
    col = r["coluna"]
    tipo = r["regra"]
    if tipo == "nao_nulo":
        falhas = df[col].isna().sum()
    elif tipo == "unico":
        # duplicated(keep=False) conta todas as linhas envolvidas numa duplicidade.
        falhas = df[col].duplicated(keep=False).sum()
    elif tipo == "regex":
        falhas = (~df[col].astype(str).str.match(r["valor"], na=False)).sum()
    elif tipo == "em_conjunto":
        falhas = (~df[col].isin(r["valor"])).sum()
    elif tipo == "maior_que":
        falhas = (df[col] <= r["valor"]).sum()
    else:
        falhas = len(df)
    return int(falhas)


def executar_gx():
    import great_expectations as gx

    context = gx.get_context(mode="ephemeral")
    context.enable_analytics(False)

    def criar_batch(nome, dataframe):
        fonte = context.data_sources.add_pandas(name=f"fonte_{nome}")
        asset = fonte.add_dataframe_asset(name=f"asset_{nome}")
        definicao = asset.add_batch_definition_whole_dataframe(name="dataset_completo")
        return definicao.get_batch(batch_parameters={"dataframe": dataframe})

    batches = {
        "clientes": criar_batch("clientes", clientes),
        "pedidos": criar_batch("pedidos", pedidos),
    }

    resultados = []
    resultados_brutos = []

    for r in regras:
        if r["regra"] == "nao_nulo":
            exp = gx.expectations.ExpectColumnValuesToNotBeNull(column=r["coluna"])
        elif r["regra"] == "unico":
            exp = gx.expectations.ExpectColumnValuesToBeUnique(column=r["coluna"])
        elif r["regra"] == "regex":
            exp = gx.expectations.ExpectColumnValuesToMatchRegex(column=r["coluna"], regex=r["valor"])
        elif r["regra"] == "em_conjunto":
            exp = gx.expectations.ExpectColumnValuesToBeInSet(column=r["coluna"], value_set=r["valor"])
        elif r["regra"] == "maior_que":
            exp = gx.expectations.ExpectColumnValuesToBeBetween(column=r["coluna"], min_value=r["valor"], strict_min=True)
        else:
            continue

        vr = batches[r["dataset"]].validate(exp, result_format="SUMMARY")
        bruto = vr.to_json_dict() if hasattr(vr, "to_json_dict") else dict(vr)
        falhas = bruto.get("result", {}).get("unexpected_count")
        if falhas is None:
            falhas = validar_pandas(clientes if r["dataset"] == "clientes" else pedidos, r)
        resultados.append({
            "motor": "Great Expectations",
            "dataset": r["dataset"],
            "expectativa": r["descricao"],
            "coluna": r["coluna"],
            "sucesso": bool(bruto.get("success", False)),
            "falhas": int(falhas),
            "total": int(len(clientes if r["dataset"] == "clientes" else pedidos)),
        })
        resultados_brutos.append({"regra": r, "resultado_gx": bruto})

    with open("reports/gx_resultados_brutos.json", "w", encoding="utf-8") as f:
        json.dump(resultados_brutos, f, ensure_ascii=False, indent=2, default=str)
    return resultados, "Great Expectations"


def executar_fallback(motivo):
    resultados = []
    for r in regras:
        df = clientes if r["dataset"] == "clientes" else pedidos
        falhas = validar_pandas(df, r)
        resultados.append({
            "motor": "pandas (fallback)",
            "dataset": r["dataset"],
            "expectativa": r["descricao"],
            "coluna": r["coluna"],
            "sucesso": falhas == 0,
            "falhas": falhas,
            "total": len(df),
        })
    Path("reports/gx_fallback_motivo.txt").write_text(str(motivo), encoding="utf-8")
    return resultados, "pandas (fallback)"


print("=== Validação declarativa de expectativas ===")
try:
    resultados, motor = executar_gx()
    print("Motor: Great Expectations (GX Core 1.x)")
except Exception as e:
    resultados, motor = executar_fallback(f"{type(e).__name__}: {e}")
    print("Motor: pandas (fallback)")
    print("O GX não pôde ser executado neste computador, então a aula continua com as mesmas regras em pandas.")
    print("Motivo registrado em reports/gx_fallback_motivo.txt")

with open("reports/expectativas_declarativas.json", "w", encoding="utf-8") as f:
    json.dump(regras, f, ensure_ascii=False, indent=2)

df_res = pd.DataFrame(resultados)
df_res.to_csv("reports/expectativas_resultado.csv", index=False, encoding="utf-8")
df_res.to_html("reports/expectativas_resultado.html", index=False)

for _, r in df_res.iterrows():
    status = "PASSOU" if r["sucesso"] else "FALHOU"
    print(f"{status:6} | {r['dataset']:8} | {r['expectativa']} | falhas={r['falhas']}")

print("\nArquivos gerados:")
print("- reports/expectativas_declarativas.json")
print("- reports/expectativas_resultado.csv")
print("- reports/expectativas_resultado.html")
if Path("reports/gx_resultados_brutos.json").exists():
    print("- reports/gx_resultados_brutos.json")
print("\nPróximo passo: python 04_mascaramento_lgpd.py")
