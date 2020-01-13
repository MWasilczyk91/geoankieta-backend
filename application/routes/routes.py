# coding: utf-8

from flask import jsonify, request
from . import bpRoutes
from ..models import db, Users, Surveys, Answers

@bpRoutes.route('/api')
def index():
    return 'API geoankiety: OK'

@bpRoutes.route('/api/user', methods = ["POST"])
def addUser():
    """
    Dodaje nowego użytkownika do bazy jeśli nie istniał.
    Zwraca informację czy użytkownik o podanym mailu już istniał w bazie danych (potrzebne dla frontu)
    oraz na którym etapie powinien wrócić do ankiety (klucz screen określa dany ekran we frontendzie).
    Payload:
    {
        email: "",
        name: "",
        surname: "",
        specialty: "",
        title: "",
        regions: "wpn, kpn"
    }
    """
    data = request.get_json(force=True)#.get('state', {}).get('userData', {})
    try:
        user = Users.get(Users.email == data['email'])
        existing = True
    except Users.DoesNotExist:
        existing = False
        try:
            user = Users.create(
                email = data['email'],
                imie = data['name'],
                nazwisko = data['surname'],
                specjalnosc = data['specialty'],
                tytul = data['title'],
                obszary = data['regions']
            )
        except KeyError:
            return jsonify({"Błąd" : "Niepoprawny payload. Brak wymaganych danych o użytkowniku."}), 400
    except KeyError:
        return jsonify({"Błąd" : "Niepoprawny payload. Brak wymaganych danych o użytkowniku."}), 400
    return jsonify({
        'user' : data['email'],
        'existing' : existing,
        'screen' : user.screen,
        'regions' : user.obszary
    }), 200

@bpRoutes.route('/api/save', methods = ["POST"])
def saveResults():
    """
    Zapisuje dane ankietowe dla danej mapy do bazy danych.
    Tworzony jest 1 wiersz do tabeli 'ankiety' i 5 wierszy do tabeli 'odpowiedzi', a w przypadku gdy podano wartość wagi
    to zamiast tworzenia wykonywany jest update (dopisanie wagi) na istniejących rekordach z tabeli 'odpowiedzi'.
    Payload w przypadku tworzenia nowych wierszy:
    {
        email: "",
        screen: "",
        region : "",
        map: "",
        reason: "",
        survey: [
            {
                grade: 2,
                certainty: 100,
                value1: 80,
                value2: 70
            }
        ]
    }
    Dla map DEM przesyłane są osobno skrajne wartości przedziałów wysokości względnej: 'value1' i 'value2', które do bazy trafiają połączone w jeden string. 
    W przypadku pozostałych map zamiast nich będzie tylko klucz 'values'.
    Payload w przypadku updatu (dopisanie wag):
    {
        email: "",
        screen: "",
        region: "",
        map: "",
        survey: [
            {
                grade: 2,
                percent: 25
            }
        ]
    }
    """
    data = request.get_json(force=True)
    #Sprawdzanie czy user istnieje
    try:
        user = Users.get(Users.email == data['email'])
    except Users.DoesNotExist:
        return jsonify({"Błąd" : "Użytkownik o podanym emailu nie istnieje."}), 404
    except KeyError:
        return jsonify({"Błąd" : "Niepoprawny payload. Brak klucza email."}), 400
    if not data.get('screen'):
        return jsonify({"Błąd" : "Niepoprawny payload. Brak klucza screen lub pusta wartość"}), 400
    else:
        screen = data['screen']
    #Początek transakcji SQLite (autocommit + rollback)
    with db.atomic():
        #Dodawanie nowego lub pobieranie obecnego wpisu z tabeli "ankiety"
        try:
            if data['survey'][0].get('percent'): #jeśli jest ten klucz to ma być wykonany update istniejącego wpisu o wartość wagi
                action = 'update'
                try:
                    survey = Surveys.get(
                        (Surveys.uzytkownik == user.id) &\
                        (Surveys.mapa == data['map']) &\
                        (Surveys.obszar == data['region'])
                    )
                except Surveys.DoesNotExist:
                    return jsonify({"Błąd" : "Próba update na nieistniejącej ankiecie. Brak wpisu w tabeli ankiety, gdzie uzytkownik={}, mapa={}, obszar={}.".format(
                        user.id,
                        data['map'],
                        data['region']
                    )}), 404
            else: #nie ma jeszcze wpisu i trzeba go utworzyć
                action = 'create'
                survey = Surveys.create(
                    uzytkownik = user.id,
                    obszar = data['region'],
                    mapa = data['map'],
                    uzasadnienie = data['reason']
                )
        except KeyError:
            return jsonify({"Błąd" : "Niepoprawny payload. Brak klucza region, map lub reason."}), 400
        except IndexError:
            return jsonify({"Błąd" : "Niepoprawny payload. Pusta lista survey."}), 400
        #Dodawanie wpisów (lub update pola waga) do tabeli "odpowiedzi" dla bieżącej ankiety 
        try:
            for answer in data['survey']:
                if answer.get('percent'): 
                    Answers.update(waga = answer['percent'])\
                        .where(
                            (Answers.ankieta_id == survey.id) &\
                            (Answers.ocena == answer['grade'])
                        )\
                        .execute()
                    
                else:
                    Answers.insert(
                        ankieta_id = survey.id,
                        czynnik = answer['values'] if answer.get('values') else '{}, {}'.format(answer['value1'], answer['value2']),
                        ocena = answer['grade'],
                        pewnosc = answer['certainty']
                    ).execute()
        except KeyError:
            if action == 'create':
                #usunięcie utworzonego wcześniej wpisu w tabeli "ankiety"
                survey.delete_instance()
            return jsonify({"Błąd" : "Niepoprawny payload. Brak części wymaganych danych."}), 400
        user.update(screen=screen).execute()
    return jsonify({'%sd_survey' % action : survey.id}), 200
