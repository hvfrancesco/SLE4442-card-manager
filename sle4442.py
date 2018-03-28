#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui

from card_ui import Ui_MainWindow

from smartcard.scard import *
import smartcard.util

SELECT = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
LEGGI = [0xFF, 0xB0, 0x00] # aggiungere indirizzo e lunghezza
SCRIVI = [0xFF, 0xD0, 0x00] # aggiungere indirizzo, lunghezza e bytes
PROTEGGI = [0xFF, 0xD1, 0x00] # aggiungere indirizzo, lunghezza e bytes
SBLOCCA_SCRITTURA = [0xFF, 0x20, 0x00, 0x00, 0x03] # aggiungi PIN
CAMBIA_PIN = [0xFF, 0xD2, 0x00, 0x01, 0x03] # aggiungi PIN
LEGGI_PROT = [0xFF, 0xB2, 0x00, 0x00, 0x04]

PIN = ''
CONTENUTO = []
for i in range (255):
    CONTENUTO.append(None)


class MyUi(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.hcard = None
        self.dwActiveProtocol = None
        self.hcontext = None
        self.reader = None
        self.setWindowTitle('sle4442 manager')
        self.PIN_PROT = [self.ui.bit_8, self.ui.bit_7, self.ui.bit_6, self.ui.bit_5, self.ui.bit_4, self.ui.bit_3, self.ui.bit_2, self.ui.bit_1,
            self.ui.bit_16, self.ui.bit_15, self.ui.bit_14, self.ui.bit_13, self.ui.bit_12, self.ui.bit_11, self.ui.bit_10, self.ui.bit_9,
            self.ui.bit_24, self.ui.bit_23, self.ui.bit_22, self.ui.bit_21, self.ui.bit_20, self.ui.bit_19, self.ui.bit_18, self.ui.bit_17,
            self.ui.bit_32, self.ui.bit_31, self.ui.bit_30, self.ui.bit_29, self.ui.bit_28, self.ui.bit_27, self.ui.bit_26, self.ui.bit_25 ]

        # segnali
        QtCore.QObject.connect(self.ui.leggi,QtCore.SIGNAL("clicked()"), self.leggi_tutto)
        QtCore.QObject.connect(self.ui.scrivi,QtCore.SIGNAL("clicked()"), self.scrivi_tutto)
        QtCore.QObject.connect(self.ui.connetti,QtCore.SIGNAL("clicked()"), self.connetti)
        QtCore.QObject.connect(self.ui.disconnetti,QtCore.SIGNAL("clicked()"), self.disconnetti)
        QtCore.QObject.connect(self.ui.sblocca,QtCore.SIGNAL("clicked()"), self.sblocca)
        QtCore.QObject.connect(self.ui.change_pin,QtCore.SIGNAL("clicked()"), self.cambia_pin)
        QtCore.QObject.connect(self.ui.proteggi,QtCore.SIGNAL("clicked()"), self.proteggi_byte)


    def connetti(self):
        try:
            hresult, self.hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to establish context : ' + SCardGetErrorMessage(hresult))
            print 'Context established!'

            try:
                hresult, readers = SCardListReaders(self.hcontext, [])
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to list readers: ' + SCardGetErrorMessage(hresult))
                print 'PCSC Readers:', readers

                if len(readers) < 1:
                    raise Exception('No smart card readers')

                self.reader = readers[0]
                print "Using reader:", self.reader

                try:
                    hresult, self.hcard, self.dwActiveProtocol = SCardConnect(self.hcontext, self.reader, SCARD_SHARE_SHARED, SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
                    if hresult != SCARD_S_SUCCESS:
                        raise Exception('Unable to connect: ' + SCardGetErrorMessage(hresult))
                    print 'Connected with active protocol', self.dwActiveProtocol

                    try:
                        hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, SELECT)
                        if hresult != SCARD_S_SUCCESS:
                            raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
                        self.ui.stato_carta.setStyleSheet('color: black')
                        self.ui.stato_carta.setText('carta connessa in lettura')
                        self.ui.scrivi.setEnabled(False)
                        self.ui.change_pin.setEnabled(False)
                        self.ui.proteggi.setEnabled(False)
                        self.ui.proteggi_n.setEnabled(False)
                        print 'Carta correttamente inizializzata'
                    except Exception, message:
                        print "Exception:", message

                except Exception, message:
                        print "Exception:", message

            except Exception, message:
                        print "Exception:", message

        except Exception, message:
            print "Exception:", message

    def leggi(self):
        try:
            hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, LEGGI + [self.ui.leggi_inizio.value(), self.ui.leggi_n_bytes.value()])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            print 'Contenuto della memoria: ' + smartcard.util.toHexString(response[0:-2], smartcard.util.HEX)
            #print 'Command: ' + smartcard.util.toASCIIString(response)
            print "letti " + str(len(response)-2) + " bytes"
            CONTENUTO[self.ui.leggi_inizio.value():self.ui.leggi_inizio.value()+self.ui.leggi_n_bytes.value()] = response[0:-2]
            print CONTENUTO
            if (response[-2] == 144):
                print "OK!"
        except Exception, message:
            print "Exception:", message

    def proteggi_byte(self):
        try:
            byte = self.ui.proteggi_n.value()-1
            hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, LEGGI + [byte, 1])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            risultato = response[0]
            try:
                hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, PROTEGGI + [byte, 1, risultato])
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
                if (response[-2] == 144):
                    self.ui.statusbar.showMessage('protetto byte ' + str(byte+1), 4000)
            except Exception, message:
                print "Exception:", message
        except Exception, message:
            print "Exception:", message

    def leggi_tutto(self):
        try:
            hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, LEGGI + [0, 255])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            if (response[-2] == 144):
                risultato = response[0:-2]
                for i in range(255):
                    self.ui.dati.setItem(i/8,i%8,QtGui.QTableWidgetItem(chr(risultato[i])))
                self.ui.statusbar.showMessage('lettura effettuata', 4000)
        except Exception, message:
            print "Exception:", message
        
        try:
            hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol,LEGGI_PROT)
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            if (response[-2] == 144):
                risultato = bin(response[0])[2:]+bin(response[1])[2:]+bin(response[2])[2:]+bin(response[3])[2:]
                for i in range(32):
                    if risultato[i] == "1":
                        self.PIN_PROT[i].setChecked(False)
                        byte = (i/8)*8+8-(i%8)-1
                        self.ui.dati.item(byte/8,byte%8).setBackground(QtGui.QColor(240,240,240))
                    elif risultato[i] == "0":
                        self.PIN_PROT[i].setChecked(True)
                        byte = (i/8)*8+8-(i%8)-1
                        self.ui.dati.item(byte/8,byte%8).setBackground(QtGui.QColor(150,100,100))
                    else:
                        raise Exception('Errore nella lettura dello stato di protezione dei byte')

        except Exception, message:
            print "Exception:", message

    def scrivi_tutto(self):
        risultato = []
        for i in range(255):
            c = self.ui.dati.item(i/8,i%8).text()
            if c == '':
                v = 0x00
            else:
                v = ord(unicode(c))
            risultato.append(v)
        try:
            hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, SCRIVI + [0, 255] + risultato)
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            if (response[-2] == 144):
                self.ui.statusbar.showMessage('scrittura corretta', 4000)
        except Exception, message:
            print "Exception:", message

    def sblocca(self):
        try:
            PIN = unicode(self.ui.pin.text())
            if len(PIN) != 3:
                self.ui.stato_carta.setStyleSheet('color: red')
                self.ui.stato_carta.setText('pin di tre caratteri')
            else:
                hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, SBLOCCA_SCRITTURA + smartcard.util.toASCIIBytes(PIN))
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
                if response[-1] == 7:
                    self.ui.stato_carta.setStyleSheet('color: green')
                    self.ui.stato_carta.setText('carta sbloccata')
                    self.ui.scrivi.setEnabled(True)
                    self.ui.change_pin.setEnabled(True)
                    self.ui.proteggi.setEnabled(True)
                    self.ui.proteggi_n.setEnabled(True)
                    print "carta sbloccata e pronta per la scrittura"
                elif response[-1] == 0:
                    print "carta bloccata"
                    self.ui.stato_carta.setStyleSheet('color: red')
                    self.ui.stato_carta.setText('carta bloccata')
                else:
                    print "pin errato"
                    self.ui.stato_carta.setStyleSheet('color: red')
                    self.ui.stato_carta.setText('pin errato')

        except Exception, message:
            print "Exception:", message

    def cambia_pin(self):
        try:
            PIN = unicode(self.ui.pin.text())
            if len(PIN) != 3:
                self.ui.stato_carta.setText('pin di tre caratteri')
            else:
                hresult, response = SCardTransmit(self.hcard, self.dwActiveProtocol, CAMBIA_PIN + smartcard.util.toASCIIBytes(PIN))
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
                if (response[-2] == 144):
                    self.ui.statusbar.showMessage('PIN modificato', 4000)

        except Exception, message:
            print "Exception:", message

    def disconnetti(self):
        try:
            hresult = SCardDisconnect(self.hcard, SCARD_UNPOWER_CARD)
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to disconnect: ' + SCardGetErrorMessage(hresult))
            print 'Disconnected'
            self.ui.stato_carta.setStyleSheet('color: black')
            self.ui.stato_carta.setText('carta disconnessa')
            self.ui.scrivi.setEnabled(False)
            self.ui.change_pin.setEnabled(False)
            self.ui.proteggi.setEnabled(False)
            self.ui.proteggi_n.setEnabled(False)
            try:
                hresult = SCardReleaseContext(self.hcontext)
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to release context: ' + SCardGetErrorMessage(hresult))
                print 'Released context.'
            except Exception, message:
                print "Exception:", message
        except Exception, message:
            print "Exception:", message


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyUi()
    myapp.show()
    sys.exit(app.exec_())
