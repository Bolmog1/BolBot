def search_real_name(user):  # Recherche un utilisateur dans le CSV
    import csv
    from config import file_acces
    fichier = open(f'{file_acces}prenom.csv')
    table = list(csv.DictReader(fichier))
    for a in table:
        if a['user_name'] == user:
            fichier.close()
            return a['real_name']
    fichier.close()
    return 0


def add_user(user,name):  # Ajoute un utilisateur au CSV
    import csv
    dict = {'user_name': user, 'real_name': name}
    field_names = ['user_name','real_name']
    try:
        from config import file_acces
        with open(f'{file_acces}prenom.csv', 'a') as csv_file:
            dict_object = csv.DictWriter(csv_file, fieldnames=field_names)
            dict_object.writerow(dict)
            csv_file.close()
            return 0
    except:
        return 1


def act_sem():  # Retrun le numero semaine actuelle
    import time
    timestamp = time.time()
    num_sem = time.strftime("%U", time.localtime(timestamp))
    return int(num_sem)


def log(msg):  # Enregistre le msg dans les logs
    with open(f'log_{act_sem()}.txt', 'a') as f:
        f.write(f'\n{h()} - {msg}')
        f.close()


def h():  # Retrun l'heure + la date actuelle
    import time
    timestamp = time.time()
    t = time.gmtime(timestamp)
    minutes = t.tm_yday * 24 * 60 + t.tm_hour * 60 + t.tm_min
    day = time.strftime("%a", time.localtime(timestamp))
    return "{}-{:02d}:{:02d}".format(day, (minutes % (24 * 60)) // 60, minutes % 60)
