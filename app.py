from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo123'  # chave da sessão

# ----------------------------------------
# BANCO DE DADOS
# ----------------------------------------
def conectar_bd():
    conn = sqlite3.connect('locadora.db')
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar_bd()
    cursor = conn.cursor()

    # tabela de veículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            ano INTEGER,
            valor_diaria REAL
        )
    ''')

    # tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT,
            cpf TEXT UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

criar_tabelas()

# ----------------------------------------
# ROTAS PRINCIPAIS
# ----------------------------------------
@app.route('/')
def index():
    usuario = session.get('usuario')
    return render_template('index.html', usuario=usuario)

@app.route('/carros')
def carros():
    conn = conectar_bd()
    carros = conn.execute('SELECT * FROM veiculos').fetchall()
    conn.close()
    return render_template('carros.html', carros=carros)

# ----------------------------------------
# CADASTRO DE CLIENTE
# ----------------------------------------
@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        senha = request.form['senha']

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nome, email, telefone, cpf, senha)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, email, telefone, cpf, senha))
        conn.commit()
        conn.close()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro_cliente.html')

# ----------------------------------------
# LOGIN / LOGOUT DE CLIENTE
# ----------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE email = ? AND senha = ?', (email, senha))
        cliente = cursor.fetchone()
        conn.close()

        if cliente:
            session['usuario'] = cliente['nome']
            flash(f'Bem-vindo, {cliente["nome"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('index'))

# ----------------------------------------
# CADASTRO DE CARROS (NOVO)
# ----------------------------------------
@app.route('/cadastro_carro', methods=['GET', 'POST'])
def cadastro_carro():
    if request.method == 'POST':
        modelo = request.form['modelo']
        marca = request.form['marca']
        ano = request.form['ano']
        valor_diaria = request.form['valor_diaria']

        conn = conectar_bd()
        conn.execute('''
            INSERT INTO veiculos (modelo, marca, ano, valor_diaria)
            VALUES (?, ?, ?, ?)
        ''', (modelo, marca, ano, valor_diaria))
        conn.commit()
        conn.close()
        flash('Carro adicionado com sucesso!', 'success')
        return redirect(url_for('carros'))

    return render_template('cadastro_carro.html')

# ----------------------------------------
# EXECUÇÃO
# ----------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
