from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict


class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, float] = defaultdict(float)

    async def log_message(self, message: str):
        print(message)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        time_since_last_request = current_time - \
            self.rate_limit_records[client_ip]
        if time_since_last_request < 0.1:
            return Response(content="Rate limit exceeded", status_code=429)

        # Update the time of the last request for this client IP
        self.rate_limit_records[client_ip] = current_time

        # Asynchronous logging
        path = request.url.path
        await self.log_message(f"Request to {path} from {client_ip}")

        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add custom headers to show processing time
        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        # Asynchronous logging for processing time
        await self.log_message(f"Response for {path} took {process_time} seconds")

        return response
