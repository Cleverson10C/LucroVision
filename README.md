# LucroVision

Sistema desktop para gestão de produtos, estoque e vendas, feito em Python. A interface usa CustomTkinter, os dados ficam em SQLite e a API FastAPI permite compartilhar o mesmo banco entre o computador administrativo e os caixas.

## Recursos

- Interface desktop com tema claro, controles arredondados e tabelas formatadas.
- Login com senhas protegidas por PBKDF2-SHA256 e migração de senhas antigas no primeiro acesso.
- Perfis `admin` e `caixa`, validados também pela API.
- Cadastro e atualização de produtos, código de barras, validade e média ponderada de custo/preço.
- Estoque baixo, dashboard, itens mais vendidos, produtos próximos do vencimento e relatórios de lucratividade.
- Vendas com múltiplos produtos, leitor de código de barras e baixa de estoque.
- Quantidades fracionadas para Carnes, Frios, Padaria e Hortifruti.
- API central para compartilhar dados entre computadores na rede local.
- Cópia de segurança consistente do banco, automática a cada 24 horas.

## Tecnologias

- Python 3.10 ou superior
- CustomTkinter 6.0.0 e Tkinter/Tcl-Tk
- SQLite
- FastAPI, Uvicorn e Pydantic
- Requests e Pillow
- cx_Freeze para gerar executáveis Windows

## Instalação para desenvolvimento

No Windows, abra o PowerShell na pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Inicie o painel administrativo local:

```powershell
python main.py
```

No primeiro acesso local, escolha **Criar administrador** para configurar a conta inicial.

## Operação em dois computadores

O computador do administrador também hospeda a API e o banco central. Os computadores devem estar na mesma rede local.

### Computador servidor/administrador

Inicie a API em um terminal e mantenha-o aberto:

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Consulte o IPv4 do computador com `ipconfig`. Em outro terminal, inicie o painel apontando para esse IP:

```powershell
.\venv\Scripts\Activate.ps1
$env:LUCROVISOR_API_URL = "http://192.168.0.10:8000"
python main.py
```

Troque `192.168.0.10` pelo IPv4 real. No primeiro acesso à base central, crie o administrador pela tela de login.

### Computador caixa

Instale o projeto e as dependências, ou use o executável do caixa. Configure o mesmo endereço do servidor:

```powershell
.\venv\Scripts\Activate.ps1
$env:LUCROVISOR_API_URL = "http://192.168.0.10:8000"
python caixa_main.py
```

O programa do caixa solicita login. No painel administrativo, abra **Usuários** para cadastrar funcionários com perfil `caixa` ou outros administradores.

| Perfil | Permissões |
|---|---|
| `admin` | Dashboard, cadastro de produtos, estoque, relatórios, usuários e vendas |
| `caixa` | Consultar produtos disponíveis e registrar vendas |

A sessão precisa ser iniciada novamente depois que a API reiniciar. A API usa HTTP sem criptografia: restrinja a porta 8000 à rede privada da loja e não a encaminhe para a internet.

## Banco de dados e backups

O arquivo principal chama-se `comercio.db`.

- Ao executar scripts Python, fica na pasta do projeto.
- No executável, fica em `%LOCALAPPDATA%\LucroVisor\comercio.db`.
- `LUCROVISOR_DB_PATH` permite definir outro caminho.

Ao iniciar o painel local ou a API, o LucroVision cria um snapshot SQLite consistente em `backups\comercio-AAAAMMDD-HHMMSS.sqlite3`. Outro backup é criado a cada 24 horas e os arquivos com mais de 30 dias são removidos. Mantenha cópias periódicas em outro disco ou computador.

As tabelas são criadas e migradas na inicialização. Em bancos existentes sem perfil de usuário, a migração atribui `admin` ao usuário mais antigo e `caixa` aos demais. Faça uma cópia do banco antes da primeira atualização.

## Executáveis

Gere o executável administrativo:

```powershell
python setup.py build
```

Gere o executável de vendas:

```powershell
python setup_caixa.py build
```

O build inclui CustomTkinter e os arquivos de tema necessários. Para o caixa, ajuste o IP no arquivo `iniciar_caixa.bat` antes de distribuir.

## Estrutura

```text
main.py              Inicialização do painel administrativo
caixa_main.py        Login e entrada dedicada do caixa
ui_compat.py         Tema e adaptação dos widgets CustomTkinter
dashboard.py         Dashboard administrativo
cadastro_produto.py  Cadastro de produtos
vendas.py            Registro de vendas
estoque.py           Consulta e filtros do estoque
relatorios.py        Relatórios de lucratividade
api_server.py        API central FastAPI
api_client.py        Cliente da API
database.py          SQLite, migrações e backups
security.py          Hash e validação de senhas
licenses/            Avisos de licenças de terceiros
tests/               Testes automatizados existentes
```

## Licenças de terceiros

CustomTkinter é distribuído sob licença MIT. A licença e o aviso de copyright estão em [`licenses/customtkinter-MIT.txt`](licenses/customtkinter-MIT.txt) e devem acompanhar as distribuições do software. Consulte também as licenças das demais dependências incluídas no executável.
