let isDetected = false;
let isMobileMode = false;
let mobileVideoStream = null;
let captureInterval = null;

// Mapeamento dos selos de ninjutsu (Zodiaco)
const sealData = {
    'Rat':     { kanji: '子', japanese: 'Ne (子)', romaji: 'Nezumi' },
    'Ox':      { kanji: '丑', japanese: 'Ushi (丑)', romaji: 'Ushi' },
    'Tiger':   { kanji: '寅', japanese: 'Tora (寅)', romaji: 'Tora' },
    'Hare':    { kanji: '卯', japanese: 'U (卯)', romaji: 'Usagi' },
    'Dragon':  { kanji: '辰', japanese: 'Tatsu (辰)', romaji: 'Tatsu' },
    'Serpent': { kanji: '巳', japanese: 'Mi (巳)', romaji: 'Hebi' },
    'Horse':   { kanji: '午', japanese: 'Uma (午)', romaji: 'Uma' },
    'Ram':     { kanji: '未', japanese: 'Hitsuji (未)', romaji: 'Hitsuji' },
    'Monkey':  { kanji: '申', japanese: 'Saru (申)', romaji: 'Saru' },
    'Bird':    { kanji: '酉', japanese: 'Tori (酉)', romaji: 'Tori' },
    'Dog':     { kanji: '戌', japanese: 'Inu (戌)', romaji: 'Inu' },
    'Boar':    { kanji: '亥', japanese: 'I (亥)', romaji: 'Inoshishi' }
};

// Detecta se o acesso é remoto (celular)
function isRemoteAccess() {
    const hostname = window.location.hostname;
    // Se não for localhost ou 127.0.0.1, é acesso remoto (celular)
    return hostname !== 'localhost' && hostname !== '127.0.0.1';
}

// Inicializa o modo correto
async function initCamera() {
    const serverVideo = document.getElementById('serverVideo');
    const mobileVideo = document.getElementById('mobileVideo');
    const videoLabel = document.getElementById('videoLabel');
    
    if (isRemoteAccess()) {
        // Modo Mobile: usar câmera do celular
        isMobileMode = true;
        serverVideo.style.display = 'none';
        mobileVideo.style.display = 'block';
        videoLabel.textContent = '📱 Câmera do Celular Ativada 📱';
        
        try {
            // Solicita acesso à câmera traseira
            const constraints = {
                video: {
                    facingMode: { ideal: 'environment' },
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            };
            
            mobileVideoStream = await navigator.mediaDevices.getUserMedia(constraints);
            mobileVideo.srcObject = mobileVideoStream;
            
            // Inicia captura e envio de frames
            startMobileCapture();
            
            console.log('📱 Modo celular ativado');
        } catch (err) {
            console.error('Erro ao acessar câmera:', err);
            videoLabel.textContent = '❌ Erro ao acessar câmera. Permita o acesso. ❌';
        }
    } else {
        // Modo Desktop: usar webcam do servidor
        isMobileMode = false;
        serverVideo.style.display = 'block';
        mobileVideo.style.display = 'none';
        videoLabel.textContent = '🔥 Faça o selo com suas mãos 🔥';
        
        // Usa o modo tradicional de polling
        setInterval(checkDetectionDesktop, 500);
        
        console.log('💻 Modo desktop ativado');
    }
}

// Captura frames do celular e envia para o servidor
function startMobileCapture() {
    const video = document.getElementById('mobileVideo');
    const canvas = document.getElementById('captureCanvas');
    const ctx = canvas.getContext('2d');
    
    captureInterval = setInterval(async () => {
        if (isDetected) return;
        
        // Configura canvas com tamanho do vídeo
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        // Desenha frame atual no canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Converte para base64 JPEG
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        try {
            // Envia para o servidor processar
            const response = await fetch('/process_frame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const data = await response.json();
            
            if (data.detected && data.confidence >= 0.7) {
                showDetection(data.class_name, data.confidence);
            }
        } catch (err) {
            console.error('Erro ao processar frame:', err);
        }
    }, 500); // Processa a cada 500ms
}

// Verifica detecção no modo desktop
function checkDetectionDesktop() {
    if (isDetected) return;
    
    fetch('/detection_status')
        .then(response => response.json())
        .then(data => {
            if (data.detected && data.confidence >= 0.7) {
                showDetection(data.class_name, data.confidence);
            }
        });
}

function showDetection(className, confidence) {
    isDetected = true;
    
    const seal = sealData[className] || { kanji: '?', japanese: className, romaji: '' };
    
    document.getElementById('videoContainer').classList.add('shrink');
    document.getElementById('detectionCard').classList.add('show');
    document.getElementById('sealSymbol').textContent = seal.kanji;
    document.getElementById('className').textContent = className;
    document.getElementById('japaneseName').textContent = seal.japanese;
    document.getElementById('confidenceText').textContent = `Chakra: ${(confidence * 100).toFixed(1)}%`;
    document.getElementById('confidenceFill').style.width = `${confidence * 100}%`;
}

function resetDetection() {
    fetch('/reset_detection')
        .then(() => {
            isDetected = false;
            document.getElementById('videoContainer').classList.remove('shrink');
            document.getElementById('detectionCard').classList.remove('show');
        });
}

// Inicializa quando a página carregar
document.addEventListener('DOMContentLoaded', initCamera);
