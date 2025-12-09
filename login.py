import tkinter as tk
from tkinter import messagebox
from database import conectar
import dashboard
import requests

def acesso_permitido(licenca):
    try:
        # Agora sem headers e sem token
        requisicao = requests.get('https://servidor-licencas-5g4e.onrender.com/')
        LICENCA_ESPECIFICA = 'WOSNJ-ORKPT-F7ZQQ-BXJYM-Y7B1X'
        if requisicao.status_code == 200 and requisicao.text:
            resultado = requisicao.json()
            if 'Licenças' in resultado:
                licencas_validas = [item['licenca'] for item in resultado['Licenças']]
                if licenca == LICENCA_ESPECIFICA and licenca in licencas_validas:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        return False

# Janela para pedir a licença
class LicencaDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Licença de acesso")
        self.geometry("350x150")
        # self.resizable(False, False)
        self.licenca = None

        self.label = tk.Label(self, text="Digite sua licença de acesso:", font=("Arial", 11))
        self.label.pack(pady=10)

        self.entry = tk.Entry(self, width=32)
        self.entry.pack(pady=5)

        self.button = tk.Button(self, text="Validar", bg="#3498db", fg="white",  font=("Arial", 10, "bold"), command=self.validar)
        self.button.pack(pady=10)

    def validar(self):
        self.licenca = self.entry.get()
        self.destroy()


def verificar_login(usuario, senha):
    """Verifica se o usuário e senha são válidos no banco de dados"""
    conexao_banco = conectar()
    cursor_banco = conexao_banco.cursor()
    cursor_banco.execute("SELECT * FROM funcionarios WHERE usuario=? AND senha=?", (usuario, senha))
    funcionario_encontrado = cursor_banco.fetchone()
    conexao_banco.close()
    return funcionario_encontrado is not None

def cadastrar_usuario():
    """Abre tela para cadastrar novo usuário"""
    def salvar_usuario():
        """Salva o novo usuário no banco de dados"""
        novo_usuario = campo_novo_usuario.get().strip()
        nova_senha = campo_nova_senha.get().strip()
        confirmar_senha = campo_confirmar_senha.get().strip()
        
        # Validações
        if not novo_usuario or not nova_senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if len(novo_usuario) < 4:
            messagebox.showerror("Erro", "Usuário deve ter pelo menos 4 caracteres!")
            return
        
        if len(nova_senha) < 4:
            messagebox.showerror("Erro", "Senha deve ter pelo menos 4 caracteres!")
            return
        
        if nova_senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return
        
        # Verificar se usuário já existe
        conexao_banco = conectar()
        cursor_banco = conexao_banco.cursor()
        cursor_banco.execute("SELECT * FROM funcionarios WHERE usuario=?", (novo_usuario,))
        usuario_existente = cursor_banco.fetchone()
        
        if usuario_existente:
            messagebox.showerror("Erro", "Usuário já cadastrado!")
            conexao_banco.close()
            return
        
        # Cadastrar novo usuário
        try:
            cursor_banco.execute("INSERT INTO funcionarios (usuario, senha) VALUES (?, ?)", 
                               (novo_usuario, nova_senha))
            conexao_banco.commit()
            conexao_banco.close()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela_cadastro.destroy()
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(erro)}")
            conexao_banco.close()
    
    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastrar Novo Usuário")
    janela_cadastro.geometry("450x330")
    # janela_cadastro.resizable(False, False)
    janela_cadastro.configure(bg="#f0f0f0")
    
    tk.Label(janela_cadastro, text="Cadastro de Usuário", font=("Arial", 14, "bold"), 
             bg="#f0f0f0").pack(pady=10)
    
    tk.Label(janela_cadastro, text="Usuário:", font=("Arial", 10), bg="#f0f0f0").pack(pady=5)
    campo_novo_usuario = tk.Entry(janela_cadastro, width=30)
    campo_novo_usuario.pack()
    
    tk.Label(janela_cadastro, text="Senha:", font=("Arial", 10), bg="#f0f0f0").pack(pady=5)
    campo_nova_senha = tk.Entry(janela_cadastro, width=30, show="*")
    campo_nova_senha.pack()
    
    tk.Label(janela_cadastro, text="Confirmar Senha:", font=("Arial", 10), bg="#f0f0f0").pack(pady=5)
    campo_confirmar_senha = tk.Entry(janela_cadastro, width=30, show="*")
    campo_confirmar_senha.pack()
    
    frame_botoes = tk.Frame(janela_cadastro, bg="#f0f0f0")
    frame_botoes.pack(pady=20)
    
    tk.Button(frame_botoes, text="Cadastrar", command=salvar_usuario, 
             bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
             padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="Cancelar", command=janela_cadastro.destroy, 
             bg="#c0392b", fg="white", font=("Arial", 11, "bold"), 
             padx=20, pady=5).pack(side=tk.LEFT, padx=5)

def tela_login():
    """Cria e exibe a tela de login do sistema"""
    
    # Validar licença primeiro
    dialog = LicencaDialog()
    dialog.mainloop()
    licenca = dialog.licenca
    
    if not licenca or not acesso_permitido(licenca):
        messagebox.showerror("Erro", "Licença inválida! Acesso negado.")
        return
    
    def autenticar_usuario():
        """Valida as credenciais e abre o dashboard se correto"""
        nome_usuario = campo_usuario.get().strip()
        senha_usuario = campo_senha.get().strip()
        
        if not nome_usuario or not senha_usuario:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if verificar_login(nome_usuario, senha_usuario):
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            janela_login.destroy()
            dashboard.abrir_dashboard()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    janela_login = tk.Tk()
    janela_login.title("Login - Sistema Gerenciamento")
    janela_login.geometry("450x350")
    # janela_login.resizable(False, False)
    janela_login.configure(bg="#f0f0f0")

    tk.Label(janela_login, text="Gerenciamento de Usuários", font=("Arial", 14, "bold"), 
             bg="#f0f0f0").pack(pady=15)

    tk.Label(janela_login, text="Usuário:", font=("Arial", 10), bg="#f0f0f0").pack(pady=5)
    campo_usuario = tk.Entry(janela_login, width=30)
    campo_usuario.pack()

    tk.Label(janela_login, text="Senha:", font=("Arial", 10), bg="#f0f0f0").pack(pady=5)
    campo_senha = tk.Entry(janela_login, width=30, show="*")
    campo_senha.pack()

    # Permitir Enter para fazer login
    campo_senha.bind('<Return>', lambda event: autenticar_usuario())

    tk.Button(janela_login, text="Entrar", command=autenticar_usuario, 
             bg="#3498db", fg="white", font=("Arial", 11, "bold"), 
             padx=40, pady=8).pack(pady=20)
    
    tk.Label(janela_login, text="Não tem cadastro?", bg="#f0f0f0", 
             font=("Arial", 10)).pack()
    
    tk.Button(janela_login, text="Cadastrar novo usuário", command=cadastrar_usuario, 
             bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
             padx=20, pady=5).pack(pady=5)

    janela_login.mainloop()