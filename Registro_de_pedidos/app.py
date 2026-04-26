from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
# A secret_key permite que o Flask lembre do pedido e do cliente durante a navegação
app.secret_key = "shark_foodtruck_key"

# --- BANCO DE DADOS ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sua_password", # COLOQUE SUA SENHA AQUI
        database="db_foodtruck"
    )

# --- O SEU DICIONÁRIO DE PREÇOS (O CARDÁPIO) ---
menu = {
    "ZOIÃO SIMPLES": 17.00, "BURGUER": 20.00, "SALADA": 22.00,
    "CHEDDAR": 22.00, "FRANGUITO": 22.00, "PORQUINHO": 22.00,
    "BURGUER A CAVALO": 25.00, "BACON": 28.00, "TUDO": 30.00,
    "MEGA TUDO": 42.00, "BIG ZOIÃO": 35.00, "TRIO PARADA DURA": 52.00
}

@app.route("/", methods=["GET", "POST"])
def index():
    # Inicializa a sessão se estiver vazia
    if "pedido" not in session:
        session["pedido"] = []
    if "cliente" not in session:
        session["cliente"] = {"nome": "Consumidor", "telefone": ""}

    if request.method == "POST":
        # 1. Lógica de Identificação do Cliente
        if "nome_cliente" in request.form:
            session["cliente"] = {
                "nome": request.form.get("nome_cliente") or "Consumidor",
                "telefone": request.form.get("telefone_cliente") or ""
            }
        
        # 2. Lógica de Adicionar Itens ao Carrinho
        elif "item" in request.form:
            item_nome = request.form.get("item")
            quantidade = request.form.get("quantidade", type=int)
            if item_nome in menu and quantidade > 0:
                pedido_atual = session["pedido"]
                pedido_atual.append({
                    "item": item_nome, 
                    "quantidade": quantidade, 
                    "preco": menu[item_nome]
                })
                session["pedido"] = pedido_atual
        
        session.modified = True
        return redirect(url_for("index"))

    total_conta = sum(item['quantidade'] * item['preco'] for item in session["pedido"])
    return render_template("index.html", menu=menu, pedido=session["pedido"], 
                           total=total_conta, cliente=session["cliente"])

@app.route("/pagamento", methods=["POST"])
def pagamento():
    # Aqui é onde a mágica do troco acontece
    total = float(request.form.get("total_pedido", 0))
    forma = request.form.get("forma_pagamento")
    recebido = float(request.form.get("valor_recebido") or 0)
    
    troco = recebido - total if forma == "Dinheiro" else 0
    
    # No futuro, aqui você salva no MySQL para o Data Science
    return render_template("sucesso.html", troco=troco, forma=forma, cliente=session["cliente"])

@app.route("/limpar")
def limpar_pedido():
    session.clear() # Limpa tudo para o próximo cliente
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)