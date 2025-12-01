"""
Script para cadastrar produtos iniciais no banco de dados
"""

from database import conectar
from lista_produtos import produtos_supermercado
import random

def cadastrar_produtos_iniciais():
    """Cadastra todos os produtos do dicionário no banco de dados"""
    
    from datetime import datetime, timedelta
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    produtos_cadastrados = 0
    produtos_ja_existentes = 0
    
    print("Iniciando cadastro de produtos...\n")
    
    # Definir validades diferentes por categoria
    validades_por_categoria = {
        "Alimentos": (6, 24),  # 6 a 24 meses
        "Hortifruti": (0.25, 0.5),  # 1 a 2 semanas (em meses)
        "Laticínios": (0.5, 2),  # 2 semanas a 2 meses
        "Carnes e Frios": (0.25, 1),  # 1 semana a 1 mês
        "Bebidas": (6, 18),  # 6 a 18 meses
        "Padaria": (0.1, 0.3),  # 3 a 10 dias
        "Higiene Pessoal": (12, 36),  # 1 a 3 anos
        "Limpeza": (12, 36),  # 1 a 3 anos
        "Congelados": (6, 12),  # 6 meses a 1 ano
        "Mercearia": (6, 18)  # 6 a 18 meses
    }
    
    for categoria, lista_produtos in produtos_supermercado.items():
        print(f"Categoria: {categoria}")
        
        for produto in lista_produtos:
            try:
                # Gerar preços aleatórios para exemplo
                preco_custo = round(random.uniform(2.0, 50.0), 2)
                preco_venda = round(preco_custo * random.uniform(1.2, 1.8), 2)
                quantidade = random.randint(10, 100)
                estoque_minimo = random.randint(5, 20)
                
                # Gerar validade baseada na categoria
                min_meses, max_meses = validades_por_categoria.get(categoria, (6, 12))
                meses_validade = random.uniform(min_meses, max_meses)
                dias_validade = int(meses_validade * 30)
                data_validade = datetime.now() + timedelta(days=dias_validade)
                validade_formatada = data_validade.strftime("%Y-%m")
                
                # Inserir produto
                cursor.execute("""
                    INSERT INTO produtos (nome, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (produto, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade_formatada))
                
                produtos_cadastrados += 1
                print(f"  ✓ {produto}")
                
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    produtos_ja_existentes += 1
                    print(f"  - {produto} (já existe)")
                else:
                    print(f"  ✗ Erro ao cadastrar {produto}: {e}")
        
        print()
    
    conexao.commit()
    conexao.close()
    
    print("=" * 50)
    print(f"Produtos cadastrados com sucesso: {produtos_cadastrados}")
    print(f"Produtos já existentes: {produtos_ja_existentes}")
    print(f"Total processado: {produtos_cadastrados + produtos_ja_existentes}")
    print("=" * 50)

if __name__ == "__main__":
    cadastrar_produtos_iniciais()
