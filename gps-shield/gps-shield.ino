/*******************************************************************************
 * Copyright (c) 2019 Thomas Telkamp and Matthijs Kooijman
 *
 * Permission is hereby granted, free of charge, to anyone
 * obtaining a copy of this document and accompanying files,
 * to do whatever they want with them without any restriction,
 * including, but not limited to, copying, modification and redistribution.
 * NO WARRANTY OF ANY KIND IS PROVIDED.
 *
 * Modified by Benjamin Hempel <benjamin.hempel@htw-dresden.de>
 *******************************************************************************/

#include <TinyGPS.h>
#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <SoftwareSerial.h>

TinyGPS gps;
SoftwareSerial ss(4, 3);

unsigned int count = 0;

float flon, flat, falt;

static uint8_t mydata[11] ={0x03,0x88,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00}; 

static const PROGMEM u1_t NWKSKEY[16] ={ 0x5B, 0xEB, 0xDD, 0xC9, 0x6D, 0xE8, 0x7C, 0x7B, 0x83, 0x97, 0x8D, 0xC5, 0xC0, 0xF2, 0xC1, 0xD0 };
static const u1_t PROGMEM APPSKEY[16] ={ 0x48, 0x59, 0x05, 0x1A, 0x37, 0x1C, 0xAD, 0x63, 0xAC, 0x00, 0xD5, 0xE3, 0x6C, 0x79, 0xE8, 0xBE };
static const u4_t DEVADDR = 0x26013EDA;

static osjob_t sendjob;

const unsigned TX_INTERVAL = 1;

const lmic_pinmap lmic_pins = {
    .nss = 10,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 9,
    .dio = {2, 6, 7},
};

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static void smartdelay(unsigned long ms);

void onEvent (ev_t ev) {
  Serial.print(os_getTime());
  Serial.print(": ");
  switch(ev) {
    case EV_JOINING:
      Serial.println(F("EV_JOINING"));
      break;
    case EV_JOINED:
      Serial.println(F("EV_JOINED"));
      break;
    case EV_JOIN_FAILED:
      Serial.println(F("EV_JOIN_FAILED"));
      break;
    case EV_REJOIN_FAILED:
      Serial.println(F("EV_REJOIN_FAILED"));
      break;
    case EV_TXCOMPLETE:
      Serial.println(F("EV_TXCOMPLETE (includes waiting for RX windows)"));
      if(LMIC.txrxFlags & TXRX_ACK)
        Serial.println(F("Received ACK"));
      if(LMIC.dataLen) {
        Serial.print(F("Received "));
        Serial.print(LMIC.dataLen);
        Serial.println(F(" bytes of payload"));
      }
      os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
      break;
    case EV_RXCOMPLETE:
      Serial.println(F("EV_RXCOMPLETE"));
      break;
    default:
      Serial.println(F("Unknown event"));
      break;
  }
}

void GPSRead()
{
  unsigned long age;
  
  gps.f_get_position(&flat, &flon, &age);
  falt=gps.f_altitude();
  
  flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6;
  flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6;
  falt == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : falt, 2;
  
  int32_t lat = flat * 10000;
  int32_t lon = flon * 10000;
  int32_t alt = falt * 100;

  mydata[2] = lat >> 16;
  mydata[3] = lat >> 8;
  mydata[4] = lat;
  mydata[5] = lon >> 16;
  mydata[6] = lon >> 8;
  mydata[7] = lon;
  mydata[8] = alt >> 16;
  mydata[9] = alt >> 8;
  mydata[10] = alt;  
}

void printdata(){
  Serial.print(F("########## "));
  Serial.print(F("NO. "));
  Serial.print(count);
  Serial.println(F(" ##########"));
  if(flon != 1000.000000) {  
    Serial.println(F("[lon,lat,alt]"));
    Serial.print(F("["));
    Serial.print(flon,6);
    Serial.print(F(","));
    Serial.print(flat,6);
    Serial.print(F(","));
    Serial.print(falt,2);
    Serial.println(F("]"));
    count++;
  }
  else {
    Serial.println(F("Failed to get position"));
  }
}

static void smartdelay(unsigned long ms) {
  unsigned long start = millis();
  
  do {
    while (ss.available()) {
      gps.encode(ss.read());
    }
  } while(millis() - start < ms);
}

void do_send(osjob_t* j){
  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println(F("OP_TXRXPEND, not sending"));
  } 
  else {
    smartdelay(1000);
    GPSRead();
    printdata();
    LMIC_setTxData2(1, mydata, sizeof(mydata), 0);
    Serial.println(F("Packet queued"));
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println(F("Starting"));
  ss.begin(9600);
  #ifdef VCC_ENABLE
    pinMode(VCC_ENABLE, OUTPUT);
    digitalWrite(VCC_ENABLE, HIGH);
    delay(1000);
  #endif

  os_init();
  LMIC_reset();

  #ifdef PROGMEM
    uint8_t appskey[sizeof(APPSKEY)];
    uint8_t nwkskey[sizeof(NWKSKEY)];
    memcpy_P(appskey, APPSKEY, sizeof(APPSKEY));
    memcpy_P(nwkskey, NWKSKEY, sizeof(NWKSKEY));
    LMIC_setSession (0x1, DEVADDR, nwkskey, appskey);
  #else
    LMIC_setSession (0x1, DEVADDR, NWKSKEY, APPSKEY);
  #endif

  #if defined(CFG_eu868)
    LMIC_setupChannel(0, 868100000, DR_RANGE_MAP(DR_SF7, DR_SF7),  BAND_CENTI);
    for(int i = 1; i <= 8; i++) LMIC_disableChannel(i);
  #elif defined(CFG_us915)
    LMIC_selectSubBand(1);
  #endif

  LMIC_setLinkCheckMode(0);
  LMIC.dn2Dr = DR_SF9;
  LMIC_setDrTxpow(DR_SF7,14);
  
  do_send(&sendjob);
}

void loop() {
  os_runloop_once();
}
