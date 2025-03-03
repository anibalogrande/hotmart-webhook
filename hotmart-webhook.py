from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Simulando um banco de dados temporário
usuarios = {}

@app.route('/webhook', methods=['POST'])
def receber_notificacao():
    dados = request.json
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Sem dados"}), 400

    email = dados.get('buyer', {}).get('email')
    status = dados.get('status')

    if email:
        if status == "APPROVED":
            usuarios[email] = "ativo"
        elif status in ["CANCELED", "CHARGEBACK", "EXPIRED", "REFUNDED"]:
            usuarios[email] = "cancelado"

    return jsonify({"status": "sucesso", "mensagem": "Notificação recebida"}), 200

@app.route('/verificar_usuario', methods=['GET'])
def verificar_usuario():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "erro", "mensagem": "Informe um email"}), 400

    status = usuarios.get(email, "inexistente")
    return jsonify({"status": status})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
