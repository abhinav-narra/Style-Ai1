import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv('c:/styleai/backend/.env')

sys.path.insert(0, 'c:/styleai/backend')

from app.api.v1.endpoints.chat import generate_chat_response

async def main():
    print('Testing Chatbot Groq Connection...')
    reply = await generate_chat_response('What should I wear to a winter wedding in New York?', [])
    print('\n--- AI STYLIST REPLY ---')
    print(reply)

if __name__ == '__main__':
    asyncio.run(main())
