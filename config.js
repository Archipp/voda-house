import firebase from 'firebase/compat/app'
import { getDatabase } from 'firebase/database'

const firebaseConfig = {
    apiKey: "AIzaSyBnBqgkIAVpPwUX_rPKNpZ3G367g07IBbw",
    databaseURL: "https://voda-house-9ed6d-default-rtdb.firebaseio.com/",
  };
  
  const app = firebase.initializeApp(firebaseConfig);
  
  const db = getDatabase(app);

  export { db };