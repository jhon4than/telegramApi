import requests
import time

url = 'https://cgp.safe-iplay.com/cgpapi/liveFeed/GetLiveTables'

headers = {
    'authority': 'cgp.safe-iplay.com',
    'method': 'POST',
    'path': '/cgpapi/liveFeed/GetLiveTables',
    'scheme': 'https',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,es;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://br.888casino.com',
    'Referer': 'https://br.888casino.com/',

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0 Safari/537.36',
  
}

data = 'regulationID=4&lang=por'

while True:
    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response_json = response.json()
            live_tables = response_json.get('LiveTables', {})
            specific_game_id = '2330135'  # Coloque aqui o id do live table

            if specific_game_id in live_tables:
                specific_game_info = live_tables[specific_game_id]
                
                if 'RouletteLast5Numbers' in specific_game_info:
                    last_5_numbers = specific_game_info['RouletteLast5Numbers']
                    print(f"Últimos 5 números da roleta para o GameID {specific_game_id}: {last_5_numbers}")
                else:
                    print(f"A chave 'RouletteLast5Numbers' não foi encontrada para o GameID {specific_game_id}.")
            else:
                print(f"GameID {specific_game_id} não encontrado na resposta.")

        else:
            print(f"Erro na requisição: {response.status_code}")

        # Aguardar 5 segundos antes de fazer a próxima requisição
        time.sleep(5)

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro durante a requisição: {e}")
        # Aguardar 5 segundos antes de tentar novamente
        time.sleep(5)