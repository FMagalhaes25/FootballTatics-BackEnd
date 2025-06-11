import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import joblib

def load_training_data(data_path):
    """Carrega os dados de treinamento e teste (não normalizados) dos arquivos CSV."""
    print(f"Carregando dados de: {data_path}")
    X_train = pd.read_csv(data_path / 'X_train.csv')
    y_train = pd.read_csv(data_path / 'y_train.csv')
    X_test = pd.read_csv(data_path / 'X_test.csv')
    y_test = pd.read_csv(data_path / 'y_test.csv')
    return X_train.values, y_train.values, X_test.values, y_test.values

def build_model(input_shape, output_shape):
    """Constrói o modelo Keras sequencial."""
    print("Construindo o modelo...")
    model = Sequential([
        Dense(128, activation='elu', input_dim=input_shape),
        BatchNormalization(),
        Dropout(0.2),
        Dense(256, activation='elu'),
        BatchNormalization(),
        Dropout(0.2),
        Dense(128, activation='elu'),
        BatchNormalization(),
        Dropout(0.1),
        Dense(output_shape, activation='sigmoid')
    ])
    return model

def fit_and_save_scaler(X_train_data, save_path):
    """
    Ajusta um MinMaxScaler nos dados de treino, salva o objeto em um arquivo .pkl
    e retorna o scaler ajustado.
    """
    print(f"Ajustando e salvando o scaler em: {save_path.absolute()}")
    scaler = MinMaxScaler()
    scaler.fit(X_train_data)
    joblib.dump(scaler, save_path)
    return scaler

if __name__ == '__main__':
    # --- AJUSTE DE CAMINHOS (FORMA ROBUSTA) ---
    # Pega o caminho absoluto do script atual (train_model.py)
    script_path = Path(__file__).resolve()
    # O diretório 'deep_learning_model' é o pai do script
    DEEP_LEARNING_DIR = script_path.parent
    # Define os outros caminhos a partir deste
    DATA_PATH = DEEP_LEARNING_DIR / 'data' / 'training_data'
    MODEL_SAVE_PATH = DEEP_LEARNING_DIR / 'models'
    
    print(f"Diretório do projeto de Deep Learning: {DEEP_LEARNING_DIR}")
    print(f"Caminho para os dados de treino: {DATA_PATH}")
    print(f"Caminho para salvar os modelos: {MODEL_SAVE_PATH}")
    
    MODEL_SAVE_PATH.mkdir(exist_ok=True)
    
    # --- NOMES DE ARQUIVOS PARA V12 ---
    model_version = 'v12'
    model_filename = f'modelspi2025_{model_version}.h5'
    history_filename = f'training_history_{model_version}.csv'
    scaler_filename = f'scaler_{model_version}.pkl'

    # 1. Carrega os dados (não normalizados)
    try:
        X_train, y_train, X_test, y_test = load_training_data(DATA_PATH)
    except FileNotFoundError:
        print(f"Erro: Arquivos de dados não encontrados em '{DATA_PATH}'.")
        exit()

    # 2. Ajusta, salva e aplica o Scaler
    scaler_save_path = DATA_PATH / scaler_filename
    scaler = fit_and_save_scaler(X_train, scaler_save_path)
    
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 3. Constrói o modelo
    input_features = X_train_scaled.shape[1]
    output_classes = y_train.shape[1]
    model = build_model(input_shape=input_features, output_shape=output_classes)

    # 4. Compila o modelo
    model.compile(
        optimizer=tf.keras.optimizers.Nadam(learning_rate=0.0007),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    model.summary()

    # 5. Define Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=20, verbose=1, mode='min', restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, verbose=1, min_lr=1e-6)

    # 6. Treina o modelo
    print("\n--- INICIANDO TREINAMENTO DO MODELO (v12) ---")
    history = model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=64,
        validation_data=(X_test_scaled, y_test),
        callbacks=[early_stopping, reduce_lr]
    )
    print("--- TREINAMENTO CONCLUÍDO ---\n")

    # 7. Salva o modelo, histórico e scaler
    model_file_path = MODEL_SAVE_PATH / model_filename
    history_file_path = DATA_PATH / history_filename

    print(f"Salvando modelo treinado em: {model_file_path.absolute()}")
    model.save(model_file_path)

    print(f"Salvando histórico de treino em: {history_file_path.absolute()}")
    pd.DataFrame(history.history).to_csv(history_file_path, index=False)