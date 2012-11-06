# -*- coding: utf-8 -*-
# ##############################################################################
#
# Copyright (C) 2003 noze Srl and Contributors.
# All Rights Reserved.
#
# http://noze.it
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details at
# http://www.gnu.org/copyleft/lgpl.html
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
__doc__='''GestPayCrypt Class
$Id: GestPayCrypt.py,v 2.0 2003/12/09 20:03:52 stefanoferi Exp $'''
__version__='$Revision: 2.0 $'[11:-2]

import httplib
import string
import re

from livesettings import config_value


class GestPayCrypt:

    def __init__(self):
        self.ShopLogin = ''
        self.Currency = '242' # 242 = Euro
        self.Amount = ''
        self.ShopTransactionID = ''
        self.CardNumber = ''
        self.ExpMonth = ''
        self.ExpYear = ''
        self.BuyerName = ''
        self.BuyerEmail = ''
        self.Language = ''
        self.CustomInfo = ''
        self.AuthorizationCode = ''
        self.ErrorCode = '0'
        self.ErrorDescription = ''
        self.BankTransactionID = ''
        self.AlertCode = ''
        self.AlertDescription = ''
        self.EncryptedString = ''
        self.ToBeEncrypt = ''
        self.Decrypted = ''
        self.TransactionResult = ''
        self.ProtocolAuthServer = 'http'
        self.DomainName = 'ecomm.sella.it'
        self.TestDomainName = 'testecomm.sella.it'
        self.ScriptEnCrypt = '/CryptHTTP/Encrypt.asp'
        self.ScriptDecrypt = '/CryptHTTP/Decrypt.asp'
        self.separator = '*P1*'
        self.errDescription = ''
        self.errNumber = '0'
        self.Version = '2.0'
        self.Min = ''
        self.CVV = ''
        self.country = ''
        self.vbvrisp = ''
        self.vbv = ''

    def SetShopLogin(self, val):
        self.ShopLogin = val

    def SetCurrency(self, val):
        self.Currency = val

    def SetAmount(self, val):
        self.Amount = val

    def SetShopTransactionID(self, val):
        self.ShopTransactionID = val

    def SetCardNumber(self, val):
        self.CardNumber = val

    def SetExpMonth(self, val):
        self.ExpMonth = val

    def SetExpYear(self, val):
        self.ExpYear = val

    def SetMIN(self, val):
        self.Min = val

    def SetCVV(self, val):
        self.CVV = val

    def SetBuyerName(self, val):
        self.BuyerName = val

    def SetBuyerEmail(self, val):
        self.BuyerEmail = val

    def SetLanguage(self, val):
        self.Language = val

    def SetCustomInfo(self, val):
        self.CustomInfo = val

    def SetEncryptedString(self, val):
        self.EncryptedString = val

    def GetShopLogin(self):
        return self.ShopLogin

    def GetCurrency(self):
        return self.Currency

    def GetAmount(self):
        return self.Amount

    def GetCountry(self):
        return self.country

    def GetVBV(self):
        return self.vbv

    def GetVBVrisp(self):
        return self.vbvrisp

    def GetShopTransactionID(self):
        return self.ShopTransactionID

    def GetBuyerName(self):
        return self.BuyerName

    def GetBuyerEmail(self):
        return self.BuyerEmail

    def GetCustomInfo(self):
        return self.CustomInfo

    def GetAuthorizationCode(self):
        return self.AuthorizationCode

    def GetErrorCode(self):
        return self.ErrorCode

    def GetErrorDescription(self):
        return self.ErrorDescription

    def GetBankTransactionID(self):
        return self.BankTransactionID

    def GetTransactionResult(self):
        return self.TransactionResult

    def GetAlertCode(self):
        return self.AlertCode

    def GetAlertDescription(self):
        return self.AlertDescription

    def GetEncryptedString(self):
        return self.EncryptedString

    def Encrypt(self):
        self.ErrorCode = '0'
        self.ErrorDescription = ''
        self.ToBeEncrypt = ''

        if not self.ShopLogin:
            self.ErrorCode = '546'
            self.ErrorDescription = 'IDshop not valid'
            return None

        if not self.Currency:
            self.ErrorCode = '552'
            self.ErrorDescription = 'Currency not valid'
            return None

        if not self.Amount:
            self.ErrorCode = '553'
            self.ErrorDescription = 'Amount not valid'
            return None

        if not self.ShopTransactionID:
            self.ErrorCode = '551'
            self.ErrorDescription = 'Shop Transaction ID not valid'
            return None

        self.ToEncrypt(self.CVV, 'PAY1_CVV')
        self.ToEncrypt(self.Min, 'PAY1_MIN')
        self.ToEncrypt(self.Currency, 'PAY1_UICCODE')
        self.ToEncrypt(self.Amount, 'PAY1_AMOUNT')
        self.ToEncrypt(self.ShopTransactionID, 'PAY1_SHOPTRANSACTIONID')
        self.ToEncrypt(self.CardNumber, 'PAY1_CARDNUMBER')
        self.ToEncrypt(self.ExpMonth, 'PAY1_EXPMONTH')
        self.ToEncrypt(self.ExpYear, 'PAY1_EXPYEAR')
        self.ToEncrypt(self.BuyerName, 'PAY1_CHNAME')
        self.ToEncrypt(self.BuyerEmail, 'PAY1_CHEMAIL')
        self.ToEncrypt(self.Language, 'PAY1_IDLANGUAGE')
        self.ToEncrypt(self.CustomInfo, '')

        self.ToBeEncrypt = string.replace(self.ToBeEncrypt, ' ', '§')	

        uri = '%s?a=%s&b=%s' % (self.ScriptEnCrypt, self.ShopLogin, self.ToBeEncrypt[len(self.separator):])
        
        live = config_value('PAYMENT_CREDITCARD', 'LIVE')
        if live:
            self.EncryptedString = self.HttpGetResponse(self.DomainName, uri, 1)
        else:
            self.EncryptedString = self.HttpGetResponse(self.TestDomainName, uri, 1)
        
        if not self.EncryptedString:
            return None
        
        return 1

    def Decrypt(self):
        self.ErrorCode = '0'
        self.ErrorDescription = ''

        if not self.ShopLogin:
            self.ErrorCode = '546'
            self.ErrorDescription = 'IDshop not valid'
            return None

        if not self.EncryptedString:
            self.ErrorCode = '1009'
            self.ErrorDescription = 'String to Decrypt not valid'
            return None

        uri = '%s?a=%s&b=%s' % (self.ScriptDecrypt, self.ShopLogin, self.EncryptedString)


        live = config_value('PAYMENT_CREDITCARD', 'LIVE')
        if live:
            self.Decrypted = self.HttpGetResponse(self.DomainName, uri, None)
        else:
            self.Decrypted = self.HttpGetResponse(self.TestDomainName, uri, None)
        
        if not self.Decrypted:
            return None

        elif self.Decrypted == '':
            self.ErrorCode = '9999'
            self.ErrorDescription = 'Empty decrypted string'
            return None

        self.Decrypted = string.replace(self.Decrypted, '§', ' ')

        self.Parsing()

        return 1


    def ToEncrypt(self, value, tagvalue):
        """ """
        equal = tagvalue and '=' or ''

        if value:
            self.ToBeEncrypt = self.ToBeEncrypt + '%s%s%s%s' % (self.separator, tagvalue, equal, value)


    def HttpGetResponse(self, host, uri, crypt):
        response = ''
        req = crypt and 'crypt' or 'decrypt'
        
        line = self.HttpGetLine(host, uri)
        
        if not line:
            return None
            
        crypt_re = re.compile('#'+req+'string#([\w\W]*)#/'+req+'string#')
        error_re = re.compile('#error#([\w\W]*)#/error#')

        if crypt_re.match(line):
            response = string.strip(crypt_re.split(line)[1])

        elif error_re.match(line):
            err = string.split(error_re.split(line)[1],'-')
            
            if not err[0] and not err[1]:
                self.ErrorCode = '9999'
                self.ErrorDescription = 'Unknown error'

            else:
                self.ErrorCode = err[0]
                self.ErrorDescription = err[1]

            return None
        else:
            self.ErrorCode = '9999'
            self.ErrorDescription = 'Response from server not valid'
            return None

        return response


    def HttpGetLine(self, host, uri, port = 80):
        h = httplib.HTTP()
        h.connect(host, port)

        if not h:
            self.ErrorCode = '9999'
            self.ErrorDescription = 'Impossible to connect to host: %s' % host

            return None

        else:
            h.putrequest('GET', uri)
            h.endheaders()

        status, reason, headers = h.getreply()

        line = h.getfile().read()  

        return line


    def Parsing(self):
        keyval = string.split(self.Decrypted, self.separator)

        for tagPAY1 in keyval:
            tagPAY1val = string.split(tagPAY1, '=')

            if tagPAY1val[0] == 'PAY1_UICCODE':
                self.Currency = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_AMOUNT':
                self.Amount = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_SHOPTRANSACTIONID':
                self.ShopTransactionID = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_CHNAME':
                self.BuyerName = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_CHEMAIL':
                self.BuyerEmail = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_AUTHORIZATIONCODE':
                self.AuthorizationCode = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_ERRORCODE':
                self.ErrorCode = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_ERRORDESCRIPTION':
                self.ErrorDescription = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_BANKTRANSACTIONID':
                self.BankTransactionID = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_ALERTCODE':
                self.AlertCode = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_ALERTDESCRIPTION':
                self.AlertDescription = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_CARDNUMBER':
                self.CardNumber = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_EXPMONTH':
                self.ExpMonth = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_EXPYEAR':
                self.ExpYear = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_COUNTRY':
                self.country = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_VBVRISP':
                self.vbvrisp = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_VBV':
                self.vbv = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_IDLANGUAGE':
                self.Language = tagPAY1val[1]

            elif tagPAY1val[0] == 'PAY1_TRANSACTIONRESULT':
                self.TransactionResult = tagPAY1val[1]

            else:
                self.CustomInfo = self.CustomInfo + tagPAY1 + self.separator

        self.CustomInfo = self.CustomInfo[:len(self.separator)]
