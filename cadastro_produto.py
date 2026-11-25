from ui_compat import tk
from tkinter import messagebox
from database import conectar
import logging
from api_client import api_habilitada, salvar_produto as api_salvar_produto

logger = logging.getLogger(__name__)

def tela_cadastro():
    """Cria e exibe a tela de cadastro de produtos"""
    logger.info("Tela de cadastro de produto aberta")

    def normalizar_categoria(categoria_texto):
        """Padroniza categoria para evitar duplicidade por maiúscula/minúscula."""
        categoria_limpa = " ".join(categoria_texto.strip().split())
        return categoria_limpa.title()
    
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
            logger.warning("Formato de data invalido recebido: %s", data_limpa)
            raise ValueError("Formato de data inválido")
        
        if len(partes) != 2:
            logger.warning("Data com partes invalidas: %s", data_limpa)
            raise ValueError("Data deve ter mês e ano")
        
        mes, ano = partes
        
        # Validar valores
        if len(mes) != 2 or len(ano) != 4:
            logger.warning("Data fora do padrao MM/YYYY: %s", data_limpa)
            raise ValueError("Data deve estar no formato MM/YYYY")
        
        mes_int = int(mes)
        ano_int = int(ano)
        
        if mes_int < 1 or mes_int > 12:
            logger.warning("Mes invalido na data: %s", data_limpa)
            raise ValueError("Mês inválido (1-12)")
        if ano_int < 2000 or ano_int > 2100:
            logger.warning("Ano invalido na data: %s", data_limpa)
            raise ValueError("Ano inválido")
        
        # Retornar no formato YYYY-MM (sem dia)
        return f"{ano}-{mes}"
    
    def salvar_produto():
        """Valida e salva o produto no banco de dados"""
        try:
            # Converter valores monetários com tratamento de vírgula
            preco_custo_produto = converter_valor_monetario(campo_preco_custo.get())
            preco_venda_produto = converter_valor_monetario(campo_preco_venda.get())
            categoria_digitada = campo_categoria.get().strip().lower()
            usa_peso = categoria_digitada in {"carnes", "frios", "padaria", "hortifruti"}
            converter_quantidade = (lambda texto: float(texto.replace(",", "."))) if usa_peso else int
            quantidade_produto = converter_quantidade(campo_quantidade.get().strip())
            estoque_minimo_produto = converter_quantidade(campo_estoque_minimo.get().strip())
            
            # Validações de campos obrigatórios
            nome_produto = campo_nome.get().strip()
            if not nome_produto:
                logger.warning("Cadastro de produto falhou: nome obrigatorio vazio")
                messagebox.showerror("Erro", "O nome do produto é obrigatório!")
                return
            
            # Validações de valores
            if preco_custo_produto <= 0 or preco_venda_produto <= 0:
                logger.warning("Cadastro de produto falhou: preco invalido para '%s'", nome_produto)
                messagebox.showerror("Erro", "Os preços devem ser maiores que zero!")
                return
            
            if quantidade_produto < 0 or estoque_minimo_produto < 0:
                logger.warning("Cadastro de produto falhou: quantidade negativa para '%s'", nome_produto)
                messagebox.showerror("Erro", "As quantidades não podem ser negativas!")
                return
            
            # Converter e validar data
            try:
                data_validade_convertida = converter_data_para_banco(campo_validade.get())
            except ValueError as erro_data:
                logger.warning("Cadastro de produto falhou: validade invalida para '%s' (%s)", nome_produto, erro_data)
                messagebox.showerror("Erro", f"Data de validade inválida: {str(erro_data)}\nUse o formato MM/YYYY (ex: 12/2026)")
                return
            
            # Preparar dados para inserção
            categoria_produto = normalizar_categoria(campo_categoria.get())
            codigo_barras_informado = campo_codigo_barras.get().strip()
            # Em SQLite, UNIQUE permite vários NULL, mas não permite vários "".
            # Por isso, quando o campo está vazio, salvamos como NULL.
            codigo_barras_produto = codigo_barras_informado if codigo_barras_informado else None
            dados_produto = (
                nome_produto,
                codigo_barras_produto,
                categoria_produto,
                preco_custo_produto,
                preco_venda_produto,
                quantidade_produto,
                estoque_minimo_produto,
                data_validade_convertida
            )

            if api_habilitada():
                payload = {
                    "nome": nome_produto,
                    "codigo_barras": codigo_barras_produto,
                    "categoria": categoria_produto,
                    "preco_custo": preco_custo_produto,
                    "preco_venda": preco_venda_produto,
                    "quantidade": quantidade_produto,
                    "estoque_minimo": estoque_minimo_produto,
                    "validade": data_validade_convertida,
                }
                logger.info("Enviando cadastro/atualizacao de produto '%s' para API", nome_produto)
                resposta = api_salvar_produto(payload)
                if resposta.get("resultado") == "atualizado":
                    messagebox.showinfo("Sucesso", f"Produto atualizado! Categoria definida como '{categoria_produto}'. Quantidade somada ao estoque. Preço de venda e custo ajustados pela média ponderada.")
                else:
                    messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            else:
                # Inserir ou atualizar no banco de dados
                conexao_banco = conectar()
                cursor_banco = conexao_banco.cursor()

                try:
                    logger.info("Tentando inserir produto '%s' (categoria='%s')", nome_produto, categoria_produto)
                    cursor_banco.execute("""
                        INSERT INTO produtos (nome, codigo_barras, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, dados_produto)
                    logger.info("Produto '%s' cadastrado com sucesso", nome_produto)
                    messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
                except Exception as e:
                    if "UNIQUE constraint failed: produtos.codigo_barras" in str(e):
                        logger.warning("Cadastro de produto falhou: codigo de barras duplicado para '%s'", nome_produto)
                        messagebox.showerror("Erro", "Código de barras já cadastrado para outro produto.")
                    elif "UNIQUE constraint failed" in str(e):
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
                            UPDATE produtos
                            SET categoria=?,
                                codigo_barras=COALESCE(?, codigo_barras),
                                preco_custo=?,
                                preco_venda=?,
                                quantidade=quantidade+?,
                                estoque_minimo=?,
                                validade=?
                            WHERE nome=?
                        """, (
                            categoria_produto,
                            codigo_barras_produto,
                            novo_preco_custo,
                            novo_preco_venda,
                            quantidade_produto,
                            estoque_minimo_produto,
                            data_validade_convertida,
                            nome_produto
                        ))
                        logger.info("Produto '%s' atualizado por media ponderada e soma de estoque", nome_produto)
                        messagebox.showinfo("Sucesso", f"Produto atualizado! Categoria definida como '{categoria_produto}'. Quantidade somada ao estoque. Preço de venda e custo ajustados pela média ponderada.")
                    else:
                        logger.exception("Erro inesperado ao salvar produto '%s': %s", nome_produto, e)
                        messagebox.showerror("Erro", f"Erro ao cadastrar produto: {str(e)}")
                conexao_banco.commit()
                conexao_banco.close()
            janela_cadastro.destroy()
            
        except ValueError:
            logger.warning("Cadastro de produto falhou: valores numericos invalidos")
            messagebox.showerror("Erro", "Valores numéricos inválidos! Verifique os campos de preço e quantidade.")
    janela_cadastro = tk.Toplevel() 
    janela_cadastro.title("Cadastro de Produto")
    janela_cadastro.geometry("380x600")
    # janela_cadastro.resizable(False, False)
    
    # Definir campos do formulário
    campos_formulario = [
        ("Nome", "campo_nome"),
        ("Categoria", "campo_categoria"),
        ("Código de Barras", "campo_codigo_barras"),
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

    
    # Atribuir campos a variáveis específicas
    campo_nome = campos_entrada["campo_nome"]
    campo_categoria = campos_entrada["campo_categoria"]
    campo_codigo_barras = campos_entrada["campo_codigo_barras"]
    campo_preco_custo = campos_entrada["campo_preco_custo"]
    campo_preco_venda = campos_entrada["campo_preco_venda"]
    campo_quantidade = campos_entrada["campo_quantidade"]
    campo_estoque_minimo = campos_entrada["campo_estoque_minimo"]
    campo_validade = campos_entrada["campo_validade"]

    # Label de exemplo para categorias em kg
    label_kg_exemplo = tk.Label(janela_cadastro, text="Exemplo: 2.5 (kg)", fg="gray")

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
