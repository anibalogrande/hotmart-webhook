import json
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Nome do arquivo onde os dados serão armazenados
DB_FILE = "usuarios.json"

# Função para carregar os usuários do arquivo JSON
def carregar_usuarios():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar os usuários no arquivo JSON
def salvar_usuarios(usuarios):
    with open(DB_FILE, "w") as f:
        json.dump(usuarios, f)

# Inicializa os usuários carregando do arquivo
usuarios = carregar_usuarios()

@app.route('/webhook', methods=['POST'])
def receber_notificacao():
    dados = request.json  # Recebe os dados da Hotmart
    print("🔹 Dados recebidos:", dados)  # Debug: Mostra os dados no log

    if not dados:
        return jsonify({"status": "erro", "mensagem": "Sem dados"}), 400

    email = dados.get('buyer', {}).get('email')
    status = dados.get('status')

    print(f"🔹 Processando email: {email} | Status: {status}")  # Debug

    if email:
        if status == "APPROVED":  # Pagamento aprovado
            usuarios[email] = "ativo"
        elif status in ["CANCELED", "CHARGEBACK", "EXPIRED", "REFUNDED"]:  # Cancelado
            usuarios[email] = "cancelado"

        # Salvar os usuários no arquivo JSON para persistência
        salvar_usuarios(usuarios)

    print("🔹 Usuários registrados:", usuarios)  # Debug

    return jsonify({"status": "sucesso", "mensagem": "Notificação recebida"}), 200

@app.route('/verificar_usuario', methods=['GET'])
def verificar_usuario():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "erro", "mensagem": "Informe um email"}), 400

    # Recarregar os usuários do arquivo antes de consultar
    usuarios_atualizados = carregar_usuarios()
    status = usuarios_atualizados.get(email, "inexistente")

    return jsonify({"status": status})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
