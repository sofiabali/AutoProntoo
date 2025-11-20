from werkzeug.security import generate_password_hash
import sqlite3

# nova senha
nova_senha = "Sbf.1645"
hash_senha = generate_password_hash(nova_senha)

conn = sqlite3.connect('locadora.db')
cursor = conn.cursor()
cursor.execute('UPDATE clientes SET senha=? WHERE email=?', (hash_senha, 'bali@dominio.com'))
conn.commit()
conn.close()

print("Senha alterada com sucesso!")
