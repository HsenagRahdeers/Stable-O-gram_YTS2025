
const int DOUT[4] = {2, 4, 6, 8};   // HX711 DOUT pins
const int SCLK[4]  = {3, 5, 7, 9};   // HX711 SCK pins

long tareOffsets[4]; // Stores tare offset for each channel

long readHX711(int doutPin, int sckPin) {
  while (digitalRead(doutPin)); // Wait for DOUT to go LOW

  long count = 0;
  unsigned long timeout = millis() + 5;
  while (digitalRead(doutPin)) {
    if (millis() > timeout) return 0;
  }

  noInterrupts();
  for (int i = 0; i < 24; i++) {
    digitalWrite(sckPin, HIGH);
    count = count << 1;
    digitalWrite(sckPin, LOW);
    if (digitalRead(doutPin)) count++;
  }
  digitalWrite(sckPin, HIGH); // 25th pulse to set gain
  digitalWrite(sckPin, LOW);
  interrupts();

  if (count & 0x800000) count |= ~0xFFFFFFL; // Convert from 24-bit two's complement
  return count;
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) {
    pinMode(DOUT[i], INPUT);
    pinMode(SCLK[i], OUTPUT);
    digitalWrite(SCLK[i], LOW);
  }

  delay(1000); // Allow HX711s to settle

  Serial.println("Taring...");

  // Read and store initial tare offsets
  for (int i = 0; i < 4; i++) {
    long sum = 0;
    for (int j = 0; j < 100; j++) {
      sum += readHX711(DOUT[i], SCLK[i]);
      delay(10);
    }
    tareOffsets[i] = sum / 100;
    Serial.print("Tare "); Serial.print(i + 1); Serial.print(": ");
    Serial.println(tareOffsets[i]);
  }

  Serial.println("Taring complete.");
}

void loop() {
  long values[4];
  unsigned long timestamp = micros(); 
  for (int i = 0; i < 4; i++) {
    values[i] = readHX711(DOUT[i], SCLK[i]) - tareOffsets[i];
  }
    Serial.print(timestamp);  
    Serial.print(',');
    Serial.print(values[0]);
    Serial.print(',');
    Serial.print(values[1]);
    Serial.print(',');
    Serial.print(values[2]);
    Serial.print(',');
    Serial.print(values[3]);
  
  Serial.println();
}
