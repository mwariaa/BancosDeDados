from pathlib import Path
import pandas as pd
from faker import Faker
from random import Random
from datetime import date, timedelta

fake = Faker("pt_BR")
rng = Random(42)
Path("dados").mkdir(exist_ok=True)

cidades = ["Teresina", "São Luís", "Fortaleza", "Recife", "Belém", None]
status_validos = ["ativo", "inativo", "bloqueado"]
clientes = []

for i in range(1, 121):
    nome = fake.name()
    email = fake.email()
    cpf = fake.cpf()
    nascimento = fake.date_of_birth(minimum_age=18, maximum_age=75)
    cidade = rng.choice(cidades)
    status = rng.choice(status_validos)

    # Problemas intencionais
    if i in [7, 34, 88]:
        email = "email_sem_arroba.com"
    if i in [12, 64]:
        cpf = "111.222.333-44"  # duplicado proposital
    if i in [22, 95]:
        nascimento = date.today() + timedelta(days=rng.randint(30, 400))  # futuro
    if i in [41, 79]:
        status = "ATIVO"  # fora do padrão minúsculo
    if i in [17, 52]:
        cidade = None

    clientes.append({
        "cliente_id": i,
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "idade": max(18, int((date.today() - nascimento).days / 365)) if nascimento <= date.today() else -1,
        "data_nascimento": nascimento.isoformat(),
        "cidade": cidade,
        "status_cliente": status,
        "telefone": fake.phone_number()
    })

df_clientes = pd.DataFrame(clientes)

pedidos = []
base = date(2025, 1, 1)
for pid in range(1, 721):
    cliente_id = rng.randint(1, 120)
    total = round(rng.uniform(25, 1500), 2)
    if pid in [15, 147, 412]:
        total = -round(rng.uniform(10, 300), 2)  # valor inválido
    status = rng.choice(["criado", "pago", "entregue", "cancelado"])
    if pid in [81, 303]:
        status = "FINALIZADO"  # fora do domínio esperado
    criado_em = base + timedelta(days=rng.randint(0, 160))
    pedidos.append({
        "pedido_id": pid,
        "cliente_id": cliente_id,
        "total": total,
        "status": status,
        "criado_em": criado_em.isoformat(),
        "canal": rng.choice(["site", "app", "loja"])
    })

df_pedidos = pd.DataFrame(pedidos)

df_clientes.to_csv("dados/clientes_raw.csv", index=False, encoding="utf-8")
df_pedidos.to_csv("dados/pedidos_raw.csv", index=False, encoding="utf-8")

print("=== Dados gerados ===")
print(f"dados/clientes_raw.csv: {len(df_clientes)} clientes")
print(f"dados/pedidos_raw.csv : {len(df_pedidos)} pedidos")
print("\nProblemas intencionais incluídos:")
print("- e-mails inválidos")
print("- CPF duplicado")
print("- datas de nascimento futuras")
print("- cidade nula")
print("- status fora do padrão")
print("- pedidos com total negativo")
print("\nPróximo passo: python 02_diagnostico_qualidade.py")
