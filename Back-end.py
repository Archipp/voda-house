from PyP100 import PyP110, PyL530
import time
import pyrebase
import vonage

plug_ip1 = '172.20.10.6'
plug_ip2 = '172.20.10.7'
lamp_ip1 = '172.20.10.4'
lamp_ip2 = '172.20.10.5'
email = 'armunda2020@gmail.com'
password = 'Kinshasa2@2@'

firebaseConfig = {
  'apiKey': "AIzaSyBnBqgkIAVpPwUX_rPKNpZ3G367g07IBbw",
  'authDomain': "voda-house-9ed6d.firebaseapp.com",
  'databaseURL': "https://voda-house-9ed6d-default-rtdb.firebaseio.com",
  'projectId': "voda-house-9ed6d",
  'storageBucket': "voda-house-9ed6d.appspot.com",
  'messagingSenderId': "686192896938",
  'appId': "1:686192896938:web:785a024be47302836159d3"
}

client = vonage.Client(key="2eb6fdcd", secret="OM4B4mDW3QT047Sq")
sms = vonage.Sms(client)

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

previous_courant_state = True

def try_connect(plug_ip):
    plug = PyP110.P110(plug_ip, email, password)
    try:
        plug.handshake()
        plug.login()
        return plug
    except Exception as e:
        print(f"Echec de connexion à la prise {plug_ip}: {e}")
        return None

def try_connect_lamp(lamp_ip):
    lamp = PyL530.L530(lamp_ip, email, password)
    try:
        lamp.handshake()
        lamp.login()
        return lamp
    except Exception as e:
        print(f"Echec de connexion à la lampe {lamp_ip}: {e}")
        return None

def update_lamp_state(lamp, state, intensity, firebase_path):
    if lamp is not None:
        try:
            if state:
                lamp.turnOn()
                lamp.setBrightness(intensity)
            else:
                lamp.turnOff()
            db.child(firebase_path).update({'etat': state, 'intensity': intensity})
            print(f"{firebase_path} {'allumée' if state else 'éteinte'} à {intensity}%")
        except Exception as e:
            print(f"Erreur lors de la mise à jour pour {firebase_path}: {e}")

def update_energy_usage(plug, firebase_path):
    if plug is not None:
        try:
            energy_data = plug.getEnergyUsage()
            month_energy_wh = energy_data.get('month_energy', 0)
            month_energy_kwh = month_energy_wh / 1000.0
            db.child("PriseState").update({firebase_path: month_energy_kwh})
            print(f"Mise à jour de la consommation pour {firebase_path}: {month_energy_kwh} kWh")
        except Exception as e:
            print(f"Impossible de récupérer ou mettre à jour la consommation d'énergie pour {firebase_path}: {e}")

def check_and_update_connection_state(p100, p200, l530_1, l530_2, etat_prise1, etat_prise2):
    global previous_courant_state
    current_state = not (p100 is None or p200 is None)

    lamp_externe_data = db.child("LampExterne").get().val() or {'etat': False, 'intensity': 0}
    lamp_chambre_data = db.child("LampChambre").get().val() or {'etat': False, 'intensity': 0}

    if current_state != previous_courant_state:
        db.child("PriseState").update({"EtatCourant": current_state})
        if not current_state:
            # C'est ici que l'on fait appel à l'API SMS
            responseData = sms.send_message({
                "from": "VODA-HOUSE",
                "to": "243821745904",
                "text": "Coupure du courant !",
            })
        else:
            print("Rétablissement du courant")
            if p100 is not None:
                update_energy_usage(p100, "Refrigerateur_energy")
            if p200 is not None:
                update_energy_usage(p200, "Television_energy")

            # Also Here

            message_text = (
                "Rétablissement du courant à la maison:\n"
                f"Prise du réfrigérateur est {'allumée' if etat_prise1 else 'éteinte'}\n"
                f"Prise de la télévision est {'allumée' if etat_prise2 else 'éteinte'}\n"
                f"Lampe externe est {'allumée' if lamp_externe_data['etat'] else 'éteinte'} à {lamp_externe_data['intensity']}%\n"
                f"Lampe chambre est {'allumée' if lamp_chambre_data['etat'] else 'éteinte'} à {lamp_chambre_data['intensity']}%"
            )
            responseData = sms.send_message({
                "from": "VODA-HOUSE",
                "to": "243821745904",
                "text": message_text,
            })

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
    l530_1 = try_connect_lamp(lamp_ip1)
    l530_2 = try_connect_lamp(lamp_ip2)
    etat_prise1 = False
    etat_prise2 = False
    check_and_update_connection_state(p100, p200, l530_1, l530_2, etat_prise1, etat_prise2)

    while True:
        try:
            result = db.child("PriseState").get()
            etat_prise1 = result.val().get('prise_1', False)
            etat_prise2 = result.val().get('prise_2', False)

            lamp_externe_data = db.child("LampExterne").get().val() or {'etat': False, 'intensity': 0}
            lamp_chambre_data = db.child("LampChambre").get().val() or {'etat': False, 'intensity': 0}
            update_lamp_state(l530_1, lamp_externe_data['etat'], lamp_externe_data['intensity'], "LampExterne")
            update_lamp_state(l530_2, lamp_chambre_data['etat'], lamp_chambre_data['intensity'], "LampChambre")
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
