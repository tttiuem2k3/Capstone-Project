#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include <ArduinoJson.h>
#include "esp_timer.h"
#include "driver/dac.h"
// const char* ssid     = "PHAT";
// const char* password = "0968718348";
// #define IP_SERVER      "192.168.100.33"
const char* ssid     = "TTT";
const char* password = "12345121123";
#define IP_SERVER      "172.20.10.2"

#define I2S_WS 15                // Chân WS của micro INMP441 I2S
#define I2S_SD 13               // Chân SD của micro INMP441 I2S
#define I2S_SCK 2              // Chân SCK của micro INMP441 I2S
#define I2S_PORT I2S_NUM_0    // cổng I2S số 0
#define I2S_SAMPLE_RATE             (16000)     // Tốc độ lấy mẫu của âm thanh 
#define I2S_SAMPLE_BITS             (16)        // Mỗi mẫu âm thanh chiếm 16 bit = 2 byte.
#define I2S_READ_LEN                (4 * 1024)  // Độ dài mỗi chunk đọc từ mic: **4 KB (4096 bytes)**
#define SEND_WAKE_WORD_RECORD_API   "http://" IP_SERVER ":8888/wake_word_record"
#define CHECK_WAKE_WORD_API         "http://" IP_SERVER ":8888/check_wake_word"
#define SEND_RECORD_API             "http://" IP_SERVER ":8888/stream_record"
#define END_RECORD_API              "http://" IP_SERVER ":8888/end_stream_record"
#define AI_PROCESS_AUDIO_API        "http://" IP_SERVER ":8888/start_ai_process"
#define CHECK_STATUS_AUDIO_API      "http://" IP_SERVER ":8888/check_status"
#define RECEIVE_SPEECH_API          "http://" IP_SERVER ":8888/output_audio"
#define RECEIVE_LIST_MUSIC_API      "http://" IP_SERVER ":8888/list_music"
#define RECEIVE_MUSIC_API           "http://" IP_SERVER ":8888/play_music/"
#define BUFFER_SIZE                 4096    // Kích thước buffer stream
const int SAMPLE_DELAY_US   =       62.5 ;  //999999 / I2S_SAMPLE_RATE;  
#define SKIP_LAST_BYTES             24
#define SILENCE_THRESHOLD           4000    // Ngưỡng có tiếng nói
#define SILENCE_MS                  2400   // Khoảng thời gian để kết thúc ghi âm
#define WAKE_WORD_MS                1200  // Khoảng thời gian để kết thúc kiểm tra từ khóa

volatile bool isStreaming = false;
char* i2s_read_buff = NULL;
uint8_t* scaled_buff = NULL;
unsigned long last_sound_time = 0;
std::vector<String> playlist;
int stop = 0; // 1: stop_music ; 2: pre_music; 3:next_music ; 4 : stop_ai
int currentMusicIndex = 0;
int mode_server = 0;

// Hàm kết nối wifi
void connectToWiFi() {
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}
void initI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = i2s_bits_per_sample_t(I2S_SAMPLE_BITS),
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = 0,// .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 64, //8
    .dma_buf_len = 1024,
    .use_apll = 1,
    // .tx_desc_auto_clear = false,
    // .fixed_mclk = 0,
  };
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}
// Hàm chuẩn hóa âm thanh
void scale_i2s_data(uint8_t * d_buff, uint8_t* s_buff, uint32_t len) {
  uint32_t j = 0;
  uint32_t dac_value = 0;
  for (int i = 0; i < len; i += 2) {
        dac_value = ((((uint16_t) (s_buff[i + 1] & 0xf) << 8) | ((s_buff[i + 0]))));
        d_buff[j++] = 0;
        d_buff[j++] = dac_value * 256 / 2048;
  }
}

// Hàm kiểm tra im lặng
bool isSilent(uint8_t *buff, size_t len) {
  int16_t *samples = (int16_t*)buff;
  size_t count = len / 2;
  long sum = 0;
  for (size_t i = 0; i < count; ++i) {
    sum += abs(samples[i]);
  }
  int avg = sum / count;
  Serial.print("Biên độ âm thanh: ");
  Serial.println(avg);
  return avg < SILENCE_THRESHOLD;
}

// Hàm thu âm gửi âm thanh thu được đến Server
void audio_recording() {
  size_t bytes_read;
  if (!i2s_read_buff) {
    i2s_read_buff = (char*) calloc(I2S_READ_LEN, sizeof(char));
    scaled_buff = (uint8_t*) calloc(I2S_READ_LEN, sizeof(char));
  } 
  last_sound_time = millis();
  while (true) {
    check_stop();
    if (stop!=0){
      free(i2s_read_buff);
      free(scaled_buff);
      i2s_read_buff = NULL;
      scaled_buff = NULL;
      return;
    } 
    i2s_read(I2S_PORT, (void*)i2s_read_buff, I2S_READ_LEN, &bytes_read, portMAX_DELAY);
    scale_i2s_data(scaled_buff, (uint8_t*)i2s_read_buff, bytes_read);
    if(!isSilent(scaled_buff, bytes_read)) {
      last_sound_time = millis();
    }
    HTTPClient client;
    client.begin(SEND_RECORD_API);
    client.addHeader("Content-Type", "application/octet-stream");
    int code = client.POST((uint8_t*)scaled_buff, bytes_read);
    client.end();
    if (millis() - last_sound_time > SILENCE_MS) {
      HTTPClient endClient;
      endClient.begin(END_RECORD_API);
      endClient.POST("");
      endClient.end();
      break;
    }
  }
  free(i2s_read_buff);
  free(scaled_buff);
  i2s_read_buff = NULL;
  scaled_buff = NULL;
  return;
}
int check_wake_word() {
  size_t bytes_read;
  if (!i2s_read_buff) {
    i2s_read_buff = (char*) calloc(I2S_READ_LEN, sizeof(char));
    scaled_buff = (uint8_t*) calloc(I2S_READ_LEN, sizeof(char));
  } 
  last_sound_time = millis();
  while (millis() - last_sound_time < WAKE_WORD_MS) {
    check_stop();
    if (stop!=0){
      free(i2s_read_buff);
      free(scaled_buff);
      i2s_read_buff = NULL;
      scaled_buff = NULL;
      return 0;
    } 
    i2s_read(I2S_PORT, (void*)i2s_read_buff, I2S_READ_LEN, &bytes_read, portMAX_DELAY);
    scale_i2s_data(scaled_buff, (uint8_t*)i2s_read_buff, bytes_read);
    HTTPClient client;
    client.begin(SEND_WAKE_WORD_RECORD_API);
    int code = client.POST((uint8_t*)scaled_buff, bytes_read);
    client.end();
  }
  free(i2s_read_buff);
  free(scaled_buff);
  i2s_read_buff = NULL;
  scaled_buff = NULL;
  HTTPClient check_wake_http;
  check_wake_http.begin(CHECK_WAKE_WORD_API);
  check_wake_http.setTimeout(10000);
  int httpCode = check_wake_http.GET();
  check_stop();
  if (stop != 0) {
    check_wake_http.end();
    return 0;
  } else if (httpCode == 200) {
    check_wake_http.end();
    return 1;
  } else if (httpCode == 202) {
    check_wake_http.end();
    return 2;
  } else {
    check_wake_http.end();
    return 0;
  }
}
void playBeep(int frequency = 1000, int duration_ms = 100, int amplitude = 100) {
  const int sampleRate = 16000; 
  const float pi = 3.14159265;
  int samples = (sampleRate * duration_ms) / 1000;
  int fadeSamples = sampleRate * 0.01;  // 10ms fade

  dac_output_enable(DAC_CHANNEL_1);
  dac_output_enable(DAC_CHANNEL_2);

  int64_t lastMicros = esp_timer_get_time();

  for (int i = 0; i < samples; i++) {
    float theta = 2.0 * pi * frequency * i / sampleRate;
    
    float fade = 1.0;
    if (i < fadeSamples) fade = (float)i / fadeSamples;
    else if (i > samples - fadeSamples) fade = (float)(samples - i) / fadeSamples;

    float sine = sin(theta);
    uint8_t sample = (uint8_t)(amplitude * fade * sine + 128);
    
    dac_output_voltage(DAC_CHANNEL_1, sample);
    dac_output_voltage(DAC_CHANNEL_2, sample);

    while (esp_timer_get_time() - lastMicros < 62.5) {}
    lastMicros += 62.5;
  }

  dac_output_disable(DAC_CHANNEL_1);
  dac_output_disable(DAC_CHANNEL_2);
}

// Hàm nhận và phát âm thanh từ Server
void playAudio(String filename) {
  static uint8_t buffer[BUFFER_SIZE]; 
  HTTPClient playAudio_http;
  if (filename == "0") {
    playAudio_http.begin(RECEIVE_SPEECH_API);
  } else {
    String url = RECEIVE_MUSIC_API + filename;
    playAudio_http.begin(url);
  }
  playAudio_http.setTimeout(15000);
  int httpCode = playAudio_http.GET();
  if (httpCode == HTTP_CODE_OK) {
    WiFiClient* stream = playAudio_http.getStreamPtr();
    for (int i = 0; i < 44; i++) {
      while (!stream->available()) {
        check_stop(); // kiểm tra trong khi chờ
        if (stop!=0){
          playAudio_http.end();
          return;
        }
      }
      stream->read();
    }
    dac_output_enable(DAC_CHANNEL_1);
    dac_output_enable(DAC_CHANNEL_2);
    int64_t lastMicros = esp_timer_get_time();
    int contentLength = playAudio_http.getSize();
    int totalRead = 0;
    while (playAudio_http.connected() && totalRead < contentLength) {
      int bytesRead = stream->readBytes(buffer, BUFFER_SIZE);
      totalRead += bytesRead;
      if (totalRead + bytesRead > contentLength - SKIP_LAST_BYTES) break;
      for (int i = 0; i < bytesRead; i++) {
        uint8_t sample = buffer[i];
        sample = constrain(sample, 0, 255);
        dac_output_voltage(DAC_CHANNEL_1, sample);
        dac_output_voltage(DAC_CHANNEL_2, sample);
        while (esp_timer_get_time() - lastMicros < SAMPLE_DELAY_US) {
          check_stop(); 
          if (stop!=0){
            playAudio_http.end();
            dac_output_disable(DAC_CHANNEL_1);
            dac_output_disable(DAC_CHANNEL_2);
            return;
          }
        }
        lastMicros += SAMPLE_DELAY_US;
      }
    }
    dac_output_disable(DAC_CHANNEL_1);
    dac_output_disable(DAC_CHANNEL_2);
  }
  playAudio_http.end();
}
void fetchPlaylist() {
  HTTPClient fetchPlaylist_http;
  fetchPlaylist_http.begin(RECEIVE_LIST_MUSIC_API);
  fetchPlaylist_http.setTimeout(15000);
  int httpCode = fetchPlaylist_http.GET();
  if (httpCode == HTTP_CODE_OK) {
    String payload = fetchPlaylist_http.getString();
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);
    playlist.clear();
    for (JsonVariant v : doc.as<JsonArray>()) {
      playlist.push_back(v.as<String>());
    }
  }
  fetchPlaylist_http.end();
}
String getESP_ui_Command() {
  if (Serial1.available()) {
    String command = Serial1.readStringUntil('\n');
    command.trim();
    return command;
  }
  return "";  
}
void check_stop(){
  String cmd = getESP_ui_Command();
  if (cmd == "start_ai") {
    stop = 1;
    mode_server = 1;
  } else if (cmd == "stop_ai"){
    stop = 2;
    mode_server = 0;
  } else if (cmd == "play_music"){
    stop = 3;
    mode_server = 2;
  } else if (cmd == "pre_music"){
    stop = 4;
  } else if (cmd == "stop_music"){
    stop = 5;
    mode_server = 0;
  } else if (cmd == "next_music"){
    stop = 6;
  } else if (cmd == "alarm_mode"){
    stop = 7;
    mode_server = 3;
  } else if (cmd == "start_alarm"){
    stop = 8;
    mode_server = 4;
  } else if (cmd == "stop_alarm"){
    stop = 9;
    mode_server = 0;
  } else if (cmd == "stop_alarm_mode"){
    stop = 10;
    mode_server = 0;
  } else if (cmd == "stop_mode_pro"){
    stop = 11;
    mode_server = 0;
  } 
}
void check_record(){
  int check_wake = check_wake_word();
  if (check_wake == 1){
    Serial1.println("start_ai");
    playAudio("female_response.wav");
    Ai_processing();
    Serial1.println("end_ai");
  } else if (check_wake == 2){
    Serial1.println("start_mode_pro");
    playAudio("male_response.wav");
    Ai_processing();
    Serial1.println("end_mode_pro");
  }
}
void clearI2SBuffer() {
  size_t bytesRead;
  char dummy[I2S_READ_LEN];
  unsigned long start = millis();
  while (millis() - start < 100) { 
    i2s_read(I2S_PORT, &dummy, I2S_READ_LEN, &bytesRead, 10);  
  }
}
void call_ai_process_async() {
  HTTPClient http;
  http.begin(AI_PROCESS_AUDIO_API);
  int response = http.GET();
  http.end();
  if (response == 200) {
    while (true) {
      delay(30);
      check_stop(); 
      if (stop!=0){
        return;
      }
      HTTPClient check;
      check.begin(CHECK_STATUS_AUDIO_API);
      int status_code = check.GET();
      if (status_code == 200) {
          check.end();
          return;
      }
      check.end();
    }
  } 
}

void Ai_processing(){     
  clearI2SBuffer();  
  Serial1.println("led_recording");
  audio_recording();
  if(stop!= 0){
    clearI2SBuffer();
    stop=0;
    return;
  }
  Serial1.println("led_loading");
  call_ai_process_async();
  if(stop!= 0){
    clearI2SBuffer();
    stop=0;
    return;
  }
  Serial1.println("led_playing");
  playAudio("0");
  if(stop!= 0){
    clearI2SBuffer();
    stop=0;
    return;
  }
  clearI2SBuffer();
  mode_server = 0;
}
void Music_processing(){
  while (true) {
    if(stop == 4){
      currentMusicIndex = (currentMusicIndex - 1 + playlist.size()) % playlist.size();
    } else if(stop == 5){
      stop=0;
      currentMusicIndex = (currentMusicIndex - 1 + playlist.size()) % playlist.size();
      clearI2SBuffer();
      return;
    } else if(stop == 8){
      stop=0;
      currentMusicIndex = (currentMusicIndex - 1 + playlist.size()) % playlist.size();
      return;
    } else{
      currentMusicIndex = (currentMusicIndex + 1) % playlist.size();
    } 
    stop=0;
    Serial1.println(playlist[currentMusicIndex]);
    playAudio(playlist[currentMusicIndex]);
  }
}
void Alarm_wait(){
   while (true) {
    check_stop();
    if (stop==8){
      stop = 0;
      mode_server = 4;
      return;
    } else if (stop==10) 
    {
      stop = 0;
      clearI2SBuffer();
      mode_server = 0;
      return;
    }
  }
}
void Alarm_processing(){
  while (true) {
    playAudio("bao_thuc.wav");
    if(stop == 9){
      stop = 0;
      clearI2SBuffer();
      return;
    }
  }
}
void setup() {
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, 16, 17);
  Serial1.setTimeout(10); 
  connectToWiFi();
  initI2S();
  fetchPlaylist();
  currentMusicIndex = playlist.size() - 1;
}

void loop() {
  stop = 0;
  if(mode_server == 0){
    check_record();
  } else if(mode_server == 1){
    playBeep(2000, 100); 
    Ai_processing();
    Serial1.println("end_ai");
  } else if(mode_server == 2){
    Music_processing();
  } else if(mode_server == 3){
    Alarm_wait();
  } else if(mode_server == 4){
    Alarm_processing();
  }
}