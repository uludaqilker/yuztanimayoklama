#-------------KÜTÜPHANELER-----------#
#------------------------------------#

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from yoklama_form import *
import cv2
import numpy as np
from PIL import Image
import os

#---------------Yüz_tespit_tanım-------------#
#------------------------------------#
detector = cv2.CascadeClassifier('opencv-files/haarcascade_frontalface_default.xml')
cam= cv2.VideoCapture(0)
path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
id = 0
#---------------UYGULAMA-------------#
#------------------------------------#

YoklamaApp = QApplication(sys.argv)
AnaPencere = QMainWindow()
ui = Ui_Form()
ui.setupUi(AnaPencere)
AnaPencere.show()


#--------------VERİTABANI------------#
#------------------------------------#

import sqlite3
global curs
global conn

conn = sqlite3.connect('yoklama_db.db')
curs = conn.cursor()


#--------------VT_KAYDET_SİL-------------#
#----------------------------------------#
def tabloGetir():
    sorguTblAdlari = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    tabloAdlari = curs.execute(sorguTblAdlari).fetchall()
    for tablo in tabloAdlari:
        ui.sinifSec_cb2.addItem(tablo[0])
        ui.sinifSec_cb.addItem(tablo[0])
tabloGetir()        
#----------------------------------------#
#   _tarih_de = ui.tarih_de.date().toString(QtCore.Qt.ISODate)

def imgsandlables(path):
    imagePaths = [os.path.join(path, i) for i in os.listdir(path)]
    indfaces = []
    ids = []
    for imagePath in imagePaths:
        img = Image.open(imagePath).convert('L')
        imgnp = np.array(img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[0])

        faces = detector.detectMultiScale(imgnp)
        for (x, y, w, h) in faces:
            indfaces.append(imgnp[y:y + h, x:x + w])
            ids.append(id)
    return indfaces, ids

def sinifEkle():
    _sinifAd_le = ui.sinifAd_le.text()
    ui.sinifSec_cb.addItem(_sinifAd_le)
    ui.sinifSec_cb2.addItem(_sinifAd_le)
    sorguCrtTblSınıf = ("CREATE TABLE IF NOT EXISTS {}   (                  \
                    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,      \
                    Ad TEXT NOT NULL,                                   \
                    Soyad TEXT NOT NULL,                                \
                    OgrenciNo TEXT NOT NULL,                            \
                    Durum TEXT NOT NULL DEFAULT 0,                                \
                    Tarih TEXT NOT NULL DEFAULT 2000,                                \
                    ToplamDevamsizlik TEXT NOT NULL DEFAULT 0)".format(_sinifAd_le) )
    curs.execute(sorguCrtTblSınıf)
    conn.commit()

def sinifSil():
    _sinifSec_cb2 = ui.sinifSec_cb2.currentText()
    sorguDropTblSınıf = ("DROP TABLE {}".format(_sinifSec_cb2))
    curs.execute(sorguDropTblSınıf)
    conn.commit()

def ogrIsmiGetir(ogrNo):
    _sinifSec_cb = ui.sinifSec_cb.currentText()
    sorgu = "SELECT Ad FROM {} WHERE OgrenciNo = ?".format(_sinifSec_cb)
    curs.execute(sorgu, (ogrNo,))
    sonuc = curs.fetchone()
    if sonuc:
        ogrIsmi = sonuc[0]
        return ogrIsmi
    else:
        return None
    
def devamsizlikKaydet():
    _sinifSec_cb = ui.sinifSec_cb.currentText()
    _ogrNo_le = ui.ogrNo_le.text()
    _toplamDevamsizlik_sb = 0
    _tarih_de = ui.tarih_de.date().toString(QtCore.Qt.ISODate)
    _durum_cb = 'var'

    sorgu = "UPDATE {} SET ToplamDevamsizlik = ?, Tarih = ?, Durum = ? WHERE OgrenciNo = ?".format(_sinifSec_cb)
    curs.execute(sorgu, (_toplamDevamsizlik_sb, _tarih_de, _durum_cb, _ogrNo_le))
    conn.commit()
    print("Devamsızlık bilgileri kaydedildi.")


def yoklamaBaslat():
    faces, ids = imgsandlables(path)
    recognizer.train(faces, np.array(ids))
    
    while True:
        _, img = cam.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, )
        

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            if (confidence < 100):
                id = ogrIsmiGetir(id)
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "kayit yok :)"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(id), (x - 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        cv2.imshow('camera', img)
        devamsizlikKaydet()
        k = cv2.waitKey(10) & 0xff

        if k == 27:
            break
    


    


def ogrEkle():
    _ogrAd_le = ui.ogrAd_le.text()
    _ogrSoyad_le = ui.ogrSoyad_le.text()
    _ogrNo_le = ui.ogrNo_le.text()
    _sinifSec_cb = ui.sinifSec_cb.currentText()
    _tarih_de = ui.tarih_de.date().toString(QtCore.Qt.ISODate)
    yüzKayit(_ogrNo_le)
    sorguInsTblSınıf = ("INSERT INTO {} (Ad, Soyad, OgrenciNo) VALUES (?, ?, ?)".format(_sinifSec_cb))

    try:
        curs.execute(sorguInsTblSınıf, (_ogrAd_le, _ogrSoyad_le, _ogrNo_le))
        conn.commit()
        print("Öğrenci eklendi.")
    except Exception as e:
        print(f"Hata: {e}")



def ogrSil():
    try:
        _ogrNo_le = ui.ogrNo_le.text()
        _sinifSec_cb = ui.sinifSec_cb.currentText()

        sorguDelTblSınıf = ("DELETE FROM {} WHERE OgrenciNo = {}"
                            .format(_sinifSec_cb, _ogrNo_le))

        curs.execute(sorguDelTblSınıf)
        conn.commit() 
    except Exception as e:
        print("Bir hata oluştu: ", e)
#-----------------YÜZ_KAYIT----------------#
#------------------------------------------# 

def yüzKayit(_ogrNo_le):
    
    id = _ogrNo_le
    count = 0
    while(True):
        _, img= cam.read()
        img= cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray,1.3,5 )
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            count += 1

            cv2.imwrite("data/" + str(id) + '.' +  str(count) + ".jpg", gray[y:y+h,x:x+w])
            cv2.imshow('image', img)

        k = cv2.waitKey(100) &  0xFF == ord('s')
        if k == 10:
            break
        elif count >= 30:
            break


#-----------------LİSTELE----------------#
#----------------------------------------# 

def listele():
   # Seçili sınıfın adını alın
    sinif_adi = ui.sinifSec_cb.currentText()
    
    # Veritabanında sınıfa ait bilgileri sorgulayın
    sorgu = "SELECT Ad, Soyad, OgrenciNo, Durum, Tarih FROM {}".format(sinif_adi)
    curs.execute(sorgu)
    veriler = curs.fetchall()
    
    # TableWidget'i temizleyin
    ui.yoklama_tw.clear()
    
    # Tablo başlıklarını ayarlayın
    ui.yoklama_tw.setColumnCount(5)
    ui.yoklama_tw.setHorizontalHeaderLabels(('Adı', 'Soyadı', 'Öğrenci No', 'Durum', 'Tarih'))
    
    # Verileri tabloya ekleme
    row_count = 0
    for veri in veriler:
        ui.yoklama_tw.insertRow(row_count)
        ui.yoklama_tw.setItem(row_count, 0, QTableWidgetItem(veri[0]))
        ui.yoklama_tw.setItem(row_count, 1, QTableWidgetItem(veri[1]))
        ui.yoklama_tw.setItem(row_count, 2, QTableWidgetItem(veri[2]))
        ui.yoklama_tw.setItem(row_count, 3, QTableWidgetItem(veri[3]))
        ui.yoklama_tw.setItem(row_count, 4, QTableWidgetItem(veri[4]))
        row_count += 1





#---------------SİNYAL-SLOT--------------#
#----------------------------------------#
ui.yeniSinif_pb.clicked.connect(sinifEkle)
ui.ogrenciKayit_pb.clicked.connect(ogrEkle)
ui.sinifSil_pb.clicked.connect(sinifSil)
ui.ogrenciSil_pb.clicked.connect(ogrSil)
ui.yoklamaBaslat_pb.clicked.connect(yoklamaBaslat)
ui.sonucGor_pb.clicked.connect(listele)



sys.exit(YoklamaApp.exec_())
