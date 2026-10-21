import telebot
import requests
import os
from PIL import Image, ImageFont, ImageDraw, ImageOps

KEY_TELEGRAM = os.getenv("CHAVE_TELEGRAM") # Chave do bot do Telegram, obtida através do BotFather
KEY_OPENTHEWEATHER = os.getenv("CHAVE_OPENWEATHER") # Chave da API do OpenWeatherMap, obtida através do site https://openweathermap.org/api

bot = telebot.TeleBot(KEY_TELEGRAM)
def pegar_clima(cidade):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={KEY_OPENTHEWEATHER}&lang=pt_br&units=metric"
    
    resposta = requests.get(url)
    dados = resposta.json() #converte a resposta da API em um dicionário Python

    if dados['cod'] == 200:
        return {
            "sucesso": True,
            "cidade": cidade.title(),
            "descricao": dados['weather'][0]['description'],
            "temperatura": int(dados['main']['temp']),
            "condicao_principal": dados['weather'][0]['main'] # 'Clear' (Sol), 'Clouds' (Nuvens), 'Rain' (Chuva)
        }
    else:
        return {"sucesso": False}

    
def gerar_imagem(dados_clima):
    condicao = dados_clima["condicao_principal"]
    
    # Escolhe a imagem de fundo baseada no clima
    if condicao == "Clear":
        arquivo_fundo = "sol.jpeg"
    elif condicao in ["Clouds", "Mist", "Fog"]:
        arquivo_fundo = "nublado.jpeg"
    elif condicao in ["Rain", "Drizzle", "Thunderstorm"]:
        arquivo_fundo = "chuva.jpeg"
    else:
        arquivo_fundo = "padrao.jpeg"
    
    try:
        img = Image.open(arquivo_fundo)
        img = ImageOps.fit(img, (600, 400))  # Ajusta a imagem para 600x400 pixels
    except FileNotFoundError: 
        print(f"Aviso: Imagem '{arquivo_fundo}' não encontrada. Usando fundo azul.") #caso a imagem não seja encontrada, cria uma imagem azul como fundo
        img = Image.new('RGB', (600, 400), color=(73, 109, 137))
    
    draw = ImageDraw.Draw(img)
    try:
        fonte_cidade = ImageFont.truetype("arial.ttf", 50)
        fonte_temp = ImageFont.truetype("arial.ttf", 80)
        fonte_desc = ImageFont.truetype("arial.ttf", 40)
    except:
        fonte_cidade = ImageFont.load_default()
        fonte_temp = ImageFont.load_default()
        fonte_desc = ImageFont.load_default()
    
    texto_cidade = dados_clima["cidade"]
    texto_temp = f"{dados_clima['temperatura']}°C"
    texto_desc = dados_clima["descricao"].capitalize()

    largura_img, altura_img = img.size #pega a largura e altura da imagem para posicionar o texto de forma proporcional

    pos_x_cidade = largura_img * 0.05
    pos_y_cidade = altura_img * 0.05

    pos_x_temp = largura_img * 0.05
    pos_y_temp = altura_img * 0.75
 
    pos_x_desc = largura_img * 0.05
    pos_y_desc = altura_img * 0.65

    deslocamento_sombra = 2  #sombra para o texto, para melhorar a visibilidade

    draw.text((pos_x_cidade + deslocamento_sombra, pos_y_cidade + deslocamento_sombra), texto_cidade, font=fonte_cidade, fill=(0, 0, 0))
    draw.text((pos_x_temp + deslocamento_sombra, pos_y_temp + deslocamento_sombra), texto_temp, font=fonte_temp, fill=(0, 0, 0))
    draw.text((pos_x_desc + deslocamento_sombra, pos_y_desc + deslocamento_sombra), texto_desc, font=fonte_desc, fill=(0, 0, 0))

    draw.text((pos_x_cidade, pos_y_cidade), texto_cidade, font=fonte_cidade, fill=(255, 255, 255))
    draw.text((pos_x_temp, pos_y_temp), texto_temp, font=fonte_temp, fill=(255, 255, 255))
    draw.text((pos_x_desc, pos_y_desc), texto_desc, font=fonte_desc, fill=(255, 255, 255))

    caminho_imagem_salva = "clima_gerado.jpg" #salva a imagem gerada com o nome clima_gerado.jpg
    img.save(caminho_imagem_salva)
    return caminho_imagem_salva
    
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Olá! Eu sou o bot de clima.\nDigite /clima e em seguida o nome de uma cidade para saber o clima atual.")


@bot.message_handler(commands=['clima'])
def clima(message):
    cidade = message.text.replace('/clima ', '').strip()
    if cidade != '':
        resposta_clima = pegar_clima(cidade)

        if resposta_clima["sucesso"]:
            caminho_imagem = gerar_imagem(resposta_clima)
            with open(caminho_imagem, 'rb') as img:
                bot.send_photo(message.chat.id, img)
            os.remove(caminho_imagem) #remove a imagem temporária após o envio para o usuário
            bot.reply_to(message, f"O clima em {resposta_clima['cidade']} é: {resposta_clima['descricao']}, com temperatura de {resposta_clima['temperatura']:.1f}°C.")
        
        else:
            bot.reply_to(message, "Cidade não encontrada. Verifique se você digitou o nome corretamente!")
    else:
        bot.reply_to(message, "Por favor, digite o nome de uma cidade após o comando /clima.")

print("Bot com imagem está rodando...")
bot.polling()
