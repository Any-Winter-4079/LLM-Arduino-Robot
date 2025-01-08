/*
 * ESP32-CAM Image Streaming Controller
 * Configures ESP32-CAM (Ai-Thinker) to capture and send JPEG images to computer
 * Features:
 * - Dual WiFi network support with static IPs
 * - Async web server for improved performance
 * - Configurable camera parameters via HTTP endpoints
 * - JPEG image streaming with stabilization
 */

// Required libraries for WiFi, async server, and camera functionality
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <esp_camera.h>

// Primary network configuration (home WiFi)
const char* ssid1 = "";                     // Home WiFi's SSID
const char* password1 = "";                 // Home WiFi's password
IPAddress staticIP1(192, 168, 1, 181);      // Static IP for home network
IPAddress gateway1(192, 168, 1, 1);         // Gateway for home network
IPAddress subnet1(255, 255, 255, 0);        // Subnet mask

// Fallback network configuration (phone hotspot)
const char* ssid2 = "";                     // Phone hotspot's SSID
const char* password2 = "";                 // Phone hotspot's password
IPAddress staticIP2(172, 20, 10, 11);       // Static IP for hotspot
IPAddress gateway2(172, 20, 10, 1);         // Gateway for hotspot
IPAddress subnet2(255, 255, 255, 0);        // Subnet mask

// Web server initialization on port 80
AsyncWebServer server(80);

// Content type definition for JPEG images
static const char * JPG_CONTENT_TYPE = "image/jpeg";

/*
 * AsyncBufferResponse Class
 * Handles asynchronous delivery of buffer data over HTTP
 * Used for non-JPEG format images that need conversion
 */
class AsyncBufferResponse: public AsyncAbstractResponse {
    private:
        uint8_t * _buf;                    // Buffer pointer
        size_t _len;                       // Buffer length
        size_t _index;                     // Current position in buffer
    public:
        // Constructor initializes buffer response with content
        AsyncBufferResponse(uint8_t * buf, size_t len, const char * contentType){
            _buf = buf;
            _len = len;
            _callback = nullptr;
            _code = 200;
            _contentLength = _len;
            _contentType = contentType;
            _index = 0;
        }
        
        // Destructor frees allocated buffer
        ~AsyncBufferResponse(){
            if(_buf != nullptr){
                free(_buf);
            }
        }
        
        // Validates buffer existence
        bool _sourceValid() const { return _buf != nullptr; }
        
        // Fills response buffer with data
        virtual size_t _fillBuffer(uint8_t *buf, size_t maxLen) override{
            size_t ret = _content(buf, maxLen, _index);
            if(ret != RESPONSE_TRY_AGAIN){
                _index += ret;
            }
            return ret;
        }
        
        // Copies content to response buffer
        size_t _content(uint8_t *buffer, size_t maxLen, size_t index){
            memcpy(buffer, _buf+index, maxLen);
            if((index+maxLen) == _len){
                free(_buf);
                _buf = nullptr;
            }
            return maxLen;
        }
};

/*
 * AsyncFrameResponse Class
 * Handles asynchronous delivery of camera frames over HTTP
 * Used for direct JPEG format images from camera
 */
class AsyncFrameResponse: public AsyncAbstractResponse {
    private:
        camera_fb_t * fb;                  // Camera frame buffer
        size_t _index;                     // Current position in frame
    public:
        // Constructor initializes frame response
        AsyncFrameResponse(camera_fb_t * frame, const char * contentType){
            _callback = nullptr;
            _code = 200;
            _contentLength = frame->len;
            _contentType = contentType;
            _index = 0;
            fb = frame;
        }
        
        // Destructor returns frame buffer to camera
        ~AsyncFrameResponse(){
            if(fb != nullptr){
                esp_camera_fb_return(fb);
            }
        }
        
        // Validates frame existence
        bool _sourceValid() const { return fb != nullptr; }
        
        // Fills response buffer with frame data
        virtual size_t _fillBuffer(uint8_t *buf, size_t maxLen) override{
            size_t ret = _content(buf, maxLen, _index);
            if(ret != RESPONSE_TRY_AGAIN){
                _index += ret;
            }
            return ret;
        }
        
        // Copies frame content to response buffer
        size_t _content(uint8_t *buffer, size_t maxLen, size_t index){
            memcpy(buffer, fb->buf+index, maxLen);
            if((index+maxLen) == fb->len){
                esp_camera_fb_return(fb);
                fb = nullptr;
            }
            return maxLen;
        }
};

/*
 * Handles requests for JPEG images
 * Captures frame from camera and sends it as HTTP response
 */
void sendJpg(AsyncWebServerRequest *request){
    camera_fb_t * fb = esp_camera_fb_get();
    if (fb == NULL) {
        log_e("Camera frame failed");
        request->send(501);
        return;
    }

    // Handle direct JPEG format from camera
    if(fb->format == PIXFORMAT_JPEG){
        AsyncFrameResponse * response = new AsyncFrameResponse(fb, JPG_CONTENT_TYPE);
        if (response == NULL) {
            log_e("Response alloc failed");
            request->send(501);
            return;
        }
        response->addHeader("Access-Control-Allow-Origin", "*");
        request->send(response);
        return;
    }

    // Convert non-JPEG format to JPEG
    size_t jpg_buf_len = 0;
    uint8_t * jpg_buf = NULL;
    unsigned long st = millis();
    bool jpeg_converted = frame2jpg(fb, 80, &jpg_buf, &jpg_buf_len);
    esp_camera_fb_return(fb);
    
    if(!jpeg_converted){
        log_e("JPEG compression failed: %lu", millis());
        request->send(501);
        return;
    }
    log_i("JPEG: %lums, %uB", millis() - st, jpg_buf_len);

    // Send converted JPEG
    AsyncBufferResponse * response = new AsyncBufferResponse(jpg_buf, jpg_buf_len, JPG_CONTENT_TYPE);
    if (response == NULL) {
        log_e("Response alloc failed");
        request->send(501);
        return;
    }
    response->addHeader("Access-Control-Allow-Origin", "*");
    request->send(response);
}

/*
 * Handles camera configuration updates via HTTP POST
 * Allows remote adjustment of frame size and JPEG quality
 */
void handleCameraConfig(AsyncWebServerRequest *request) {
    camera_config_t config;

    if (request->method() == HTTP_POST) {
        // Process JPEG quality parameter
        if (request->hasParam("jpeg_quality", true)) {
            String jpegQuality = request->getParam("jpeg_quality", true)->value();
            int jpegQualityInt = jpegQuality.toInt();
            if (jpegQualityInt < 0 || jpegQualityInt > 63) {
                request->send(400, "text/plain", "Parameter 'jpeg_quality' is invalid");
                return;
            }
            else {
                config.jpeg_quality = jpegQualityInt;
            }
        } else {
            request->send(400, "text/plain", "Parameter 'jpeg_quality' is missing");
            return;
        }

        // Process frame size parameter
        if (request->hasParam("frame_size", true)) {
            String frameSize = request->getParam("frame_size", true)->value();
            if (strcmp(frameSize.c_str(), "FRAMESIZE_QVGA") == 0) {
                config.frame_size = FRAMESIZE_QVGA;          // 320x240
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_VGA") == 0) {
                config.frame_size = FRAMESIZE_VGA;           // 640x480
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_SVGA") == 0) {
                config.frame_size = FRAMESIZE_SVGA;          // 800x600
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_XGA") == 0) {
                config.frame_size = FRAMESIZE_XGA;           // 1024x768
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_SXGA") == 0) {
                config.frame_size = FRAMESIZE_SXGA;          // 1280x1024
            }
            else if (strcmp(frameSize.c_str(), "FRAMESIZE_UXGA") == 0) {
                config.frame_size = FRAMESIZE_UXGA;          // 1600x1200
            }
            else {
                request->send(400, "text/plain", "Parameter 'frame_size' is invalid");
                return;
            }
        } else {
            request->send(400, "text/plain", "Parameter 'frame_size' is missing");
            return;
        }

        // Set fixed camera configuration parameters
        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer = LEDC_TIMER_0;
        config.pixel_format = PIXFORMAT_JPEG;
        config.fb_count = 1;
        config.xclk_freq_hz = 20000000;    // 20 MHz clock frequency
        config.grab_mode = CAMERA_GRAB_LATEST;
        config.fb_location = CAMERA_FB_IN_PSRAM;

        // Configure camera pins for Ai-Thinker ESP32-CAM
        config.pin_d0 = 5;
        config.pin_d1 = 18;
        config.pin_d2 = 19;
        config.pin_d3 = 21;
        config.pin_d4 = 36;
        config.pin_d5 = 39;
        config.pin_d6 = 34;
        config.pin_d7 = 35;
        config.pin_xclk = 0;
        config.pin_pclk = 22;
        config.pin_vsync = 25;
        config.pin_href = 23;
        config.pin_sscb_sda = 26;
        config.pin_sscb_scl = 27;
        config.pin_pwdn = 32;
        config.pin_reset = -1;

        // Apply new configuration
        esp_camera_deinit();
        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            request->send(500, "text/plain", "Camera config update failed");
        }
        else {
            request->send(200, "text/plain", "Camera config updated");
        }
    } else {
        request->send(405, "text/plain", "Method Not Allowed");
    }
}

/*
 * Attempts to connect to specified WiFi network
 * Returns true if connection successful, false otherwise
 */
bool connectToWiFi(const char* ssid, const char* password, IPAddress staticIP, IPAddress gateway, IPAddress subnet) {
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.config(staticIP, gateway, subnet);
    WiFi.begin(ssid, password);

    for (int i = 0; i < 10; i++) {        // Try connecting for 10 seconds
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("Connected!");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());
            return true;
        }
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Connection failed.");
    return false;
}

/*
 * Setup function - runs once at startup
 * Initializes camera, WiFi connection, and web server
 */
void setup() {
    Serial.begin(115200);

    // Configure camera settings
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;     // 640x480 resolution
    config.jpeg_quality = 12;              // Higher quality (0-63, lower is better)
    config.fb_count = 1;
    config.xclk_freq_hz = 20000000;        // 20 MHz clock frequency
    config.grab_mode = CAMERA_GRAB_LATEST;
    config.fb_location = CAMERA_FB_IN_PSRAM;

    // Configure camera pins for Ai-Thinker ESP32-CAM
    config.pin_d0 = 5;
    config.pin_d1 = 18;
    config.pin_d2 = 19;
    config.pin_d3 = 21;
    config.pin_d4 = 36;
    config.pin_d5 = 39;
    config.pin_d6 = 34;
    config.pin_d7 = 35;
    config.pin_xclk = 0;
    config.pin_pclk = 22;
    config.pin_vsync = 25;
    config.pin_href = 23;
    config.pin_sscb_sda = 26;
    config.pin_sscb_scl = 27;
    config.pin_pwdn = 32;
    config.pin_reset = -1;

    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }

    // Attempt WiFi connection to primary network, then fallback
    bool connected = false;
    while (!connected) {
        connected = connectToWiFi(ssid1, password1, staticIP1, gateway1, subnet1);
        if (!connected) {
            connected = connectToWiFi(ssid2, password2, staticIP2, gateway2, subnet2);
        }
    }

    // Configure and start web server
    server.on("/image.jpg", HTTP_GET, sendJpg);
    server.on("/camera_config", HTTP_POST, handleCameraConfig);
    server.begin();
}

/*
 * Main loop - currently empty as all operations are event-driven
 */
void loop() {
    // Server handles requests asynchronously
}