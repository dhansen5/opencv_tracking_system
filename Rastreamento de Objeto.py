# Importação de bibliotecas

import cv2
import numpy as np
import serial
import datetime

# Configuração da Comunicação Serial

porta = 'COM3'
baudRate = 115200 #

ligarArduino = True # Para testar somente a câmera sem controle, mudar para False

if ligarArduino:
    SerialArduino = serial.Serial(porta, baudRate)

# Captura de video através da webcam
webcam = cv2.VideoCapture(1) # Númeração da webcam

# t1 = datetime.datetime.now() só usa se quiser monitorar o tempo de execução de cada looping

# Loop principal
while 1:

    # Leitura do video obtido pela
    # webcam em imagens
    _, imageFrame = webcam.read()
    imageFrame = cv2.flip(imageFrame, 1)  # Inverte a imagem

    # Identifica dimensões da imagem e posição central
    alturaImagem, larguraImagem = imageFrame.shape[:2]

    centroX = int(larguraImagem / 2)
    centroY = int(alturaImagem / 2)
    centroImagem = (centroX, centroY)

    # Converte as imagens obtidas no espaço RGB para espaço HSV
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Ranges de cor a ser detectada
    obj_lower = np.array([0, 92, 177], np.uint8)    # Ranges inferiores da cor
    obj_upper = np.array([30, 248, 255], np.uint8)  # Ranges superiores da cor

    # Criação da máscara de cor e aplicação de filtragem mediana
    obj_mask_nof = cv2.inRange(hsvFrame, obj_lower, obj_upper)
    obj_mask = cv2.medianBlur(obj_mask_nof, 5)

    # Transformação morfológica para detectar uma única cor
    kernal = np.ones((5, 5), "uint8")

    obj_mask = cv2.dilate(obj_mask, kernal)
    res_obj = cv2.bitwise_and(imageFrame, imageFrame,
                               mask=obj_mask)

    # Detecção de contornos
    contours, hierarchy = cv2.findContours(obj_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 320:
            x, y, w, h = cv2.boundingRect(contour)  # Posição eixo x, Posição eixo y, Largura, Altura
            imageFrame = cv2.rectangle(imageFrame, (x, y),
                                       (x + w, y + h),
                                       (255, 0, 0), 2)
            centroObjX = x + int(w / 2)
            centroObjY = y + int(h / 2)
            centroObj = (centroObjX, centroObjY)
            cv2.circle(imageFrame, centroObj, 2, 0, 0, 255)  # cv2.circle(Imagem a desenhar, coordenadas, raio, cor)

            cv2.putText(imageFrame, "OBJETO", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255, 0, 0))

            # Cálculo do erro
            erroX = centroX - centroObjX
            erroY = centroY - centroObjY


            # Envia os valores de erro para o Arduino
            if ligarArduino:
                SerialArduino.write(('X' + str(erroX) + 'Y' + str(erroY)).encode())

            # t2 = datetime.datetime.now()    # só usa se quiser monitorar o tempo de execução de cada looping
            # period = t2 - t1
            # print(period, " ", erroX, " ", erroY)

            print("Erro X: ", erroX, " Erro Y: ", erroY)

    # Visualiza imagem e encerramento do programa através
    cv2.imshow("Sistema de Rastreamento de Objetos", imageFrame)
    cv2.imshow("Mascara", obj_mask)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        SerialArduino.close()
        webcam.release()
        cv2.destroyAllWindows()
        break
