# minimal_starlette_test.py
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.types import Scope, Receive, Send
import uvicorn

async def homepage(scope: Scope, receive: Receive, send: Send):
    if scope['type'] == 'http':
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'text/plain'),
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, world!',
            'more_body': False,
        })

app = Starlette(routes=[
    Route('/', endpoint=homepage)
])

if __name__ == "__main__":
    print("Starting minimal Starlette test server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000) 