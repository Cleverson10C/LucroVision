import sqlite3

con = sqlite3.connect('comercio.db')
cur = con.cursor()

# Corrigir categorias de produtos conhecidos
correcoes = {
    'Arroz': 'Alimentos',
    'Feijão': 'Alimentos',
    'Carne Bovina (Alcatra)': 'Carnes',
    'Carne Bovina (Patinho)': 'Carnes',
    'Frango Inteiro': 'Carnes',
    'Presunto': 'Frios',
    'Queijo Mussarela': 'Laticínios',
    'Alface': 'Hortifruti',
    'Sabonete': 'Higiene Pessoal',
    'Detergente': 'Limpeza',
    # Adicione mais conforme necessário
}

for nome, categoria in correcoes.items():
    cur.execute("UPDATE produtos SET categoria=? WHERE nome=?", (categoria, nome))

con.commit()
con.close()
print('Categorias corrigidas!')
