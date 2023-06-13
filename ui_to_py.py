from PyQt5 import uic

with open('yoklama_form.py', 'w' , encoding="utf-8") as fout:
    uic.compileUi('yoklama_form.ui' , fout)