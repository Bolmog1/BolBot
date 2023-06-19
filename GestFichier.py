def search_real_name(user):
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


def add_user(user,name):
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