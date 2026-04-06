"""
Split de Imagens para Classificação
====================================

Divide as imagens de cada classe em:
- Train: 70%
- Test: 15%
- Val: 15%

Cada classe (subpasta) é processada separadamente,
mantendo a estrutura de pastas por classe.
"""

import os
import shutil
import random
from pathlib import Path


def split_images(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.70,
    test_ratio: float = 0.15,
    val_ratio: float = 0.15,
    seed: int = 42
):
    """
    Divide as imagens de cada classe em train/test/val.
    
    Args:
        source_dir: Diretório com as subpastas de classes
        output_dir: Diretório base de saída (com train/test/val)
        train_ratio: Proporção para treino (default: 70%)
        test_ratio: Proporção para teste (default: 15%)
        val_ratio: Proporção para validação (default: 15%)
        seed: Seed para reprodutibilidade
    """
    # Verifica se as proporções somam 1
    assert abs(train_ratio + test_ratio + val_ratio - 1.0) < 0.001, \
        "As proporções devem somar 1.0"
    
    random.seed(seed)
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Extensões de imagem suportadas
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
    # Cria as pastas de saída
    train_dir = output_path / 'train'
    test_dir = output_path / 'test'
    val_dir = output_path / 'val'
    
    # Estatísticas
    stats = {
        'total': 0,
        'train': 0,
        'test': 0,
        'val': 0,
        'classes': {}
    }
    
    # Processa cada classe (subpasta)
    for class_dir in sorted(source_path.iterdir()):
        if not class_dir.is_dir():
            continue
        
        class_name = class_dir.name
        print(f"\nProcessando classe: {class_name}")
        
        # Lista todas as imagens da classe
        images = [
            f for f in class_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not images:
            print(f"  Nenhuma imagem encontrada!")
            continue
        
        # Embaralha as imagens
        random.shuffle(images)
        
        # Calcula os índices de divisão
        total = len(images)
        train_end = int(total * train_ratio)
        test_end = train_end + int(total * test_ratio)
        
        # Divide as imagens
        train_images = images[:train_end]
        test_images = images[train_end:test_end]
        val_images = images[test_end:]
        
        # Cria as pastas de destino para a classe
        (train_dir / class_name).mkdir(parents=True, exist_ok=True)
        (test_dir / class_name).mkdir(parents=True, exist_ok=True)
        (val_dir / class_name).mkdir(parents=True, exist_ok=True)
        
        # Copia as imagens para as respectivas pastas
        for img in train_images:
            shutil.copy2(img, train_dir / class_name / img.name)
        
        for img in test_images:
            shutil.copy2(img, test_dir / class_name / img.name)
        
        for img in val_images:
            shutil.copy2(img, val_dir / class_name / img.name)
        
        # Atualiza estatísticas
        stats['total'] += total
        stats['train'] += len(train_images)
        stats['test'] += len(test_images)
        stats['val'] += len(val_images)
        stats['classes'][class_name] = {
            'total': total,
            'train': len(train_images),
            'test': len(test_images),
            'val': len(val_images)
        }
        
        print(f"  Total: {total} | Train: {len(train_images)} | Test: {len(test_images)} | Val: {len(val_images)}")
    
    # Exibe resumo final
    print(f"\n{'='*60}")
    print("RESUMO DO SPLIT")
    print(f"{'='*60}")
    print(f"Total de imagens: {stats['total']}")
    print(f"Train: {stats['train']} ({stats['train']/stats['total']*100:.1f}%)")
    print(f"Test:  {stats['test']} ({stats['test']/stats['total']*100:.1f}%)")
    print(f"Val:   {stats['val']} ({stats['val']/stats['total']*100:.1f}%)")
    print(f"\nClasses processadas: {len(stats['classes'])}")
    print(f"{'='*60}")
    
    return stats


if __name__ == "__main__":
    # Diretórios
    source_dir = "/Users/carlosnobuaki/synapse/AULA7-Classification/images"
    output_dir = "/Users/carlosnobuaki/synapse/AULA7-Classification/classification"
    
    # Executa o split
    split_images(
        source_dir=source_dir,
        output_dir=output_dir,
        train_ratio=0.70,  # 70% para treino
        test_ratio=0.15,   # 15% para teste
        val_ratio=0.15     # 15% para validação
    )
