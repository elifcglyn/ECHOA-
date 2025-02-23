import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
} from 'react-native';

const WelcomeScreen = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../assets/robot.png')}
        style={styles.robotImage}
      />
      <Text style={styles.title}>Welcome to ECHO AI</Text>
      <Text style={styles.subtitle}>your friendly AI assistant at hand</Text>
      
      <TouchableOpacity 
        style={styles.continueButton}
        onPress={() => navigation.navigate('Login')}
      >
        <Text style={styles.buttonText}>Continue</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#3B4990',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  robotImage: {
    width: 150,
    height: 150,
    marginBottom: 30,
  },
  title: {
    fontSize: 24,
    color: 'white',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 40,
  },
  continueButton: {
    backgroundColor: '#2A3362',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 25,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default WelcomeScreen; 