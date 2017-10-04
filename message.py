# -*- coding: utf-8 -*-
from flask import Flask, session, render_template, redirect, url_for, request
import random, string, re
from urllib2 import Request, urlopen, HTTPError
from werkzeug import SharedDataMiddleware
import json, urllib
app_url = '/makosak/message'
app = Flask(__name__, static_url_path='/makosak/message/static', static_folder='static')
app.secret_key = "SecretAppKeyXxX"
@app.route(app_url + '/login')
def login():
	if session.has_key('uid'):
		return redirect(app_url + '/mailbox')
	else:
		return render_template('/login.html')

@app.route(app_url + '/check', methods=['POST', 'GET'])
def check():
	values_dict = {}
	values_dict['login'] = request.form["login"]
	values_dict['password'] = request.form["password"]
	values = json.dumps(values_dict)
	headers = {'Content-Type': 'application/json'}
	requestedData = Request('http://edi.iem.pw.edu.pl/bach/mail/api/login', data=values, headers=headers)
	try:
		response = urlopen(requestedData)
		response_dict = json.load(response)
		if response.getcode() == 200 and response_dict['message'] == 'OK':
			session['token'] = response_dict['token']
			session['uid'] = response_dict['uid']
			headers = {'Content-Type' : 'application/json', 'token' : session['token']}
                	requestedData2 = Request('http://edi.iem.pw.edu.pl/bach/mail/api/users/' + str(session['uid']), headers=headers)
			response2 = urlopen(requestedData2)
			response2_dict = json.load(response2)
			session['username'] = response2_dict['username']
			return redirect(app_url + '/mailbox')
		
	except HTTPError, error:
		print error.code 
		return render_template('/login_error.html')
@app.route(app_url + '/mailbox')
def mailbox():
	if session.has_key('uid'):
		return render_template('/mailbox.html', username = session['username'], message = "Witaj uzytkowniku, wybierz co chcesz zobic z panelu po lewej stro	nie.")
	else:
		return redirect(app_url + '/login')

@app.route(app_url + '/new_message')
def new_message():
	if session.has_key('uid'):
                return render_template('/new_message.html')
        else:
                return redirect(app_url + '/login')

@app.route(app_url + '/send', methods=['POST', 'GET'])
def send():
	if session.has_key('uid'):
		headers = {"Content-Type" : 'application/json', "token" : session['token']}
		to = request.form["new_msg_to"]
		try:
			requestedData2 = Request('http://edi.iem.pw.edu.pl/bach/mail/api/users/' + str(to), headers=headers)
                	response2 = urlopen(requestedData2)
                	response2_dict = json.load(response2)
			destination = response2_dict['uid']
		except Exception:
			return render_template('/mailbox.html', username = session['username'], message = "Nie udalo sie wyslac wiadomosci. Nie ma takiego uzytkownika!")
		
		values_dict = {}
		values_dict['content'] = request.form["new_msg_content"]
		values_dict['to'] = int(destination)
		values_dict['from'] = int(session['uid'])
		values_dict['subject'] = request.form["new_msg_subject"]
		values = json.dumps(values_dict)
		if values_dict['to'] == values_dict['from']:
			return render_template('/mailbox.html', username = session['username'], message = "Nie udalo sie wyslac wiadomosci. Nie przewidziano mozliwosci wysylania wiadomosci do samego siebie.")
		if values_dict['to'] == 1 or values_dict['to'] == 2 or values_dict['to'] == 3 or values_dict['to'] == 4:
			requestedData = Request('http://edi.iem.pw.edu.pl/bach/mail/api/messages', data=values, headers=headers)
			response = urlopen(requestedData)
			response_dict = json.load(response)
			if response_dict.has_key('id'):
				return render_template('/mailbox.html', username = session['username'], message = "Wiadomosc wyslana.")
			else:
				return redirect(app_url + '/login')
		else:
			return render_template('/mailbox.html', username = session['username'], message = "Nie udalo sie wyslac wiadomosci. Nie ma uzytkownika o podanym identyfikatorze.")

@app.route(app_url + '/logout')
def logout():
	session.clear()
	return redirect(app_url + '/login')

@app.route(app_url + '/inbox', methods=['GET'])
def received():
	return message_list("inbox")

@app.route(app_url + '/outbox', methods=['GET'])
def sent():
	return message_list("outbox")

@app.route(app_url + '/delete/<msg_id>', methods=['DELETE'])
def delete(msg_id):
	if 'uid' in session:
        	headers = {"token" : session['token'], "Content-Type" : 'application/json'}
        	requestedData = Request("http://edi.iem.pw.edu.pl/bach/mail/api/messages/" + str(msg_id), headers=headers)
		requestedData.get_method = lambda: 'DELETE'
		response = urlopen(requestedData).read()
		return render_template('/alert.html', alert  = "Usunieto wiadomosc.")
	else:
                return redirect(app_url + '/login')

@app.route(app_url + '/no_delete')
def no_delete():
	return render_template('/alert.html', alert = "Nie udalo sie usunac wiadomosci. Mozna usunac wiadomosci o identyfikatorze wiekszym lub rownym 10.")

@app.route(app_url + '/change_unread/<msg_id>', methods=['PUT'])
def change_unread(msg_id):
        if 'uid' in session: 
		headers = {"token" : session['token'], "Content-Type" : 'application/json'}
                requestedData = Request("http://edi.iem.pw.edu.pl/bach/mail/api/messages/" + str(msg_id), headers=headers)
                response = urlopen(requestedData)
                response_dict = json.load(response)
		if response_dict['to'] == session['uid']:
			unread = response_dict['unread']
			if unread == False:
				set_unread = True
			else:
				set_unread = False
        		headers = {"Content-Type" : 'application/json'}
			values_dict = {"unread" : set_unread, "token" : session['token']}
			values = json.dumps(values_dict)
        		requestedData2 = Request("http://edi.iem.pw.edu.pl/bach/mail/api/messages/" + str(msg_id), data=values, headers=headers)
        		requestedData2.get_method = lambda: 'PUT'
        		response2 = urlopen(requestedData2).read()
			count_unread()
                	return render_template('/alert.html', alert = "Zmieniono status przeczytania wiadomosci na przeciwny.")
		else:
			return render_template('/alert.html', alert = "Nie mozna zmienic statusu wyslanych wiadomosci.")
	else:
		return redirect(app_url + '/login')

@app.route(app_url + '/count_unread', methods=['GET'])
def count_unread():
	if 'uid' in session:
		headers = {"Content-Type" : 'application/json', "token" : session['token']}
                requestedData = Request('http://edi.iem.pw.edu.pl/bach/mail/api/messages/unread/count', headers=headers)
		response = urlopen(requestedData)
		response_dict = json.load(response)
		unread = response_dict['unread_count']
		if unread > 0:
			return "Otworz skrzynke odbiorcza (Nieprzeczytanych:" + str(unread) + ")"
		else:
			return "Otworz skrzynke odbiorcza"
	else:
		return redirect(app_url + '/login')

@app.route(app_url + '/display/<msg_id>')
def display(msg_id):
	if 'uid' in session:
		headers = {"token" : session['token'], "Content-Type" : 'application/json'}
		requestedData = Request("http://edi.iem.pw.edu.pl/bach/mail/api/messages/" + str(msg_id), headers=headers)
		response = urlopen(requestedData)
		response_dict = json.load(response)
		if response.getcode() == 200:
			msg_subject = response_dict['subject']
			msg_from = response_dict['from']
			msg_to = response_dict['to']
			msg_content = response_dict['content']

			if response_dict['unread'] == True:
				change_unread(msg_id)		
			return render_template("single_message.html", msg_subject=msg_subject, msg_from=msg_from, msg_to=msg_to, msg_content=msg_content, id=msg_id)
		else:
			return render_template("alert.html", alert="Niestety nie udalo sie wyswietlic wiadomosci...")
	else:
		return redirect(app_url + '/login')


def message_list(msg_type):
	if 'uid' in session:
		headers = {"token": session['token'], "Content-Type" : 'application/json'}
		requestedData = Request("http://edi.iem.pw.edu.pl/bach/mail/api/messages", headers=headers)
		response = urlopen(requestedData)
		response_dict = json.load(response)
        	actors = []
       		subjects = []
		ids = []
		unread = []
        	for msg in response_dict:
        	        if msg_type == "inbox" and session['uid'] == msg["to"]:

				requestedData2 = Request('http://edi.iem.pw.edu.pl/bach/mail/api/users/' + str(msg['from']), headers=headers)
	        	        response2 = urlopen(requestedData2)
        	       		response2_dict = json.load(response2)
					
	       	                actors.append(response2_dict["username"])
        	                subjects.append(msg["subject"])
				ids.append(msg['id'])
				unread.append(msg['unread'])
			elif msg_type == "outbox" and session['uid'] == msg["from"]:
				
				requestedData2 = Request('http://edi.iem.pw.edu.pl/bach/mail/api/users/' + str(msg['to']), headers=headers)
                                response2 = urlopen(requestedData2)
                                response2_dict = json.load(response2)

				actors.append(response2_dict["username"])
				subjects.append(msg["subject"])
                                ids.append(msg['id'])
		return render_template("message_list.html", msg_type = msg_type, actors = actors, subjects = subjects, ids = ids, unread=unread)
	else:
		return redirect(app_url + '/login')
@app.route(app_url)
def normalpath():
	return redirect(app_url + '/mailbox')
@app.errorhandler(404)
def page_not_found(e):
	print("Nie znaleziono strony.")
	return "Nie znaleziono strony."
