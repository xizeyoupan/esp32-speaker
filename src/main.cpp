#include <Arduino.h>
#include <WiFi.h>
#include <AsyncUDP.h>

#include "../.pio/libdeps/esp32doit-devkit-v1/Arduino_JSON/src/Arduino_JSON.h"
#include "../.pio/libdeps/esp32doit-devkit-v1/ESP32-audioI2S-master/src/Audio.h"

#define bclkpin 4
#define wclkpin 2
#define doutpin 16
#define mclkpin 3

#define LISTEN_PORT 33333

AsyncUDP udp;

Audio audio;

void operate(const String& json) {
    JSONVar getObj = JSON.parse(json);
    String cmd = (const char *) getObj["cmd"];
    Serial.println("cmd: " + cmd);

    if (cmd.equals("discover")) {
        String server_ip = (const char *) getObj["server_ip"];
        int server_port = (int) getObj["port"];
        Serial.println("receive package: server_ip: " + server_ip + " ,server port: " + String(server_port));

        JSONVar obj;
        obj["msg"] = "success";
        obj["ip"] = WiFi.localIP().toString();
        obj["port"] = String(LISTEN_PORT);

        const String &str = JSON.stringify(obj);
        Serial.println("replay: " + str);

        IPAddress ip;
        ip.fromString(server_ip);
        udp.writeTo((const uint8_t *) str.c_str(), str.length(), ip, server_port);
    } else if (cmd.equals("play")) {
        String url = (const char *) getObj["url"];
//        url = get_real_url(url);
        String format = (const char *) getObj["fmt"];
        Serial.println(url);
        audio.setPinout(bclkpin, wclkpin, doutpin);
        audio.i2s_mclk_pin_select(mclkpin);
        audio.setVolume(4); // default 0...21
        audio.connecttohost(url.c_str());
    }
}


void setup() {
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.begin("****", "****");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println(WiFi.RSSI());
    Serial.print("WIFI Mode: ");
    Serial.println(WiFi.getMode());

    if (udp.listen(LISTEN_PORT)) {
        Serial.print("UDP Listening on IP: ");
        Serial.println(WiFi.localIP());
        udp.onPacket([](AsyncUDPPacket packet) {
            Serial.print("UDP Packet Type: ");
            Serial.print(packet.isBroadcast() ? "Broadcast" : packet.isMulticast() ? "Multicast" : "Unicast");
            Serial.print(", From: ");
            Serial.print(packet.remoteIP());
            Serial.print(":");
            Serial.print(packet.remotePort());
            Serial.print(", To: ");
            Serial.print(packet.localIP());
            Serial.print(":");
            Serial.print(packet.localPort());
            Serial.print(", Length: ");
            Serial.print(packet.length());
            Serial.print(", Data: ");
            Serial.write(packet.data(), packet.length());
            Serial.println();
            packet.printf("Got %u bytes of data", packet.length());
            operate(packet.readString());
        });
    }
}

void audio_info(const char *info) {
    Serial.print("info        ");
    Serial.println(info);
}

void loop() {
    audio.loop();
}
