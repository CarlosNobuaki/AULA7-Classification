"""
Treinamento de Classificação com YOLO
=====================================

Utiliza o modelo YOLO para classificação de imagens.
Dataset estruturado em train/test/val com subpastas por classe.
"""

from ultralytics import YOLO
import os


def train_classification_model(
    data_dir: str,
    model_name: str = "yolo26n-cls.pt",
    epochs: int = 5,
    imgsz: int = 224,
    batch: int = 16,
    project: str = "runs/classify",
    name: str = "zodiac_classification"
):
    """
    Treina um modelo YOLO para classificação de imagens.
    
    Args:
        data_dir: Diretório com as pastas train/test/val
        model_name: Nome do modelo pré-treinado (yolo26n-cls, yolo26s-cls, etc.)
        epochs: Número de épocas de treinamento
        imgsz: Tamanho das imagens (default: 224)
        batch: Tamanho do batch (default: 16)
        project: Pasta do projeto para salvar resultados
        name: Nome do experimento
    
    Returns:
        Resultados do treinamento
    """
    print("="*60)
    print("TREINAMENTO DE CLASSIFICAÇÃO COM YOLO")
    print("="*60)
    print(f"\nDataset: {data_dir}")
    print(f"Modelo: {model_name}")
    print(f"Épocas: {epochs}")
    print(f"Tamanho da imagem: {imgsz}")
    print(f"Batch size: {batch}")
    print("="*60)
    
    # Carrega o modelo pré-treinado para classificação
    model = YOLO(model_name)
    
    # Treina o modelo
    results = model.train(
        data=data_dir,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
        patience=20,          # Early stopping
        save=True,            # Salva checkpoints
        save_period=10,       # Salva a cada 10 épocas
        verbose=True,
        plots=True,           # Gera gráficos
        val=True,             # Valida durante treino
    )
    
    return model, results


def evaluate_model(model, data_dir: str):
    """
    Avalia o modelo e exibe todas as métricas.
    
    Args:
        model: Modelo YOLO treinado
        data_dir: Diretório do dataset
    """
    print("\n" + "="*60)
    print("AVALIAÇÃO DO MODELO")
    print("="*60)
    
    # Avalia no conjunto de validação
    val_results = model.val(data=data_dir, split='val')
    
    print("\n--- Métricas de Validação ---")
    print(f"Top-1 Accuracy: {val_results.top1:.4f} ({val_results.top1*100:.2f}%)")
    print(f"Top-5 Accuracy: {val_results.top5:.4f} ({val_results.top5*100:.2f}%)")
    
    # Avalia no conjunto de teste
    test_results = model.val(data=data_dir, split='test')
    
    print("\n--- Métricas de Teste ---")
    print(f"Top-1 Accuracy: {test_results.top1:.4f} ({test_results.top1*100:.2f}%)")
    print(f"Top-5 Accuracy: {test_results.top5:.4f} ({test_results.top5*100:.2f}%)")
    
    return val_results, test_results


def print_final_metrics(model, train_results, val_results, test_results):
    """
    Exibe um resumo completo de todas as métricas.
    """
    print("\n" + "="*60)
    print("RESUMO FINAL DO TREINAMENTO")
    print("="*60)
    
    print("\n📊 MÉTRICAS DE TREINAMENTO:")
    print("-"*40)
    if hasattr(train_results, 'results_dict'):
        for key, value in train_results.results_dict.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.4f}")
    
    print("\n📊 MÉTRICAS DE VALIDAÇÃO:")
    print("-"*40)
    print(f"  Top-1 Accuracy: {val_results.top1:.4f} ({val_results.top1*100:.2f}%)")
    print(f"  Top-5 Accuracy: {val_results.top5:.4f} ({val_results.top5*100:.2f}%)")
    
    print("\n📊 MÉTRICAS DE TESTE:")
    print("-"*40)
    print(f"  Top-1 Accuracy: {test_results.top1:.4f} ({test_results.top1*100:.2f}%)")
    print(f"  Top-5 Accuracy: {test_results.top5:.4f} ({test_results.top5*100:.2f}%)")
    
    print("\n📁 CLASSES DO MODELO:")
    print("-"*40)
    if hasattr(model, 'names'):
        for idx, name in model.names.items():
            print(f"  {idx}: {name}")
    
    print("\n💾 MODELO SALVO EM:")
    print("-"*40)
    print(f"  Melhor modelo: runs/classify/zodiac_classification/weights/best.pt")
    print(f"  Último modelo: runs/classify/zodiac_classification/weights/last.pt")
    
    print("\n" + "="*60)
    print("TREINAMENTO CONCLUÍDO!")
    print("="*60)


if __name__ == "__main__":
    # Diretório do dataset
    data_dir = "/Users/carlosnobuaki/synapse/AULA7-Classification/classification"
    
    # Treina o modelo
    model, train_results = train_classification_model(
        data_dir=data_dir,
        model_name="yolo26n-cls.pt",  # Modelo nano para classificação
        epochs=100,
        imgsz=224,
        batch=16,
        project="runs/classify",
        name="Naruto_classification"
    )
    
    # Avalia o modelo
    val_results, test_results = evaluate_model(model, data_dir)
    
    # Exibe todas as métricas
    print_final_metrics(model, train_results, val_results, test_results)
