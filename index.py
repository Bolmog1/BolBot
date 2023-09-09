import discord
from discord import app_commands
from discord.ext import tasks, commands
from config import token, file_acces, role_modo, role_membre  # Importation du token du bot + Racine des fichiers annexes
from GestFichier import add_user, search_real_name, log, act_sem, create_table, dl_users, initialize_db_logs, \
    get_logs_and_export
from Pronote import search_user_exist, add_pronote_id, if_pronote_ok, daily_check_pronote
import sqlite3


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


async def renvoie_erreur(obj, msg):
    deco = discord.Embed(title=msg, color=0xE74C3C)
    await obj.response.send_message(embed=deco)


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
    print('have start')
    # my_task.start()
    try:
        synced = await bot.tree.sync()
        log(f"-> {len(synced)} command sync")
    except Exception as e:
        log(e)


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


@bot.event
async def on_member_remove(member):
    log(f'{member.display_name} a quitté le serveur.')
    general_channel = bot.get_channel(1114119568802185288)
    await general_channel.send(f'{member.display_name} a quitté le serveur')


@bot.tree.command(name='ping', description='Répond pong !')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'pong ! ≈{round(bot.latency * 1000)}ms')
    create_table()
    initialize_db_logs()
    return


@bot.tree.command(name='test', description='effectue un test')
async def test(interaction: discord.Interaction):
    deco = discord.Embed(title='CECI EST UN TEST', color=0x32a852)
    await interaction.response.send_message(embed=deco)
    return


@bot.tree.command(name='tki', description='Permet de savoir qui est qui !')
@app_commands.describe(qui = 'qui est-ce que tu cherche ? @la personne ou id')
async def tki(interaction: discord.Interaction, qui: str):
    if qui[:2] == '<@':
        qui = qui[2:20]
    resp = search_real_name(qui)
    if resp == 0:
        await interaction.response.send_message(f"__Aucun résultat__ pour {qui}. Réessaye comme en pingant la personne " +
                        "ou sont id utilisateur", delete_after=10)
        return
    else:
        await interaction.response.send_message(f"Il s'agit de **{resp}**")
        return


@bot.tree.command(name='dlcsv', description='Permet de telecharger la liste des utilisateurs associé à leurs prénom')
async def dlcsv(interaction: discord.Interaction):
    if interaction.channel_id == 1114479881858859070 or interaction.channel_id == 1114480297745072220 or \
            interaction.channel_id == 1131626233457823887:
        try:
            dl_users()  # Actualise le fichier utilisateur.csv
            await interaction.response.send_message(file=discord.File(r'{}utilisateurs.csv'.format(file_acces)))
        except Exception as e:
            log(f'Erreur !dlcsv -> {e}')
            await renvoie_erreur(interaction, 'Erreur envoi du fichier')
    else:
        await renvoie_erreur(interaction, 'mauvais channel')


@bot.tree.command(name='prenom', description="Permet d'associé ton pseudo et ton prénom !")
@app_commands.describe(ton_nom = "Comment t'appelle tu ?")
async def prenom(interaction: discord.Interaction, ton_nom: str):
    channelName = str(interaction.channel)
    if channelName[0:14] == 'Direct Message':
        channel_info = 'https://discord.com/channels/1114119568244359231/1114639638116716597'
        deco = discord.Embed(title=f"Fait `/prenom` dans {channel_info} !", color=0xE74C3C)
        await interaction.response.send_message(embed=deco)
        return
    elif search_real_name(interaction.user.id) != 0:
        deco = discord.Embed(title=f"Ton prénom est déja connu {search_real_name(interaction.user.id)}",
                             color=0xE74C3C, description='contact les modérateurs si erreur !')
        await interaction.response.send_message(embed=deco, delete_after=10)
    else:
        name = ton_nom
        log(f'{interaction.user.display_name} est désormais connu sous : {name}')
        deco = discord.Embed(title=f'Tu es désormais connu sous le prénom : **{name}** !',
                             description="Les modérateurs néssiterons pas à ban si le nom est troll", color=0xE74C3C)
        await interaction.response.send_message(embed=deco)
        add_user(interaction.user.id, name)
        role_id = 1115021521040187412
        user_id = interaction.user.id
        user = interaction.guild.get_member(user_id)

        if interaction.user is None:
            await interaction.channel.send("Utilisateur introuvable.")
            return

        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.channel.send("Rôle introuvable.")
            return

        # Ajout du rôle à l'utilisateur
        await user.add_roles(role)


@bot.tree.command(name='setstatus', description="Permet de changer l'activité en cours")
@app_commands.describe(type = "Quel type d'activité [W/L/G]?", a_quoi = "Qu'est ce que tu écoute/lis etc...")
async def setstatus(interaction: discord.Interaction, type: str, a_quoi: str):
    if role_modo in [y.id for y in interaction.user.roles]:
        Act = str(a_quoi)
        tipe = type
        if tipe == 'G':
            await bot.change_presence(activity=discord.Game(name=Act))
            deco = discord.Embed(title="Changer avec succès",color=0x32a852)
            await interaction.response.send_message(embed=deco)
        elif tipe == 'L':
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=Act))
            deco = discord.Embed(title="Changer avec succès", color=0x32a852)
            await interaction.response.send_message(embed=deco)
        elif tipe == 'W':
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=Act))
            deco = discord.Embed(title="Changer avec succès", color=0x32a852)
            await interaction.response.send_message(embed=deco)
        else:
            deco = discord.Embed(title="Utilisez la commande comme : `!setstatus [G/L/W] [status]",
                                 color=0xE74C3C, description='G=Joue a...\nL=Ecoute...\nW=Regarde...')
            await interaction.response.send_message(embed=deco)
    else:
        await renvoie_erreur(interaction, "Vous n'avez pas l'autorisation de faire ceci")
        log(f'{interaction.user.display_name} a tente de changer l activite')


@bot.tree.command(name='dllog', description="Permet de télécharger les log par semaine")
async def dllog(interaction: discord.Interaction):
    if interaction.channel_id == 1114479881858859070 or interaction.channel_id == 1114480297745072220 or interaction.channel_id == 1131626233457823887:
        file = get_logs_and_export()
        if file:
            try:
                await interaction.response.send_message(file=discord.File(r'{}'.format(file)))
            except Exception as e:
                await renvoie_erreur(interaction, f'Erreur envoie du fichier: {e}')
        else:
            await renvoie_erreur(interaction, 'Erreur création du fichier')
    else:
        await renvoie_erreur(interaction, 'mauvais channel')


@bot.tree.command(name='sem', description="Renvoie la semaine actuelle")
async def sem(interaction: discord.Interaction):
    week = act_sem()
    await interaction.response.send_message(f'Nous en sommes a la semaine {week} de l année')


@bot.tree.command(name='version', description="Permet de connaitre la version actuel")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message('- actuellement en version - **V0.5.1**')


@bot.tree.command(name='pronote_in', description="Permet de t'inscrire au notifications Discord pour Pronote")
@app_commands.describe(id = "Ton identifiant pronote ?",
                       mdp = "ton mot de passe pronote (chiffré) ?",
                       etab = "Ton établissement ? [wal/wat]")
async def pronote_in(interaction: discord.Interaction, id: str, mdp: str, etab: str):
    eyed = id
    pwd = mdp
    channelName = str(interaction.channel)
    if channelName[0:14] == 'Direct Message':  # Si le message est en DM
        if search_user_exist(interaction.user.id):  # Check si client est pas deja dans db
            if if_pronote_ok(eyed, pwd)[0]:  # Si identifiant MDP sont ok
                log(f'{interaction.user.display_name} a validé sa connexion a pronote')
                test = add_pronote_id(interaction.user.id, eyed, pwd, etab)
                if test[0]:  # Ajoute l'utilisteur à la db
                    log(f'{interaction.user.display_name} est désormais inscrit au notifications Pronote')
                    deco = discord.Embed(title=f"Vous etes désormais inscrit {interaction.user.display_name} !",
                                         color=0x32a852)
                    await interaction.response.send_message(embed=deco)
                else:
                    log(f'{interaction.user.display_name} a eu une erreur lors son inscription : {test[1]}')
                    deco = discord.Embed(title=f"Une erreur est survenu. Revoyez la syntaxe ou contacter un modo.",
                                         description=test[1], color=0xE74C3C)
                    await interaction.response.send_message(embed=deco)
            else:
                await renvoie_erreur(interaction, 'Vos identifiant / MdP ne fonctionne pas.')
        else:
            await renvoie_erreur(interaction, "Vous etes déjà inscrit")
    else:
        await renvoie_erreur(interaction, "Pour plus de sécurité, envoyez vos identifiants en MP.")


@bot.tree.command(name='pronote_check', description="Permet de t'inscrire au notifications Discord pour Pronote")
@app_commands.describe(id = "Quels est l'id de la personne ?")
async def pronote_check(interaction: discord.Interaction, id: str):
    if role_modo in [y.id for y in interaction.user.roles]:
        ed = id
        if search_user_exist(ed):
            await renvoie_erreur(interaction, 'Utilisateur introuvable !')
        else:
            await interaction.response.send_message('Utilisateur trouvé !')


@bot.tree.command(name='helpbot', description="Permet d'obtenir de l'aide !")
async def helpbot(interaction: discord.Interaction):
    deco = discord.Embed(title="Un peu d'aide ?", description=
                            "- `/prenom [Ton_prenom]` afin d'acceder à l'integralité du Discord\n"+
                            "- `/tki [Pseudo d'une personne]` afin de savoir qui est la personne que tu demande\n"+
                            "- `/helpbot pronote` afin d'avoir de l'aide concernant les __notifications Pronote__",
                         color=0x256D1B)
    await interaction.response.send_message(embed=deco)


@bot.tree.command(name='helpbot_pronote', description="Permet d'obtenir de l'aide !")
async def helpbot_pronote(interaction: discord.Interaction):
    deco = discord.Embed(title="Un peu d'aide ?", description=
                        "Inscrit toi au **notifications pronote !**, fais `/pronote_in [nom_d'utilisateur] [MotDePasse]"
                        + " [wat/wal]` \nFais bien `wal` si tu viens de wallon ou `wat` pour watteau !",
                        color=0x256D1B)
    await interaction.response.send_message(embed=deco)


@bot.tree.command(name='helpbot_admin', description="Permet d'obtenir de l'aide !")
async def helpbot_admin(interaction: discord.Interaction):
    if interaction.channel_id == 1114479881858859070 or interaction.channel.id == 1114480297745072220:
        if role_modo in [y.id for y in interaction.user.roles]:
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
            await interaction.response.send_message(embed=deco)
        else:
            await renvoie_erreur(interaction, "Vous n'avez pas l'autorisation néccéssaire")
    else:
        await renvoie_erreur(interaction, 'mauvais channel')


@bot.tree.command(name='force_exe', description="force l'execution des tache normallement programmé")
async def force_exe(interaction: discord.Interaction):
    await interaction.response.send_message('Execution...')
    #await my_task()
    channel = bot.get_channel(interaction.channel_id)
    await channel.send('tache forcé Executé.')


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
    await renvoie_erreur(ctx, "Une Erreur est survenu.")
    log(error)


'''
@tasks.loop(hours=1)  # Lance des automatisation, s'éxecute toute les heures
async def my_task():
    etab = ''
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        query = "SELECT discord_id, user_key, etab, pronote_pwd, pronote_id FROM pronote"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            discord_id, user_key_b, etab_db, pronote_pwd, pronote_id = row
            user_key = user_key_b

            if etab_db == 'wal':
                etab = 'https://0590221v.index-education.net/pronote/eleve.html'
            elif etab_db == 'wat':
                etab = 'https://0590222w.index-education.net/pronote/eleve.html'
            else:
                log(f'Erreur Etablissement non reconnu pour {discord_id}')
                continue

            news = daily_check_pronote(row)

            if news[0] == 2:
                log(f'Error login pronote {news[1]}')
            elif news[0] == 0:
                pass
            else:
                deco = discord.Embed(title=f"Notification pronote pour {news[2]}!", description=news[1], color=0xE74C3C)
                user = await bot.fetch_user(discord_id)
                await user.send(embed=deco)

        log('Notification Pronote Effectué!')
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des données depuis la base de données :", e)
    finally:
        # Fermeture de la connexion à la base de données
        connection.close()
'''

# Launch the bot on the internets !
bot.run(token)
