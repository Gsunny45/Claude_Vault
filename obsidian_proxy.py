import asyncio, sys

LISTEN_PORT = 27124
OBSIDIAN_HOST = "127.0.0.1"
OBSIDIAN_PORT = 27123

async def pipe(reader, writer):
    try:
        while chunk := await reader.read(4096):
            writer.write(chunk)
            await writer.drain()
    except Exception:
        pass
    finally:
        try: writer.close()
        except: pass

async def handle(client_r, client_w):
    try:
        obs_r, obs_w = await asyncio.open_connection(OBSIDIAN_HOST, OBSIDIAN_PORT)
        await asyncio.gather(pipe(client_r, obs_w), pipe(obs_r, client_w))
    except Exception as e:
        pass

async def main():
    srv = await asyncio.start_server(handle, "0.0.0.0", LISTEN_PORT)
    print(f"Obsidian proxy: 0.0.0.0:{LISTEN_PORT} -> {OBSIDIAN_HOST}:{OBSIDIAN_PORT}", flush=True)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())