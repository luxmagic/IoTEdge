import asyncio
import aiocoap.resource as resource
from aiocoap.credentials import CredentialsMap, PreSharedKey
import aiocoap

import secret

class GetPutResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.set_content(b"Default Data (padded) ")

    def set_content(self, content):  # Заполнение
        self.content = content
        # while len(self.content) <= 1024:
        #     self.content += b"0123456789\n"

    async def render_get(self, request):  # Обработчик GET
        print("[GET] Request received")
        return aiocoap.Message(payload=self.content)

    async def render_put(self, request):  # Обработчик PUT
        print("[PUT] Payload received:", request.payload)
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)


async def main():
    credentials = CredentialsMap()
    credentials['coaps://*'] = PreSharedKey(secret.CLIENT, secret.CLIENT_KEY)

    # Создание корневого ресурса
    root = resource.Site()

    # Ресурс для .well-known/core (для совместимости)
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    # Пользовательский ресурс
    root.add_resource(('iot', 'api'), GetPutResource())

    await aiocoap.Context.create_server_context(root, bind=("localhost", 5684), server_credentials=credentials)
    print("🚀 CoAP server is running...")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())