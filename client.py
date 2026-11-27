import asyncio
import json
import uuid

import httpx

async def main():
    async with httpx.AsyncClient(
            base_url="http://localhost:8000",
            timeout=httpx.Timeout(10.0, connect=3.0)
        ) as client:
            session_id = str(uuid.uuid4())
            is_new_chat= True
            while True:
            
                user_message = input("You:").strip()

                response = await client.post("/api/chat-prompt-template-langchain",
                    json={
                        "session_id": session_id,
                        "question":user_message,
                        "is_new_chat": is_new_chat
                    }
                )
                is_new_chat = False
                if response.status_code != 200 :

                    print("Error in generating response")
                    break
                result = response.json()
                print("Bot : ",result["response"])

                if(user_message.lower() == "end"):
                    print("Chat Terminated !! Thanks ")
                    break

asyncio.run(main())

