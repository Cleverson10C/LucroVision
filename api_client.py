import logging
import os
from typing import Any, Dict, List
import requests

logger = logging.getLogger(__name__)

def api_url() -> str:
    return os.environ.get("LUCROVISOR_API_URL", "").strip().rstrip("/")

def api_habilitada() -> bool:
    return bool(api_url())

def _request(method: str, path: str, *, params=None, json=None, timeout: int = 8) -> Dict[str, Any]:
    base = api_url()
    if not base:
        raise RuntimeError("LUCROVISOR_API_URL não configurada")

    url = f"{base}{path}"
    logger.debug("API request %s %s", method, url)
    resposta = requests.request(method, url, params=params, json=json, timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()

def login(usuario: str, senha: str) -> bool:
    data = _request("POST", "/auth/login", json={"usuario": usuario, "senha": senha})
    return bool(data.get("autenticado", False))

def cadastrar_usuario(usuario: str, senha: str) -> None:
    _request("POST", "/auth/register", json={"usuario": usuario, "senha": senha})

def dashboard_dados() -> Dict[str, Any]:
    return _request("GET", "/dashboard")

def produtos_disponiveis(filtro: str = "") -> List[Dict[str, Any]]:
    data = _request("GET", "/produtos/disponiveis", params={"filtro": filtro})
    return data.get("itens", [])


def produto_por_codigo(codigo: str) -> Dict[str, Any] | None:
    data = _request("GET", f"/produtos/codigo/{codigo}")
    return data.get("item")


def registrar_venda(itens: List[Dict[str, Any]], data_venda: str) -> Dict[str, Any]:
    return _request("POST", "/vendas", json={"itens": itens, "data_venda": data_venda})

def salvar_produto(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _request("POST", "/produtos/salvar", json=payload)

def estoque_categorias() -> List[str]:
    data = _request("GET", "/estoque/categorias")
    return data.get("categorias", [])

def estoque_lista(tipo: str, categoria: str) -> List[Dict[str, Any]]:
    data = _request("GET", "/estoque", params={"tipo": tipo, "categoria": categoria})
    return data.get("itens", [])

def estoque_estatisticas() -> Dict[str, Any]:
    return _request("GET", "/estoque/estatisticas")

def relatorios_dados() -> Dict[str, Any]:
    return _request("GET", "/relatorios")
