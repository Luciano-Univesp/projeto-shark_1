from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# A secret_key é necessária para usar 'session'
app.secret_key = "shark_foodtruck_key"

# IMPORTANTE: Os nomes aqui devem ser IGUAIS aos 'value' do seu <select> no HTML
menu = {
    "ZOIÃO SIMPLES": 17.00,
    "BURGUER": 20.00,
    "SALADA": 22.00,
    "CHEDDAR": 22.00,
    "FRANGUITO": 22.00,
    "PORQUINHO": 22.00,
    "BURGUER A CAVALO": 25.00,
    "BACON": 28.00,
    "TUDO": 30.00,
    "MEGA TUDO": 42.00,
    "BIG ZOIÃO": 35.00,
    "TRIO PARADA DURA": 52.00
}

def calcular_total(itens_pedido):
    # Soma (quantidade * preco) de cada item no pedido
    return sum(item['quantidade'] * item['preco'] for item in itens_pedido)

@app.route("/", methods=["GET", "POST"])
def index():
    # Inicializa a sessão do pedido se não existir
    if "pedido" not in session:
        session["pedido"] = []

    if request.method == "POST":
        item_nome = request.form.get("item")
        quantidade = request.form.get("quantidade", type=int)

        # Verifica se o item existe no nosso dicionário 'menu'
        if item_nome in menu and quantidade and quantidade > 0:
            # No Flask, para atualizar listas em session, precisamos reatribuir
            pedido_atual = session["pedido"]
            pedido_atual.append({
                "item": item_nome, 
                "quantidade": quantidade, 
                "preco": menu[item_nome]
            })
            session["pedido"] = pedido_atual
            session.modified = True # Garante que o Flask salve a mudança
            
        return redirect(url_for("index"))

    # Pega os dados para exibir no HTML
    pedido_para_exibir = session.get("pedido", [])
    total_conta = calcular_total(pedido_para_exibir)
    
    return render_template("index.html", menu=menu, pedido=pedido_para_exibir, total=total_conta)

@app.route("/limpar")
def limpar_pedido():
    # Remove a lista de pedidos da sessão
    session.pop("pedido", None)
    return redirect(url_for("index"))

# Rotas vazias apenas para o menu lateral não dar erro 404
@app.route("/custos")
def custos(): return "<h1>Página de Custos e Lucros em construção</h1>"

@app.route("/relatorios")
def relatorios(): return "<h1>Página de Relatórios em construção</h1>"

@app.route("/vendas")
def vendas(): return "<h1>Página de Vendas em Tempo Real em construção</h1>"

@app.route("/estoque")
def estoque(): return "<h1>Página de Controle de Estoque em construção</h1>"

if __name__ == "__main__":
    # Roda o servidor
    app.run(debug=True, port=5000)