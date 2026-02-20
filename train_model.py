import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input  # 🆕 CRITICAL
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.utils.class_weight import compute_class_weight


# CONFIG

IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 30
DATASET_PATH = "dataset"


# 🆕 DATA GENERATORS WITH PROPER PREPROCESSING

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,  # 🎯 EfficientNet-specific
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.9, 1.1],
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,  # 🎯 EfficientNet-specific
    validation_split=0.2
)

print("🔄 Loading training data...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
    seed=42
)

print("🔄 Loading validation data...")
val_generator = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
    seed=42
)

NUM_CLASSES = train_generator.num_classes
print(f"\n✅ Found {NUM_CLASSES} classes:")
# SAVE CLASS INDICES (IMPORTANT)

import json

with open("backend/model/class_indices.json", "w") as f:
    json.dump(train_generator.class_indices, f)

print("✅ class_indices.json saved")

for class_name, class_idx in train_generator.class_indices.items():
    print(f"   {class_idx}: {class_name}")

# ======================
# CLASS IMBALANCE HANDLING
# ======================
class_counts = np.bincount(train_generator.classes)
print(f"\n📊 Original class distribution:")
for i, count in enumerate(class_counts):
    print(f"   Class {i}: {count} images")

# Calculate class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)
class_weight_dict = dict(enumerate(class_weights))

print(f"\n⚖️ Class weights (higher = more important):")
for class_idx, weight in class_weight_dict.items():
    if weight > 2.0:
        print(f"   🔴 Class {class_idx}: {weight:.2f} (minority)")
    elif weight < 0.8:
        print(f"   🔵 Class {class_idx}: {weight:.2f} (majority)")
    else:
        print(f"   ⚪ Class {class_idx}: {weight:.2f}")



# MODEL
def create_model(learning_rate=0.001):
    base_model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    base_model.trainable = False

    x = base_model.output
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

    model = models.Model(inputs=base_model.input, outputs=outputs)

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model, base_model


model, base_model = create_model(learning_rate=0.001)
model.summary()

# CALLBACKS

os.makedirs("backend/model", exist_ok=True)

checkpoint = ModelCheckpoint(
    "backend/model/plant_disease_model_best.keras",
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=2,
    min_lr=1e-6,
    verbose=1
)


# PHASE 1: TRAIN TOP LAYERS

print("\n" + "=" * 60)
print("🚀 PHASE 1: Training top layers (backbone frozen)")
print("=" * 60)

history1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    callbacks=[checkpoint, early_stop, reduce_lr],
    class_weight=class_weight_dict,
    verbose=1
)

# Check Phase 1 results
val_acc_phase1 = history1.history['val_accuracy'][-1]
print(f"\n📊 Phase 1 final validation accuracy: {val_acc_phase1:.4f}")


# PHASE 2: FINE-TUNE

print("\n" + "=" * 60)
print("🔧 PHASE 2: Fine-tuning backbone")
print("=" * 60)

# Unfreeze base model
base_model.trainable = True

# Freeze first 100 layers
for layer in base_model.layers[:100]:
    layer.trainable = False

# Adjust learning rate based on Phase 1 performance
if val_acc_phase1 < 0.55:
    fine_tune_lr = 5e-6
    print(f"⚠️  Slow start detected, using extra low LR: {fine_tune_lr}")
else:
    fine_tune_lr = 1e-5
    print(f"✅ Good start, using standard LR: {fine_tune_lr}")

model.compile(
    optimizer=Adam(learning_rate=fine_tune_lr),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    initial_epoch=len(history1.epoch),
    callbacks=[checkpoint, early_stop, reduce_lr],
    class_weight=class_weight_dict,
    verbose=1
)


# COMBINE HISTORIES

history = {}
all_metrics = set(history1.history.keys()) | set(history2.history.keys())

for key in all_metrics:
    if key in history1.history and key in history2.history:
        history[key] = history1.history[key] + history2.history[key]
    elif key in history1.history:
        history[key] = history1.history[key] + [None] * len(history2.epoch)
    else:
        history[key] = [None] * len(history1.epoch) + history2.history[key]

# ======================
# VISUALIZE
# ======================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Accuracy
axes[0].plot(history['accuracy'], label='Train', linewidth=2, color='blue')
axes[0].plot(history['val_accuracy'], label='Validation', linewidth=2, color='orange')
axes[0].axvline(x=len(history1.epoch) - 1, color='red', linestyle='--', alpha=0.7, label='Fine-tuning start')
axes[0].set_title(f'Model Accuracy (Final: {history["val_accuracy"][-1]:.2f})', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Accuracy')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim([0, 1])

# Loss
axes[1].plot(history['loss'], label='Train', linewidth=2, color='blue')
axes[1].plot(history['val_loss'], label='Validation', linewidth=2, color='orange')
axes[1].axvline(x=len(history1.epoch) - 1, color='red', linestyle='--', alpha=0.7, label='Fine-tuning start')
axes[1].set_title(f'Model Loss (Final: {history["val_loss"][-1]:.2f})', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Loss')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_history.png', dpi=150)
plt.show()

# ======================
# FINAL EVALUATION
# ======================
print("\n" + "=" * 60)
print("🎯 FINAL EVALUATION")
print("=" * 60)

# Load best model
best_model = tf.keras.models.load_model("backend/model/plant_disease_model_best.keras")

# Evaluate
val_loss, val_acc = best_model.evaluate(val_generator)
print(f"\n✅ Best Model Performance:")
print(f"   Validation Accuracy: {val_acc:.4f}")
print(f"   Validation Loss: {val_loss:.4f}")

print("\n" + "=" * 60)
print("📊 AFTER EPOCH 1, SEND ME THIS:")
print("👉 Epoch 1 val_accuracy = ?")
print("=" * 60)