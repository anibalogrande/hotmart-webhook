import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuração do banco PostgreSQL (pegue a Connection String do Render)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://usuario:senha@host:porta/dbname")

# Função para conectar ao banco
def conectar_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Criar tabela de usuários
def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para salvar um usuário no banco
def salvar_usuario(email, status):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (email, status) VALUES (%s, %s)
        ON CONFLICT (email) DO UPDATE SET status = EXCLUDED.status
    ''', (email, status))
    conn.commit()
    conn.close()

# Função para buscar um usuário no banco
def verificar_usuario_db(email):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM usuarios WHERE email = %s', (email,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "inexistente"

# Inicializa o banco ao iniciar o servidor
inicializar_db()

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
            salvar_usuario(email, "ativo")
        elif status in ["CANCELED", "CHARGEBACK", "EXPIRED", "REFUNDED"]:  # Cancelado
            salvar_usuario(email, "cancelado")

    print(f"🔹 Usuário {email} salvo como {status}")  # Debug

    return jsonify({"status": "sucesso", "mensagem": "Notificação recebida"}), 200

@app.route('/verificar_usuario', methods=['GET'])
def verificar_usuario():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "erro", "mensagem": "Informe um email"}), 400

    status = verificar_usuario_db(email)

    return jsonify({"status": status})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
