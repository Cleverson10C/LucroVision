from ui_compat import tk
from tkinter import messagebox
from database import conectar
import dashboard
import vendas
import logging
from api_client import (api_habilitada, bootstrap_necessario, cadastrar_usuario as api_cadastrar_usuario,
                        login as api_login, perfil_atual as api_perfil_atual)
from api_client import encerrar_sessao as api_encerrar_sessao
from security import gerar_hash_senha, verificar_hash_senha
logger = logging.getLogger(__name__)
_perfil_local = ""


def perfil_atual():
    return api_perfil_atual() if api_habilitada() else _perfil_local


def _cadastrar_usuario_local(usuario, senha):
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        if cursor.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0] > 0:
            raise ValueError("O cadastro inicial já foi concluído. Cadastros adicionais exigem um administrador.")
        cursor.execute(
            "INSERT INTO funcionarios (usuario, senha, perfil) VALUES (?, ?, 'admin')",
            (usuario, gerar_hash_senha(senha)),
        )
        conexao.commit()
    finally:
        conexao.close()


def verificar_login(usuario, senha):
    """Verifica se o usuário e senha são válidos no banco de dados."""
    global _perfil_local
    logger.info("Tentativa de login para usuario '%s'", usuario)
    if api_habilitada():
        try:
            autenticado = api_login(usuario, senha)
            if autenticado:
                logger.info(
                    "Login via API realizado para usuario '%s' com perfil '%s'",
                    usuario,
                    api_perfil_atual(),
                )
            else:
                logger.warning("Falha de login via API para usuario '%s'", usuario)
            return autenticado
        except Exception as exc:
            logger.exception("Falha ao autenticar via API: %s", exc)
            return False

    conexao_banco = conectar()
    cursor_banco = conexao_banco.cursor()
    cursor_banco.execute("SELECT id, senha, perfil FROM funcionarios WHERE usuario=?", (usuario,))
    funcionario_encontrado = cursor_banco.fetchone()

    if not funcionario_encontrado:
        logger.warning("Falha de login: usuario '%s' nao encontrado", usuario)
        conexao_banco.close()
        return False

    funcionario_id, senha_armazenada, perfil = funcionario_encontrado
    _perfil_local = perfil or "caixa"
    senha_armazenada = senha_armazenada or ""

    # Suporta usuários antigos com senha em texto puro e migra para hash no primeiro login.
    if "$" in senha_armazenada and verificar_hash_senha(senha, senha_armazenada):
        logger.info("Login realizado com sucesso para usuario '%s' (hash)", usuario)
        conexao_banco.close()
        return True

    if senha_armazenada == senha:
        novo_hash = gerar_hash_senha(senha)
        cursor_banco.execute("UPDATE funcionarios SET senha=? WHERE id=?", (novo_hash, funcionario_id))
        conexao_banco.commit()
        logger.info("Senha legado migrada para hash para usuario '%s'", usuario)
        logger.info("Login realizado com sucesso para usuario '%s' (migrado)", usuario)
        conexao_banco.close()
        return True

    logger.warning("Falha de login: senha invalida para usuario '%s'", usuario)
    conexao_banco.close()
    return False


def cadastrar_usuario():
    """Abre tela para cadastrar novo usuário"""
    logger.info("Tela de cadastro de usuario aberta")
    def salvar_usuario():
        """Salva o novo usuário no banco de dados"""
        novo_usuario = campo_novo_usuario.get().strip()
        nova_senha = campo_nova_senha.get().strip()
        confirmar_senha = campo_confirmar_senha.get().strip()
        
        # Validações
        if not novo_usuario or not nova_senha:
            logger.warning("Cadastro de usuario falhou: campos obrigatorios vazios")
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if len(novo_usuario) < 4:
            logger.warning("Cadastro de usuario falhou: usuario curto (%s)", novo_usuario)
            messagebox.showerror("Erro", "Usuário deve ter pelo menos 4 caracteres!")
            return
        
        if len(nova_senha) < 4:
            logger.warning("Cadastro de usuario falhou: senha curta para usuario '%s'", novo_usuario)
            messagebox.showerror("Erro", "Senha deve ter pelo menos 4 caracteres!")
            return
        
        if nova_senha != confirmar_senha:
            logger.warning("Cadastro de usuario falhou: confirmacao divergente para usuario '%s'", novo_usuario)
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return
        
        if api_habilitada():
            try:
                if not bootstrap_necessario():
                    messagebox.showerror("Acesso restrito", "O cadastro inicial já foi concluído. Peça ao administrador para criar usuários.")
                    return
            except Exception as erro:
                messagebox.showerror("Erro de conexão", f"Não foi possível verificar o servidor: {erro}")
                return

        # Cadastrar novo usuário
        try:
            logger.info("Tentando cadastrar usuario '%s'", novo_usuario)
            if api_habilitada():
                api_cadastrar_usuario(novo_usuario, nova_senha, "admin")
            else:
                _cadastrar_usuario_local(novo_usuario, nova_senha)
            logger.info("Usuario '%s' cadastrado com sucesso", novo_usuario)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela_cadastro.destroy()
        except Exception as erro:
            logger.exception("Erro ao cadastrar usuario '%s': %s", novo_usuario, erro)
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(erro)}")
    
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
    logger.info("Tela de login iniciada")
    
    def autenticar_usuario():
        """Valida as credenciais e abre a tela permitida pelo perfil."""
        nome_usuario = campo_usuario.get().strip()
        senha_usuario = campo_senha.get().strip()
        
        if not nome_usuario or not senha_usuario:
            logger.warning("Tentativa de login com campos vazios")
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if verificar_login(nome_usuario, senha_usuario):
            perfil = perfil_atual()
            logger.info("Usuario '%s' autenticado com perfil '%s'.", nome_usuario, perfil)
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            if perfil == "admin":
                janela_login.destroy()
                dashboard.abrir_dashboard()
            elif perfil == "caixa":
                janela_login.withdraw()
                vendas.tela_vendas(ao_fechar=janela_login.destroy)
            else:
                logger.error("Acesso negado para perfil desconhecido '%s'.", perfil)
                if api_habilitada():
                    api_encerrar_sessao()
                messagebox.showerror("Acesso negado", "O perfil deste usuário não é válido.")
        else:
            logger.warning("Autenticacao negada para usuario '%s'", nome_usuario)
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    janela_login = tk.Tk()
    janela_login.title("Login - Sistema Gerenciamento")
    janela_login.geometry("450x320")
    # janela_login.resizable(False, False)
    janela_login.configure(bg="#f0f0f0")

    tk.Label(janela_login, text="Gerenciamento de Usuários", font=("Segoe UI", 20, "bold"),
             bg="#f0f0f0").pack(pady=15)

    tk.Label(janela_login, text="Usuário:", font=("Arial", 15, "bold"), bg="#f0f0f0").pack(pady=5)
    campo_usuario = tk.Entry(janela_login, width=300, height=40)
    campo_usuario.pack()

    tk.Label(janela_login, text="Senha:", font=("Arial", 15, "bold"), bg="#f0f0f0").pack(pady=5)
    campo_senha = tk.Entry(janela_login, width=300, height=40, show="*")
    campo_senha.pack()

    # Permitir Enter para fazer login
    campo_senha.bind('<Return>', lambda event: autenticar_usuario())

    tk.Button(janela_login, text="Entrar", command=autenticar_usuario,
             width=100, height=40, bg="#3498db", fg="white", font=("Segoe UI", 16, "bold"),
             padx=40, pady=8).pack(pady=20)
    
    inicializacao_pendente = False
    try:
        if api_habilitada():
            inicializacao_pendente = bootstrap_necessario()
        else:
            conexao = conectar()
            inicializacao_pendente = conexao.execute("SELECT COUNT(*) FROM funcionarios").fetchone()[0] == 0
            conexao.close()
    except Exception:
        logger.exception("Não foi possível consultar estado de configuração inicial")
    if inicializacao_pendente:
        tk.Label(janela_login, text="Primeira configuração: crie a conta administradora.", bg="#f0f0f0", font=("Segoe UI", 15, "bold")).pack()
        tk.Button(janela_login, text="Criar administrador", command=cadastrar_usuario,
                  bg="#27ae60", fg="white", font=("Segoe UI", 15, "bold"), padx=20, pady=5).pack(pady=5)

    janela_login.mainloop()
