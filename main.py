import asyncpg
import uvicorn
import logging
import os
import dotenv

dotenv.load()
UVCORN_HOST = os.getenv("UVCORN_HOST")




logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)')
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

if __name__ == '__main__':
    uvicorn.run('app.app:app', reload=False, host=UVCORN_HOST, port=8000)
