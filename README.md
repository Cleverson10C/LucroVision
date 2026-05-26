# LucroVision

Sistema desktop de gerenciamento de estoque e vendas em Python, com interface Tkinter e banco SQLite.

## Visão geral

O LucroVision centraliza operações de cadastro de produtos, controle de estoque, registro de vendas e visualização de indicadores de desempenho.

## Funcionalidades

- Login e cadastro de usuários (local ou via API), com hash de senha (`PBKDF2-SHA256`) e migração automática de senha legada
- Dashboard com métricas em tempo real:
  - Total de produtos
  - Produtos com estoque baixo
  - Total de itens em estoque
  - Vendas no mês
  - Valor estimado do estoque
- Ranking de produtos mais vendidos (últimos 30 dias)
- Lista de produtos próximos ao vencimento
- Cadastro de produtos com validações:
  - Nome, categoria, código de barras, preços, quantidade, estoque mínimo e validade
  - Conversão de validade `MM/YYYY` para `YYYY-MM`
  - Atualização de produto existente por nome com média ponderada de preço
- Registro de vendas:
  - Busca por nome
  - Leitura por código de barras
  - Venda com múltiplos itens
  - Atualização automática do estoque
- Controle de estoque com filtros por status e categoria
- Relatórios de lucratividade mensal e anual
- Modo cliente-servidor opcional para operação multi-caixa (API FastAPI)
- Modo Caixa dedicado (somente vendas) para uso no PDV
- Logging estruturado em arquivo para facilitar troubleshooting
- Testes automatizados para regras críticas (login, estoque e relatórios)

## Tecnologias

- Python 3
- Tkinter
- SQLite3
- Pillow (logo no dashboard)
- Requests
- FastAPI
- Uvicorn
- Pydantic
- Pytest

## Requisitos

- Python 3.10+
- `pip`

## Instalação

1. Clone o projeto:

```bash
git clone <url-do-seu-repositorio>
cd LucroVision
```

2. Crie e ative um ambiente virtual (recomendado):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale dependências:

```powershell
pip install -r requirements.txt
```

## Como executar

```powershell
python main.py
```

Na primeira execução, as tabelas do banco são criadas automaticamente.

## Testes

```powershell
pytest
```

## Modo servidor local (API central)

Para operar com vários caixas, execute um servidor local (API) em uma máquina central da loja:

1. Instale dependências:

```powershell
pip install -r requirements.txt
```

2. Inicie a API:

```powershell
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

3. Em cada caixa/cliente, configure a URL da API antes de abrir o sistema:

```powershell
$env:LUCROVISOR_API_URL = "http://IP_DO_SERVIDOR:8000"
python main.py
```

Quando `LUCROVISOR_API_URL` está configurada, o cliente usa a API central para login, vendas, estoque, cadastro, dashboard e relatórios.

## Estrutura do projeto

```text
LucroVision/
|- main.py                # Ponto de entrada
|- api_server.py          # API central para modo multi-caixa
|- api_client.py          # Cliente HTTP usado pela aplicação desktop
|- security.py            # Hash e verificação de senha
|- database.py            # Conexão e criação/migração de tabelas
|- login.py               # Login e cadastro de usuários
|- dashboard.py           # Painel principal
|- cadastro_produto.py    # Cadastro e atualização de produtos
|- vendas.py              # Registro de vendas
|- estoque.py             # Visualização e filtros de estoque
|- relatorios.py          # Relatórios de lucro
|- relatorios_data.py     # Camada de dados dos relatórios (API/local)
|- caixa_main.py          # Entrypoint do modo Caixa (somente vendas)
|- setup_caixa.py         # Build do executável do Caixa
|- tests/                 # Testes automatizados (pytest)
|- requirements.txt
|- setup.py               # Build de executável (cx_Freeze)
|- Logo.png / Logo.ico
|- licenca.txt
```

## Banco de dados

Arquivo padrão: `comercio.db`

A aplicação resolve o caminho do banco assim:

- Execução como script Python: pasta do projeto
- Execução como executável: `%LOCALAPPDATA%\\LucroVisor\\comercio.db`
- Override opcional por variável de ambiente:

```powershell
$env:LUCROVISOR_DB_PATH = "C:\dados\lucrovision\comercio.db"
```

### Tabelas

- `funcionarios(id, usuario, senha)`
- `produtos(id, nome, codigo_barras, categoria, preco_custo, preco_venda, quantidade, estoque_minimo, validade)`
- `vendas(id, produto_id, quantidade, data_venda)`

## Observações importantes

- Senhas novas são salvas com hash seguro e usuários legados são migrados no primeiro login válido.
- O sistema opera local (SQLite) ou remoto (API), conforme `LUCROVISOR_API_URL`.
- Existe código de validação de licença em `login.py`, mas ele está comentado.
- Para categorias como `Carnes`, `Frios`, `Padaria` e `Hortifruti`, o sistema permite operação em kg.

## Troubleshooting

- Erro de Tkinter/Tcl ao abrir o sistema:
  - Reinstale o Python com suporte Tcl/Tk
  - Em ambiente local, prefira uma instalação estável do Python
- Ícone ou logo não carregam no executável:
  - Verifique se `Logo.png` e `Logo.ico` estão disponíveis no build

## Build de executável (opcional)

```powershell
python setup.py build
```

## Build do EXE do Caixa (somente vendas)

Arquivos adicionados:
- `caixa_main.py` (entrypoint do caixa)
- `setup_caixa.py` (build do executável do caixa)
- `iniciar_caixa.bat` (atalho para iniciar com `LUCROVISOR_API_URL`)

Gerar o EXE:

```powershell
python setup_caixa.py build
```

Após o build, copie para o computador caixa:
- conteúdo da pasta `build\...`
- `iniciar_caixa.bat` (ajuste IP/porta da API)

## Autor

Cleverson

