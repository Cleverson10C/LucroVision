"""
Sistema de Gerenciamento de Estoque Inteligente - LucroVision
Arquivo principal - Inicializa o banco de dados e abre a tela de login
"""
        
from database import criar_tabelas
from login import tela_login

if __name__ == "__main__":
    # Inicializar estrutura do banco de dados
    criar_tabelas()
    
    # Abrir tela de login do sistema (com validação de licença incluída)
    tela_login()