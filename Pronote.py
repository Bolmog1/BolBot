from cryptography.fernet import Fernet
import pronotepy  # autoslot, urllib3, soupsieve, pycryptodome, certifi, requests, beautifulsoup4, pronotepy


def decode(string):
    decode = string.decode('utf-8')
    return decode


def add_pronote_id(dis_id, pro_id_b, pro_pwd_b, etab):  # Ajoute un utilisateur au CSV
    if etab == 'wat' or etab == 'wal':
        import csv
        etab_new = etab.lower()
        key_b = Fernet.generate_key()
        key = decode(key_b)
        pro_id_c = chiffrer(pro_id_b, key_b)
        pro_pwd_c = chiffrer(pro_pwd_b, key_b)
        pro_id = decode(pro_id_c)
        pro_pwd = decode(pro_pwd_c)
        dict = {'discord_id': dis_id, 'pronote_id': pro_id, 'pronote_pwd': pro_pwd,
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


def daily_check_pronote(a, key, etab):
    import time
    t = time.gmtime(time.time())
    if t.tm_mon < 10:
        month = '0' + str(t.tm_mon)
    else:
        month = t.tm_mon
    date = str(t.tm_year) + '-' + month + '-' + str(t.tm_mday)
    news = []
    encode_key = key.encode('utf-8')
    id_pronote = a['pronote_id'].encode('utf-8')
    pwd_pronote = a['pronote_pwd'].encode('utf-8')
    client = pronotepy.Client(etab,
                              username=dechiffrer(id_pronote, encode_key),
                              password=dechiffrer(pwd_pronote, encode_key))

    if client.logged_in:
        nom_utilisateur = client.info.name  # get users name
        periods = client.periods  # Check les nouvelles notes
        for period in periods:
            for grade in period.grades:
                if str(grade.date) == date:
                    news.append(f'__Nouvelle note__: {grade.grade}/{grade.out_of} en {grade.subject} *(Coeff {grade.coefficient})*')

        infos = client.information_and_surveys()  # Checks les infos
        for info in infos:
            if str(info.start_date)[0:10] == date:
                if info.read:
                    news.append(f'*(info déjà lu)*~~{info.title} par {info.author}~~ le {info.start_date}')
                else:
                    news.append(f'**Nouvelle Info:**{info.title} par {info.author}')

        disc_s = client.discussions()  # Check les disscussions (no jugement sur l'ortho)
        for disc in disc_s:
            if str(disc.date)[0:10] == date:
                if disc.unread:
                    news.append(f'__Nouvelle disscussion__: {disc.subject} *par {disc.creator}*')
                else:
                    news.append(f'*(disscussion déjà lu)*: {disc.subject} *par {disc.creator}*')

        if len(news) == 0:  # S'il n'y a rien de nouveau : rien afficher
            return 0, 'place Older'
        propre = ''
        for ele in news:
            propre = propre + ele + '\n'
        return 1, propre, nom_utilisateur
    else:
        return 2, a['discord_id']
