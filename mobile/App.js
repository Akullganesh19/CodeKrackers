import React, { useEffect, useState } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  FlatList, 
  PermissionsAndroid, 
  Platform,
  TouchableOpacity,
  ActivityIndicator
} from 'react-native';
import SmsAndroid from 'react-native-get-sms-android';

const API_URL = "http://localhost:8000/api/detect/sms";

export default function App() {
  const [smsList, setSmsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Idle");

  useEffect(() => {
    requestSmsPermission();
    // Auto-scan every 10 seconds
    const interval = setInterval(() => {
      readSms();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const requestSmsPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.READ_SMS,
          {
            title: "SMS Permission",
            message: "VAS needs access to read SMS for threat detection.",
            buttonNeutral: "Ask Me Later",
            buttonNegative: "Cancel",
            buttonPositive: "OK"
          }
        );
        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          console.log("SMS permission granted");
          readSms();
        } else {
          console.log("SMS permission denied");
        }
      } catch (err) {
        console.warn(err);
      }
    }
  };

  const readSms = () => {
    setLoading(true);
    const filter = {
      box: 'inbox', // 'inbox' (default), 'sent', 'draft', 'outbox', 'failed', 'queued'
      maxCount: 10,
    };

    SmsAndroid.list(
      JSON.stringify(filter),
      (fail) => {
        console.log("Failed with this error: " + fail);
        setLoading(false);
      },
      (count, smsList) => {
        const parsedList = JSON.parse(smsList);
        setSmsList(parsedList);
        setLoading(false);
        setStatus("Monitoring...");
        
        // Auto-scan the most recent message if it's new
        if (parsedList.length > 0) {
          scanSms(parsedList[0]);
        }
      }
    );
  };

  const scanSms = async (sms) => {
    setStatus(`Scanning ${sms.address}...`);
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer YOUR_TOKEN_HERE' // Demo: replace with real token
        },
        body: JSON.stringify({
          sender: sms.address,
          body: sms.body
        })
      });

      if (response.status === 200) {
        const data = await response.json();
        alert(`🚨 THREAT DETECTED!\n\nType: ${data.type}\nSeverity: ${data.severity}\nContent: ${data.content}`);
        setStatus("Threat Detected!");
      } else if (response.status === 204) {
        alert("✅ SMS is Safe.");
        setStatus("Safe");
      } else {
        setStatus("Error scanning");
      }
    } catch (error) {
      console.error(error);
      setStatus("Network Error");
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>VAS Mobile Defense</Text>
        <Text style={styles.subtitle}>Status: {status}</Text>
      </View>

      <TouchableOpacity style={styles.button} onPress={readSms}>
        <Text style={styles.buttonText}>Refresh Inbox</Text>
      </TouchableOpacity>

      {loading ? (
        <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={smsList}
          keyExtractor={(item) => item._id.toString()}
          renderItem={({ item }) => (
            <View style={styles.smsItem}>
              <Text style={styles.sender}>{item.address}</Text>
              <Text style={styles.body}>{item.body}</Text>
              <TouchableOpacity 
                style={styles.scanButton} 
                onPress={() => scanSms(item)}
              >
                <Text style={styles.scanButtonText}>Scan for Threats</Text>
              </TouchableOpacity>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0b',
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  header: {
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#64748b',
    textAlign: 'center',
    marginTop: 5,
  },
  button: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  smsItem: {
    backgroundColor: '#1e293b',
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#334155',
  },
  sender: {
    color: '#818cf8',
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: 5,
  },
  body: {
    color: '#cbd5e1',
    fontSize: 14,
    lineHeight: 20,
  },
  scanButton: {
    marginTop: 10,
    backgroundColor: '#334155',
    padding: 8,
    borderRadius: 6,
    alignItems: 'center',
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  }
});
