# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import mechanize
import configparser
import io
import ssl
import re
import json

class SomfyException(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
        self.value = value

    def __str__(self):
        return repr(self.value)

class Somfy:
    def __init__(self, url, password, codes):
        ssl._create_default_https_context = ssl._create_unverified_context
        # self.config = config
        self.url = url
        self.id = id
        self.password = password
        self.codes = codes
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36')]

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    def login(self):
        login_response = self.browser.open(self.url + "/m_login.htm")
        login_html = login_response.read()
        # print(login_html)

        login_soup = self._beautiful_it_and_check_error(login_html)
        authentication_code = login_soup.find('form').find('table').findAll('tr')[5].findAll('b')[0].find(text=True)

        self.browser.select_form(nr=0)
        self.browser["password"] = self.password
        key = ("key_%s" % authentication_code)
        self.browser["key"] = self.codes[key]

        self.browser.submit()

    def logout(self):
        self.browser.open(self.url + "/m_logout.htm")

    def set_zone_a(self):
        self.browser.open(self.url + "/mu_pilotage.htm")
        self.browser.select_form(nr = 0)
        self.browser.submit()

    def set_zone_b(self):
        self.browser.open(self.url + "/mu_pilotage.htm")
        self.browser.select_form(nr = 1)
        self.browser.submit()

    def set_zone_c(self):
        self.browser.open(self.url + "/mu_pilotage.htm")
        self.browser.select_form(nr = 2)
        self.browser.submit()

    def set_all_zone(self):
        self.browser.open(self.url + "/mu_pilotage.htm")
        self.browser.select_form(nr =3)
        self.browser.submit()

    def unset_all_zone(self):
        self.browser.open(self.url + "/mu_pilotage.htm")
        self.browser.select_form(nr =4)
        self.browser.submit()

    def get_state(self):
        state_response = self.browser.open(self.url + "/mu_etat.htm")
        state_html = state_response.read()

        state_soup = self._beautiful_it_and_check_error(state_html)
        result = self.get_general_state(state_soup.findAll('table')[0])
        result.update(self.get_zone_state(state_soup.findAll('table')[0]))

        return result

    def get_zone_state(self, state_soup):
        zone_state = state_soup.findAll('table')[2].findAll('tr')

        def get_zone_a():
            return { "zone_a" : zone_state[0].find(text=True) }

        def get_zone_b():
            return { "zone_b" : zone_state[1].find(text=True) }

        def get_zone_c():
            return { "zone_c" : zone_state[2].find(text=True) }

        result = get_zone_a()
        result.update(get_zone_b())
        result.update(get_zone_c())

        return result

    def get_general_state(self, state_soup):
        general_state = state_soup.findAll('table')[1].findAll('tr')

        def get_battery_state():
            return { "battery" : general_state[0].find(text=True) }

        def get_communication_state():
            return { "communication" : general_state[1].find(text=True) }

        def get_door_state():
            return { u"door" : general_state[2].find(text=True) }

        def get_alarm_state():
            return { "alarm" : general_state[4].find(text=True) }

        def get_material_state():
            return { "material" : general_state[6].find(text=True) }

        result = get_battery_state()
        result.update(get_communication_state())
        result.update(get_door_state())
        result.update(get_alarm_state())
        result.update(get_material_state())

        return result

    def get_elements(self):
        state_response = self.browser.open(self.url + "/u_listelmt.htm")
        state_html = state_response.read()
        state_soup = self._beautiful_it_and_check_error(state_html)
        result = state_soup.find("div", {"id": "itemlist"})
        
        extract_elements = re.compile('var\sitem_type\s+=\s(.*);\nvar\sitem_label\s+=\s(.*);\nvar\sitem_pause\s+=\s(.*);\nvar\selt_name\s+=\s(.*);\nvar\selt_code\s+=\s(.*);\nvar\selt_pile\s+=\s(.*);\nvar\selt_as\s+=\s(.*);\nvar\selt_maison\s+=\s(.*);\nvar\selt_onde\s+=\s(.*);\nvar\selt_porte\s+=\s(.*);\nvar\selt_zone\s+=\s(.*);', re.IGNORECASE).search(str(result))
               
        item_type = json.loads(extract_elements.group(1))
        item_label = json.loads(extract_elements.group(2))
        item_pause = json.loads(extract_elements.group(3))
        elt_name = json.loads(extract_elements.group(4))
        elt_code = json.loads(extract_elements.group(5)) 
        elt_pile = json.loads(extract_elements.group(6))
        elt_as = json.loads(extract_elements.group(7))
        elt_maison = json.loads(extract_elements.group(8))
        elt_onde = json.loads(extract_elements.group(9))
        elt_porte = json.loads(extract_elements.group(10))
        elt_zone = json.loads(extract_elements.group(11))

        elements = {}
        for x in range(len(elt_code)):
            elements[elt_code[x]]  = { 
                "item_type" : item_type[x], 
                "item_label" : item_label[x], 
                "item_pause" : item_pause[x],
                "elt_name" : elt_name[x],
                "elt_pile" : elt_pile[x],
                "elt_as" : elt_as[x],
                "elt_maison" : elt_maison[x],
                "elt_onde" : elt_onde[x],
                "elt_porte" : elt_porte[x],
                "elt_zone" : elt_zone[x]
            }

        return  elements

    def _beautiful_it_and_check_error(self, html):
        soup = BeautifulSoup(html, "lxml")
        self._check_error(soup)
        return soup

    def _check_error(self, soup):
        if soup.find("div", {"class": "error"}):
            error_code = soup.find('div').findAll('b')[0].find(text=True)
            if '(0x0904)' == error_code:
                raise SomfyException("Nombre d'essais maximum atteint")
            if '(0x1100)' == error_code:
                raise SomfyException("Code errone")
            if '(0x0902)' == error_code:
                raise SomfyException("Session deja ouverte")
            if '(0x0812)' == error_code:
                raise SomfyException("Mauvais login/password")
            if '(0x0903)' == error_code:
                raise SomfyException("Droit d'acces insuffisant")

if __name__ == '__main__':
    url = "xxx"
    password = "xxxx"
    codes={
        "key_A1":"xxxx",
        "key_A2":"xxxx",
        "key_A3":"xxxx",
        "key_A4":"xxxx",
        "key_A5":"xxxx",
        "key_B1":"xxxx",
        "key_B2":"xxxx",
        "key_B3":"xxxx",
        "key_B4":"xxxx",
        "key_B5":"xxxx",
        "key_C1":"xxxx",
        "key_C2":"xxxx",
        "key_C3":"xxxx",
        "key_C4":"xxxx",
        "key_C5":"xxxx",
        "key_D1":"xxxx",
        "key_D2":"xxxx",
        "key_D3":"xxxx",
        "key_D4":"xxxx",
        "key_D5":"xxxx",
        "key_E1":"xxxx",
        "key_E2":"xxxx",
        "key_E3":"xxxx",
        "key_E4":"xxxx",
        "key_E5":"xxxx",
        "key_F1":"xxxx",
        "key_F2":"xxxx",
        "key_F3":"xxxx",
        "key_F4":"xxxx",
        "key_F5":"xxxx"
    }
    somfy = Somfy(url, password, codes)
    somfy.login()
    print(somfy.get_state())
    somfy.logout()
