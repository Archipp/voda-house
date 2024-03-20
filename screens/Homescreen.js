import React, {useEffect, useState} from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Appbar, Card, Avatar, Paragraph, Provider } from 'react-native-paper';
import firebase from 'firebase/compat';
import { db } from '../config';
import { ref, onValue } from 'firebase/database';

const HomeScreen = () => {
  // Valeurs statiques pour démonstration
  const energieAccumuleeStatique = 12.3456; // Exemple d'énergie accumulée statique
  const estimationCoutStatique = 1234; // Exemple d'estimation du coût statique
  const [courant, setCourant] = useState(false);

  useEffect(() => {
    const courantRef = firebase.database().ref('priseState/etat_courant');
    courantRef.on('value', (snapshot) => {
      const etatCourant = snapshot.val();
      setCourant(etatCourant);
    });
  }, []);


  return (
    <Provider>
      <View style={styles.container}>
        <Appbar.Header style={styles.header}>
          <Appbar.Content titleStyle={styles.headerTitle} title="MY VODA-HOUSE" />
        </Appbar.Header>
        <ScrollView style={styles.scrollContainer}>

        <Card style={styles.card}>
  <Card.Content>
    <View style={styles.statusRow}>
      <Avatar.Icon
        icon="alert-outline"
        style={{
          backgroundColor: courant ? "#fff" : "#fff", 
          color: courant ? "green" : "black",
          right: 15 
        }}
        color={courant ? "green" : "red"}
      />
      <Text style={{ marginLeft: 10, color: courant ? "black" : "red", fontWeight:"bold", fontSize:17, top:5, right: 21, textAlign:"center" }}>
        {courant ? "IL Y'A DU COURANT A LA MAISON" : "COUPURE DU COURANT A LA MAISON"}
      </Text>
    </View>
  </Card.Content>
</Card>

          
          <Card style={styles.card}>
            <Card.Title title="CONSOMMATION GLOBALE" titleStyle={styles.cardTitle} />
            <Card.Content>
              <Avatar.Icon
                size={60}
                icon="lightbulb-on-outline"
                style={styles.avatar}
              />
              <View style={styles.consumptionBubble}>
                <Text style={styles.consumptionText}>
                  {energieAccumuleeStatique.toFixed(4)} kWh
                </Text>
              </View>
              <Paragraph style={styles.priceText}>
                ESTIMATION DU COÛT: {estimationCoutStatique.toFixed(1)} Fc
              </Paragraph>
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Title title="CONSOMMATION PAR EQUIPEMENT" titleStyle={styles.cardTitle} />
            <Card.Content>

            <View style={styles.consumptionRow}>
              <Text style={styles.consumptionTextLeft}>LAMPES EXTERNES:</Text>
              <Text style={styles.consumptionTextRight}>1.00 kWh</Text>
            </View>

            <View style={styles.consumptionRow}>
              <Text style={styles.consumptionTextLeft}>PRISES SALON:</Text>
              <Text style={styles.consumptionTextRight}>4.00 kWh </Text>
            </View>

            <View style={styles.consumptionRow}>
              <Text style={styles.consumptionTextLeft}>PRISES CUISINE:</Text>
              <Text style={styles.consumptionTextRight}>5.00 kWh </Text>
            </View>

            <View style={styles.consumptionRow}>
              <Text style={styles.consumptionTextLeft}>PRISES CHAMBRE:</Text> 
              <Text style={styles.consumptionTextRight}>0.03 kWh</Text>
            </View>

            <View style={styles.consumptionRow}>
              <Text style={styles.consumptionTextLeft}>PRISES SALLE DE BAIN:</Text> 
              <Text style={styles.consumptionTextRight}>1.00 kWh</Text>
            </View>
            </Card.Content>
          </Card>
        </ScrollView>
      </View>
    </Provider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
  },
  scrollContainer: {
    flex: 1,
  },
  header: {
    backgroundColor: '#fff',
  },
  headerTitle: {
    color: "#E60000",
    fontSize: 20,
    fontWeight: 'bold',
  },
  card: {
    margin: 10,
    elevation: 4,
    borderRadius: 8,
    backgroundColor: '#fff',
  },
  cardTitle: {
    textTransform: 'uppercase',
    fontWeight: 'bold',
    textAlign: 'center'
  },
  consumptionBubble: {
    backgroundColor: '#E60000',
    padding: 10,
    borderRadius: 50,
    alignSelf: 'center',
    marginBottom: 10,
    fontWeight: 'bold',
  },
  consumptionText: {
    fontSize: 20,
    color: '#fff',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  priceText: {
    fontSize: 16,
    color: '#000',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  consumptionTextLeft: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
  },
  consumptionTextRight: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
  },
  avatar: {
    backgroundColor: '#E60000',
  },
  consumptionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  consumptionTextLeft: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
  },
  consumptionTextRight: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center', // Centre les éléments verticalement
  },
});

export default HomeScreen;
