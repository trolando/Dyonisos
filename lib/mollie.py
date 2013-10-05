#!/usr/bin/env python

"""A thin Python wrapper for the Mollie API.
https://www.mollie.nl/support/documentatie/betaaldiensten/ideal
"""

import cStringIO
import logging
import urllib

import pycurl
from lxml import objectify

__author__ = "Floor Terra"
__copyright__ = "Copyright 2013, Floor Terra"
__credits__ = ["Floor Terra", ]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Floor Terra"
__email__ = "floort@gmail.com"
__status__ = "Developement"

################################################################################
# Copyright (c) 2013, FLoor Terra <floort@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any 
# purpose with or without fee is hereby granted, provided that the above 
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH 
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, 
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR 
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR 
# PERFORMANCE OF THIS SOFTWARE.
################################################################################

ERR_IMPROPER_INPUT_VALUE =  -1
ERR_NO_PARTNERID =          -2
ERR_IMPROPER_REPORTURL =    -3
ERR_NO_AMOUNT =             -4
ERR_NO_BANK_ID =            -5
ERR_UNKNOWN_BANK_ID =       -6
ERR_NO_DESCRIPTION =        -7
ERR_NO_TRANSACTION_ID =     -8
ERR_ILLIGAL_CHARACTERS =    -9
ERR_UNKNOWN_ORDER =         -10
ERR_NO_PARTERID =           -11
ERR_IMPROPER_RETURNURL =    -12
ERR_LOGIN_REQUIRED =        -13
ERR_AMOUNT_TOO_LOW =        -14
ERR_ACCOUNT_NOT_ALLOWED =   -15
ERR_UNKNOWN_PROFILE =       -16
ERR_RETURNURL_INVALID =     -17

ERROR_MESSAGE = {
    ERR_IMPROPER_INPUT_VALUE:	"Did not receive a proper input value.",
    ERR_NO_PARTNERID:	        "A fetch was issued without specification of 'partnerid'.",
    ERR_IMPROPER_REPORTURL:     "A fetch was issued without (proper) specification of 'reporturl'.",
    ERR_NO_AMOUNT:	            "A fetch was issued without specification of 'amount'.",
    ERR_NO_BANK_ID: 	        "A fetch was issued without specification of 'bank_id'.",
    ERR_UNKNOWN_BANK_ID:	    "A fetch was issues without specification of a known 'bank_id'.",
    ERR_NO_DESCRIPTION:	        "A fetch was issued without specification of 'description'.",
    ERR_NO_TRANSACTION_ID: 	    "A check was issued without specification of transaction_id.",
    ERR_ILLIGAL_CHARACTERS:	    "Transaction_id contains illegal characters. (Logged as attempt to mangle).",
    ERR_UNKNOWN_ORDER:	        "This is an unknown order.",
    ERR_NO_PARTERID:	        "A check was issued without specification of your partner_id.",
    ERR_IMPROPER_RETURNURL:	    "A fetch was issued without (proper) specification of 'returnurl'.",
    ERR_LOGIN_REQUIRED:	        "This amount is only permitted when iDEAL contract is signed and sent to Mollie.",
    ERR_AMOUNT_TOO_LOW:	        "Minimum amount for an ideal transaction is € 1,20.",
    ERR_ACCOUNT_NOT_ALLOWED:	"A fetch was issued for an account which is not allowed to accept iDEAL payments (yet).",
    ERR_UNKNOWN_PROFILE: 	    "A fetch was issued for an unknown or inactive profile.",
    ERR_RETURNURL_INVALID:	    "The provided 'returnurl' cannot be used."
}


def httpsrequest(url):
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.SSL_VERIFYHOST, 2)
    c.perform()
    val = buf.getvalue()
    buf.close()
    return val
    

def banklist():
    response = httpsrequest('https://secure.mollie.nl/xml/ideal?a=banklist')
    obj = objectify.fromstring(response)
    logging.info(obj.message)
    for bank in obj.bank:
        yield bank
        
def fetch(partnerid, amount, bank_id, description, reporturl, returnurl, profile_key=None):
    if type(amount) == str:
        if not amount.isdigit(): raise ValueError("Parameter amount should not contain non-digit characters.")
        amount = int(amount)
    elif type(amount) != int:
        raise TypeError("Parameter amount should be a atring or an integer.")
    if type(bank_id) == int:
        # Bank_id should be a integer between 0 and 10000 with leading zeroes.
        if bank_id < 0: raise ValueError("Parameter bank_id should be larger then 0.")
        if bank_id >= 10000: raise ValueError("Parameter bank_id should be less than 10000.")
        bank_id = "%04d" % (bank_id, )
    elif type(bank_id) == str:
        if not bank_id.isdigit(): raise ValueError("Parameter bank_id should contain only digits.")
        if len(bank_id) != 4: raise ValueError("Parameter bank_id should contain exactly 4 digits (incl. leading zeroes).")
    else:
        raise TypeError("Parameter bank_id should be a integer or a string.")
    if len(description) > 29:
        raise ValueError("Parameter 'description' can't be longer than 29 characters.")
    
    params = urllib.urlencode({
        "a": "fetch",
        "partnerid": partnerid,
        "amount": amount,
        "bank_id": bank_id,
        "description": description,
        "reporturl": reporturl,
        "returnurl": returnurl,
        "profile_key": profile_key
    })
    response = httpsrequest("https://www.mollie.nl/xml/ideal?%s" % params)
    obj = objectify.fromstring(response)
    order = obj.order
    return order
            
def check():
    params = urllib.urlencode({
        "a": "check",
        "partnerid": partnerid,
        "transaction_id": transaction_id
    })
    response = httpsrequest("https://secure.mollie.nl/xml/ideal?%s" % params)
    obj = objectify.fromstring(response)
    return obj.order
    
def get_error(obj):
    if hasattr(obj, "item"): # Error
        return (response.item.errorcode, response.item.message)
    else:
        return False

    
    
    
