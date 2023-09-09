import sqlite3
import datetime


def create_table():
    # Connexion à la base de données (le fichier sera créé s'il n'existe pas)
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Création de la table s'il elle n'existe pas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            real_name TEXT NOT NULL
        )
    ''')

    query = '''
            CREATE TABLE IF NOT EXISTS pronote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                pronote_id TEXT NOT NULL,
                pronote_pwd TEXT NOT NULL,
                user_key TEXT NOT NULL,
                etab TEXT NOT NULL
            );
            '''
    cur.execute(query)

    # Sauvegarde des modifications et fermeture de la connexion
    conn.commit()
    conn.close()


def get_logs_and_export():
    try:
        # Connexion à la base de données
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Sélection de tous les logs dans la table
        query = "SELECT timestamp, message FROM logs ORDER BY id DESC LIMIT 100"
        cursor.execute(query)

        logs = cursor.fetchall()

        # Création d'un fichier texte pour les logs
        filename = "logs_export.txt"
        with open(filename, "w") as file:
            for log in logs:
                timestamp, message = log
                file.write(f"{timestamp}: {message}\n")

        print(f"Logs exportés dans le fichier {filename}")
        return filename

    except sqlite3.Error as e:
        print("Erreur lors de la récupération et de l'export des logs :", e)
        return None
    finally:
        # Fermeture de la connexion à la base de données
        connection.close()


def search_real_name(user):
    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Requête pour récupérer le nom réel de l'utilisateur
    cur.execute('SELECT real_name FROM utilisateurs WHERE user_name = ?', (user,))
    result = cur.fetchone()

    # Fermeture de la connexion
    conn.close()

    if result:
        return result[0]  # Renvoie le nom réel s'il est trouvé
    else:
        return 0


def add_user(user, name):
    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    try:
        # Insertion de l'utilisateur dans la table
        cur.execute('INSERT INTO utilisateurs (user_name, real_name) VALUES (?, ?)', (user, name))
        conn.commit()

        # Fermeture de la connexion
        conn.close()

        return 0
    except Exception as e:
        print("Erreur lors de l'ajout de l'utilisateur :", str(e))
        return 1


def dl_users():
    import csv
    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Récupération des données des utilisateurs depuis la base de données
    cur.execute('SELECT user_name, real_name FROM utilisateurs')
    users_data = cur.fetchall()

    # Fermeture de la connexion
    conn.close()

    # Écriture des données dans le fichier CSV
    with open('utilisateurs.csv', 'w', newline='') as csv_file:
        field_names = ['user_name', 'real_name']
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        for user_data in users_data:
            csv_writer.writerow({'user_name': user_data[0], 'real_name': user_data[1]})
    return


def act_sem():  # Retrun le numero semaine actuelle
    import time
    timestamp = time.time()
    num_sem = time.strftime("%U", time.localtime(timestamp))
    return int(num_sem)


def initialize_db_logs():
    try:
        # Connexion à la base de données
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Création de la table si elle n'existe pas déjà
        query = '''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        );
        '''
        cursor.execute(query)

        # Validation de la transaction
        connection.commit()

        print("Base de données initialisée avec succès !")

    except sqlite3.Error as e:
        print("Erreur lors de l'initialisation de la base de données :", e)
    finally:
        # Fermeture de la connexion à la base de données
        connection.close()


def log(msg):
    try:
        # Connexion à la base de données
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Récupération de la date et de l'heure actuelle
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insertion du message de log dans la table
        query = "INSERT INTO logs (timestamp, message) VALUES (?, ?)"
        cursor.execute(query, (current_datetime, msg))

        # Validation de la transaction
        connection.commit()

    except sqlite3.Error as e:
        print("Erreur lors de l'ajout du log :", e)
    finally:
        # Fermeture de la connexion à la base de données
        connection.close()


def h():  # Retrun l'heure + la date actuelle
    import time
    timestamp = time.time()
    t = time.gmtime(timestamp)
    minutes = t.tm_yday * 24 * 60 + t.tm_hour * 60 + t.tm_min
    day = time.strftime("%a", time.localtime(timestamp))
    return "{}-{:02d}:{:02d}".format(day, (minutes % (24 * 60)) // 60, minutes % 60)
