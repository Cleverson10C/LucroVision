# 📊 LucroVisor - Sistema de Gerenciamento de Estoque Inteligente

Sistema completo de gerenciamento para estoque desenvolvido em Python com interface gráfica Tkinter e banco de dados SQLite.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Banco de Dados](#banco-de-dados)
- [Credenciais Padrão](#credenciais-padrão)
- [Capturas de Tela](#capturas-de-tela)

## 🎯 Sobre o Projeto

Sistema desenvolvido para facilitar o gerenciamento de estoque, permitindo controle completo de estoque, vendas, cadastro de produtos e geração de relatórios de lucratividade.

## ✨ Funcionalidades

### 🔐 Sistema de Login
- Cadastro e autenticação de funcionários com nome e senha dinâmicos
- Senha criptografada
- Controle de acesso ao sistema

### 📊 Dashboard Interativo
- **5 Cards de Estatísticas:**
  - Total de produtos cadastrados
  - Alertas de estoque baixo
  - Total de itens em estoque
  - Vendas do mês atual
  - Valor total em estoque
- **Análises em Tempo Real:**
  - Produtos mais vendidos (últimos 30 dias)
  - Produtos próximos ao vencimento
- **Botões de Acesso Rápido** para todas as funcionalidades

### 💰 Registro de Vendas
- Interface intuitiva para registrar vendas
- Busca de produtos em tempo real
- Cálculo automático do valor total
- Validação de estoque disponível
- Atualização automática do estoque após venda
- Confirmação de venda com resumo

### 📦 Cadastro de Produtos
- Cadastro completo com:
  - Nome e categoria
  - Preços de custo e venda 
  - Quantidade em estoque
  - Estoque mínimo (para alertas)
  - Validade (formato MM/YYYY)
- Validações de dados
- Mensagens de erro descritivas

### 📋 Controle de Estoque
- Visualização em tabela de todos os produtos
- Filtros:
  - Todos os produtos
  - Apenas produtos com estoque baixo
- Destaque visual para produtos com estoque crítico
- Informações completas:
  - Nome, categoria, quantidade
  - Estoque mínimo, preço, validade
- Estatísticas em tempo real

### 📈 Relatórios de Lucratividade
- Lucro mensal detalhado
- Lucro anual consolidado
- Cálculo automático baseado em vendas
- Diferença entre preço de custo e venda

## 🛠️ Tecnologias

- **Python 3.13**
- **Tkinter** - Interface gráfica
- **SQLite3** - Banco de dados
- **datetime** - Manipulação de datas

## 📦 Requisitos

- Python 3.8 ou superior
- Tkinter (geralmente incluído no Python)
- SQLite3 (incluído no Python)

### Instalação do Python

**Windows:**
```bash
# Baixe em: https://www.python.org/downloads/
# Durante a instalação, marque "Add Python to PATH"
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-tk
```

**macOS:**
```bash
brew install python-tk
```

## 🚀 Instalação

git clone https://github.com/seu-usuario/farmacia_app.git
1. **Clone ou baixe o projeto:**
```bash
git clone https://github.com/seu-usuario/LucroVisor.git
cd LucroVisor
```

2. **Verifique se o Python está instalado:**
```bash
python --version
```

3. **Crie e ative o ambiente virtual (Windows):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. **Instale as dependências (se houver requirements.txt):**
```powershell
pip install -r requirements.txt
```

5. **Execute o sistema:**
```powershell
python main.py
```

## 💻 Como Usar

### Primeira Execução

1. Execute o arquivo `main.py`
2. O sistema criará automaticamente:
   - Banco de dados `comercio.db`
   - Tabelas necessárias
   - Permite cadastrar o primeiro funcionário

3. Faça login com o funcionário cadastrado:
   - Informe o nome de usuário e senha definidos no cadastro

### Navegação

**Dashboard Principal:**
- Visualize estatísticas gerais
- Acesse todas as funcionalidades pelos botões

**Registrar Venda:**
1. Clique em "💰 Registrar Venda"
2. Busque ou selecione o produto
3. Digite a quantidade
4. Confirme a venda

**Cadastrar Produto:**
1. Clique em "➕ Cadastrar Produto"
2. Preencha todos os campos:
   - Preços: use vírgula (ex: 12,50)
   - Validade: formato MM/YYYY (ex: 12/2026)
3. Clique em "Salvar Produto"

**Controle de Estoque:**
1. Clique em "📦 Ver Estoque"
2. Use os filtros para visualizar:
   - Todos os produtos
   - Apenas estoque baixo
3. Produtos em vermelho = estoque abaixo do mínimo

**Relatórios:**
1. Clique em "📊 Relatórios"
2. Visualize lucros mensais e anuais

## 📁 Estrutura do Projeto

farmacia_app/
│
├── main.py                 # Arquivo principal de execução
├── database.py             # Configuração do banco de dados
├── login.py                # Tela de login
├── dashboard.py            # Dashboard principal
├── vendas.py               # Módulo de vendas
├── cadastro_produto.py     # Cadastro de produtos
├── estoque.py              # Controle de estoque
├── relatorios.py           # Relatórios de lucratividade
├── utils.py                # Funções utilitárias
│
├── comercio.db             # Banco de dados (criado automaticamente)
│
└── README.md               # Este arquivo
```

## 🗄️ Banco de Dados

### Estrutura das Tabelas

**funcionarios**
```sql
- id (INTEGER PRIMARY KEY)
- usuario (TEXT UNIQUE)
- senha (TEXT)
```

**produtos**
```sql
- id (INTEGER PRIMARY KEY)
- nome (TEXT)
- categoria (TEXT)
- preco_custo (REAL)
- preco_venda (REAL)
- quantidade (INTEGER)
- estoque_minimo (INTEGER)
- validade (TEXT) -- Formato: YYYY-MM
```

**vendas**
```sql
- id (INTEGER PRIMARY KEY)
- produto_id (INTEGER)
- quantidade (INTEGER)
- data_venda (TEXT)
- FOREIGN KEY(produto_id) -> produtos(id)
```

## 🔑 Credenciais Padrão

**Login do Sistema:**
- O login agora é feito com nome e senha cadastrados pelo usuário.

⚠️ **Importante:** Cadastre um funcionário administrador na primeira execução!

## 📸 Capturas de Tela

### Dashboard
- Interface principal com cards de estatísticas
- Tabelas de análise em tempo real
- Botões de acesso rápido

### Tela de Vendas
- Busca de produtos
- Seleção e cálculo automático
- Validação de estoque

### Controle de Estoque
- Listagem completa de produtos
- Filtros e destaque visual
- Estatísticas em tempo real

## 🔧 Scripts Utilitários

**Visualizar todo o banco:**
```bash
python visualizar_banco.py
```

**Verificar status:**
```bash
python verificar_banco.py
```

## 📝 Convenções do Código

- **Variáveis:** Nomes descritivos e intuitivos em português
- **Funções:** Documentadas com docstrings
- **Comentários:** Explicativos e objetivos
- **Formatação:** PEP 8 (quando aplicável)

## 🎨 Personalização

### Alterar Cores dos Botões

Edite o arquivo correspondente e modifique os valores `bg`:

```python
# dashboard.py - linha 167
criar_botao(frame_botoes, "💰 Registrar Venda", vendas.tela_vendas, "#e67e22")
#                                                                     ^^^^^^^^
#                                                                     Código da cor
```

### Adicionar Novos Produtos Iniciais

Edite `database.py` na função `inserir_produtos_iniciais()`.

## ⚠️ Troubleshooting

**Problema:** "Tkinter não encontrado"
```bash
# Windows
pip install tk

# Linux
sudo apt-get install python3-tk
```

**Problema:** "Banco de dados não aparece"
- O banco está na mesma pasta do `main.py`
- Nome do arquivo: `farmacia.db`
- Use os scripts de verificação

**Problema:** "Estoque vazio"
- Feche completamente o programa
- Execute novamente `python main.py`
- Os produtos são criados automaticamente na primeira execução

## 📄 Licença

Este projeto é de código aberto e está disponível para fins educacionais.

## 👨‍💻 Autor

Desenvolvido por Cleverson

---

**Versão:** 1.0.0  
**Última atualização:** 30 de novembro de 2025

---

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Execute os scripts de verificação
3. Revise a documentação completa

---

**✨ Obrigado por usar o Sistema de Gerenciamento de Farmácia!**
