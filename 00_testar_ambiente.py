from pathlib import Path
import importlib.util
import sys

print("=== Semana 10 · Governança de Dados · Teste de ambiente ===")
print(f"Python: {sys.version.split()[0]}")

if sys.version_info < (3, 10):
    print("\nATENÇÃO: Great Expectations 1.x atual requer Python 3.10 ou superior.")
    print("Os demais scripts da prática funcionam com pandas, mas recomenda-se atualizar o Python.")

obrigatorias = ["pandas", "faker"]
opcionais = ["great_expectations"]
faltando = []

for pacote in obrigatorias:
    ok = importlib.util.find_spec(pacote) is not None
    print(f"{'OK   ' if ok else 'FALTA'} {pacote}")
    if not ok:
        faltando.append(pacote)

for pacote in opcionais:
    ok = importlib.util.find_spec(pacote) is not None
    print(f"{'OK   ' if ok else 'AVISO'} {pacote}" + ("" if ok else " — o script 03 possui fallback em pandas para não travar a aula"))

for pasta in ["dados", "reports", "governance"]:
    Path(pasta).mkdir(exist_ok=True)
    print(f"OK   pasta {pasta}/")

if faltando:
    print("\nInstale as dependências com:")
    print("python -m pip install -r requirements.txt")
    raise SystemExit(1)

print("\nAMBIENTE OK. Próximo passo: python 01_gerar_dados.py")
