from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "shark_foodtruck_key"

# 1. PRIMEIRO: DEFINA O MENU (O Python precisa ler isso antes das rotas)
menu = {
    "ZOIÃO SIMPLES": 17.00, "BURGUER": 20.00, "SALADA": 22.00,
    "CHEDDAR": 22.00, "FRANGUITO": 22.00, "PORQUINHO": 22.00,
    "BURGUER A CAVALO": 25.00, "BACON": 28.00, "TUDO": 30.00,
    "MEGA TUDO": 42.00, "BIG ZOIÃO": 35.00, "TRIO PARADA DURA": 52.00
}

# 2. CONEXÃO COM O BANCO
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="sua_password", # <--- COLOQUE SUA SENHA AQUI
            database="db_foodtruck"
        )
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

# 3. AGORA AS ROTAS
@app.route("/", methods=["GET", "POST"])
def index():
    if "pedido" not in session:
        session["pedido"] = []
    if "cliente" not in session:
        session["cliente"] = {"nome": "Consumidor", "telefone": ""}

    pedidos_status = []
    
    # Busca os pedidos para a barra lateral direita
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # FIX: Note que o nome da tabela/coluna deve ser igual ao seu banco
            cursor.execute("SELECT id, nome_cliente, hora_pedido FROM pedidos WHERE status != 'entregue' ORDER BY hora_pedido ASC")
            pedidos_db = cursor.fetchall()
            
            agora = datetime.now()
            for p in pedidos_db:
                diferenca = agora - p['hora_pedido']
                minutos = int(diferenca.total_seconds() / 60)
                
                if minutos <= 15:
                    status_texto, classe = "Em Preparo", "status-preparo"
                else:
                    status_texto, classe = "Pendente", "status-atrasado"
                    
                pedidos_status.append({
                    'id': p['id'], 'cliente': p['nome_cliente'],
                    'minutos': minutos, 'status': status_texto, 'classe': classe
                })
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro no SQL: {e}")

    if request.method == "POST":
        if "nome_cliente" in request.form:
            session["cliente"] = {
                "nome": request.form.get("nome_cliente") or "Consumidor",
                "telefone": request.form.get("telefone_cliente") or ""
            }
        elif "item" in request.form:
            item_nome = request.form.get("item")
            quantidade = request.form.get("quantidade", type=int)
            if item_nome in menu and quantidade > 0:
                pedido_atual = session["pedido"]
                pedido_atual.append({
                    "item": item_nome, "quantidade": quantidade, "preco": menu[item_nome]
                })
                session["pedido"] = pedido_atual
        
        session.modified = True
        return redirect(url_for("index"))

    total_conta = sum(item['quantidade'] * item['preco'] for item in session["pedido"])
    
    return render_template("index.html", 
                           menu=menu, 
                           pedido=session["pedido"], 
                           total=total_conta, 
                           cliente=session["cliente"], 
                           pedidos_vivos=pedidos_status)

@app.route("/entregar/<int:id>")
def marcar_entregue(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET status = 'entregue' WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for("index"))

@app.route("/limpar")
def limpar_pedido():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)