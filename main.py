import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

leiloes = {}
usuarios_no_leilao = {}
guild = discord.Object(id=GUILD_ID)

unicode_fonts = {
    'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽', 'G': '𝔾', 'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃',
    'M': '𝕄', 'N': 'ℕ', 'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'S': '𝕊', 'T': '𝕋', 'U': '𝕌', 'V': '𝕍', 'W': '𝕎', 'X': '𝕏',
    'Y': '𝕐', 'Z': 'ℤ',
    
    'a': '𝕒', 'b': '𝕓', 'c': '𝕔', 'd': '𝕕', 'e': '𝕖', 'f': '𝕗', 'g': '𝕘', 'h': '𝕙', 'i': '𝕚', 'j': '𝕛', 'k': '𝕜', 'l': '𝕝',
    'm': '𝕞', 'n': '𝕟', 'o': '𝕠', 'p': '𝕡', 'q': '𝕢', 'r': '𝕣', 's': '𝕤', 't': '𝕥', 'u': '𝕦', 'v': '𝕧', 'w': '𝕨', 'x': '𝕩',
    'y': '𝕪', 'z': '𝕫',
    
    'á': '𝕒́', 'é': '𝕖́', 'í': '𝕚́', 'ó': '𝕠́', 'ú': '𝕦́', 'ã': '𝕒̃', 'õ': '𝕠̃', 'à': '𝕒̀', 'è': '𝕖̀', 'ì': '𝕚̀', 'ò': '𝕠̀', 
    'ù': '𝕦̀', 'â': '𝕒̂', 'ê': '𝕖̂', 'î': '𝕚̂', 'ô': '𝕠̂', 'û': '𝕦̂', 'ä': '𝕒̈', 'ë': '𝕖̈', 'ï': '𝕚̈', 'ö': '𝕠̈', 'ü': '𝕦̈', 
    'ç': '𝕔̧', 'Ç': 'ℂ̧', 'á': '𝕒́', 'Á': '𝔸́', 'é': '𝕖́', 'É': '𝔼́', 'í': '𝕚́', 'Í': '𝕀́', 'ó': '𝕠́', 'Ó': '𝕆́', 'ú': '𝕦́', 
    'Ú': '𝕌́'
}

def to_unicode_font(text):
    return ''.join([unicode_fonts.get(char, char) for char in text])

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos de barra!')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

@bot.tree.command(name='criarleilao', description='Cria um novo leilão')
async def criarleilao(interaction: discord.Interaction, item: str, duracao: float, imagem: discord.Attachment):
    if interaction.channel_id in leiloes:
        await interaction.response.send_message('Já existe um leilão em andamento neste canal!', ephemeral=True)
        return
    
    canal_nome = to_unicode_font(item)

    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="═══════❯LEILAO DE ITENS❮═══════")

    if not category:
        category = await guild.create_category("Leilões")
    
    leilao_channel = await guild.create_text_channel(canal_nome, category=category)

    fim_leilao = datetime.now(timezone.utc) + timedelta(hours=duracao)

    leiloes[leilao_channel.id] = {
        'item': item,
        'maior_lance': 0,
        'vencedor': None,
        'imagem': imagem.url,
        'fim': fim_leilao
    }
    
    embed = discord.Embed(
        title=f"Leilão do item {item.title()}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Duração do leilão", value=f"{duracao} horas", inline=False)
    embed.add_field(name="Como dar o seu lance", value="De o seu lance com o comando /darlance", inline=True)
    embed.set_image(url=imagem.url)
    
    await leilao_channel.send(embed=embed)

    embed_comando = discord.Embed(
        title=f"Leilão iniciado para {item.title()}!",
        description=f"O leilão de **{item}** foi iniciado no canal {leilao_channel.mention}.\n\n"
                    f"**Duração**: {duracao} horas\n",
        color=discord.Color.green()
    )
    embed_comando.set_image(url=imagem.url)
    await interaction.response.send_message(embed=embed_comando)
    
    while True:
        agora = datetime.now(timezone.utc)
        fim = leiloes[leilao_channel.id]['fim']
        segundos_restantes = (fim - agora).total_seconds()

        if segundos_restantes <= 0:
            break

        await asyncio.sleep(min(10, segundos_restantes))
        
    if leiloes[leilao_channel.id]['vencedor']:
        embed = discord.Embed(
            title='Leilão Encerrado!',
            color=discord.Color.red()
        )
        embed.add_field(name='Vencedor', value=leiloes[leilao_channel.id]['vencedor'], inline=False)
        embed.add_field(name='Item Arrematado', value=leiloes[leilao_channel.id]['item'], inline=False)
        embed.add_field(name='Maior Lance', value=f"{leiloes[leilao_channel.id]['maior_lance']} pontos", inline=False)
        
        imagem_path = 'images/VENDIDO.jpg'
        file = discord.File(imagem_path, filename='VENDIDO.jpg')
        embed.set_image(url=f"attachment://VENDIDO.jpg")
        
        await leilao_channel.send(embed=embed, file=file)
    else:
        await leilao_channel.send('Leilão encerrado sem lances.')
    
    for user_id in list(usuarios_no_leilao.keys()):
        if usuarios_no_leilao[user_id] == leilao_channel.id:
            del usuarios_no_leilao[user_id]
    
    del leiloes[leilao_channel.id]

@bot.tree.command(name='darlance', description='Dá um lance em um leilão ativo')
async def darlance(interaction: discord.Interaction, valor: int):
    if interaction.channel_id not in leiloes:
        await interaction.response.send_message('Não há leilão ativo neste canal.', ephemeral=True)
        return
    
    if valor < 10:
        await interaction.response.send_message('O valor do lance deve ser maior ou igual a 10.', ephemeral=True)
        return

    if interaction.user.id in usuarios_no_leilao:
        leilao_id_atual = usuarios_no_leilao[interaction.user.id]
        if leilao_id_atual != interaction.channel_id:
            if leiloes[leilao_id_atual]['vencedor'] != interaction.user.mention:
                del usuarios_no_leilao[interaction.user.id]
            else:
                await interaction.response.send_message('Você já deu um lance em outro leilão e ainda é o maior lance! Aguarde para participar de outro.', ephemeral=True)
                return

    if valor <= leiloes[interaction.channel_id]['maior_lance']:
        await interaction.response.send_message('Seu lance deve ser maior que o lance atual!', ephemeral=True)
        return

    leiloes[interaction.channel_id]['maior_lance'] = valor
    leiloes[interaction.channel_id]['vencedor'] = interaction.user.mention
    usuarios_no_leilao[interaction.user.id] = interaction.channel_id

    leiloes[interaction.channel_id]['fim'] += timedelta(minutes=1)

    agora = datetime.now(timezone.utc)
    tempo_restante = leiloes[interaction.channel_id]['fim'] - agora
    horas, segundos = divmod(int(tempo_restante.total_seconds()), 3600)
    minutos = segundos // 60
    tempo_formatado = f"{horas}h {minutos}m" if horas > 0 else f"{minutos}m"

    embed = discord.Embed(
        title=f"Lance dado no leilão do item {leiloes[interaction.channel_id]['item']}",
        color=discord.Color.green()
    )
    embed.add_field(name="Valor do lance", value=f"{valor} pontos", inline=False)
    embed.add_field(name="Novo maior lance", value=f"{interaction.user.mention}", inline=False)
    embed.add_field(name="Tempo restante", value=tempo_formatado, inline=False)
    embed.set_image(url=leiloes[interaction.channel_id]['imagem'])

    leilao_channel = bot.get_channel(interaction.channel_id)
    await leilao_channel.send(embed=embed)

    await interaction.response.send_message(f'Novo maior lance de **{valor}** pontos! O tempo restante foi estendido.')

@bot.tree.command(name='leiloes', description='Lista os leilões ativos')
async def leiloes_comando(interaction: discord.Interaction):
    if not leiloes:
        await interaction.response.send_message('Não há leilões ativos no momento.', ephemeral=True)
        return
    
    agora = datetime.now(timezone.utc)
    embeds = []
    for channel_id, leilao in leiloes.items():
        tempo_restante = leilao['fim'] - agora
        horas, segundos = divmod(int(tempo_restante.total_seconds()), 3600)
        minutos = segundos // 60
        tempo_formatado = f"{horas}h {minutos}m" if horas > 0 else f"{minutos}m"
        
        embed = discord.Embed(
            title=f"Leilão do item {leilao['item'].title()}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Maior lance", value=f"**{leilao['maior_lance']}** por {leilao['vencedor'] or 'Ninguém'}", inline=True)
        embed.add_field(name="Tempo restante", value=f"{tempo_formatado}", inline=False)
        embed.set_image(url=leilao['imagem'])
        
        embeds.append(embed)
    
    await interaction.response.send_message(embeds=embeds)

bot.run(TOKEN)