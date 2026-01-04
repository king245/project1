from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from langchain_core.messages import HumanMessage

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello from DataPella API"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        from app.agents.graph import app_graph
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"User said: {data}")
            
            # Initial state
            inputs = {"user_query": data, "messages": [HumanMessage(content=data)]}
            
            # Run graph
            async for event in app_graph.astream(inputs):
                for key, value in event.items():
                    await manager.broadcast(f"Agent Update [{key}]: Processing complete.")
            
            # Final result extraction (simplified for streaming demo)
            # In real usage, we'd pick the final state
            final_state = await app_graph.ainvoke(inputs)
            final_response = final_state.get("final_response")
            
            await manager.broadcast(f"Final Response: {str(final_response)}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        await manager.broadcast(f"Error: {str(e)}")
        manager.disconnect(websocket)
