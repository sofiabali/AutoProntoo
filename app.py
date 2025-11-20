from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'segredo123'

# banco de dados
def conectar_bd():
    conn = sqlite3.connect('locadora.db')
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar_bd()
    cursor = conn.cursor()

    # tabela veiculos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            ano INTEGER,
            valor_diaria REAL,
            imagem TEXT,
            categoria TEXT,
            tipo TEXT,
            novo_usado TEXT
        )
    ''')

    # tabela clientes
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

    # garante que veículos antigos tenham imagem
    cursor.execute("UPDATE veiculos SET imagem = 'semfoto.png' WHERE imagem IS NULL OR imagem = ''")

    conn.commit()
    conn.close()

criar_tabelas()


# Rotas principais

@app.route('/')
def index():
    usuario = session.get('usuario')
    conn = conectar_bd()
    carros = conn.execute("SELECT * FROM veiculos LIMIT 4").fetchall()
    conn.close()
    return render_template('index.html', usuario=usuario, carros=carros)

@app.route('/carros')
def carros():
    categoria = request.args.get('categoria')
    tipo = request.args.get('tipo')

    query = "SELECT * FROM veiculos WHERE 1=1"
    params = []

    if categoria:
        query += " AND categoria=?"
        params.append(categoria)
    if tipo:
        query += " AND tipo=?"
        params.append(tipo)

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(query, params)
    carros = cursor.fetchall()
    conn.close()

    return render_template('carros.html', carros=carros)


# Cadastro cliente

@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']
        senha = request.form['senha']

        senha_hash = generate_password_hash(senha)

        conn = conectar_bd()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO clientes (nome, email, telefone, cpf, senha)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, email, telefone, cpf, senha_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('E-mail ou CPF já cadastrado!', 'error')
            conn.close()
            return redirect(url_for('cadastro_cliente'))

        conn.close()
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro_cliente.html')

# Login / Logout

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        cliente = cursor.fetchone()
        conn.close()

        if cliente and check_password_hash(cliente['senha'], senha):
            session['usuario'] = cliente['nome']
            flash(f'Bem-vindo, {cliente["nome"]}!', 'success')
            return redirect(url_for('index'))

        flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('index'))


# Carrinho

@app.route('/reservar/<int:carro_id>')
def reservar(carro_id):
    conn = conectar_bd()
    carro = conn.execute('SELECT * FROM veiculos WHERE id = ?', (carro_id,)).fetchone()
    conn.close()

    if not carro:
        flash('Carro não encontrado!', 'error')
        return redirect(url_for('carros'))

    if 'carrinho' not in session:
        session['carrinho'] = []

    for item in session['carrinho']:
        if item['id'] == carro['id']:
            flash('Esse carro já está no seu carrinho.', 'info')
            return redirect(url_for('carrinho'))

    session['carrinho'].append({
        'id': carro['id'],
        'marca': carro['marca'],
        'modelo': carro['modelo'],
        'ano': carro['ano'],
        'valor_diaria': carro['valor_diaria'],
        'imagem': carro['imagem'] if carro['imagem'] else 'semfoto.png',
        'categoria': carro['categoria'],
        'tipo': carro['tipo'],
        'novo_usado': carro['novo_usado'],
        'descricao': carro['descricao'],
        'km': carro['km'] if 'km' in carro.keys() else None,
        'combustivel': carro['combustivel'] if 'combustivel' in carro.keys() else None,
        'cambio': carro['cambio'] if 'cambio' in carro.keys() else None
    })

    flash(f'{carro["modelo"]} adicionado ao carrinho!', 'success')
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', [])
    total = sum([item['valor_diaria'] for item in carrinho])
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/finalizar_reserva', methods=['POST'])
def finalizar_reserva():
    dias = request.form.get('dias')
    unidade = request.form.get('unidade')
    email = request.form.get('email')
    telefone = request.form.get('telefone')
    endereco = request.form.get('endereco')
    data_retirada = request.form.get('data_retirada')
    data_devolucao = request.form.get('data_devolucao')

    carros_reservados = session.get('carrinho', [])

    reserva = {
        'dias': dias,
        'data_retirada': data_retirada,
        'data_devolucao': data_devolucao,
        'unidade': unidade,
        'email': email,
        'telefone': telefone,
        'endereco': endereco,
        'carros': carros_reservados
    }

    session['reserva'] = reserva
    session['carrinho'] = []
    flash('Reserva finalizada com sucesso! ✅', 'success')
    return redirect(url_for('carrinho'))

@app.route('/remover/<int:carro_id>')
def remover(carro_id):
    if 'carrinho' in session:
        session['carrinho'] = [c for c in session['carrinho'] if c['id'] != carro_id]
    flash('Carro removido do carrinho.', 'info')
    return redirect(url_for('carrinho'))

@app.route('/remover_todos')
def remover_todos():
    session['carrinho'] = []
    return '', 204

@app.route('/minha_conta')
def minha_conta():
    if 'usuario' not in session:
        flash('Faça login para acessar sua conta.', 'error')
        return redirect(url_for('login'))

    usuario = session['usuario']
    conn = conectar_bd()
    cliente = conn.execute('SELECT * FROM clientes WHERE nome = ?', (usuario,)).fetchone()
    conn.close()

    return render_template('minha_conta.html',
                           usuario=cliente['nome'],
                           email=cliente['email'],
                           telefone=cliente['telefone'],
                           cpf=cliente['cpf'])


# Execução

if __name__ == '__main__':
    app.run(debug=True)


