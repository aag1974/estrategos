"""
Gera credencial pra adicionar no login do Estrategos.

Uso:
  python3 gerar_credencial.py

Vai pedir nome de usuário e senha. Adiciona (ou atualiza) a entrada
no arquivo credenciais.json local. Esse arquivo NÃO é versionado.

Lembrete: o login é decorativo (client-side). Quem abrir o devtools
encontra o hash. Use pra evitar acesso casual, não como segurança real.
"""
import hashlib
import json
from getpass import getpass
from pathlib import Path

CRED_PATH = Path("credenciais.json")

print("\n  Gerador de credenciais — Estrategos")
print("  ────────────────────────────────────")

user = input("  Nome de usuário (lowercase, sem espaços): ").lower().strip()
if not user:
    print("  Cancelado.")
    raise SystemExit(1)

pwd = getpass("  Senha: ")
pwd_confirm = getpass("  Confirme a senha: ")

if pwd != pwd_confirm:
    print("\n  As senhas não conferem. Cancelado.")
    raise SystemExit(1)

if len(pwd) < 4:
    print("\n  Senha muito curta (mínimo 4 caracteres). Cancelado.")
    raise SystemExit(1)

h = hashlib.sha256(pwd.encode("utf-8")).hexdigest()

# Carrega arquivo existente ou cria novo
if CRED_PATH.exists():
    try:
        creds = json.loads(CRED_PATH.read_text(encoding="utf-8"))
        if not isinstance(creds, dict):
            creds = {}
    except Exception:
        creds = {}
else:
    creds = {}

acao = "atualizado" if user in creds else "criado"
creds[user] = h

CRED_PATH.write_text(
    json.dumps(creds, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8"
)

print(f"\n  ✅ Usuário '{user}' {acao} em {CRED_PATH}")
print(f"\n  Agora rebuild os dashboards:")
print(f"    python3 fase4_v2.py && python3 injeta_geopolitica.py && python3 injeta_candidato.py\n")
