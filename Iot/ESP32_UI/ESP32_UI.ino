#include "FS.h"
#include <LittleFS.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <JPEGDecoder.h>
#include <XPT2046_Touchscreen.h>
#include <Adafruit_NeoPixel.h>
#include <WiFi.h>
#include <time.h>
#define TOUCH_CS 4
XPT2046_Touchscreen ts(TOUCH_CS);
TFT_eSPI tft = TFT_eSPI();
#define PIN         14       
#define NUM_LEDS    12     
Adafruit_NeoPixel ring(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);

// const char* ssid = "PHAT";
// const char* password = "0968718348";
const char* ssid     = "TTT";
const char* password = "12345121123";

int mode = 0;  // 0: Trang chủ ; 1: Báo thức; 2: AI bot ; 3: Nghe nhạc
unsigned long lastUpdate = 0;
#include "clock_bg.h" 
#define CLOCK_X 204
#define CLOCK_Y 78
#define CLOCK_W 65
#define CLOCK_H 47
String dateStr = "";
String timeStr = "";
int second_int = 0;
char second[3];
#define BTN_SIZE 60
#define BTN_Y 173
#define BTN1_X 31   
#define BTN2_X 130
#define BTN3_X 229  

uint16_t transparent_light_yellow = tft.color565(230, 230, 120);  // vàng nhạt
uint16_t transparent_light_green = tft.color565(130, 235, 130);   // xanh lá cây nhạt
uint16_t transparent_light_pink = tft.color565(240, 130, 180);    // hồng nhạt

int step=0;
int mode_led = 0;
unsigned long lastUpdate_LED = 0;
const char* expressions[] = {
  //"/robot_mo_mat.jpg",
  "/robot_nham_mat.jpg",
  "/robot_mo_mat.jpg",
  "/robot_trai.jpg",
  "/robot_mo_mat.jpg",
  "/robot_chop_mat.jpg",
  "/robot_phai.jpg",
  "/robot_mo_mat.jpg",
  "/robot_nham_mat.jpg",
  "/robot_mo_mat.jpg",
  "/robot_nham_mat.jpg",
  "/robot_cute.jpg",
  "/robot_cuoi.jpg",
  "/robot_cute.jpg",
  "/robot_nham_mat.jpg",
  "/robot_mo_mat.jpg" 
};
const int frameDelays[] = {1500, 2, 1000, 1000, 500, 500, 1000, 1000, 2, 1000, 2, 600, 1200, 600, 2};
int currentFrame = 0;
const int totalFrames = sizeof(expressions) / sizeof(expressions[0]);

const int numBars = 32;
const int barWidth = 8;
const int spacing = 2;
const int maxHeight = 100;
const int bottomMargin = 66;

String alarm_string1 = "06:00";
String alarm_string2 = "18:00";
bool alarm1 = false;
bool alarm2 = false;
int alarm_hour = 0;
int alarm_min = 0;
bool alarm_selected = false;
String alarm_hourString, alarm_minString;
int alarmImageToggle = 0;
const char* alarmImage[] = {
  "/alarm_clock.jpg",
  "/alarm_clock1.jpg",
  "/alarm_clock2.jpg",
};
int barHeights[numBars];

#include "FontMaker.h"
void setpx(int16_t x,int16_t y,uint16_t color)
{
  tft.drawPixel(x,y,color);
}
MakeFont myfont(&setpx);
int index_mode_pro = 1;
unsigned long lastUpdate_frames_pro = 0;
void drawJpeg(const char* filename, int xpos, int ypos) {
  JpegDec.decodeFsFile(filename);
  int jpegWidth = JpegDec.width, jpegHeight = JpegDec.height;
  while (JpegDec.read()) {
    int mcuX = xpos + JpegDec.MCUx * JpegDec.MCUWidth;
    int mcuY = ypos + JpegDec.MCUy * JpegDec.MCUHeight;
    int drawW = min(JpegDec.MCUWidth, xpos + jpegWidth - mcuX);
    int drawH = min(JpegDec.MCUHeight, ypos + jpegHeight - mcuY);
    if (drawW > 0 && drawH > 0) {
      uint16_t* p = JpegDec.pImage;
      for (int row = 0; row < drawH; row++)
        tft.pushImage(mcuX, mcuY + row, drawW, 1, p + row * JpegDec.MCUWidth);
    }
  }
}
void setupWiFi() {
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  tft.fillScreen(TFT_BLACK);
  myfont.set_font(Font_Vn1);
  myfont.print(82,110,"Đang kết nối wifi.....",TFT_GREEN,TFT_BLACK);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    tft.print(".");
  }
}

void setupTime() {
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  while (time(nullptr) < 100000) {
    delay(500);
  }
}
void fetchDateTime(bool onlyTime = false) {
  time_t now = time(nullptr);
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);
  char buffer[10];
  sprintf(buffer, "%02d:%02d:", timeinfo.tm_hour, timeinfo.tm_min);
  timeStr = String(buffer);
  second_int = timeinfo.tm_sec;
  sprintf(second, "%02d", second_int);

  if (!onlyTime) {
    char dateBuffer[20];
    strftime(dateBuffer, sizeof(dateBuffer), "%d–%m–%y", &timeinfo);

    int weekday = timeinfo.tm_wday;
    String thu = "";
    switch (weekday) {
      case 0: thu = "Chủ nhật"; break;
      case 1: thu = "Thứ hai"; break;
      case 2: thu = "Thứ ba"; break;
      case 3: thu = "Thứ tư"; break;
      case 4: thu = "Thứ năm"; break;
      case 5: thu = "Thứ sáu"; break;
      case 6: thu = "Thứ bảy"; break;
    }
    dateStr = thu + ", " + String(dateBuffer);
  }
}
void fetchTimeSecond() {
  time_t now = time(nullptr);
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);
  second_int = timeinfo.tm_sec;
  sprintf(second, "%02d", second_int);
}
// Hàm hiệu ứng chạy led
void run_led(int step, int mode)
{
  const float MIN_BRIGHTNESS = 0.1;
  ring.clear();
  if (mode == 0){
  } else if (mode == 1){
    for (int i = 0; i < NUM_LEDS; i++) {
    int hue = (i * 65536L / NUM_LEDS);
    uint32_t color = ring.gamma32(ring.ColorHSV(hue));
    ring.setPixelColor(i, color);
    }
  } else {
    for (int i = 0; i < NUM_LEDS; i++) {
    int distance = (i - step + NUM_LEDS) % NUM_LEDS;
    float brightness = max((float)exp(-0.5 * distance), MIN_BRIGHTNESS);
    uint8_t r = 0, g = 0, b = 0;
    if (mode == 2) {
      int hue = (i * 65536L / NUM_LEDS);
      uint32_t color = ring.gamma32(ring.ColorHSV(hue));
      r = ((color >> 16) & 0xFF) * brightness;
      g = ((color >> 8) & 0xFF) * brightness;
      b = (color & 0xFF) * brightness;
    } else if (mode == 3) {
      r = 0;
      g = 255 * brightness;  // màu xanh lá cây
      b = 0;
    } else if (mode == 4){
      r = 0;
      g = 0;
      b = 255 * brightness;  //xanh dương
    }
    ring.setPixelColor(i, r, g, b);
    }
  }
  ring.show();
}
void setup_home_ui() {
  fetchDateTime();
  drawJpeg("/home_back_img.jpg", 0, 0);
  tft.setTextDatum(MC_DATUM);  // Canh giữa
  tft.setFreeFont(&FreeSansBold9pt7b);
  tft.setTextColor(TFT_CYAN);
  if (alarm1 && alarm2) tft.drawString(alarm_string1 + " -" + alarm_string2, 160, 148);
  else if (alarm1) tft.drawString(alarm_string1, 160, 148);
  else if (alarm2) tft.drawString(alarm_string2, 160, 148);
  myfont.set_font(tahoma10);
  myfont.print(102,122,dateStr,TFT_GREEN,TFT_BLACK);
  tft.setTextFont(6);
  tft.setTextColor(TFT_WHITE);
  tft.drawString(timeStr, 135, 108);
  tft.setTextFont(6);  
  tft.setTextColor(TFT_WHITE);
  tft.drawString(second, 232, 108);
}
void drawRainbowDashedLine(bool horizontal, int x, int y, int len, int dash = 6, int gap = 2) {
  static const uint16_t rainbow[] = {
    TFT_RED, 0xFD20, TFT_YELLOW, TFT_GREEN, TFT_CYAN, TFT_BLUE, TFT_MAGENTA
  };
  int pos = 0, colorIdx = 0, n = sizeof(rainbow) / sizeof(rainbow[0]);
  while (pos < len) {
    int seg = min(dash, len - pos);
    uint16_t color = rainbow[colorIdx++ % n];
    if (horizontal)
      tft.drawFastHLine(x + pos, y, seg, color);
    else
      tft.drawFastVLine(x, y + pos, seg, color);
    pos += seg + gap;
  }
}
void setup_alarm_ui() {
  tft.fillScreen(TFT_BLACK);
  myfont.set_font(Tahoma_bold16);
  myfont.print(75,5,"Hẹn giờ báo thức",TFT_GREEN,TFT_BLACK);
  tft.setFreeFont(&FreeSansBold18pt7b);
  String times[] = { alarm_string1, alarm_string2 };
  int states[] = { alarm1, alarm2 };
  int boxX = 25, boxY = 40, boxW = 270, boxH = 60, spacing = 8;
  for (int i = 0; i < 2; i++) {
    int x = boxX; 
    int y = boxY + i * (boxH + spacing); 
    // Viền nét đứt màu cầu vồng
    drawRainbowDashedLine(true, x, y, boxW);          // top
    drawRainbowDashedLine(true, x, y + boxH, boxW);   // bottom
    drawRainbowDashedLine(false, x, y, boxH);         // left
    drawRainbowDashedLine(false, x + boxW, y, boxH);  // right
    // Hiển thị chuỗi báo thức
    tft.setTextColor(i ? TFT_MAGENTA : TFT_CYAN);
    tft.drawString(times[i], 105, y + boxH / 2);
    drawJpeg(states[i] ? "/check_box.jpg" : "/check_box_empty_icon.jpg", 220, y + boxH / 2 - 22);
  }
  drawRainbowDashedLine(true, 25, 16, 15);     
  drawRainbowDashedLine(true, 281, 16, 15);  
  drawRainbowDashedLine(false, 25, 16, 23);   
  drawRainbowDashedLine(false, 295, 16, 23);    
  drawRainbowDashedLine(true, 25, 208, 109);     
  drawRainbowDashedLine(true, 186, 208, 110);  
  drawRainbowDashedLine(false, 25, 168, 40);   
  drawRainbowDashedLine(false, 295, 168, 40);     
  drawRainbowDashedLine(true, BTN2_X + 3, BTN_Y + 7, BTN_SIZE-6);         
  drawRainbowDashedLine(true, BTN2_X + 3, BTN_Y + 60, BTN_SIZE-6);
  drawRainbowDashedLine(false,BTN2_X + 3, BTN_Y + 7, BTN_SIZE-6);         
  drawRainbowDashedLine(false, BTN2_X + 56, BTN_Y + 7, BTN_SIZE-5);  
  drawJpeg("/home_icon.jpg", BTN2_X + 8, BTN_Y + 12);
}
void get_alarm_time() {
  if (!alarm_selected) {
    alarm_hourString = alarm_string1.substring(0, 2);
    alarm_minString = alarm_string1.substring(3, 5);
  } else {
    alarm_hourString = alarm_string2.substring(0, 2);
    alarm_minString = alarm_string2.substring(3, 5);
  }
  alarm_hour = alarm_hourString.toInt();
  alarm_min = alarm_minString.toInt();
}
void setup_alarm_setting_ui() {
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  myfont.set_font(Tahoma_bold16);
  myfont.print(76,5,"Cài đặt thời gian",TFT_GREEN,TFT_BLACK);
  drawJpeg("/up_icon.jpg", 20, 46);
  drawJpeg("/down_icon.jpg", 20, 140);
  drawJpeg("/up_icon.jpg", 256, 46);
  drawJpeg("/down_icon.jpg", 256, 140);
  get_alarm_time();
  tft.setTextFont(6);
  tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN);
  tft.drawString(alarm_hourString, 110, 120);
  tft.setTextColor(TFT_WHITE);
  tft.drawString(":", 160, 120);
  tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN);
  tft.drawString(alarm_minString, 210, 120);
  drawJpeg("/ok_icon.jpg", BTN2_X + 8, BTN_Y + 12);
}
void setup_Ai_ui() {
  mode_led = 1;
  run_led(step,mode_led);
  lastUpdate = millis();
  drawJpeg("/robot_mo_mat.jpg", 0, 0);
}
void setup_music_ui(String file_name_music) {
  drawJpeg("/music_back_img.jpg", 0, 0);
  tft.setFreeFont(&FreeSansBold9pt7b);
  tft.setTextColor(TFT_GREEN);
  tft.setTextDatum(MC_DATUM);
  if (file_name_music == "") {
    tft.drawString("Dang tai bai hat..", 160, 40);
  } else {
    String name_music = file_name_music.substring(0, file_name_music.length() - 4);
    tft.drawString(name_music, 160, 40);
  }
}
String getESP_sever_Command() {
  if (Serial1.available()) {
    String command = Serial1.readStringUntil('\n');
    command.trim();
    return command;
  }
  return "";
}
void home_handler() {
  String command = getESP_sever_Command();
  if (command == "start_ai") {
    mode = 2;
    setup_Ai_ui();
    return;
  } else if(command == "start_mode_pro") {
    mode = 6;
    setup_mode_pro_ui();
    return;
  }
  if (millis() - lastUpdate >= 1000)  // Cập nhật số giây
  {
    fetchTimeSecond();
    if (second_int == 0) {
      setup_home_ui();
    } else {
      // drawJpeg("/clock_bg.jpg", CLOCK_X, CLOCK_Y);
      tft.pushImage(CLOCK_X, CLOCK_Y, 65, 47, clock_bg);
      tft.setTextDatum(MC_DATUM);
      tft.setTextFont(6);
      tft.setTextColor(TFT_WHITE);
      tft.drawString(second, 232, 108);
    }
    lastUpdate = millis();
  }
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    
    if (x >= BTN1_X && x <= BTN1_X + BTN_SIZE && y >= BTN_Y && y <= BTN_Y + BTN_SIZE + 1) {
      tft.fillRoundRect(BTN1_X, BTN_Y + 1, BTN_SIZE, BTN_SIZE, 10, transparent_light_yellow);
      mode = 1;
      Serial1.println("alarm_mode");
      delay(50);
      setup_alarm_ui();
    } else if (x >= BTN2_X && x <= BTN2_X + BTN_SIZE && y >= BTN_Y && y <= BTN_Y + BTN_SIZE + 1) {
      tft.fillRoundRect(BTN2_X, BTN_Y + 1, BTN_SIZE, BTN_SIZE, 10, transparent_light_green);
      mode = 2;
      Serial1.println("start_ai");
      delay(20);
      setup_Ai_ui();
    } else if (x >= BTN3_X && x <= BTN3_X + BTN_SIZE && y >= BTN_Y && y <= BTN_Y + BTN_SIZE + 1) {
      tft.fillRoundRect(BTN3_X, BTN_Y + 1, BTN_SIZE, BTN_SIZE, 10, transparent_light_pink);
      Serial1.println("play_music");
      String command = getESP_sever_Command();
      mode = 3;
      delay(20);
      setup_music_ui(command);
    }
  }
}
void alarm_handler() {
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= BTN2_X + 3 && x <= BTN2_X + BTN_SIZE - 3 && y >= BTN_Y + 7 && y <= BTN_Y + BTN_SIZE + 1) {
      tft.fillRoundRect(BTN2_X + 4, BTN_Y + 8, BTN_SIZE - 9, BTN_SIZE - 8, 0, TFT_YELLOW);
      mode = 0;
      Serial1.println("stop_alarm_mode");
      delay(50);
      setup_home_ui();
    } else if (x >= 50 && x <= 180 && y >= 40 && y <= 100) {
      tft.fillRoundRect(25, 40, 270, 60, 2, TFT_DARKGREY);
      mode = 4;
      alarm_selected = 0;
      delay(50);
      setup_alarm_setting_ui();
    } else if (x >= 50 && x <= 180 && y >= 110 && y <= 170) {
      tft.fillRoundRect(25, 108, 270, 60, 2, TFT_DARKGREY);
      mode = 4;
      alarm_selected = 1;
      delay(50);
      setup_alarm_setting_ui();
    } else if (x >= 210 && x <= 270 && y >= 40 && y <= 100) {
      alarm1 = !alarm1;
      tft.fillRoundRect(220, 48, 44, 44, 0, TFT_BLACK);
      drawJpeg(alarm1 ? "/check_box.jpg" : "/check_box_empty_icon.jpg", 220, 48);
      delay(200);
    } else if (x >= 210 && x <= 270 && y >= 110 && y <= 170) {
      alarm2 = !alarm2;
      tft.fillRoundRect(220, 116, 44, 44, 0, TFT_BLACK);
      drawJpeg(alarm2 ? "/check_box.jpg" : "/check_box_empty_icon.jpg", 220, 116);
      delay(200);
    }
  }
}
void setting_alarm_handler() {
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= BTN2_X + 3 && x <= BTN2_X + BTN_SIZE - 3 && y >= BTN_Y + 7 && y <= BTN_Y + BTN_SIZE + 1) {
      tft.fillRoundRect(BTN2_X + 4, BTN_Y + 8, BTN_SIZE - 8, BTN_SIZE - 8, 8, TFT_BLUE);
      if (!alarm_selected) {
        alarm_string1 = alarm_hourString + ":" + alarm_minString;
      } else{
        alarm_string2 = alarm_hourString + ":" + alarm_minString;
      }
      mode = 1;
      delay(30);
      setup_alarm_ui();
      delay(200);
    } else if (x >= 20 && x <= 64 && y >= 46 && y <= 90) {
      alarm_hour = (alarm_hour + 1 + 24) % 24;
      alarm_hourString = (alarm_hour < 10 ? "0" : "") + String(alarm_hour);
      tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN, TFT_BLACK);
      tft.drawString(alarm_hourString, 110, 120);
      delay(200);
    } else if (x >= 20 && x <= 64 && y >= 140 && y <= 184) {
      alarm_hour = (alarm_hour - 1 + 24) % 24;
      alarm_hourString = (alarm_hour < 10 ? "0" : "") + String(alarm_hour);
      tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN, TFT_BLACK);
      tft.drawString(alarm_hourString, 110, 120);
      delay(200);
    } else if (x >= 256 && x <= 300 && y >= 46 && y <= 90) {
      alarm_min = (alarm_min + 1 + 60) % 60;
      alarm_minString = (alarm_min < 10 ? "0" : "") + String(alarm_min);
      tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN, TFT_BLACK);
      tft.drawString(alarm_minString, 210, 120);
      delay(200);
    } else if (x >= 256 && x <= 300 && y >= 140 && y <= 184) {
      alarm_min = (alarm_min - 1 + 60) % 60;
      alarm_minString = (alarm_min < 10 ? "0" : "") + String(alarm_min);
      tft.setTextColor(alarm_selected ? TFT_MAGENTA:TFT_CYAN, TFT_BLACK);
      tft.drawString(alarm_minString, 210, 120);
      delay(200);
    }
  }
}
void Ai_handler() {
  String command = getESP_sever_Command();
  if (command == "end_ai") {
    mode = 0;
    mode_led = 0;
    ring.clear();     
    ring.show(); 
    setup_home_ui();
    return;
  } else if (command == "led_recording"){
    step = 0;
    mode_led = 3;
  } else if (command == "led_loading"){
    step = 0;
    mode_led = 4;
  } else if (command == "led_playing"){
    step = 0;
    mode_led = 2;
  }
  if (millis() - lastUpdate_LED >= 45) {
    run_led(step, mode_led);
    step = (step + 1) % NUM_LEDS;
    lastUpdate_LED = millis();
  }
  if (millis() - lastUpdate >= frameDelays[currentFrame]) {
    drawJpeg(expressions[currentFrame], 0, 0);
    lastUpdate = millis();
    currentFrame = (currentFrame + 1) % totalFrames;
  }
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= 40 && x <= 280 && y >= 40 && y <= 240) {
      ring.clear();     
      ring.show(); 
      mode_led = 0;
      mode = 0;
      Serial1.println("stop_ai");
      delay(20);
      setup_home_ui();
    }
  }
}
// Hàm tạo màu cầu vồng theo vị trí
uint16_t rainbowColor(int index, int total) {
  float ratio = (float)index / total;
  int r = sin(6.28 * ratio + 0) * 127 + 128;
  int g = sin(6.28 * ratio + 2) * 127 + 128;
  int b = sin(6.28 * ratio + 4) * 127 + 128;
  return tft.color565(r, g, b);
}
void draw_music_back() {
  for (int i = 0; i < numBars; i++) {
    int oldHeight = barHeights[i];
    int newHeight = random(10, maxHeight);
    barHeights[i] = newHeight;
    int x = i * (barWidth + spacing);
    // Xoá cột cũ
    tft.fillRect(x, tft.height() - oldHeight - bottomMargin, barWidth, oldHeight, TFT_BLACK);
    uint16_t color = rainbowColor(i, numBars);
    // Vẽ cột mới
    tft.fillRect(x, tft.height() - newHeight - bottomMargin, barWidth, newHeight, color);
  }
  delay(100);
}
void music_handler() {
  String command = getESP_sever_Command();
  if (command != "") {
    setup_music_ui(command);
  }
  draw_music_back();
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= 35 && x <= 100 && y >= 175 && y <= 235) {
      tft.fillCircle(68, 205, 27, TFT_CYAN);
      Serial1.println("pre_music");
      delay(50);
    } else if (x >= 130 && x <= 190 && y >= 175 && y <= 235) {
      tft.fillCircle(159, 205, 27, TFT_CYAN);
      mode = 0;
      Serial1.println("stop_music");
      delay(50);
      setup_home_ui();
    } else if (x >= 220 && x <= 280 && y >= 175 && y <= 235) {
      tft.fillCircle(251, 205, 27, TFT_CYAN);
      Serial1.println("next_music");
      delay(50);
    }
  }
}
void setup_alarm_at_time_ui()
{
  tft.fillScreen(TFT_BLACK);
  tft.setFreeFont(&FreeSansBold18pt7b);
  tft.setTextColor(TFT_GREEN);
  tft.setTextDatum(MC_DATUM);
  tft.drawString(timeStr.substring(0, 5), 160, 30);
  drawJpeg("/alarm_clock.jpg", 60, 57);
  myfont.set_font(Font_Vn1);
  myfont.print(55,198,"Chạm vào màn hình để tắt!",TFT_CYAN,TFT_BLACK);
}
void alarm_at_time_handler() {
  if (millis() - lastUpdate_LED >= 45) {
    run_led(step, mode_led);
    step = (step + 1) % NUM_LEDS;
    lastUpdate_LED = millis();
  }
  if (millis() - lastUpdate >= 400) {
    lastUpdate = millis();
    alarmImageToggle = (alarmImageToggle+1+3)%3;
    drawJpeg(alarmImage[alarmImageToggle], 60, 57);
  }
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= 40 && x <= 280 && y >= 40 && y <= 240) {
      mode = 0;
      mode_led = 0;
      ring.clear();     
      ring.show(); 
      Serial1.println("stop_alarm");
      delay(20);
      setup_home_ui();
    }
  }
}
void check_alarm() {
  time_t now = time(nullptr);
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);
  char buffer[10];
  sprintf(buffer, "%02d:%02d:", timeinfo.tm_hour, timeinfo.tm_min);
  timeStr = String(buffer);
  if ((timeStr.substring(0, 5) == alarm_string1 && alarm1) || (timeStr.substring(0, 5) == alarm_string2 && alarm2)) {
    Serial1.println("start_alarm");
    if(timeStr.substring(0, 5) == alarm_string1) alarm1 = false;
    if(timeStr.substring(0, 5) == alarm_string2) alarm2 = false;
    mode = 5;
    mode_led = 2;
    step = 0;
    setup_alarm_at_time_ui();
  }
}
void setup_mode_pro_ui(){
  mode_led = 1;
  run_led(step,mode_led);
  lastUpdate_frames_pro = millis();
  tft.fillScreen(TFT_BLACK);
  tft.setFreeFont(&FreeSansBold9pt7b);
  tft.setTextColor(TFT_GREEN);
  tft.setTextDatum(MC_DATUM);
  tft.drawString("Medical VinaLlama 2.7B", 160, 45);
  index_mode_pro = 1;
  char filename[32];
  sprintf(filename, "/mode_pro_frames/frame_%03d.jpg", index_mode_pro);
  drawJpeg(filename, 10, 90);
  index_mode_pro++;
}
void mode_pro_handler(){
  String command = getESP_sever_Command();
  if (command == "end_mode_pro") {
    mode = 0;
    mode_led = 0;
    ring.clear();     
    ring.show(); 
    setup_home_ui();
    return;
  } else if (command == "led_recording"){
    step = 0;
    mode_led = 3;
  } else if (command == "led_loading"){
    step = 0;
    mode_led = 4;
  } else if (command == "led_playing"){
    step = 0;
    mode_led = 2;
  }
  if (millis() - lastUpdate_LED >= 45) {
    run_led(step, mode_led);
    step = (step + 1) % NUM_LEDS;
    lastUpdate_LED = millis();
  }
  if (millis() - lastUpdate_frames_pro >= 5) {
    char filename[32];
    sprintf(filename, "/mode_pro_frames/frame_%03d.jpg", index_mode_pro);
    drawJpeg(filename, 10, 90);
    if(index_mode_pro == 105){
      index_mode_pro=1;
    }
    else {
      index_mode_pro++;
    }
    lastUpdate_frames_pro = millis();
  }
  if (ts.touched()) {
    TS_Point p = ts.getPoint();
    int x = map(p.y, 300, 3900, 0, tft.width());
    int y = map(p.x, 3800, 320, 0, tft.height());
    if (x >= 40 && x <= 280 && y >= 40 && y <= 240) {
      ring.clear();     
      ring.show(); 
      mode_led = 0;
      mode = 0;
      Serial1.println("stop_mode_pro");
      delay(20);
      setup_home_ui();
    }
  }
}
void setup() {
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, 16, 17);
  Serial1.setTimeout(10); 
  ts.begin();
  LittleFS.begin();
  tft.init();
  tft.setSwapBytes(true);      
  tft.invertDisplay(false);
  tft.setRotation(1);
  // pinMode(33, OUTPUT);         
  // digitalWrite(33, HIGH);
  ring.begin();
  ring.setBrightness(40);
  ring.show();

  setupWiFi();
  tft.fillScreen(TFT_BLACK);
  myfont.set_font(Font_Vn1);
  myfont.print(60,103,"Đã kết nối wifi thành công!",TFT_GREEN,TFT_BLACK);
  myfont.print(62,123,"Đang khởi động hệ thống...",TFT_GREEN,TFT_BLACK);
  setupTime();
  setup_home_ui();
}
void loop() {
  check_alarm();
  if (mode == 0) {
    home_handler();
  } else if (mode == 1) {
    alarm_handler();
  } else if (mode == 2) {
    Ai_handler();
  } else if (mode == 3) {
    music_handler();
  } else if (mode == 4) {
    setting_alarm_handler();
  } else if (mode == 5) {
    alarm_at_time_handler();
  } else if (mode == 6) {
    mode_pro_handler();
  } 
}