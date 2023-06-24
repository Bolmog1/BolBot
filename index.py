import discord
from discord.ext import tasks, commands
from config import token, file_acces  # Importation du token du bot + Racine des fichiers annexes
from GestFichier import add_user, search_real_name, log, act_sem
from Pronote import search_user_exist, add_pronote_id, if_pronote_ok, daily_check_pronote


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


def convert_to_phrase(tuples):
    phrase = ' '.join([str(item) for item in tuples])
    return phrase


async def addrole(user_id, role_id):  # fonction des roles
    # Récupère le serveur
    SERVER_ID = 1114119568244359231
    server = bot.get_guild(int(SERVER_ID))
    if server is None:
        log("Impossible de trouver le serveur avec l'ID spécifié.")
        return

    # Récupère l'utilisateur
    user = server.get_member(int(user_id))
    if user is None:
        log("Impossible de trouver l'utilisateur avec l'ID spécifié.")
        return

    # Récupère le rôle
    role = server.get_role(int(role_id))
    if role is None:
        log("Impossible de trouver le rôle avec l'ID spécifié.")
        return

    # Ajoute le rôle à l'utilisateur
    await user.add_roles(role)
    log("Le rôle a été attribué à l'utilisateur.")


async def supprole(user_id, role_id):
    # Récupère le serveur
    SERVER_ID = 1114119568244359231
    server = bot.get_guild(int(SERVER_ID))
    if server is None:
        print("Impossible de trouver le serveur avec l'ID spécifié.")
        return

    # Récupère l'utilisateur
    user = server.get_member(int(user_id))
    if user is None:
        print("Impossible de trouver l'utilisateur avec l'ID spécifié.")
        return

    # Récupère le rôle
    role = server.get_role(int(role_id))
    if role is None:
        print("Impossible de trouver le rôle avec l'ID spécifié.")
        return

    # Ajoute le rôle à l'utilisateur
    await user.remove_roles(role)
    print("Le rôle a été supprimé à l'utilisateur.")


# print when the bot is running
@bot.event
async def on_ready():
    log("Bot lancé.")
    my_task.start()


@bot.event  # When a new member join the serveur
async def on_member_join(member):
    log(f'{member.display_name} a rejoint le Discord')
    welcome_channel = bot.get_channel(1114639638116716597)
    ui_welcome = discord.Embed(title=f'Bienvenue {member.display_name} !', color=0x04ff00,
                               description='Bienvenue sur le serveur de NSI !')
    await welcome_channel.send(content=f"<@!{member.id}>", embed=ui_welcome)
    await member.send("Salut :wave: \nEncore bienvenue sur le serveur de la NSI 1e !\nJe t'invite à __choisir t'es " +
                      "rôles__ dans le channel https://discord.com/channels/1114119568244359231/1114503731321507881!" +
                      "\n**Pour accèder au reste du serveur Discord, tu dois imprérativement donner ton prénom**. " +
                      "fais `/prenom [ton prénom]`__dans " +
                      "https://discord.com/channels/1114119568244359231/1114639638116716597" +
                      "__pour l'ajouter !")


@bot.command(description='Répond pong !')
async def ping(msg):
    await msg.reply(f'pong - {bot.latency}')
    return


@bot.command(description='Répond TEST avec embed!')
async def test(msg):
    deco = discord.Embed(title='CECI EST UN TEST', color=0x32a852)
    await msg.reply(embed=deco)
    return


@bot.command(description='Permet de savoir qui est qui !')
async def tki(msg, arg):
    resp = search_real_name(arg)
    if resp == 0:
        await msg.reply(f"__Aucun résultat__ pour {arg}. Réessaye avec le nom d'utilisateur exacte sans " +
                        "#0000", delete_after=10)
        return
    else:
        await msg.reply(f"Il s'agit de **{resp}**")
        return


@bot.command(description='Permet de telecharger la liste des utilisateurs associé à leurs prénom')
async def dlcsv(msg):
    if msg.channel.id == 1114479881858859070 or msg.channel.id == 1114480297745072220:
        try:
            await msg.reply(file=discord.File(r'{}prenom.csv'.format(file_acces)))
        except Exception as e:
            log(f'Erreur !dlcsv -> {e}')
            deco = discord.Embed(title='Erreur envoi du fichier', color=0xE74C3C)
            await msg.reply(Embed=deco)
    else:
        await msg.reply('mauvais channel', delete_after=5)


@bot.command(description="Permet d'associé ton pseudo et ton prénom !")
async def prenom(msg, arg):
    channelName = str(msg.channel)
    if channelName[0:14] == 'Direct Message':
        channel_info = 'https://discord.com/channels/1114119568244359231/1114639638116716597'
        deco = discord.Embed(title=f"Fait `/prenom` dans {channel_info} !", color=0xE74C3C)
        await msg.reply(embed=deco)
        return
    elif search_real_name(msg.author.display_name) != 0:
        deco = discord.Embed(title=f"Ton prénom est déja connu {search_real_name(msg.author.display_name)}",
                             color=0xE74C3C, description='contact les modérateurs si erreur !')
        await msg.reply(embed=deco, delete_after=10)
    else:
        name = arg
        log(f'{msg.author.display_name} est désormais connu sous : {name}')
        deco = discord.Embed(title="Les modérateurs néssiterons pas à ban si le nom est troll", color=0xE74C3C)
        await msg.reply(content=f'Tu es désormais connu sous le prénom : **{name}** !', embed=deco)
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


@bot.command(description="Permet de changer l'activité en cours")
async def setstatus(msg, tipe, *activity):
    if 1114161697498865765 in [y.id for y in msg.author.roles]:
        Act = convert_to_phrase(activity)
        if tipe == 'G':
            await bot.change_presence(activity=discord.Game(name=Act))
        elif tipe == 'L':
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=Act))
        elif tipe == 'W':
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=Act))
        else:
            deco = discord.Embed(title="Utilisez la commande comme : `!setstatus [G/L/W] [status]",
                                 color=0xE74C3C, description='G=Joue a...\nL=Ecoute...\nW=Regarde...')
            await msg.reply(Embed=deco)
    else:
        deco = discord.Embed(title="Vous n'avez pas l'autorisation de faire ceci", color=0xE74C3C)
        await msg.reply(embed=deco)
        log(f'{msg.author.display_name} a tente de changer l activite')


@bot.command(description="Permet de télécharger les log par semaine")
async def dllog(msg, semaine):
    nb = semaine
    if msg.channel.id == 1114479881858859070 or msg.channel.id == 1114480297745072220:
        try:
            int(nb)
        except Exception as e:
            await msg.reply('envoyer int pour la semaine des log', delete_after=5)
            log(f'pas int log : {e}')
        try:
            await msg.reply(file=discord.File(r'log_{}.txt'.format(nb)))
        except Exception as e:
            log(f'Erreur !dllog -> {e}')
            deco = discord.Embed(title=f'Erreur envoi du fichier {e}', color=0xE74C3C)
            await msg.reply(embed=deco)
    else:
        await msg.reply('mauvais channel', delete_after=5)


@bot.command(description="Permet de connaitre la semaine actuel")
async def sem(msg):
    week = act_sem()
    await msg.reply(f'Nous en sommes a la semaine {week} de l année')


@bot.command(description="Permet de connaitre la version actuel")
async def version(msg):
    await msg.reply('- actuellement en version - **V0.cb**')


@bot.command(description="Permet de t'inscrire au notifications Discord pour Pronote")
async def pronote_in(msg, eyed, pwd, etab):
    channelName = str(msg.channel)
    if channelName[0:14] == 'Direct Message':  # Si le message est en DM
        if search_user_exist(msg.author.id):  # Check si client est pas deja dans db
            if if_pronote_ok(eyed, pwd)[0]:  # Si identifiant MDP sont ok
                log(f'{msg.author.display_name} a validé sa connexion a pronote')
                test = add_pronote_id(msg.author.id, eyed, pwd, etab)
                if test[0]:  # Ajoute l'utilisteur à la db
                    log(f'{msg.author.display_name} est désormais inscrit au notifications Pronote')
                    deco = discord.Embed(title=f"Vous etes désormais inscrit {msg.author.display_name} !",
                                         color=0x32a852)
                    await msg.reply(embed=deco)
                else:
                    log(f'{msg.author.display_name} a eu une erreur lors son inscription : {test[1]}')
                    deco = discord.Embed(title=f"Une erreur est survenu. Revoyez la syntaxe ou contacter un modo.",
                                         description=test[1], color=0xE74C3C)
                    await msg.reply(embed=deco)
            else:
                deco = discord.Embed(title="Vos identifiant / MdP ne fonctionne pas.", color=0xE74C3C)
                await msg.reply(embed=deco)
        else:
            deco = discord.Embed(title="Vous etes déjà inscrit", color=0xE74C3C)
            await msg.reply(embed=deco)
    else:
        deco = discord.Embed(title="Pour plus de sécurité, envoyez vos identifiants en MP.", color=0xE74C3C)
        await msg.reply(embed=deco)


@bot.command(description="Permet de t'inscrire au notifications Discord pour Pronote")
async def pronote_check(msg, ed):
    if 1114161697498865765 in [y.id for y in msg.author.roles]:
        if search_user_exist(ed):
            await msg.reply('Utilisateur introuvable !')
        else:
            await msg.reply('Utilisateur trouvé !')


@bot.command(description="Permet d'obtenir de l'aide !")
async def helpbot(msg):
    deco = discord.Embed(title="Un peu d'aide ?", description=
                            "- `/prenom [Ton_prenom]` afin d'acceder à l'integralité du Discord\n"+
                            "- `/tki [Pseudo d'une personne]` afin de savoir qui est la personne que tu demande\n"+
                            "- `/helpbot pronote` afin d'avoir de l'aide concernant les __notifications Pronote__",
                         color=0x256D1B)
    await msg.reply(embed=deco)


@bot.command(description="Permet d'obtenir de l'aide !")
async def helpbot_pronote(msg):
    deco = discord.Embed(title="Un peu d'aide ?", description=
                        "Inscrit toi au **notifications pronote !**, fais `/pronote_in [nom_d'utilisateur] [MotDePasse]"
                        + " [wat/wal]` \nFais bien `wal` si tu viens de wallon ou `wat` pour watteau !",
                        color=0x256D1B)
    await msg.reply(embed=deco)


@bot.command(description="Permet d'obtenir de l'aide !")
async def helpbot_admin(msg):
    if msg.channel.id == 1114479881858859070 or msg.channel.id == 1114480297745072220:
        if 1114161697498865765 in [y.id for y in msg.author.roles]:
            deco = discord.Embed(title="Un peu d'aide ?", description=
                            "- `/dlcsv` permet de télécharger le csv de l'ensemble des prenoms des utilisateurs inscrit" +
                            "\n- `/dllog [N°DeLaSemaine]` afin de télécharger les logs d'une semaine précise" +
                            "\n- `/sem` te permet de savoir le n° de la seamine en cours *(Attention: semaine de Dim<>Sam)*" +
                            "\n- `/pronote_check [ID_Discord]` te permet de savoir si un utilisateur est inscrit aux" +
                            "notifications pronote *(debug)*" +
                            "\n- `/setstatus [W/L/G] [Activité...]` permet de mettre une activité au bot *(W = Regarde.../" +
                            "L = Ecoute.../ G = Joue a...)*" +
                            "\n- `/version` permet de connaitre la version actuelle du bot",
                                 color=0x256D1B)
            await msg.reply(embed=deco)
        else:
            await msg.reply("Vous n'avez pas l'autorisation néccéssaire", delete_after=5)
    else:
        await msg.reply('mauvais channel', delete_after=5)

@bot.event  # Action lors d'un ajout de réaction
async def on_raw_reaction_add(ctx):
    if ctx.message_id == 1114122040924979221 and str(ctx.emoji) == '😂':
        await addrole(ctx.member.id, 1114210444366856323)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟧':  # Ajouter le role Wallon si reaction emoji
        await addrole(ctx.member.id, 1115688862581272576)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟩':  # Ajouter le role Watteau si reaction emoji
        await addrole(ctx.member.id, 1115689277955776584)


@bot.event  # Action lorsqu'on retire une reaction
async def on_raw_reaction_remove(ctx):
    if ctx.message_id == 1114122040924979221 and str(ctx.emoji) == '😂':
        await supprole(ctx.user_id, 1114210444366856323)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟧':  # Retirer le role Wallon si reaction emoji
        await supprole(ctx.user_id, 1115688862581272576)

    if ctx.message_id == 1115698331629404231 and str(ctx.emoji) == '🟩':  # Retirer le role Watteau si reaction emoji
        await supprole(ctx.user_id, 1115689277955776584)


@bot.event
async def on_command_error(ctx, error):
    deco = discord.Embed(title="Une Erreur est survenu.", color=0xE74C3C)
    await ctx.send(embed=deco)
    log(error)


@tasks.loop(hours=1)  # Lance des automatisation, s'éxecute toute les heures
async def my_task():
    import time
    temps = time.localtime()
    if temps[3] == 18:  # Si il est 18h, le bot envoie un msg
        modo_channel = bot.get_channel(1114480297745072220)
        await modo_channel.send(content='Le bot fonctionne correctement!')
        etab = ''
        import csv
        import time
        from config import file_acces
        fichier = open(f'{file_acces}pronote.csv')
        table = list(csv.DictReader(fichier))
        for a in table:
            key = a['key']
            if a['etab'] == 'wal':
                etab = 'https://0590221v.index-education.net/pronote/eleve.html'
            elif a['etab'] == 'wat':
                etab = 'https://0590222w.index-education.net/pronote/eleve.html'
            else:
                log(f'Erreur Etablissement non reconnu pour {a["discord_id"]}')
            news = daily_check_pronote(a, key, etab)
            if news[0] == 0:
                deco = discord.Embed(title=f"Notification pronote pour {news[2]}!", description=news[1], color=0xE74C3C)
                user = bot.get_user(a['discord_id'])
                await user.send(embed=deco)
        modo_channel = bot.get_channel(1114480297745072220)
        await modo_channel.send(content='Notification Pronote Effectué!')


# Launch the bot on the internets !
bot.run(token)
