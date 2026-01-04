import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8002/api/ws/chat"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send a query
        query = "Analyze sales for Advil in the last month"
        print(f"Sending: {query}")
        await websocket.send(query)
        
        # Listen for responses
        try:
            while True:
                response = await websocket.recv()
                print(f"Received: {response}")
                if "Final Response" in response:
                    print("Workflow completed successfully.")
                    break
        except Exception as e:
            print(f"Connection closed or error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
