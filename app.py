from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulando um banco de dados temporário
usuarios = {}

@app.route('/webhook', methods=['POST'])
def receber_notificacao():
    dados = request.json  # Recebe os dados da Hotmart
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Sem dados"}), 400
    
    email = dados.get('buyer', {}).get('email')
    status = dados.get('status')  # Status da compra
    
    if email:
        if status == "APPROVED":  # Pagamento aprovado
            usuarios[email] = "ativo"
        elif status in ["CANCELED", "CHARGEBACK", "EXPIRED", "REFUNDED"]:  # Cancelado, reembolsado
            usuarios[email] = "cancelado"
    
    return jsonify({"status": "sucesso", "mensagem": "Notificação recebida"}), 200

@app.route('/verificar_usuario', methods=['GET'])
def verificar_usuario():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "erro", "mensagem": "Informe um email"}), 400
    
    status = usuarios.get(email, "inexistente")  # Se não estiver no banco, é inexistente
    return jsonify({"status": status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
