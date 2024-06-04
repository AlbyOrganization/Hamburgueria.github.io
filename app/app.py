from flask import Flask, render_template, request, redirect, url_for, session
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from pathlib import Path
import random

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
    if request.method == 'POST':
        pedidos = request.form.getlist('pedidos')
        quantidades = request.form.getlist('quantidades')
        
        if pedidos and quantidades:
            connection = get_db_connection()
            cursor = connection.cursor()
            idCliente = session.get('idCliente')

            for pedido, quantidade in zip(pedidos, quantidades):
                cursor.execute(
                    "SELECT preco FROM Estoque WHERE nomeItem = %s", (pedido,)
                )
                preco = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO Pedido (idCliente, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, NOW())",
                    (idCliente, pedido, preco * int(quantidade))
                )
                connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for('cardapio'))
    
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT e.nomeItem, c.preco FROM Estoque e INNER JOIN Cardapio c ON e.idItem = c.idItem WHERE e.tipoItem = 'lanche'")
    lanches = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('lanches.html', lanches=lanches)

@app.route('/bebidas', methods=['GET', 'POST'])
def bebidas():
    if request.method == 'POST':
        pedidos = request.form.getlist('pedidos')
        quantidades = request.form.getlist('quantidades')
        
        if pedidos and quantidades:
            connection = get_db_connection()
            cursor = connection.cursor()
            idCliente = session.get('idCliente')  # Certifique-se de que o idCliente está na sessão

            for pedido, quantidade in zip(pedidos, quantidades):
                cursor.execute(
                    "SELECT preco FROM Estoque WHERE nomeItem = %s", (pedido,)
                )
                preco = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO Pedido (idCliente, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, NOW())",
                    (idCliente, pedido, preco * int(quantidade))
                )
                connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for('cardapio'))
    
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT e.nomeItem, c.preco FROM Estoque e INNER JOIN Cardapio c ON e.idItem = c.idItem WHERE e.tipoItem = 'bebida'")
    bebidas = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('bebidas.html', bebidas=bebidas)


@app.route('/porcoes', methods=['GET', 'POST'])
def porcoes():
    if request.method == 'POST':
        pedidos = request.form.getlist('pedidos')
        quantidades = request.form.getlist('quantidades')
        
        if pedidos and quantidades:
            connection = get_db_connection()
            cursor = connection.cursor()
            idCliente = session.get('idCliente')  # Certifique-se de que o idCliente está na sessão

            for pedido, quantidade in zip(pedidos, quantidades):
                cursor.execute(
                    "SELECT preco FROM Estoque WHERE nomeItem = %s", (pedido,)
                )
                preco = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO Pedido (idCliente, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, NOW())",
                    (idCliente, pedido, preco * int(quantidade))
                )
                connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for('cardapio'))
    
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

@app.route('/forma-pagamento')
def forma_pagamento(): 
    if request.method == 'POST':
        forma_pagamento = request.form.get('formaPagamento')
        tipo_entrega = request.form.get('tipoEntrega')

        # Obtendo o ID do cliente da sessão
        id_cliente = session.get('idCliente')

        # Verifique se todas as informações necessárias foram fornecidas
        if forma_pagamento and tipo_entrega and id_cliente:
            try:
                # Conectar ao banco de dados
                connection = get_db_connection()
                cursor = connection.cursor()

                # Inserir os dados na tabela de pagamento
                cursor.execute(
                    "INSERT INTO Pagamento (idCliente, metodoPagamento, valorPagamento, tipoEntrega, dataHoraPaga) VALUES (%s, %s, %s, %s, NOW())",
                    (id_cliente, forma_pagamento, 0, tipo_entrega)  # O valor do pagamento pode ser ajustado conforme necessário
                )
                connection.commit()

                # Fechar a conexão com o banco de dados
                cursor.close()
                connection.close()

                # Redirecionar para a próxima página após o pagamento bem-sucedido
                return redirect(url_for('pagamento.html'))

            except Exception as e:
                # Em caso de erro, imprima o erro para depuração
                print("Erro ao inserir pagamento no banco de dados:", e)
                # Renderizar uma página de erro ou redirecionar para uma página apropriada
                return render_template('erro_no_pagamento.html')

@app.route('/erro-pagamento')
def erro_pagamento():
    return render_template('erro_no_pagamento.html')

@app.route('/pagamento', methods=['POST', 'GET'])
def pagamento():
    if request.method == 'POST':
        try:
            # Recebe os dados do formulário
            nomePorcoes = request.form.getlist('pedidos')
            quantidades = request.form.getlist('quantidades')

            # Adiciona as porções selecionadas na tabela de pedidos
            connection = get_db_connection()
            cursor = connection.cursor()
            for nomePorcao, quantidade in zip(nomePorcoes, quantidades):
                cursor.execute(
                    "INSERT INTO Pedido (idCliente, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, NOW())",
                    (session['idCliente'], nomePorcao, quantidade)
                )
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

            cursor.close()
            connection.close()

            return redirect(url_for('pagamento_feito_com_sucesso.html'))

        except Exception as e:
                        # Em caso de erro, redirecionar para a página de erro_no_pagamento.html
            print("Erro durante o pagamento:", e)
            return redirect(url_for('erro_pagamento'))
        
    # Se o método for GET, renderiza a página de pagamento normalmente
    return render_template('pagamento.html', pedidos=pedidos, valor_total=valor_total)

@app.route('/pagamento-bem-sucedido')
def pagamentosucesso():
    return render_template('pagamento_feito_com_sucesso.html')

@app.route('/status-pedido')
def status_pedido():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT numPed FROM Pedido'")
        pedidos_nao_concluidos = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('ver_pedidos.html', pedidos=pedidos_nao_concluidos)
    
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return render_template('ver_pedido.html', error="Erro ao conectar ao banco de dados")
    return render_template('status_do_pedido.html')

@app.route('/pedido/<int:numPed>')
def ver_pedido(numPed):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("SELECT * FROM Pedido WHERE numPed = %s", (numPed,))
        pedido = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if pedido:
            return render_template('detalhes_pedido.html', pedido=pedido)
        else:
            return render_template('detalhes_pedido.html', error="Pedido não encontrado")
    
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return render_template('detalhes_pedido.html', error="Erro ao conectar ao banco de dados")

@app.route('/pedido/<int:numPed>/pronto', methods=['POST'])
def pedido_pronto(numPed):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM Pedido WHERE numPed = %s", (numPed,))
        cursor.execute("DELETE FROM PedidoItens WHERE numPed = %s", (numPed,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return redirect(url_for('status_pedido'))
    
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return redirect(url_for('status_pedido', error="Erro ao atualizar o pedido"))


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

def is_employee(username):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT f.idFunc FROM Funcionario f
        JOIN Cadastro c ON f.idCadastro = c.idCadastro
        WHERE c.email = %s
    """, (username,))
    employee = cursor.fetchone()
    cursor.close()
    connection.close()

    return employee is not None

def get_cliente_id(idCadastro):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT idCliente FROM Cliente WHERE idCadastro = %s", (idCadastro,))
    cliente = cursor.fetchone()
    cursor.close()
    connection.close()
    return cliente['idCliente'] if cliente else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('senha')
        

        if verify_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            session['is_employee'] = is_employee(username)
            session['idCliente'] = get_cliente_id('idCadastro')
            return redirect(url_for('index'))
        else:
            mensagem = 'E-mail ou senha incorretos. Tente novamente.'
            return render_template('login.html', mensagem=mensagem)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/termos')
def termos():
    return redirect(url_for('termos.html'))

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
            print(f"Cardápio atualizado: idCardapio = {codigo}, preco = {preco}")

            # Atualizar o estoque
            cursor.execute("UPDATE Estoque SET nomeItem = %s, tipoItem = %s WHERE idItem = %s", (nome_lanche, classificacao, codigo))
            connection.commit()
            print(f"Estoque atualizado: idItem = {codigo}, nomeItem = {nome_lanche}, tipoItem = {classificacao}")


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

@app.route('/senha')
def senha():
    numero_senha = random.randint(100, 999)

    return render_template('senha.html', numero_senha=numero_senha)

@app.route('/inserir-pedido', methods=['POST'])
def inserir_pedido():
    if request.method == 'POST':
        senha_pedido = request.form.get('senha_pedido')

        # Verifique se a senha do pedido foi enviada
        if senha_pedido:
            try:
                # Conecte-se ao banco de dados
                connection = get_db_connection()
                cursor = connection.cursor()

                num_pedido = random.randint(1000, 9999)  # Ou qualquer outra lógica que você preferir

                # Insira os dados da senha do pedido na tabela de pedidos
                cursor.execute(
                    "INSERT INTO Pedido (idCliente, numPed, itemPed, valTotal, dataHoraPed) VALUES (%s, %s, %s, %s, NOW())",
                    (session['idCliente'], num_pedido, '', 0)  # Adicione os valores reais conforme necessário
                )
                connection.commit()

                # Fechar conexão com o banco de dados
                cursor.close()
                connection.close()

                # Redirecionar para a página inicial após inserir o pedido com sucesso
                return redirect(url_for('index'))

            except Exception as e:
                # Em caso de erro, imprima o erro para depuração
                print("Erro ao inserir pedido no banco de dados:", e)
                # Renderizar uma página de erro ou redirecionar para uma página apropriada
                return render_template('senha.html', error="Erro ao inserir pedido no banco de dados")

    # Se o método não for POST, redirecione para a página inicial
    return redirect(url_for('index'))


@app.route('/informacoes_salvas')
def informacoes_salvas():
    if request.method == 'POST':

        # Redirecionamento após o processamento bem-sucedido
        return redirect(url_for('informacoes_salvas'))

    # Se o método for GET, apenas renderize o template
    return render_template('alterar_cardapio.html')

if __name__ == '__main__':
    app.run(debug=True)
