from cryptography.fernet import Fernet
import pronotepy  # autoslot, urllib3, soupsieve, pycryptodome, certifi, requests, beautifulsoup4, pronotepy


def add_pronote_id(dis_id, pro_id, pro_pwd, etab):  # Ajoute un utilisateur au CSV
    if etab == 'wat' or etab == 'wal':
        import csv
        etab_new = etab.lower()
        key = Fernet.generate_key()
        dict = {'discord_id': dis_id, 'pronote_id': chiffrer(pro_id, key), 'pronote_pwd': chiffrer(pro_pwd, key),
                'user_key': key, 'etab': etab_new}
        field_names = ['discord_id', 'pronote_id', 'pronote_pwd', 'user_key', 'etab']
        try:
            from config import file_acces
            with open(f'{file_acces}pronote.csv', 'a') as csv_file:
                dict_object = csv.DictWriter(csv_file, fieldnames=field_names)
                dict_object.writerow(dict)
                csv_file.close()
                return True, 'ok'
        except Exception as e:
            return False, e  # Erreur
    else:
        return False, 'Erreur etablissement, revoyez la syntaxe de l etablissement [wal/wat]'


def search_user_exist(user):  # Recherche un utilisateur dans le CSV
    import csv
    from config import file_acces
    fichier = open(f'{file_acces}pronote.csv')
    table = list(csv.DictReader(fichier))
    for a in table:
        if str(a['discord_id']) == str(user):
            fichier.close()
            return False
    fichier.close()
    return True


def generer_cle():
    # Génère une nouvelle clé de chiffrement aléatoire
    cle = Fernet.generate_key()
    return cle


def chiffrer(message, cle):
    # Crée un objet Fernet à partir de la clé
    f = Fernet(cle)
    # Chiffre le message
    message_chiffre = f.encrypt(message.encode())
    return message_chiffre


def dechiffrer(message_chiffre, cle):
    # Crée un objet Fernet à partir de la clé
    f = Fernet(cle)
    # Déchiffre le message
    message_dechiffre = f.decrypt(message_chiffre)
    return message_dechiffre.decode()


def if_pronote_ok(id,pwd):
    client = pronotepy.Client('https://0590221v.index-education.net/pronote/eleve.html',username=id,password=pwd)
    if client.logged_in:
        nom_utilisateur = client.info.name  # get users name
        return True, nom_utilisateur
    else:
        return False


def daily_check_pronote(a, key):
    etab = ''
    import time
    t = time.gmtime(time.time())
    if t.tm_mon < 10:
        month = '0' + str(t.tm_mon)
    else:
        month = t.tm_mon
    date = str(t.tm_year) + '-' + month + '-' + str(t.tm_mday)
    news = []
    client = pronotepy.Client(etab,
                              username=dechiffrer(a['pronote_id'], key),
                              password=dechiffrer(a['pronote_pwd'], key))

    if client.logged_in:
        nom_utilisateur = client.info.name  # get users name
        periods = client.periods
        for period in periods:
            for grade in period.grades:  # iterate over all the grades
                if str(grade.date) == date:
                    news.append(f'__Nouvelle note__: {grade.grade}/{grade.out_of} en {grade.subject} *(Coeff {grade.coefficient})*')

        infos = client.information_and_surveys()
        for info in infos:
            if info.start_date[0:9] == date:
                if info.read:
                    news.append(f'*(déjà lu)*~~{info.title} par {info.author}~~')
                else:
                    news.append(f'**Nouvelle Info:**{info.title} par {info.author}')
        if len(news) == 0:
            return 0
        propre = ''
        for ele in news:
            propre = propre + ele + '\n'
        return 1, propre, nom_utilisateur
    else:
        return 0


'''
# Exemple d'utilisation
# Générer une nouvelle clé
cle = generer_cle()
print("Clé de chiffrement:", cle)

# Chiffrer un message
message = "Mot de passe secret"
message_chiffre = chiffrer(message, cle)
print("Message chiffré:", message_chiffre)

# Déchiffrer un message
message_dechiffre = dechiffrer(message_chiffre, cle)
print("Message déchiffré:", message_dechiffre)
'''
