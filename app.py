from flask import Flask, render_template, request, redirect, url_for, session, make_response
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "shark_foodtruck_key"

menu = {
    "ZOIÃO SIMPLES": 17.00, "BURGUER": 20.00, "SALADA": 22.00,
    "CHEDDAR": 22.00, "FRANGUITO": 22.00, "PORQUINHO": 22.00,
    "BURGUER A CAVALO": 25.00, "BACON": 28.00, "TUDO": 30.00,
    "MEGA TUDO": 42.00, "BIG ZOIÃO": 35.00, "TRIO PARADA DURA": 52.00
}

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="foodtruck-mysql",
            user="root",
            password="root",
            database="foodtruck"
        )
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def get_produto_id(cursor, nome, preco):
    cursor.execute("SELECT id_produtos FROM produtos WHERE nome = %s", (nome,))
    row = cursor.fetchone()
    if row: return row[0]
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (%s, %s)", (nome, preco))
    return cursor.lastrowid

@app.route("/", methods=["GET", "POST"])
def index():
    if "pedido" not in session: session["pedido"] = []
    if "cliente" not in session: session["cliente"] = {"nome": "Consumidor", "telefone": ""}
    
    pedidos_status = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_pedidos, nome_cliente, hora_pedido FROM pedidos WHERE status != 'entregue' ORDER BY hora_pedido ASC")
        pedidos_db = cursor.fetchall()
        agora = datetime.now()
        for p in pedidos_db:
            minutos = int((agora - p["hora_pedido"]).total_seconds() / 60)
            status_texto, classe = ("Em Preparo", "status-preparo") if minutos <= 15 else ("Pendente", "status-atrasado")
            pedidos_status.append({"id": p["id_pedidos"], "cliente": p["nome_cliente"], "minutos": minutos, "status": status_texto, "classe": classe})
        cursor.close()
        conn.close()

    if request.method == "POST":
        if "nome_cliente" in request.form:
            session["cliente"] = {"nome": request.form.get("nome_cliente") or "Consumidor", "telefone": request.form.get("telefone_cliente") or ""}
        elif "item" in request.form:
            item_nome, qty = request.form.get("item"), request.form.get("quantidade", type=int)
            if item_nome in menu and qty > 0:
                pedido_atual = session["pedido"]
                pedido_atual.append({"item": item_nome, "quantidade": qty, "preco": menu[item_nome]})
                session["pedido"] = pedido_atual
        session.modified = True
        return redirect(url_for("index"))

    total = sum(item["quantidade"] * item["preco"] for item in session["pedido"])
    ticket_id = request.args.get('ticket')
    return render_template("index.html", menu=menu, pedido=session["pedido"], total=total, cliente=session["cliente"], pedidos_vivos=pedidos_status, ticket_id=ticket_id)

@app.route("/pagamento", methods=["POST"])
def pagamento():
    if not session.get("pedido"): return redirect(url_for("index"))
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            total = sum(item["quantidade"] * item["preco"] for item in session["pedido"])
            # Voltamos para o INSERT que funciona (sem telefone_cliente)
            sql = "INSERT INTO pedidos (nome_cliente, total, status, hora_pedido) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (session["cliente"]["nome"], total, "preparo", datetime.now()))
            pedido_id = cursor.lastrowid
            for item in session["pedido"]:
                prod_id = get_produto_id(cursor, item["item"], item["preco"])
                cursor.execute("INSERT INTO itens_pedido (quantidade, preco_unitario, pedidos_id_pedidos, produtos_id_produtos) VALUES (%s, %s, %s, %s)", (item["quantidade"], item["preco"], pedido_id, prod_id))
            conn.commit()
            session.pop("pedido", None)
            return redirect(url_for("index", ticket=pedido_id))
        except Exception as e:
            return f"Erro no banco: {e}", 500
        finally:
            conn.close()
    return "Erro de conexão", 500

@app.route("/imprimir_ticket/<int:pedido_id>")
def imprimir_ticket(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_pedidos, nome_cliente, total, hora_pedido FROM pedidos WHERE id_pedidos = %s", (pedido_id,))
    pedido = cursor.fetchone()
    cursor.execute("SELECT i.quantidade, i.preco_unitario, p.nome FROM itens_pedido i JOIN produtos p ON i.produtos_id_produtos = p.id_produtos WHERE i.pedidos_id_pedidos = %s", (pedido_id,))
    itens = cursor.fetchall()
    conn.close()
    return render_template("ticket.html", pedido=pedido, itens=itens)

@app.route("/entregar/<int:id>")
def marcar_entregue(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET status = 'entregue' WHERE id_pedidos = %s", (id,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route('/limpar_pedido')
def limpar_pedido():
    session.pop('pedido', None)
    return redirect(url_for('index'))

@app.route('/estoque')
def estoque(): return render_template("estoque.html")

@app.route('/relatorios')
def relatorios(): return render_template("relatorios.html")

@app.route('/custos')
def custos(): return render_template("custos.html", vendas=0)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)