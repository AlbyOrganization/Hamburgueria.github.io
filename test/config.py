from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('environment/.env')
load_dotenv(dotenv_path=dotenv_path)

host = os.getenv('HOST_NAME')
usuario = os.getenv('USER_NAME')
senha = os.getenv('PWD_NAME')
database = os.getenv('DB_NAME')

print(f"Host: {host}")
print(f"Usuário: {usuario}")
print(f"Senha: {'*****' if senha else 'None'}")
print(f"Database: {database}")

try:
    db_connection = psycopg2.connect(
        host=host,
        user=usuario,
        password=senha,
        database=database
    )
    print(db_connection, 'Conectado com sucesso')

except psycopg2.Error as erro:
    print("Algo deu errado:", erro)

def get_db_connection():
    host = os.getenv('HOST_NAME')
    usuario = os.getenv('USER_NAME')
    senha = os.getenv('PWD_NAME')
    database = os.getenv('DB_NAME')

    return psycopg2.connect(
        host=host,
        user=usuario,
        password=senha,
        database=database
    )

app = Flask(__name__, static_folder='../assets', template_folder='../pages')
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/lanche', methods=['GET', 'POST'])
def lanche():
    print("Entrou na rota /lanche")
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT e.nomeItem, c.preco FROM Estoque e INNER JOIN Cardapio c ON e.idItem = c.idItem WHERE e.tipoItem = 'lanche'")
    lanches = cursor.fetchall()
    print(lanches)
    cursor.close()
    connection.close()
    
    return render_template('lanches.html', lanches=lanches)

@app.route('/bebidas')
def bebidas():
    print("Entrou na rota /bebidas")
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Verificar todos os itens no estoque
    cursor.execute("SELECT * FROM Estoque")
    estoque_todos = cursor.fetchall()
    print("Todos os Itens no Estoque:", estoque_todos)
    
    # Verificar se há itens no estoque com tipo 'bebida'
    cursor.execute("SELECT * FROM Estoque WHERE tipoItem = 'bebida'")
    estoque_bebidas = cursor.fetchall()
    print("Estoque Bebidas:", estoque_bebidas)
    
    # Verificar se há correspondência no cardápio
    cursor.execute("SELECT * FROM Cardapio")
    cardapio = cursor.fetchall()
    print("Cardapio:", cardapio)

    # Consulta para obter as bebidas
    cursor.execute("SELECT e.nomeItem, c.preco FROM Estoque e INNER JOIN Cardapio c ON e.idItem = c.idItem WHERE e.tipoItem = 'bebida' AND c.disponibilidade = true")
    bebidas = cursor.fetchall()
    print("Bebidas:", bebidas)
    
    cursor.close()
    connection.close()
    
    return render_template('bebidas.html', bebidas=bebidas)


@app.route('/porcoes')
def porcoes():
    print("Entrou na rota /porcoes")
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT e.nomeItem, c.preco FROM Estoque e INNER JOIN Cardapio c ON e.idItem = c.idItem WHERE e.tipoItem = 'porção'")
    porcoes = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('porcoes.html', porcoes=porcoes)

@app.route('/cardapio')
def cardapio():
    return render_template('opcoes_e_pedidos.html')

@app.route('/pagamento', methods=['POST', 'GET'])
def pagamento():
    if request.method == 'POST':
        # Recebe os dados do formulário
        nomePorcoes = request.form.getlist('pedidos')
        quantidades = request.form.getlist('quantidades')

        # Adiciona as porções selecionadas na tabela de pedidos
        connection = get_db_connection()
        cursor = connection.cursor()
        for nomePorcao, quantidade in zip(nomePorcoes, quantidades):
            cursor.execute("INSERT INTO Pedido (idCliente, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, NOW())", (session['idCliente'], nomePorcao, quantidade))
            connection.commit()
        cursor.close()
        connection.close()

        # Obter os itens do pedido do cliente
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT itemPed, valTotal FROM Pedido WHERE idCliente = %s", (session['idCliente'],))
        pedidos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Calcular o valor total
        valor_total = sum([pedido['valTotal'] for pedido in pedidos])

        return render_template('pagamento.html', pedidos=pedidos, valor_total=valor_total)

    # Se o método for GET, renderiza a página de pagamento normalmente
    return render_template('forma_de_pagamento.html')

@app.route('/pagamento-bem-sucedido')
def pagamentosucesso():
    return render_template('pagamento_feito_com_sucesso.html')

@app.route('/status-pedido')
def pedidostatus():
    return render_template('status_do_pedido.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        password = request.form['senha']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert into Cadastro
            cursor.execute(
                "INSERT INTO Cadastro (cpf, email, telefone, endereco, senha) VALUES (%s, %s, %s, %s, %s) RETURNING idCadastro",
                (cpf, email, telefone, endereco, password)
            )
            idCadastro = cursor.fetchone()[0]
            connection.commit()

            # Insert into Cliente using the returned idCadastro
            cursor.execute("INSERT INTO Cliente (idCadastro) VALUES (%s)", (idCadastro,))
            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for('login'))

        except psycopg2.Error as e:
            # Log the error for debugging
            print(f"Database error: {e}")
            return render_template('cadastro.html', error="Erro ao conectar ao banco de dados")

    return render_template('cadastro.html')

def verify_credentials(username, password):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Cadastro WHERE email = %s AND senha = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user and user['senha'] == password:
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('senha')
        

        if verify_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            mensagem = 'E-mail ou senha incorretos. Tente novamente.'
            return render_template('login.html', mensagem=mensagem)

    
    return render_template('login.html')

@app.route('/alterar-cardapio', methods=['GET', 'POST'])
def alterar_cardapio():  
    if request.method == 'POST':
        # Obter os dados do formulário
        classificacao = request.form['escolha']
        codigo = request.form['codigo']
        nome_lanche = request.form['nome_lanche']
        preco = request.form['preco']

        # Validar os dados de entrada
        if not (codigo.isdigit() and preco.replace('.', '').isdigit()):
            return render_template('alterar_cardapio.html', error="Dados inválidos")

        # Conectar ao banco de dados
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Atualizar o cardápio
            cursor.execute("UPDATE Cardapio SET preco = %s WHERE idCardapio = %s", (preco, codigo))
            connection.commit()

            # Atualizar o estoque
            cursor.execute("UPDATE Estoque SET nomeItem = %s, tipoItem = %s WHERE idItem = %s", (nome_lanche, classificacao, codigo))
            connection.commit()

            # Fechar conexão e cursor
            cursor.close()
            connection.close()

            # Redirecionar para a página de sucesso
            return render_template('informacoes_salvas.html')

        except psycopg2.Error as e:
            # Em caso de erro, renderize o template com uma mensagem de erro genérica
            return render_template('alterar_cardapio.html', error="Erro ao conectar ao banco de dados")

    # Se o método for GET, apenas renderize o template
    return render_template('alterar_cardapio.html')

@app.route('/informacoes_salvas')
def informacoes_salvas():
    if request.method == 'POST':

        # Redirecionamento após o processamento bem-sucedido
        return redirect(url_for('informacoes_salvas'))

    # Se o método for GET, apenas renderize o template
    return render_template('alterar_cardapio.html')

if __name__ == '__main__':
    app.run(debug=True)
