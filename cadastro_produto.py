import tkinter as tk
from tkinter import messagebox
from database import conectar

def tela_cadastro():
    """Cria e exibe a tela de cadastro de produtos"""
    
    def converter_valor_monetario(valor_texto):
        """Converte string para float, aceitando vírgula ou ponto como separador decimal"""
        return float(valor_texto.replace(',', '.'))
    
    def converter_data_para_banco(data_texto):
        """Converte data de MM/YYYY para YYYY-MM (formato do banco)"""
        data_limpa = data_texto.strip()
        if not data_limpa:
            return ""
        
        # Aceitar tanto MM/YYYY quanto MM-YYYY
        if '/' in data_limpa:
            partes = data_limpa.split('/')
        elif '-' in data_limpa:
            partes = data_limpa.split('-')
        else:
            raise ValueError("Formato de data inválido")
        
        if len(partes) != 2:
            raise ValueError("Data deve ter mês e ano")
        
        mes, ano = partes
        
        # Validar valores
        if len(mes) != 2 or len(ano) != 4:
            raise ValueError("Data deve estar no formato MM/YYYY")
        
        mes_int = int(mes)
        ano_int = int(ano)
        
        if mes_int < 1 or mes_int > 12:
            raise ValueError("Mês inválido (1-12)")
        if ano_int < 2000 or ano_int > 2100:
            raise ValueError("Ano inválido")
        
        # Retornar no formato YYYY-MM (sem dia)
        return f"{ano}-{mes}"
    
    def salvar_produto():
        """Valida e salva o produto no banco de dados"""
        try:
            # Converter valores monetários com tratamento de vírgula
            preco_custo_produto = converter_valor_monetario(campo_preco_custo.get())
            preco_venda_produto = converter_valor_monetario(campo_preco_venda.get())
            quantidade_produto = int(campo_quantidade.get())
            estoque_minimo_produto = int(campo_estoque_minimo.get())
            
            # Validações de campos obrigatórios
            nome_produto = campo_nome.get().strip()
            if not nome_produto:
                messagebox.showerror("Erro", "O nome do produto é obrigatório!")
                return
            
            # Validações de valores
            if preco_custo_produto <= 0 or preco_venda_produto <= 0:
                messagebox.showerror("Erro", "Os preços devem ser maiores que zero!")
                return
            
            if quantidade_produto < 0 or estoque_minimo_produto < 0:
                messagebox.showerror("Erro", "As quantidades não podem ser negativas!")
                return
            
            # Converter e validar data
            try:
                data_validade_convertida = converter_data_para_banco(campo_validade.get())
            except ValueError as erro_data:
                messagebox.showerror("Erro", f"Data de validade inválida: {str(erro_data)}\nUse o formato MM/YYYY (ex: 12/2026)")
                return
            
            # Preparar dados para inserção
            categoria_produto = campo_categoria.get().strip()
            dados_produto = (
                nome_produto,
                categoria_produto,
                preco_custo_produto,
                preco_venda_produto,
                quantidade_produto,
                estoque_minimo_produto,
                data_validade_convertida
            )
            
            # Inserir ou atualizar no banco de dados
            conexao_banco = conectar()
            cursor_banco = conexao_banco.cursor()

            try:
                cursor_banco.execute("""
                    INSERT INTO produtos (nome, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, dados_produto)
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    # Buscar dados atuais do produto
                    cursor_banco.execute("SELECT quantidade, preco_venda, preco_custo FROM produtos WHERE nome=?", (nome_produto,))
                    atual = cursor_banco.fetchone()
                    qtd_atual = atual[0] if atual else 0
                    preco_venda_atual = atual[1] if atual else 0.0
                    preco_custo_atual = atual[2] if atual else 0.0
                    # Calcular preço médio ponderado
                    novo_preco_venda = ((qtd_atual * preco_venda_atual) + (quantidade_produto * preco_venda_produto)) / (qtd_atual + quantidade_produto)
                    novo_preco_custo = ((qtd_atual * preco_custo_atual) + (quantidade_produto * preco_custo_produto)) / (qtd_atual + quantidade_produto)
                    # Atualiza o produto existente e a categoria
                    cursor_banco.execute("""
                        UPDATE produtos SET categoria=?, preco_custo=?, preco_venda=?, quantidade=quantidade+?, estoque_minimo=?, validade=? WHERE nome=?
                    """, (
                        categoria_produto,
                        novo_preco_custo,
                        novo_preco_venda,
                        quantidade_produto,
                        estoque_minimo_produto,
                        data_validade_convertida,
                        nome_produto
                    ))
                    messagebox.showinfo("Sucesso", f"Produto atualizado! Categoria definida como '{campo_categoria.get()}'. Quantidade somada ao estoque. Preço de venda e custo ajustados pela média ponderada.")
                else:
                    messagebox.showerror("Erro", f"Erro ao cadastrar produto: {str(e)}")
            conexao_banco.commit()
            conexao_banco.close()
            janela_cadastro.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores numéricos estão corretos!\nUse vírgula ou ponto para decimais.")
    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastro de Produto")
    janela_cadastro.geometry("380x480")
    # janela_cadastro.resizable(False, False)
    
    # Definir campos do formulário
    campos_formulario = [
        ("Nome", "campo_nome"),
        ("Categoria", "campo_categoria"),
        ("Preço de Custo", "campo_preco_custo"),
        ("Preço de Venda", "campo_preco_venda"),
        ("Quantidade", "campo_quantidade"),
        ("Estoque Mínimo", "campo_estoque_minimo"),
        ("Validade (MM/YYYY)", "campo_validade")
    ]

    # Criar campos de entrada
    campos_entrada = {}
    labels_campos = {}
    for rotulo_campo, nome_variavel in campos_formulario:
        labels_campos[nome_variavel] = tk.Label(janela_cadastro, text=rotulo_campo)
        labels_campos[nome_variavel].pack(pady=5)
        campos_entrada[nome_variavel] = tk.Entry(janela_cadastro)
        campos_entrada[nome_variavel].pack(padx=15, pady=2)

    # Campo e label para exemplo de kg
    label_kg_exemplo = tk.Label(janela_cadastro, text="(Ex: 0,350 para 350g. Digite o peso em kg)", fg="gray")

    # Atribuir campos a variáveis específicas
    campo_nome = campos_entrada["campo_nome"]
    campo_categoria = campos_entrada["campo_categoria"]
    campo_preco_custo = campos_entrada["campo_preco_custo"]
    campo_preco_venda = campos_entrada["campo_preco_venda"]
    campo_quantidade = campos_entrada["campo_quantidade"]
    campo_estoque_minimo = campos_entrada["campo_estoque_minimo"]
    campo_validade = campos_entrada["campo_validade"]

    def ao_mudar_categoria(event):
        categoria = campo_categoria.get().strip().lower()
        categorias_kg = ["carnes", "frios", "padaria", "hortifruti"]
        if categoria in categorias_kg:
            label_kg_exemplo.pack(after=campo_quantidade)
            labels_campos["campo_quantidade"].config(text="Peso (kg)")
        else:
            label_kg_exemplo.pack_forget()
            labels_campos["campo_quantidade"].config(text="Quantidade")

    campo_categoria.bind("<FocusOut>", ao_mudar_categoria)
    campo_categoria.bind("<KeyRelease>", ao_mudar_categoria)

    # Botão de salvar
    tk.Button(janela_cadastro, text="Salvar Produto", bg="#27ae60", fg="white", command=salvar_produto).pack(pady=10)