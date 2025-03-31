import discord
from discord.ext import commands
import asyncio
import os 

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

leiloes = {}
usuarios_no_leilao = {}
guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos de barra!')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

@bot.tree.command(name='criarleilao', description='Cria um novo leilão')
async def criarleilao(interaction: discord.Interaction, item: str, duracao: int, imagem: discord.Attachment):
    if interaction.channel_id in leiloes:
        await interaction.response.send_message('Já existe um leilão em andamento neste canal!', ephemeral=True)
        return
    
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="═════❯𝐋𝐄𝐈𝐋𝐀̃𝐎 𝐃𝐄 𝐈𝐓𝐄𝐍𝐒❮═════")
    
    if not category:
        category = await guild.create_category("Leilões")
    
    leilao_channel = await guild.create_text_channel(item, category=category)
    
    leiloes[leilao_channel.id] = {
        'item': item,
        'maior_lance': 0,
        'vencedor': None,
        'imagem': imagem.url,
        'duracao': duracao
    }
    
    embed = discord.Embed(
        title=f"Leilão do item {item.title()}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Duração do leilão", value=f"{duracao} horas", inline=False)
    embed.add_field(name="Como dar o seu lance", value="De o seu lance com o comando /darlance", inline=True)
    embed.set_image(url=imagem.url)
    
    await leilao_channel.send(embed=embed)
    await interaction.response.send_message(f'Leilão iniciado para **{item}**! Duração: {duracao} horas. O canal do leilão foi criado em {leilao_channel.mention}. Dê lances com /darlance <valor>.')
    
    await asyncio.sleep(duracao * 3600)
    if leiloes[leilao_channel.id]['vencedor']:
        await leilao_channel.send(f'Leilão encerrado! **{leiloes[leilao_channel.id]["vencedor"]}** venceu com um lance de **{leiloes[leilao_channel.id]["maior_lance"]}** moedas!')
    else:
        await leilao_channel.send('Leilão encerrado sem lances.')
    
    del leiloes[leilao_channel.id]

@bot.tree.command(name='darlance', description='Dá um lance em um leilão ativo')
async def darlance(interaction: discord.Interaction, valor: int):
    if interaction.channel_id not in leiloes:
        await interaction.response.send_message('Não há leilão ativo neste canal.', ephemeral=True)
        return
    
    if interaction.user.id in usuarios_no_leilao and usuarios_no_leilao[interaction.user.id] != interaction.channel_id:
        await interaction.response.send_message('Você já deu um lance em outro leilão! Não pode dar lance em mais de um.', ephemeral=True)
        return
    
    if valor <= leiloes[interaction.channel_id]['maior_lance']:
        await interaction.response.send_message('Seu lance deve ser maior que o lance atual!', ephemeral=True)
        return
    
    leiloes[interaction.channel_id]['maior_lance'] = valor
    leiloes[interaction.channel_id]['vencedor'] = interaction.user.mention
    usuarios_no_leilao[interaction.user.id] = interaction.channel_id
    
    await interaction.response.send_message(f'Novo maior lance: **{valor}** moedas por {interaction.user.mention}!')

@bot.tree.command(name='leiloes', description='Lista os leilões ativos')
async def leiloes_comando(interaction: discord.Interaction):
    if not leiloes:
        await interaction.response.send_message('Não há leilões ativos no momento.', ephemeral=True)
        return
    
    embeds = []
    for channel_id, leilao in leiloes.items():
        canal = bot.get_channel(channel_id)
        embed = discord.Embed(
            title=f"Leilão do item {leilao['item'].title()}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Canal do Leilão", value=f"{canal.mention}", inline=False)
        embed.add_field(name="Item leiloado", value=f"**{leilao['item']}**", inline=False)
        embed.add_field(name="Maior lance", value=f"**{leilao['maior_lance']}** por {leilao['vencedor'] or 'Ninguém'}", inline=True)
        
        if 'imagem' in leilao:
            embed.set_image(url=leilao['imagem'])
        
        embeds.append(embed)
    
    await interaction.response.send_message(embeds=embeds)

bot.run(TOKEN)