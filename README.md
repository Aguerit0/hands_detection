# 🖐️ Hand Gesture Presentation Controller

Este proyecto utiliza **OpenCV** y **MediaPipe** para controlar una presentación de imágenes mediante **gestos con las manos** detectados por la cámara.  
Permite cambiar de diapositiva, dibujar y usar un puntero sin necesidad de un mouse o teclado.

---

##  Características

- **Detección de manos en tiempo real** con MediaPipe  
- **Control por gestos:**
  - 👍 **Pulgar levantado** → Imagen anterior  
  - 🤚 **Meñique levantado** → Imagen siguiente  
  - ☝️ **Índice levantado** → Dibuja sobre la diapositiva  
  - ✌️ **Índice + Medio levantados** → Modo puntero  
- Muestra una **mini ventana con la cámara**  
- Permite **limpiar el lienzo** presionando **`C`**  
- **Salida del programa** con **`Q`**

---

## 📁 Estructura del proyecto
```
hands_detection/
│
├── img/              # Carpeta con las imágenes de la presentación
├── main.py           # Código principal del proyecto
├── README.md         # Este archivo
└── .gitignore        # Archivos a ignorar por Git
```

---

##  Requisitos

Instala las dependencias con:
```bash
pip install -r requirements.txt
```

---

##  Ejecución

Ejecutá el programa desde la terminal:
```bash
python3 main.py
```

Asegurate de tener conectada una cámara y de que la carpeta `img/` contenga imágenes.
En caso de no detecte la camara, se puede cambiar el puerto en la línea siguiente:
cambia 
```bash
cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
```
```bash
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)#0, 1, 2, ..., n
```
---

##  Desarrollado por [Aguerit0](https://github.com/Aguerit0)


###  Próximas mejoras

- [ ] Agregar más gestos personalizables
- [ ] Exportar anotaciones a PDF
- [ ] Soporte para videos además de imágenes
- [ ] Calibración automática de sensibilidad de gestos
- [ ] Autodetectar puertos de la cámara
---
