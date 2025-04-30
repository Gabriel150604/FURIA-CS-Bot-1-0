import multiprocessing
from api import run_api  # type: ignore # Suponha que você tenha uma função `run_api` para rodar a API
from bot import main     # type: ignore # Suponha que o código do seu bot está na função `main` no arquivo bot.py

def run_bot():
    main()  # Chama a função que roda o bot

def run_server():
    run_api()  # Chama a função que roda a API

if __name__ == '__main__':
    # Cria dois processos para rodar API e Bot simultaneamente
    api_process = multiprocessing.Process(target=run_server)
    bot_process = multiprocessing.Process(target=run_bot)

    # Inicia os dois processos
    api_process.start()
    bot_process.start()

    # Aguarda ambos os processos terminarem (o que normalmente nunca ocorre até você finalizar)
    api_process.join()
    bot_process.join()
