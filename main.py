import asyncio, aiocoap
import aiocoap.resource as resource
from aiocoap.credentials import CredentialsMap
from shared_context import EncryptionContext
import secret

class SecureResource(resource.Resource):
    def __init__(self):
        self.server_context = EncryptionContext(
            secret.MASTER_KEY, 
            secret.SENDER_ID, 
            secret.RECIPIENT_ID
        )
        self.content = "".encode()

    def set_content(self, content):
        self.content += content

    async def render_get(self, request):
        print("[GET] Request received")
        protected_payload = self.server_context.protect(self.content)
        return aiocoap.Message(payload=protected_payload)

    async def render_put(self, request):
        unprotected_payload = self.server_context.unprotect(request.payload)
        print("[PUT] Payload received:", unprotected_payload)
        self.set_content(unprotected_payload)
        protected_payload = self.server_context.protect(self.content)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=protected_payload)


async def main():
    root = resource.Site()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    root.add_resource(('iot', 'api'), SecureResource())

    await aiocoap.Context.create_server_context(root, bind=("localhost", 5683))
    print("🚀 CoAP server is running...")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())