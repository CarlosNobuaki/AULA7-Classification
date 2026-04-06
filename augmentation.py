"""
Data Augmentation para Imagens de Classificação
================================================

Técnicas de Augmentation Utilizadas:
------------------------------------
1. Rotação aleatória (máximo ±25 graus)
2. Espelhamento horizontal (flip horizontal)
3. Ajuste de brilho (±20%)
4. Ajuste de contraste (±20%)
5. Ajuste de saturação (±20%)
6. Translação (deslocamento horizontal/vertical)
7. Zoom leve (crop e resize)

Cada imagem é replicada 10 vezes com combinações aleatórias dessas técnicas.
"""

import os
import random
from PIL import Image, ImageEnhance, ImageOps
from pathlib import Path


def random_rotation(image, max_angle=25):
    """Rotaciona a imagem aleatoriamente até max_angle graus."""
    angle = random.uniform(-max_angle, max_angle)
    return image.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))


def horizontal_flip(image):
    """Espelhamento horizontal."""
    return ImageOps.mirror(image)


def adjust_brightness(image, factor_range=(0.8, 1.2)):
    """Ajusta o brilho da imagem aleatoriamente."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def adjust_contrast(image, factor_range=(0.8, 1.2)):
    """Ajusta o contraste da imagem aleatoriamente."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def adjust_saturation(image, factor_range=(0.8, 1.2)):
    """Ajusta a saturação da imagem aleatoriamente."""
    factor = random.uniform(*factor_range)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)


def random_translation(image, max_shift_ratio=0.1):
    """Translada a imagem aleatoriamente."""
    width, height = image.size
    max_shift_x = int(width * max_shift_ratio)
    max_shift_y = int(height * max_shift_ratio)
    shift_x = random.randint(-max_shift_x, max_shift_x)
    shift_y = random.randint(-max_shift_y, max_shift_y)
    
    # Usa affine transform para transladar
    return image.transform(
        image.size,
        Image.AFFINE,
        (1, 0, shift_x, 0, 1, shift_y),
        resample=Image.BICUBIC,
        fillcolor=(255, 255, 255)
    )


def random_zoom(image, zoom_range=(0.85, 1.0)):
    """Aplica zoom aleatório (crop central e resize)."""
    width, height = image.size
    zoom_factor = random.uniform(*zoom_range)
    
    # Calcula nova área de crop
    new_width = int(width * zoom_factor)
    new_height = int(height * zoom_factor)
    
    # Calcula posição do crop (centralizado com variação aleatória)
    left = random.randint(0, width - new_width)
    top = random.randint(0, height - new_height)
    
    # Crop e resize para tamanho original
    cropped = image.crop((left, top, left + new_width, top + new_height))
    return cropped.resize((width, height), Image.BICUBIC)


def apply_augmentation(image):
    """
    Aplica uma combinação aleatória de técnicas de augmentation.
    Retorna a imagem aumentada.
    """
    # Converte para RGB se necessário
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    augmented = image.copy()
    
    # Lista de augmentations com suas probabilidades
    augmentations = [
        (random_rotation, 0.7),          # 70% chance de rotação
        (horizontal_flip, 0.5),          # 50% chance de flip horizontal
        (adjust_brightness, 0.6),        # 60% chance de ajuste de brilho
        (adjust_contrast, 0.6),          # 60% chance de ajuste de contraste
        (adjust_saturation, 0.5),        # 50% chance de ajuste de saturação
        (random_translation, 0.4),       # 40% chance de translação
        (random_zoom, 0.4),              # 40% chance de zoom
    ]
    
    # Aplica cada augmentation com sua probabilidade
    for aug_func, probability in augmentations:
        if random.random() < probability:
            augmented = aug_func(augmented)
    
    return augmented


def augment_images(input_dir, output_dir=None, num_augmentations=10):
    """
    Processa todas as imagens nas subpastas do diretório de entrada,
    gerando versões aumentadas.
    
    Args:
        input_dir: Diretório contendo as pastas de categorias com imagens
        output_dir: Diretório de saída (se None, salva no mesmo local)
        num_augmentations: Número de versões aumentadas por imagem
    """
    input_path = Path(input_dir)
    
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path
    
    # Extensões de imagem suportadas
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
    # Contador de estatísticas
    total_original = 0
    total_augmented = 0
    
    # Percorre todas as subpastas (categorias)
    for category_dir in input_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        print(f"\nProcessando categoria: {category_name}")
        
        # Cria diretório de saída para a categoria
        output_category_dir = output_path / category_name
        output_category_dir.mkdir(parents=True, exist_ok=True)
        
        # Processa cada imagem na categoria
        for image_file in category_dir.iterdir():
            if image_file.suffix.lower() not in image_extensions:
                continue
            
            total_original += 1
            print(f"  Processando: {image_file.name}")
            
            try:
                # Carrega a imagem original
                with Image.open(image_file) as img:
                    # Gera as versões aumentadas
                    for i in range(num_augmentations):
                        augmented = apply_augmentation(img)
                        
                        # Nome do arquivo aumentado
                        stem = image_file.stem
                        suffix = image_file.suffix
                        aug_filename = f"{stem}_aug_{i+1:02d}{suffix}"
                        aug_path = output_category_dir / aug_filename
                        
                        # Salva a imagem aumentada
                        augmented.save(aug_path, quality=95)
                        total_augmented += 1
                        
            except Exception as e:
                print(f"    Erro ao processar {image_file.name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Augmentation concluído!")
    print(f"Imagens originais processadas: {total_original}")
    print(f"Imagens aumentadas geradas: {total_augmented}")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Diretório com as imagens originais
    images_dir = "/Users/carlosnobuaki/synapse/AULA7-Classification/images"
    
    # Executa o augmentation
    # As imagens aumentadas serão salvas nas mesmas pastas das originais
    augment_images(
        input_dir=images_dir,
        output_dir=None,  # Salva no mesmo diretório
        num_augmentations=10  # 10 versões por imagem
    )
