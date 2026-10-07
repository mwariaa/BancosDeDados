from pathlib import Path
import json
import pandas as pd

Path("reports").mkdir(exist_ok=True)

arquivos = [
    "dados/clientes_raw.csv",
    "dados/pedidos_raw.csv",
    "reports/diagnostico_qualidade.csv",
    "reports/expectativas_resultado.csv",
    "dados/clientes_silver_mascarado.csv",
    "governance/catalog.json",
    "governance/lineage_log.json",
]

linhas = ["# Resumo da Entrega · Semana 10 · Governança de Dados\n"]
linhas.append("## Arquivos verificados\n")
for arq in arquivos:
    p = Path(arq)
    linhas.append(f"- [{'x' if p.exists() else ' '}] `{arq}`")

linhas.append("\n## Principais achados de qualidade\n")
diag = Path("reports/diagnostico_qualidade.csv")
if diag.exists():
    df = pd.read_csv(diag)
    falhas = df[df["falhas"] > 0].copy()
    if len(falhas):
        for _, r in falhas.iterrows():
            linhas.append(f"- `{r['dataset']}` · {r['dimensao']}: {r['regra']} → {r['falhas']} falhas ({r['pct_falha']}%).")
    else:
        linhas.append("- Nenhuma falha encontrada.")
else:
    linhas.append("- Diagnóstico ainda não executado.")

linhas.append("\n## Evidências que devem aparecer no caderno/PDF\n")
linhas += [
    "- Print do terminal após `00_testar_ambiente.py`.",
    "- Print do relatório `reports/diagnostico_qualidade.html`.",
    "- Print da validação de expectativas (`03_expectativas_gx.py`).",
    "- Print do antes/depois do mascaramento.",
    "- Print do `catalog.json` e/ou `lineage_log.json` no VS Code.",
    "- Respostas escritas explicando risco, técnica aplicada e decisão de governança."
]

Path("reports/resumo_entrega.md").write_text("\n".join(linhas), encoding="utf-8")

# HTML simples
html = "<html><head><meta charset='utf-8'><title>Resumo da Entrega</title><style>body{font-family:Arial;max-width:900px;margin:30px auto;line-height:1.5}code{background:#eee;padding:2px 4px;border-radius:4px}</style></head><body>"
html += "\n".join([f"<p>{l}</p>" if l and not l.startswith("#") and not l.startswith("-") else f"<h2>{l.strip('# ')}</h2>" if l.startswith("#") else f"<li>{l[2:]}</li>" if l.startswith("-") else "" for l in linhas])
html += "</body></html>"
Path("reports/resumo_entrega.html").write_text(html, encoding="utf-8")

print("=== Resumo final gerado ===")
print("reports/resumo_entrega.md")
print("reports/resumo_entrega.html")
print("\nAgora finalize o caderno do aluno e exporte em PDF.")
