from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            role TEXT DEFAULT 'cliente'
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

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario' not in session:
            flash('Faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'usuario' not in session:
                flash('Faça login para acessar esta página.', 'error')
                return redirect(url_for('login'))

            conn = sqlite3.connect('locadora.db')
            conn.row_factory = sqlite3.Row
            user = conn.execute('SELECT * FROM clientes WHERE nome = ?', (session['usuario'],)).fetchone()
            conn.close()

            if not user or user['role'] != role:
                abort(403)  # proíbe acesso
            return f(*args, **kwargs)
        return decorated
    return decorator


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




#admin login

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin['senha'], senha) and admin['role'] == 'admin':
            session['usuario'] = admin['nome']
            session['role'] = 'admin'
            flash(f'Bem-vindo, {admin["nome"]}!', 'success')
            return redirect(url_for('admin_dashboard'))


        flash('E-mail ou senha incorretos / sem permissão administrativa.', 'error')

    return render_template('login_admin.html')

@app.route('/admin')
def admin_dashboard():
    if 'usuario' not in session or session.get('role') != 'admin':
        flash('Faça o login para prosseguir!', 'error')
        return redirect(url_for('admin_login'))

    return render_template('admin/index.html', usuario=session['usuario'])

@app.route('/admin/veiculos')
def admin_veiculos():
    if 'role' not in session or session['role'] != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('admin_login'))

    conn = conectar_bd()
    veiculos = conn.execute('SELECT * FROM veiculos').fetchall()
    conn.close()
    return render_template('admin/veiculos.html', veiculos=veiculos)

@app.route('/admin/usuarios')
def admin_usuarios():
    # verifica se está logado como admin
    if 'usuario' not in session or session.get('role') != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('admin_login'))

    conn = conectar_bd()
    clientes = conn.execute('SELECT id, nome, email, telefone, cpf FROM clientes').fetchall()
    conn.close()

    return render_template('admin_usuarios.html', clientes=clientes, usuario=session['usuario'])


@app.route('/admin/veiculos/adicionar', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_adicionar_veiculo():
    if request.method == 'POST':
        modelo = request.form.get('modelo')
        marca = request.form.get('marca')
        ano = request.form.get('ano')
        valor_diaria = request.form.get('valor_diaria')
        categoria = request.form.get('categoria')
        tipo = request.form.get('tipo')
        novo_usado = request.form.get('novo_usado')
        descricao = request.form.get('descricao')

        conn = conectar_bd()
        try:
            conn.execute('''
                INSERT INTO veiculos (modelo, marca, ano, valor_diaria, categoria, tipo, novo_usado, descricao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (modelo, marca, ano, valor_diaria, categoria, tipo, novo_usado, descricao))
            conn.commit()
        finally:
            conn.close()

        flash('Veículo adicionado com sucesso!', 'success')
        return redirect(url_for('admin_veiculos'))

    return render_template('admin/admin_adicionar_veiculo.html')



@app.route('/admin/veiculos/deletar/<int:vid>', methods=['POST'])
@login_required
@role_required('admin')
def admin_veiculos_deletar(vid):
    conn = conectar_bd()
    try:
        conn.execute('DELETE FROM veiculos WHERE id = ?', (vid,))
        conn.commit()
    finally:
        conn.close()
    flash('Veículo removido com sucesso.', 'success')
    return redirect(url_for('admin_veiculos'))

@app.route('/admin/veiculos/editar/<int:vid>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_veiculos_editar(vid):
    conn = conectar_bd()
    carro = conn.execute('SELECT * FROM veiculos WHERE id=?', (vid,)).fetchone()
    conn.close()

    if not carro:
        flash('Veículo não encontrado.', 'error')
        return redirect(url_for('admin_veiculos'))

    if request.method == 'POST':
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        categoria = request.form.get('categoria')
        tipo = request.form.get('tipo')
        valor_diaria = request.form.get('valor_diaria') or 0
        descricao = request.form.get('descricao')

        # imagem
        imagem_filename = carro['imagem'] or 'semfoto.png'
        if 'imagem' in request.files:
            f = request.files['imagem']
            if f.filename != '' and allowed_file(f.filename):
                from werkzeug.utils import secure_filename
                import os
                filename = secure_filename(f.filename)
                caminho = os.path.join('static/img', filename)
                f.save(caminho)
                imagem_filename = filename

        # Atualiza o veículo
        conn = conectar_bd()
        conn.execute('''
            UPDATE veiculos
            SET marca=?, modelo=?, categoria=?, tipo=?, valor_diaria=?, descricao=?, imagem=?
            WHERE id=?
        ''', (marca, modelo, categoria, tipo, valor_diaria, descricao, imagem_filename, vid))
        conn.commit()
        conn.close()

        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('admin_veiculos'))

    return render_template('admin/admin_adicionar_veiculo.html', carro=carro)



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

@app.route('/fale_conosco')
def fale_conosco():
    return render_template('fale_conosco.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        tipo = request.form.get('tipo')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')

        conn = sqlite3.connect('locadora.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO contato (nome, email, telefone, tipo, assunto, mensagem)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, email, telefone, tipo, assunto, mensagem))

        conn.commit()
        conn.close()

        flash('Mensagem enviada com sucesso! 📩', 'success')
        return redirect(url_for('contato'))

    return render_template('fale_conosco.html')


    

    

# Execução

if __name__ == '__main__':
    app.run(debug=True)


