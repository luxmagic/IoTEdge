import asyncio, aiocoap
import aiocoap.resource as resource
from aiocoap.credentials import CredentialsMap
from shared_context import EncryptionContext
from serial_asyncio import open_serial_connection
import secret
from datetime import datetime, timedelta, timezone

time_1 = None
time_2 = None


class SecureResource(resource.Resource):
    
    def __init__(self, serial_writer=None):
        self.server_context = EncryptionContext(
            secret.MASTER_KEY, 
            secret.SENDER_ID, 
            secret.RECIPIENT_ID
        )
        self.content = []
        self.cmd_status = True
        self.status_dev = True
        self.status_web = True
        self.serial_writer = serial_writer
        self.serial_task = None
        self.current_port = None
        self.current_baudrate = None

    def set_content(self, content):
        self.content.append(content)

    def set_status(self, status):
        self.cmd_status = status
    
    def set_device_status(self, status):
        self.status_dev = status

    async def render_get(self, request):
        print("[GET] Data get success")
        protected_payload = self.server_context.protect(self.content.pop())
        self.content = []
        return aiocoap.Message(payload=protected_payload)


    async def render_put(self, request):
        global time_1, time_2
        unprotected_payload = self.server_context.unprotect(request.payload)
        print("[PUT] Cmd: ", unprotected_payload)

        if unprotected_payload.decode().split(':')[0] != str(secret.CMD_COM):
            if self.serial_writer:
                try:
                    time_1 = datetime.now(timezone.utc)
                    encrypted_payload = self.server_context.protect(unprotected_payload)
                    self.serial_writer.write(encrypted_payload + b'\r\n')
                    await self.serial_writer.drain()
                except Exception as e:
                    self.set_device_status(False)
                    self.set_status(False)
                    print("[UART] Write error:", e)
            else:
                self.set_device_status(False)
        else:
            if self.serial_task:
                self.serial_task.cancel()
                try:
                    await self.serial_task
                except asyncio.CancelledError:
                    print("[CMD] Previous serial task cancelled")

            self.current_port = unprotected_payload.decode().split(':')[1]
            self.current_baudrate = unprotected_payload.decode().split(':')[2]
            self.serial_task = asyncio.create_task(read_serial(self.current_port, self.current_baudrate, self))
            
        self.set_content(unprotected_payload)
        protected_payload = self.server_context.protect(self.content.pop())
        return aiocoap.Message(code=aiocoap.CHANGED, payload=protected_payload)

async def read_serial(port, br, res):
    global time_1, time_2
    try:
        reader, writer = await open_serial_connection(url=port, baudrate=br)
        print(f"✅ Connected to to serial port {port}")
        res.serial_writer = writer
        
        while True:
            data = await reader.readuntil(b'\n')
            if data:
                try:
                    data = data[:-2]
                    decrypted_data = res.server_context.unprotect(data)
                    decrypted_data = decrypted_data.decode();
                    time_2 =  datetime.now(timezone.utc)
                    print((time_2-time_1).total_seconds()/2)
                    if decrypted_data.split(':')[0] == str(secret.CMD_DATA):
                        form_data = decrypted_data + ":" + str(datetime.now(timezone.utc))
                        print(form_data)
                        res.set_content(form_data.encode())
                    else:
                        res.set_content(decrypted_data.encode())
                    print(f"[Serial] Data receive")

                except Exception as e:
                    res.set_status(False)
                    print(f"[Serial] Decryption error: {e}")
    except Exception as e:
        res.set_device_status(False)
        print(f"[Serial] Error: {e}")
        await asyncio.sleep(5)
        return
    # finally:
    #     if res.serial_writer:
    #         res.serial_writer.close()
    #         try:
    #             await res.serial_writer.wait_closed()
    #         except:
    #             pass
    #         res.serial_writer = None

async def main():
    root = resource.Site()
    # res = Resource()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    res = SecureResource() 

    root.add_resource(('iot','cmd'), res)
    root.add_resource(('iot', 'data'), res)

    await aiocoap.Context.create_server_context(root, bind=("localhost", 5683))
    print("🚀 CoAP server is running...")
    print("⚠️  Wait COM port number and baudrate")

    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())