from PyP100 import PyP100
import time
import pyrebase
import vonage

# commentaire pour les messages

plug_ip1 = '172.20.10.6'
plug_ip2 = '172.20.10.7'
email = 'armunda2020@gmail.com'
password = 'Kinshasa2@2@'

firebaseConfig = {
    'apiKey': "AIzaSyCZWQZvpna_XIhtTzjTuf-BUwLO4M7BM2E",
    'authDomain': "voda-house-10049.firebaseapp.com",
    'databaseURL': "https://voda-house-10049-default-rtdb.firebaseio.com",
    'projectId': "voda-house-10049",
    'storageBucket': "voda-house-10049.appspot.com",
    'messagingSenderId': "478166648342",
    'appId': "1:478166648342:web:c284c902d9a1672bc05737"
}

client = vonage.Client(key="1d3a44a5", secret="PU0yL4u3Lf3y15Ak")
sms = vonage.Sms(client)

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

previous_courant_state = True

def try_connect(plug_ip):
    p100 = PyP100.P100(plug_ip, email, password)
    try:
        p100.handshake()
        p100.login()
        return p100
    except Exception as e:
        print(f"Echec de connexion à la prise {plug_ip}: {e}")
        return None

def check_and_update_connection_state(p100, p200, etat_prise1, etat_prise2):
    global previous_courant_state
    current_state = not (p100 is None or p200 is None)

    if current_state != previous_courant_state:
        db.child("priseState").update({"etat_courant": current_state})
        if not current_state:
          responseData = sms.send_message(
            {
             "from": "VODA-HOUSE",
             "to": "243814444777",
             "text": "Coupure du courant à la maison",
    }
)
        else:
             message_text = f"Rétablissement du courant à la maison : \n la prise du réfrigérateur est {'allumée' if etat_prise1 else 'éteinte'} \n la prise de la télévision est {'allumée' if etat_prise2 else 'éteinte'}\n"
             responseData = sms.send_message(
                {
                "from": "VODA-HOUSE",
                "to": "243814444777",
                "text": message_text,
                }
             )

        previous_courant_state = current_state

def attempt_reconnect(plug_ip):
    for attempt in range(1):
        print(f"Tentative de reconnexion {attempt+1} pour la prise {plug_ip}...")
        plug = try_connect(plug_ip)
        if plug is not None:
            return plug
        time.sleep(1)
    return None

def main_loop():
    global previous_courant_state
    p100 = try_connect(plug_ip1)
    p200 = try_connect(plug_ip2)
    etat_prise1 = False
    etat_prise2 = False
    check_and_update_connection_state(p100, p200, etat_prise1, etat_prise2)

    while True:
        try:
            result = db.child("priseState").get()
            etat_prise1 = result.val().get('prise_1', False)
            etat_prise2 = result.val().get('prise_2', False)

            if p100 is not None:
                if etat_prise1:
                    p100.turnOn()
                    print("Prise 1 allumée")
                else:
                    p100.turnOff()
                    print("Prise 1 éteinte")
            else:
                p100 = attempt_reconnect(plug_ip1)

            if p200 is not None:
                if etat_prise2:
                    p200.turnOn()
                    print("Prise 2 allumée")
                else:
                    p200.turnOff()
                    print("Prise 2 éteinte")
            else:
                p200 = attempt_reconnect(plug_ip2)

            check_and_update_connection_state(p100, p200, etat_prise1, etat_prise2)
        except Exception as e:
            print(f"Erreur : {e}")
            p100, p200 = None, None
        time.sleep(1)

if __name__ == "__main__":
    main_loop()
