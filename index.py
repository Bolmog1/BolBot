import time
import discord
from discord.ext import tasks
from config import token, file_acces  # Importation du token du bot
from GestFichier import add_user, search_real_name


intents = discord.Intents.default()  # Preparation du bot.
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


def log(msg):
    with open(f'log_{act_sem()}.txt', 'a') as f:
        f.write(f'\n{h()} - {msg}')
        f.close()


def act_sem():
    import time
    timestamp = time.time()
    num_sem = time.strftime("%U", time.localtime(timestamp))
    return int(num_sem)


def h():
    import time
    timestamp = time.time()
    t = time.gmtime(timestamp)
    minutes = t.tm_yday * 24 * 60 + t.tm_hour * 60 + t.tm_min
    day = time.strftime("%a", time.localtime(timestamp))
    return "{}-{:02d}:{:02d}".format(day, (minutes % (24 * 60)) // 60, minutes % 60)


async def addrole(USER_ID,ROLE_ID):  # fonction des roles
    # Récupère le serveur
    SERVER_ID = 1114119568244359231
    server = client.get_guild(int(SERVER_ID))
    if server is None:
        log("Impossible de trouver le serveur avec l'ID spécifié.")
        return

    # Récupère l'utilisateur
    user = server.get_member(int(USER_ID))
    if user is None:
        log("Impossible de trouver l'utilisateur avec l'ID spécifié.")
        return

    # Récupère le rôle
    role = server.get_role(int(ROLE_ID))
    if role is None:
        log("Impossible de trouver le rôle avec l'ID spécifié.")
        return

    # Ajoute le rôle à l'utilisateur
    await user.add_roles(role)
    log("Le rôle a été attribué à l'utilisateur.")


async def supprole(USER_ID,ROLE_ID):
    # Récupère le serveur
    SERVER_ID = 1114119568244359231
    server = client.get_guild(int(SERVER_ID))
    if server is None:
        print("Impossible de trouver le serveur avec l'ID spécifié.")
        return

    # Récupère l'utilisateur
    user = server.get_member(int(USER_ID))
    if user is None:
        print("Impossible de trouver l'utilisateur avec l'ID spécifié.")
        return

    # Récupère le rôle
    role = server.get_role(int(ROLE_ID))
    if role is None:
        print("Impossible de trouver le rôle avec l'ID spécifié.")
        return

    # Ajoute le rôle à l'utilisateur
    await user.remove_roles(role)
    print("Le rôle a été supprimé à l'utilisateur.")


# print when the bot is running
@client.event
async def on_ready():
    log("Bot lancé.")
    my_task.start()


@client.event  # When a new member join the serveur
async def on_member_join(member):
    log(f'{member.display_name} a rejoint le Discord')
    welcome_channel = client.get_channel(1114639638116716597)
    ui_welcome = discord.Embed(title=f'Bienvenue {member.display_name} !', color=0x04ff00,
                               description='Bienvenue sur le serveur de NSI !')
    await welcome_channel.send(content=f"<@!{member.id}>", embed=ui_welcome)
    await member.send("Salut :wave: \nEncore bienvenue sur le serveur de la NSI 1e !\nJe t'invite à __choisir t'es " +
                      "rôles__ dans le channel https://discord.com/channels/1114119568244359231/1114503731321507881!\n" +
                      "**Pour accèder au reste du serveur Discord, tu dois imprérativement donner ton prénom**. fais `" +
                      "!prenom [ton prénom]`__dans " +
                      "https://discord.com/channels/1114119568244359231/1114639638116716597" +
                      "__pour l'ajouter !")


@client.event  # Lorsque un message est envoyer
async def on_message(msg):
    if msg.author == client.user:
        return

    if msg.content.lower() == 'ping':
        await msg.channel.send('pong')
        return

    if msg.content.lower() == 'test':
        deco = discord.Embed(title='CECI EST UN TEST', color=0x32a852)
        await msg.channel.send(embed=deco)
        return

    if msg.content.startswith('!tki'):
        name = msg.content[5:]
        resp = search_real_name(name)
        if resp == 0:
            await msg.channel.send(f"__Aucun résultat__ pour {name}. Réessaye avec le nom d'utilisateur exacte sans " +
                                   "#0000", delete_after=10)
        else:
            await msg.channel.send(f"Il s'agit de **{resp}**")

    if msg.content.startswith('!dlcsv'):
        if msg.channel.id == 1114479881858859070 or msg.channel.id == 1114480297745072220:
            try:
                await msg.channel.send(file=discord.File(r'{}prenom.csv'.format(file_acces)))
            except Exception as e:
                log(f'Erreur !dlcsv -> {e}')
                deco = discord.Embed(title='Erreur envoi du fichier', color=0xE74C3C)
                await msg.channel.send(Embed=deco)
        else:
            await msg.channel.send('mauvais channel', delete_after=5)

    if msg.content.startswith('!prenom'):
        channelName = str(msg.channel)
        if channelName[0:14] == 'Direct Message':
            channel_info = 'https://discord.com/channels/1114119568244359231/1114639638116716597'
            deco = discord.Embed(title=f"Fait `!prenom` dans {channel_info} !", color=0xE74C3C)
            await msg.channel.send(embed=deco)
            return
        elif search_real_name(msg.author.display_name) != 0:
            deco = discord.Embed(title=f"Ton prénom est déja connu {search_real_name(msg.author.display_name)}",
                                 color=0xE74C3C, description='contact les modérateurs si erreur !')
            await msg.channel.send(embed=deco, delete_after=10)
        else:
            name = msg.content[8:]
            log(f'{msg.author.display_name} est désormais connu sous : {name}')
            deco = discord.Embed(title="Les modérateurs néssiterons pas à ban si le nom est troll", color=0xE74C3C)
            await msg.channel.send(content=f'Tu es désormais connu sous le prénom : **{name}** !', embed=deco)
            add_user(msg.author.display_name, name)
            role_id = 1115021521040187412
            role_income = 1115020283502411786
            user_id = msg.author.id
            user = msg.guild.get_member(user_id)

            if user is None:
                await msg.channel.send("Utilisateur introuvable.")
                return

            role = msg.guild.get_role(role_id)
            role_in = msg.guild.get_role(role_income)

            if role is None:
                await msg.channel.send("Rôle introuvable.")
                return

            # Ajout du rôle à l'utilisateur
            await user.add_roles(role)
            await user.add_roles(role_in)

    # !setstatus G Mon jeux
    if msg.content.startswith('!setstatus'):
        if 1114161697498865765 in [y.id for y in msg.author.roles]:
            if msg.content[11] == 'G':
                await client.change_presence(activity=discord.Game(name=msg.content[13:]))
            elif msg.content[11] == 'L':
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.listening, name=msg.content[13:]))
            elif msg.content[11] == 'W':
                await client.change_presence(
                    activity=discord.Activity(type=discord.ActivityType.watching, name=msg.content[13:]))
            else:
                deco = discord.Embed(title="Utilisez la commande comme : `!setstatus [G/L/W] [status]",
                                     color=0xE74C3C, description='G=Joue a...\nL=Ecoute...\nW=Regarde...')
                await msg.channel.send(Embed=deco)
        else:
            deco = discord.Embed(title="Vous n'avez pas l'autorisation de faire ceci", color=0xE74C3C)
            await msg.channel.send(embed=deco)
            log(f'{msg.author.display_name} a tente de changer l activite')

    if msg.content.startswith('!dllog'):
        nb = msg.content[7:]
        if msg.channel.id == 1114479881858859070 or msg.channel.id == 1114480297745072220:
            try:
                int(nb)
            except:
                await msg.channel.send('envoyer int pour la semaine des log', delete_after=5)
            try:
                await msg.channel.send(file=discord.File(r'log_{}.txt'.format(nb)))
            except Exception as e:
                log(f'Erreur !dllog -> {e}')
                deco = discord.Embed(title=f'Erreur envoi du fichier {e}', color=0xE74C3C)
                await msg.channel.send(embed=deco)
        else:
            await msg.channel.send('mauvais channel', delete_after=5)

    if msg.content.startswith('!sem'):
        week = act_sem()
        await msg.channel.send(f'Nous en sommes a la semaine {week} de l année')

    if msg.content.startswith('!version'):
        await msg.channel.send('- actuellement en version - **V0.3**')


@client.event  # Action lors d'un ajout de réaction
async def on_raw_reaction_add(ctx):
    if ctx.message_id == 1114122040924979221 and str(ctx.emoji) == '😂':
        await addrole(ctx.member.id, 1114210444366856323)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟧':  # Ajouter le role Wallon si reaction emoji
        await addrole(ctx.member.id, 1115688862581272576)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟩':  # Ajouter le role Watteau si reaction emoji
        await addrole(ctx.member.id, 1115689277955776584)


@client.event  # Action lorsqu'on retire une reaction
async def on_raw_reaction_remove(ctx):
    if ctx.message_id == 1114122040924979221 and str(ctx.emoji) == '😂':
        await supprole(ctx.user_id, 1114210444366856323)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟧':  # Retirer le role Wallon si reaction emoji
        await supprole(ctx.user_id, 1115688862581272576)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟩':  # Retirer le role Watteau si reaction emoji
        await supprole(ctx.user_id, 1115689277955776584)


@tasks.loop(hours=1)
async def my_task():
    temps = time.localtime()
    if temps[3] == 18:
        modo_channel = client.get_channel(1114480297745072220)
        await modo_channel.send(content='Le bot fonctionne correctement!')
    print('ok')


# Launch the bot on the internets !
client.run(token)
