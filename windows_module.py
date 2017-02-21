#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Andrezio
#
# Created:     20/02/2017
# Copyright:   (c) Andrezio 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from Tkinter import *
from ttk import *
import sys
import tkMessageBox
from tkFileDialog   import askopenfilename,askdirectory
import matplotlib.pyplot as plt
from math import sin, cos
import numpy as np
from tkFileDialog   import askopenfilename
import copy

from math import sin,cos,pi,radians,tan,sqrt,log1p
from scipy import stats

root = Tk()

#metodos
def Open_file():
    namefile = askdirectory()
    print namefile


def close_window ():
    Fechar()
    root.destroy()


def help():
    import tkMessageBox
    tkMessageBox.showinfo("NETWORK",\
    "This is a freeware Software/")
#metodos

#buttons
horizontal=0
vertical=40

btnPlotar = Button(root, text="FOLDER",command=Open_file).place(x=horizontal,y=vertical)
vertical+=30
btnnNETWORK = Button(root, text="NETWORK").place(x=horizontal,y=vertical)
#buttons


#years
ak=240
texto = Label(text='YEAR').place(x=50,y=ak-30)
a=2000
b=2010
xc = Label(root, text = "Min")
xc.place(bordermode = OUTSIDE, height = 30, width = 30, x =0,y=ak )

bB = Entry(root, textvariable = a)
bB.place(bordermode = OUTSIDE, height = 30, width = 40, x = 30, y =ak )

xd = Label(root, text = "Max")
xd.place(bordermode = OUTSIDE, height = 30, width = 30, x =70,y=ak )

cC = Entry(root, textvariable = b)
cC.place(bordermode = OUTSIDE, height = 30, width = 50, x = 100, y =ak )

cC.delete(0,END)
bB.delete(0,END)
cC.insert(1,int(b))
bB.insert(1,int(a))



#years



menubar = Menu(root)
filemenu= Menu(menubar)
filemenu.add_command(label="Open Folder",command=Open_file)
filemenu.add_command(label="Close",command=close_window)
filemenu.add_separator()

menubar.add_cascade(label="File",menu=filemenu)
helpmenu = Menu(menubar)
helpmenu.add_command(label="Help Index")
helpmenu.add_command(label="About",command=help)
menubar.add_cascade(label="Help",menu=helpmenu)
root.config(menu=menubar)





#janela----

root.title("NETWORK - COCITATION")
root.geometry("650x330+10+10")
root.mainloop()