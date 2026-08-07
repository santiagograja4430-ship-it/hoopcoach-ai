import os
import shutil
import random
import glob
import datetime


base_dir = "dataset_yolo"
carpetas = ["train/images", "train/labels", "val/images", "val/labels"]

for c in carpetas: 
    os.makedirs(os.path.join(base_dir, c), exist_ok=True)

imagenes = glob.glob("dataset_balon/*.jpg")
if not imagenes:
    print("No se encontraron fotos en 'dataset_balon/'. Revisa la ruta.")
    exit()


random.shuffle(imagenes)
split_idx = int(len(imagenes) * 0.8)
train_imgs = imagenes[:split_idx]
val_imgs = imagenes[split_idx:]

def mover_archivos(lista_imgs, split_name):
    contador = 0
    for img_path in lista_imgs:
        nombre_base = os.path.basename(img_path)
        nombre_txt = nombre_base.replace(".jpg", ".txt")

        txt_path = os.path.join("dataset_balon_labels", nombre_txt)

        shutil.copy(img_path, os.path.join(base_dir, split_name, "images", nombre_base))


        if os.path.exists(txt_path):
            shutil.copy(txt_path, os.path.join(base_dir, split_name, "labels", nombre_txt))
            contador += 1
    return contador

cant_train = mover_archivos(train_imgs, "train")
cant_val = mover_archivos(val_imgs, "val")


yaml_content = f"""path: {os.path.abspath(base_dir)}
train: train/images
val: val/images

names:
  0: balon
"""

with open(os.path.join(base_dir, "data.yaml"), "w") as f:
    f.write(yaml_content)

def obtener_tamaño_carpeta(ruta):
    tamaño_total = 0
    for dirpath, _, filenames in os.walk(ruta):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                tamaño_total += os.path.getsiza(fp)
    return tamaño_total / (1024 * 1024)
tamaño_mb = obtener_tamaño_carpeta(base_dir)
fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("--------------------------------------------------")
print("¡Dataset estructuradocon exito!")
print(f"Entrenar (train): {len(train_imgs)} imagenes ({cant_train} etiquetadas)")
print(f"Validar (val): {len(val_imgs)} imagenes ({cant_val} etiquetadas)")
print(f"Archivo 'data.yaml' creado en: {os.path.join(base_dir, 'data.yaml')}")
print(f"tamaño total del dataset: {tamaño_mb:.2f} MB")
print(f"Procesando el: {fecha_actual}")
print("--------------------------------------------------")