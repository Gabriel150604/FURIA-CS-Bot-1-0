import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from cachetools import TTLCache

app = Flask(__name__)
cache = TTLCache(maxsize=1, ttl=600)  # Cache de 10 minutos

def obter_dados_furia():
    url = 'https://www.hltv.org/team/8297/furia'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ranking
    ranking_div = soup.find('div', class_='profile-team-stat')
    ranking = ranking_div.text.strip() if ranking_div else 'N/A'

    # Jogadores
    jogadores = []
    jogadores_divs = soup.find_all('div', class_='playerFlagName')
    for div in jogadores_divs:
        jogadores.append(div.text.strip())

    # Notícias
    noticias = []
    noticias_section = soup.find_all('a', class_='subTab-newsArticle')[:5]
    for n in noticias_section:
        titulo = n.text.strip()
        link = 'https://www.hltv.org/team/8297/furia#tab-newsBox' + n['href']
        noticias.append({'titulo': titulo, 'link': link})

    # Próximos jogos
    proximos_jogos = []
    eventos = soup.find_all('div', class_='upcomingMatch')[:5]
    for evento in eventos:
        try:
            oponente = evento.find('div', class_='matchTeam team2').text.strip()
            data = evento.find('div', class_='matchTime').text.strip()
            torneio = evento.find('div', class_='matchEventName').text.strip()
            link = 'https://www.hltv.org' + evento.find('a')['href']
            proximos_jogos.append({
                'vs': oponente,
                'data': data,
                'torneio': torneio,
                'link': link
            })
        except:
            continue

    return {
        'ranking': ranking,
        'jogadores': jogadores,
        'noticias': noticias,
        'proximos_jogos': proximos_jogos
    }

@app.route('/furia', methods=['GET'])
def api_furia():
    if 'furia' not in cache:
        cache['furia'] = obter_dados_furia()
    return jsonify(cache['furia'])

@app.route('/limpar_cache', methods=['GET'])
def limpar_cache():
    cache.clear()
    return jsonify({'mensagem': 'Cache limpo com sucesso'})

def run_api():
    app.run(host='0.0.0.0', port=5000)  # Inicializa a API Flask na porta 5000

if __name__ == '__main__':
    run_api()
