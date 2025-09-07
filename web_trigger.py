#!/usr/bin/env python3
"""
Web触发服务 - 支持手动触发人脸识别
"""
from flask import Flask, render_template, request, jsonify
import json
import threading
import time
from core.main import FaceUnlockSystem

app = Flask(__name__)
face_system = None
is_processing = False

def init_face_system():
    """初始化人脸识别系统"""
    global face_system
    try:
        face_system = FaceUnlockSystem()
        print("✓ 人脸识别系统初始化完成")
        return True
    except Exception as e:
        print(f"✗ 系统初始化失败: {e}")
        return False

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>人脸识别解锁系统</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
                background: linear-gradient(135deg, #e3f2fd 0%%, #f3e5f5 50%%, #ffffff 100%%);
                min-height: 100vh;
                padding: 15px;
                color: #2c3e50;
            }
            
            .container {
                max-width: 420px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 24px;
                padding: 25px 20px;
                box-shadow: 0 10px 40px rgba(33, 150, 243, 0.15);
                border: 1px solid #e1f5fe;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            h1 {
                font-size: 24px;
                font-weight: 600;
                color: #1976d2;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            .subtitle {
                font-size: 14px;
                color: #7b1fa2;
                opacity: 0.8;
            }
            
            .status-panel {
                background: linear-gradient(135deg, #e3f2fd 0%%, #f8bbd9 100%%);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 25px;
                border: 1px solid #bbdefb;
            }
            
            .status-title {
                font-size: 16px;
                font-weight: 600;
                color: #1565c0;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
            
            .status-item {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 12px;
                padding: 12px;
                text-align: center;
                border: 1px solid rgba(25, 118, 210, 0.1);
            }
            
            .status-label {
                font-size: 12px;
                color: #7b1fa2;
                margin-bottom: 4px;
                font-weight: 500;
            }
            
            .status-value {
                font-size: 14px;
                font-weight: 600;
                color: #1976d2;
            }
            
            .button-container {
                display: flex;
                flex-direction: column;
                gap: 15px;
                margin-bottom: 25px;
            }
            
            button {
                width: 100%%;
                height: 60px;
                font-size: 16px;
                font-weight: 600;
                border: none;
                border-radius: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                touch-action: manipulation;
                -webkit-tap-highlight-color: transparent;
                font-family: inherit;
            }
            
            .primary-btn {
                background: linear-gradient(135deg, #2196f3 0%%, #9c27b0 100%%);
                color: white;
                height: 65px;
                font-size: 18px;
                box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
            }
            
            .secondary-btn {
                background: #ffffff;
                color: #1976d2;
                border: 2px solid #e3f2fd;
                box-shadow: 0 4px 15px rgba(33, 150, 243, 0.1);
            }
            
            .refresh-btn {
                background: linear-gradient(135deg, #9c27b0 0%%, #e91e63 100%%);
                color: white;
                box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
            }
            
            button:disabled {
                background: #ffffff !important;
                color: #9e9e9e !important;
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            }
            
            #result {
                border-radius: 16px;
                padding: 20px;
                font-size: 15px;
                line-height: 1.6;
                word-wrap: break-word;
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                color: #495057;
                min-height: 60px;
            }
            
            .success { 
                background: #e8f5e8 !important;
                border-color: #4caf50 !important;
                color: #2e7d32 !important;
            }
            
            .error { 
                background: #ffebee !important;
                border-color: #f44336 !important;
                color: #c62828 !important;
            }
            
            .processing { 
                background: #fff3e0 !important;
                border-color: #ff9800 !important;
                color: #ef6c00 !important;
            }
            
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #e3f2fd;
                border-radius: 50%%;
                border-top-color: #2196f3;
                animation: spin 1s ease-in-out infinite;
                margin-right: 8px;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 人脸识别解锁系统</h1>
                <div class="subtitle">智能安全，便捷解锁</div>
            </div>
            
            <div class="status-panel">
                <div class="status-title">
                    📊 系统状态
                </div>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">系统状态</div>
                        <div class="status-value" id="systemStatus">检查中...</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">处理状态</div>
                        <div class="status-value" id="processStatus">检查中...</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Mac服务</div>
                        <div class="status-value" id="macStatus">检查中...</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">最后更新</div>
                        <div class="status-value" id="lastUpdate">-</div>
                    </div>
                </div>
            </div>
            
            <div class="button-container">
                <button onclick="triggerUnlock()" id="unlockBtn" class="primary-btn">
                    🔓 触发人脸识别解锁
                </button>
                
                <button onclick="refreshStatus()" id="refreshBtn" class="refresh-btn">
                    🔄 刷新状态
                </button>
                
                <button onclick="testMacService()" id="testMacBtn" class="secondary-btn">
                    🖥 测试Mac服务
                </button>
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            function showResult(message, className) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>' + message + '</p>';
                resultDiv.className = className || '';
            }
            
            function updateStatusDisplay(data) {
                document.getElementById('systemStatus').textContent = 
                    data.system_initialized ? '✅ 正常' : '❌ 异常';
                document.getElementById('processStatus').textContent = 
                    data.is_processing ? '🔄 处理中' : '✅ 空闲';
                document.getElementById('lastUpdate').textContent = 
                    new Date().toLocaleTimeString('zh-CN', {hour12: false});
            }
            
            function updateMacStatus(success) {
                document.getElementById('macStatus').textContent = 
                    success ? '✅ 连接正常' : '❌ 连接异常';
            }
            
            function triggerUnlock() {
                const btn = document.getElementById('unlockBtn');
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner"></span>识别中...';
                showResult('🔄 正在进行人脸识别，请稍候...', 'processing');
                
                fetch('/trigger_unlock', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showResult('✅ ' + data.message, 'success');
                        } else {
                            showResult('❌ ' + data.message, 'error');
                        }
                        setTimeout(checkStatus, 1000);
                    })
                    .catch(error => {
                        showResult('❌ 网络请求失败: ' + error, 'error');
                    })
                    .finally(() => {
                        btn.disabled = false;
                        btn.innerHTML = '🔓 触发人脸识别解锁';
                    });
            }
            
            function checkStatus() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        updateStatusDisplay(data);
                    })
                    .catch(error => {
                        console.error('状态检查失败:', error);
                    });
            }
            
            function testMacService() {
                const btn = document.getElementById('testMacBtn');
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner"></span>测试中...';
                showResult('🔄 正在测试Mac服务连接...', 'processing');
                
                fetch('/test_mac')
                    .then(response => response.json())
                    .then(data => {
                        updateMacStatus(data.success);
                        if (data.success) {
                            showResult('✅ Mac服务连接正常', 'success');
                        } else {
                            showResult('❌ Mac服务异常: ' + data.message, 'error');
                        }
                    })
                    .catch(error => {
                        updateMacStatus(false);
                        showResult('❌ 测试失败: ' + error, 'error');
                    })
                    .finally(() => {
                        btn.disabled = false;
                        btn.innerHTML = '🖥 测试Mac服务';
                    });
            }
            
            function refreshStatus() {
                const btn = document.getElementById('refreshBtn');
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner"></span>刷新中...';
                showResult('🔄 正在刷新系统状态...', 'processing');
                
                Promise.all([
                    fetch('/status').then(r => r.json()),
                    fetch('/test_mac').then(r => r.json())
                ])
                .then(([statusData, macData]) => {
                    updateStatusDisplay(statusData);
                    updateMacStatus(macData.success);
                    showResult('✅ 状态刷新完成', 'success');
                })
                .catch(error => {
                    showResult('❌ 刷新失败: ' + error, 'error');
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.innerHTML = '🔄 刷新状态';
                });
            }
            
            // 页面加载时自动检查状态
            window.addEventListener('load', function() {
                showResult('🚀 正在初始化系统状态...', 'processing');
                setTimeout(() => {
                    refreshStatus();
                    setInterval(checkStatus, 30000); // 每30秒自动刷新
                }, 500);
            });
        </script>
    </body>
    </html>
    """

@app.route('/trigger_unlock', methods=['POST'])
def trigger_unlock():
    """触发人脸识别解锁"""
    global is_processing, face_system
    
    if is_processing:
        return jsonify({
            'success': False,
            'message': '系统正在处理中，请稍后再试'
        })
    
    if not face_system:
        return jsonify({
            'success': False,
            'message': '系统未初始化'
        })
    
    is_processing = True
    
    try:
        # 在新线程中执行识别
        def run_recognition():
            global is_processing
            try:
                result = face_system.run_once()
                return result
            finally:
                is_processing = False
        
        # 启动识别线程
        thread = threading.Thread(target=run_recognition)
        thread.start()
        thread.join(timeout=30)  # 30秒超时
        
        if thread.is_alive():
            return jsonify({
                'success': False,
                'message': '识别超时'
            })
        
        return jsonify({
            'success': True,
            'message': '人脸识别完成，请查看终端输出'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'识别失败: {str(e)}'
        })
    finally:
        is_processing = False

@app.route('/status')
def status():
    """系统状态"""
    global face_system, is_processing
    
    return jsonify({
        'system_initialized': face_system is not None,
        'is_processing': is_processing,
        'stats': face_system.stats if face_system else None
    })

@app.route('/test_mac')
def test_mac():
    """测试Mac服务"""
    global face_system
    
    if not face_system:
        return jsonify({
            'success': False,
            'message': '系统未初始化'
        })
    
    try:
        result = face_system.check_mac_service()
        return jsonify({
            'success': result,
            'message': 'Mac服务正常' if result else 'Mac服务异常'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/health')
def health_check():
    """健康检查接口"""
    global face_system, is_processing
    
    return jsonify({
        'status': 'healthy',
        'service': 'face-unlock-web',
        'timestamp': time.time(),
        'system_initialized': face_system is not None,
        'is_processing': is_processing,
        'version': '1.0'
    })

if __name__ == '__main__':
    print("="*50)
    print("人脸识别Web触发服务")
    print("="*50)
    
    # 初始化系统
    if init_face_system():
        print("\n🌐 启动Web服务...")
        print("访问地址: http://树莓派IP:5000")
        print("按 Ctrl+C 停止服务\n")
        
        try:
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n👋 服务已停止")
    else:
        print("✗ 无法启动服务")