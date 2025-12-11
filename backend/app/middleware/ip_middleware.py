from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable


class IPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Получение IP адреса клиента
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0]
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Добавление IP в state запроса
        request.state.client_ip = client_ip
        
        response = await call_next(request)
        return response

