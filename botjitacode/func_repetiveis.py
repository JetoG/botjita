import discord
import asyncio
from func_utils import *

# ENVIAR NOTIFICAÇÕES
async def enviar_notificacoes(recipients, title, description):
    embed = discord.Embed(title=title, description=description)
    for recipient in recipients:
        await recipient.send(embed=embed)

# CANAL MEMBROS
# Função para verificar o canal de membros no evento on_ready
notificacao_enviada_membros = False
async def verifica_canal_membros_on_ready(guild):
    global notificacao_enviada_membros

    channel_id = await get_member_count_channel(guild)
    if not channel_id:
        if not notificacao_enviada_membros:
            owner = guild.owner
            admins = [
                member for member in guild.members if member.guild_permissions.administrator]
            recipients = [owner] + admins
            title = "Canal de Contagem de Membros"
            description = '''
                O Canal de Contagem de Membros, não existe ou foi deletado.
                Caso deseje criar o canal novamente utilize o comando:
                **%criarcanalmembros**
                *Observação: Essa Mensagem será apagada após 24 horas...*
            '''
            msgnoti = await enviar_notificacoes(recipients, title, description)
            notificacao_enviada_membros = True

            await asyncio.sleep(24 * 60 * 60)
            if msgnoti:
                await msgnoti.delete()
        return None
     
    channel = guild.get_channel(int(channel_id))
    return channel


# Função de Verificação e de Criar o canal ao entrar no Servidor
async def verifica_canal_membros(guild):
    channel_id = await get_member_count_channel(guild)
    if not channel_id:
        channel = await create_member_count_channel(guild)
    else:
        channel = guild.get_channel(int(channel_id))



# CANAL TROCAS
# Função para verificar o canal de trocas no evento on_ready
notificacao_enviada_trocas = False
async def verifica_canal_trade_on_ready(guild, bot):
    global notificacao_enviada_trocas

    channel_id = await get_trade_notifications_channel(guild)
    if not channel_id:
        if not notificacao_enviada_trocas:
            owner = guild.owner
            admins = [
                member for member in guild.members if member.guild_permissions.administrator]
            recipients = [owner] + admins
            title = "Canal de Trocas do Servidor"
            description = '''
                O Canal de Trocas do Servidor, não existe ou foi deletado.
                Caso deseje criar o canal novamente utilize o comando:
                **%criarcanaltrocas**
                *Observação: Essa Mensagem será apagada após 24 horas...*
            '''
            msgnoti = await enviar_notificacoes(recipients, title, description)
            notificacao_enviada_trocas = True

            await asyncio.sleep(24 * 60 * 60)
            if msgnoti:
                await msgnoti.delete()
        return None

    channel = guild.get_channel(int(channel_id))
    return channel

# Função de Verificação e de Criar o canal ao entrar no Servidor
async def verifica_canal_trade(guild):
    channel_id = await get_trade_notifications_channel(guild)
    if not channel_id:
        channel = await create_trade_notifications_channel(guild)
    else:
        channel = guild.get_channel(int(channel_id))
