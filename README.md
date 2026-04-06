# AULA7 - Classificação de Imagens com YOLO

Projeto de classificação de imagens dos 12 signos do zodíaco chinês utilizando YOLO.

## Estrutura do Projeto

```
├── images/                  # Imagens originais por classe
│   ├── Bird/
│   ├── Boar/
│   ├── Dog/
│   ├── Dragon/
│   ├── Hare/
│   ├── Horse/
│   ├── Monkey/
│   ├── Ox/
│   ├── Ram/
│   ├── Rat/
│   ├── Serpent/
│   └── Tiger/
├── classification/          # Dataset dividido para treino
│   ├── train/              # 70% das imagens
│   ├── test/               # 15% das imagens
│   └── val/                # 15% das imagens
├── runs/                    # Resultados do treinamento
├── augmentation.py          # Script de data augmentation
├── split_images.py          # Script de divisão do dataset
├── yolo26.py                # Script de treinamento YOLO
├── inference.py             # Script de inferência
├── augmentation.ipynb       # Notebook de augmentation
├── split_images.ipynb       # Notebook de split
├── yolo26.ipynb             # Notebook de treinamento
└── requirements.txt         # Dependências
```

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### 1. Data Augmentation

Aplica técnicas de augmentation para aumentar o dataset:

- Rotação aleatória (±25 graus)
- Espelhamento horizontal
- Ajuste de brilho (±20%)
- Ajuste de contraste (±20%)
- Ajuste de saturação (±20%)
- Translação
- Zoom

```bash
python augmentation.py
```

### 2. Split do Dataset

Divide as imagens em train/test/val (70%/15%/15%):

```bash
python split_images.py
```

### 3. Treinamento

Treina o modelo YOLO para classificação:

```bash
python yolo26.py
```

### 4. Inferência

Para fazer predições com o modelo treinado:

```bash
python inference.py
```

## Classes

O modelo classifica 12 signos do zodíaco chinês:

| ID | Classe   |
|----|----------|
| 0  | Bird     |
| 1  | Boar     |
| 2  | Dog      |
| 3  | Dragon   |
| 4  | Hare     |
| 5  | Horse    |
| 6  | Monkey   |
| 7  | Ox       |
| 8  | Ram      |
| 9  | Rat      |
| 10 | Serpent  |
| 11 | Tiger    |

## Métricas

O treinamento gera as seguintes métricas:

- **Top-1 Accuracy**: Acurácia considerando a classe mais provável
- **Top-5 Accuracy**: Acurácia considerando as 5 classes mais prováveis

Os resultados são salvos em `runs/classify/zodiac_classification/`.

## Modelo

- **Arquitetura**: YOLO26n-cls (nano)
- **Tamanho da imagem**: 224x224
- **Épocas**: 100
- **Batch size**: 16

## Requisitos

- Python 3.8+
- Pillow
- ultralytics
