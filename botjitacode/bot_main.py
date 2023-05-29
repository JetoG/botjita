import discord
import asyncio
import os
import dotenv

dotenv.load_dotenv()
from discord.ext import commands
from bot_json import load_member_count_channels, get_member_count_channel, update_member_count, update_json_member_channel, update_json_trade_channel, get_trade_notifications_channel, load_trade_notification_channels
from bot_repeatable import verifica_canal_membros_on_ready, verifica_canal_membros, verifica_canal_trade_on_ready, verifica_canal_trade
from bot_commands import InicarComandos
# Configuraçãoes e Importação JSON dos Canais.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='%', intents=intents)
token = str(os.getenv("TOKEN"))


# Dicionário para armazenar os canais de contagem (ID do servidor e ID do canal)
member_count_channels = {}
trade_notification_channels = {}


bot.remove_command("help")
# Função de quando o bot está online e pronto para uso.

@bot.event
async def on_ready():
    await bot.add_cog(InicarComandos(bot))
    await load_trade_notification_channels()
    await load_member_count_channels()
    for guild in bot.guilds:
        await verifica_canal_membros_on_ready(guild)
        await verifica_canal_trade_on_ready(guild)
        channel_id = await get_member_count_channel(guild)
        if channel_id:
            channel = guild.get_channel(int(channel_id))
            await update_member_count(channel)

        channel_id = await get_trade_notifications_channel(guild)
        if channel_id:
            channel = guild.get_channel(int(channel_id))

        await update_json_member_channel(channel)
        await update_json_trade_channel(channel)

    await bot.change_presence(activity=discord.Game("%help"))
    print(f"Bot {bot.user} está pronto!")
    print(discord.__version__)


# Função de criar um canal de membros quando o BOT entrar em um servidor.
@bot.event
async def on_guild_join(guild):
    await verifica_canal_membros(guild)
    await verifica_canal_trade(guild)
    print(f'Bot {bot.user} entrou no servidor: {guild.name} (ID: {guild.id})')


# Função de avisar quando um membro entra no servidor.
@bot.event
async def on_member_join(member):
    guild = member.guild
    member_count = guild.member_count
    channel_id = await get_member_count_channel(guild)
    if channel_id:
        channel = guild.get_channel(int(channel_id))
        await update_member_count(channel)

        embed = discord.Embed(
            description=f'''
            Espero que goste do servidor! 
            Total de membros: {member_count}''', color=discord.Color.green(),
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)
        embed.title = f'Bem-Vindo(a)! {member.display_name}'
        embed.set_footer(text=f'ID do usuário: {member.id}')
        await channel.send(embed=embed)

# Função de avisar quando um membro sai do servidor.
@bot.event
async def on_member_remove(member):
    guild = member.guild
    member_count = guild.member_count
    channel_id = await get_member_count_channel(guild)

    if channel_id:
        channel = guild.get_channel(int(channel_id))
        await update_member_count(channel)

        embed = discord.Embed(
            description=f'''
            É uma pena que não gostou do servidor! 
            Total de membros: {member_count}''', color=discord.Color.red(),
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)
        embed.title = f'Adeus! {member.display_name}'
        embed.set_footer(text=f'ID do usuário: {member.id}')
        await channel.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    await update_json_member_channel(channel)
    await update_json_trade_channel(channel)



async def reconnect_bot():
    print('Bot desconectado, tentando reconectar...')
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            await bot.run(token)
            break
        except discord.ConnectionClosed:
            print('Conexão fechada.')
            attempts += 1
            print(f'Tentativa de reconexão: {attempts}/{max_attempts}')
            await asyncio.sleep(5)

    if attempts == max_attempts:
        # Código para enviar uma notificação em um canal específico
        channel_id = 1112454933644595280
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send('O bot falhou em se reconectar após várias tentativas.')
        else:
            print(f'Canal de notificação não encontrado: {channel_id}')


@bot.event
async def on_disconnect():
    print('Bot desconectado, tentando reconectar...')
    await reconnect_bot()

        
bot.run(token)
