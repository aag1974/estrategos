"""
servidor_diag.py — servidor local para o Diagnóstico do dashboard SPE.

Uso:
  python3 servidor_diag.py

Sobe um servidor em http://127.0.0.1:8765 que:
  - serve o dashboard (dashboard_com_candidato.html) na raiz
  - expõe POST /api/gerar para gerar o relatório Word in-memory
    (recebe JSON com a config; devolve o .docx como download)

O navegador é aberto automaticamente. Para parar, Ctrl+C.
"""

from pathlib import Path
import io, threading, webbrowser, traceback, sys
from flask import Flask, request, send_file, send_from_directory, jsonify

import gerar_relatorio_diag as gen

ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = "dashboard_com_candidato.html"
PORT = 8765

app = Flask(__name__, static_folder=None)
_DATA = {"ready": False}
_LOCK = threading.Lock()


def _ensure_dados():
    """Carrega candidatos + dados das RAs uma vez (custoso: lê 1.1M linhas do TSE)."""
    if _DATA["ready"]:
        return
    with _LOCK:
        if _DATA["ready"]:
            return
        print("[servidor] Carregando dados (uma única vez — pode demorar ~30s)...", flush=True)
        d = gen.carregar_dados()
        _DATA.update(d)
        _DATA["ready"] = True
        print(f"[servidor] OK — {len(d['cands'])} candidatos, {len(d['dados_ra'])} RAs em cache.", flush=True)


@app.route("/")
def index():
    p = ROOT / DASHBOARD_FILE
    if not p.exists():
        return (f"<h1>{DASHBOARD_FILE} não encontrado</h1>"
                f"<p>Rode o pipeline antes: "
                f"<code>python3 gerar_estrategos.py</code></p>"), 404
    return send_from_directory(str(ROOT), DASHBOARD_FILE)


@app.route("/health")
def health():
    return jsonify({"ok": True, "data_ready": _DATA["ready"]})


@app.route("/api/gerar", methods=["POST"])
def api_gerar():
    try:
        cfg = request.get_json(force=True, silent=False)
        if not cfg:
            return jsonify({"erro": "JSON inválido."}), 400
        _ensure_dados()
        bio = io.BytesIO()
        meta = gen.gerar(cfg, {"cands": _DATA["cands"], "dados_ra": _DATA["dados_ra"]},
                         bio, log=lambda m: print("[gerar]", m, flush=True))
        bio.seek(0)
        fname = f"relatorio_diag_{meta['slug']}.docx"
        return send_file(
            bio,
            as_attachment=True,
            download_name=fname,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except ValueError as e:
        print("[servidor] ValueError:", e, flush=True)
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": f"Falha ao gerar: {e}"}), 500


def _open_browser():
    webbrowser.open(f"http://127.0.0.1:{PORT}/")


if __name__ == "__main__":
    print()
    print("  servidor_diag.py")
    print("  " + "─" * 40)
    print(f"  http://127.0.0.1:{PORT}/   (Ctrl+C para parar)")
    print()
    # Pré-carrega em thread separada para o servidor ficar responsivo na home
    threading.Thread(target=_ensure_dados, daemon=True).start()
    threading.Timer(1.2, _open_browser).start()
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
