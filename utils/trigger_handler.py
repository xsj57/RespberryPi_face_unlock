import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template_string, jsonify

class TriggerHandler:
    def __init__(self, callback_func):
        self.callback_func = callback_func
        self.is_processing = False
        
    def setup_gpio_button(self, pin=17):
        """设置GPIO按钮触发"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        def button_callback(channel):
            if not self.is_processing:
                self.is_processing = True
                print("按钮触发！开始人脸识别...")
                self.callback_func()
                time.sleep(2)  # 防止重复触发
                self.is_processing = False
        
        GPIO.add_event_detect(pin, GPIO.FALLING, 
                             callback=button_callback, 
                             bouncetime=300)
    
    def setup_web_trigger(self, port=5000):
        """设置Web界面触发"""
        app = Flask(__name__)
        
        html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>人脸解锁系统</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                h1 {
                    color: #333;
                    margin-bottom: 30px;
                }
                .unlock-btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 20px 50px;
                    font-size: 20px;
                    border-radius: 50px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .unlock-btn:hover {
                    transform: scale(1.05);
                    box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                }
                .unlock-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .status {
                    margin-top: 20px;
                    font-size: 16px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔓 人脸解锁系统</h1>
                <button id="unlockBtn" class="unlock-btn" onclick="triggerUnlock()">
                    开始识别
                </button>
                <div id="status" class="status"></div>
            </div>
            
            <script>
                function triggerUnlock() {
                    const btn = document.getElementById('unlockBtn');
                    const status = document.getElementById('status');
                    
                    btn.disabled = true;
                    btn.textContent = '识别中...';
                    status.textContent = '正在进行人脸识别...';
                    
                    fetch('/trigger')
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                status.textContent = '✅ ' + data.message;
                            } else {
                                status.textContent = '❌ ' + data.message;
                            }
                            setTimeout(() => {
                                btn.disabled = false;
                                btn.textContent = '开始识别';
                                status.textContent = '';
                            }, 3000);
                        })
                        .catch(error => {
                            status.textContent = '❌ 触发失败';
                            btn.disabled = false;
                            btn.textContent = '开始识别';
                        });
                }
            </script>
        </body>
        </html>
        '''
        
        @app.route('/')
        def index():
            return render_template_string(html_template)
        
        @app.route('/trigger')
        def trigger():
            if not self.is_processing:
                self.is_processing = True
                try:
                    result = self.callback_func()
                    self.is_processing = False
                    return jsonify({
                        'success': result, 
                        'message': '解锁成功！' if result else '识别失败，请重试'
                    })
                except Exception as e:
                    self.is_processing = False
                    return jsonify({'success': False, 'message': str(e)})
            else:
                return jsonify({'success': False, 'message': '正在处理中，请稍后...'})
        
        # 在后台线程运行Flask
        thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port))
        thread.daemon = True
        thread.start()
