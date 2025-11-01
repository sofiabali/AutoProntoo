from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo123'  # chave da sessão

# Banco de dados
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
            valor_diaria REAL,
            imagem TEXT
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

    # garante que veículos antigos tenham imagem sem foto
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
    categoria = request.args.get('categoria', '').strip()
    tipo = request.args.get('tipo', '').strip()
    preco = request.args.get('preco', '').strip()
    ano = request.args.get('ano', '').strip()

    query = "SELECT * FROM veiculos WHERE 1=1"
    params = []

    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    if preco:
        query += " AND valor_diaria <= ?"
        params.append(float(preco))
    if ano:
        query += " AND ano >= ?"
        params.append(int(ano))

    conn = conectar_bd()
    carros = conn.execute(query, params).fetchall()
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

# Login
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

    imagem = carro['imagem'] if 'imagem' in carro.keys() and carro['imagem'] else 'semfoto.png'

    session['carrinho'].append({
        'id': carro['id'],
        'marca': carro['marca'],
        'modelo': carro['modelo'],
        'ano': carro['ano'],
        'valor_diaria': carro['valor_diaria'],
        'imagem': imagem
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

    carros_reservados = session.get('carrinho', [])

    reserva = {
        'dias': dias,
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

# Remover carro do carrinho
@app.route('/remover/<int:carro_id>')
def remover(carro_id):
    if 'carrinho' in session:
        session['carrinho'] = [c for c in session['carrinho'] if c['id'] != carro_id]
    flash('Carro removido do carrinho.', 'info')
    return redirect(url_for('carrinho'))

# Limpar carrinho
@app.route('/remover_todos')
def remover_todos():
    session['carrinho'] = []
    return '', 204

# Execução
if __name__ == '__main__':
    app.run(debug=True)
