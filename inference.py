"""
Servidor Flask para Inferência de Classificação com YOLO
========================================================

Cria uma página web que utiliza a câmera do dispositivo para
detectar e classificar símbolos do zodíaco chinês em tempo real.
"""

from flask import Flask, render_template, Response, jsonify, request
from ultralytics import YOLO
import cv2
import threading
import numpy as np
import base64

app = Flask(__name__)

# Carrega o modelo treinado
MODEL_PATH = "/Users/carlosnobuaki/synapse/AULA7-Classification/runs/classify/runs/classify/zodiac_classification/weights/best.pt"
model = YOLO(MODEL_PATH)

# Estado global da detecção
detection_state = {
    "class_name": None,
    "confidence": 0.0,
    "detected": False
}

# Lock para thread safety
state_lock = threading.Lock()

# Limiar de confiança para considerar uma detecção válida
CONFIDENCE_THRESHOLD = 0.7

# Câmera global
camera = None


def get_camera():
    """Obtém a instância da câmera."""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera


def release_camera():
    """Libera a câmera."""
    global camera
    if camera is not None:
        camera.release()
        camera = None


def generate_frames():
    """Gera frames da câmera com inferência."""
    global detection_state
    
    cam = get_camera()
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        
        # Faz a inferência
        results = model(frame, verbose=False)
        
        if results and len(results) > 0:
            result = results[0]
            
            if hasattr(result, 'probs') and result.probs is not None:
                probs = result.probs
                top1_idx = probs.top1
                top1_conf = probs.top1conf.item()
                class_name = model.names[top1_idx]
                
                # Atualiza o estado se a confiança for alta
                with state_lock:
                    if top1_conf >= CONFIDENCE_THRESHOLD:
                        detection_state["class_name"] = class_name
                        detection_state["confidence"] = top1_conf
                        detection_state["detected"] = True
                    else:
                        detection_state["detected"] = False
                
                # Desenha informações no frame
                label = f"{class_name}: {top1_conf*100:.1f}%"
                cv2.putText(frame, label, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Barra de confiança
                bar_width = int(300 * top1_conf)
                cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), (0, 255, 0), -1)
                cv2.rectangle(frame, (10, 50), (310, 70), (255, 255, 255), 2)
        
        # Codifica o frame para JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Stream de vídeo."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detection_status')
def detection_status():
    """Retorna o status atual da detecção."""
    with state_lock:
        return jsonify(detection_state)


@app.route('/reset_detection')
def reset_detection():
    """Reseta o estado da detecção."""
    global detection_state
    with state_lock:
        detection_state = {
            "class_name": None,
            "confidence": 0.0,
            "detected": False
        }
    return jsonify({"status": "ok"})


@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Processa um frame enviado pelo celular."""
    global detection_state
    
    try:
        # Recebe o frame em base64
        data = request.json
        image_data = data.get('image', '')
        
        # Remove o prefixo data:image/jpeg;base64, se existir
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decodifica base64 para imagem
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image"}), 400
        
        # Faz a inferência
        results = model(frame, verbose=False)
        
        response_data = {
            "class_name": None,
            "confidence": 0.0,
            "detected": False
        }
        
        if results and len(results) > 0:
            result = results[0]
            
            if hasattr(result, 'probs') and result.probs is not None:
                probs = result.probs
                top1_idx = probs.top1
                top1_conf = probs.top1conf.item()
                class_name = model.names[top1_idx]
                
                response_data["class_name"] = class_name
                response_data["confidence"] = top1_conf
                
                if top1_conf >= CONFIDENCE_THRESHOLD:
                    response_data["detected"] = True
                    
                    # Atualiza estado global também
                    with state_lock:
                        detection_state["class_name"] = class_name
                        detection_state["confidence"] = top1_conf
                        detection_state["detected"] = True
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    import ssl
    
    # Caminho dos certificados SSL
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
    
    # Verifica se os certificados existem
    use_ssl = os.path.exists(cert_path) and os.path.exists(key_path)
    
    print("="*50)
    print("🍥 Servidor Ninjutsu - Detector de Selos 🍥")
    print("="*50)
    print(f"Modelo: {MODEL_PATH}")
    
    if use_ssl:
        print("\nHTTPS habilitado para câmera do celular")
        print("\nNo celular acesse:")
        print("   https://172.18.1.37:6060")
        print("\n⚠️  Aceite o certificado auto-assinado no navegador")
        print("   (Safari: Toque em 'Mostrar Detalhes' → 'visitar este site')")
    else:
        print("\n⚠️  Certificados SSL não encontrados")
        print("   Câmera do celular não funcionará")
    
    print("\nNo computador acesse:")
    print("   http://localhost:6060")
    print("="*50)
    
    try:
        if use_ssl:
            # HTTPS para suportar câmera do celular
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_path, key_path)
            app.run(host='0.0.0.0', port=6060, debug=False, threaded=True, ssl_context=context)
        else:
            app.run(host='0.0.0.0', port=6060, debug=False, threaded=True)
    finally:
        release_camera()

