from odoo import http
from odoo.http import request, Response
import dateutil.parser
import hashlib

import datetime
import dateutil.parser
import pytz
import json
import os
import base64

APPTOKEN = 'Project Transhybrid Ekadata'

class TranshybridSignInApi(http.Controller):


	def check_app_token(self,paramAppToken):

		appToken = hashlib.md5()
		appToken.update(APPTOKEN)
		appToken = appToken.hexdigest()

		if(str(paramAppToken)==str(appToken)):
			return True
		else:
			return False


	def check_empty_input_user(self,paramInputUser):

		kondisi = False
		tmpParamInputUser = paramInputUser
		tmpParamInputUser = tmpParamInputUser.strip()

		if(len(tmpParamInputUser)==0):
			kondisi = True

		return kondisi




	@http.route("/signin/",auth='none',csrf=False, type='json')
	def signIn(self,**values):

		resUsersModel = request.env['res.users']

		body = request.jsonrequest
		username = body['username']
		password = body['password']

		if(self.check_empty_input_user(username)):
			return {
					'code': 404,
					'message': 'Username Can Not Be Empty'
				}

		if(self.check_empty_input_user(password)):
			return {
					'code': 404,
					'message': 'Password Can Not Be Empty'
				}


		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')


		dbname = ''
		if request.session.db:
			dbname = request.session.db
			uid = request.session.uid
		elif dbname is None:
			dbname = db_monodb()


		uid = resUsersModel.authenticate(dbname, username, password, None)
		uid = resUsersModel.sudo().browse(uid)


		if(uid):

			
			dataUser = resUsersModel.sudo().search([('id','=',uid.id)],limit=1,order="id desc")
			if(dataUser):

				listAvatar = []
				listAvatar.append(str("data:image/png;base64,"))
				listAvatar.append(str(uid.image))
				outAvatar = ''.join(listAvatar)
				
				return{
					"username": username,
					"name": uid.name,
					"avatar": outAvatar,
					"code" : 200,
					"message" : "OK",
				}
				
			else:

				return {
						  "code": 404,
						  "message": "User Is Not Found"
						}
			

		else:

			return {
				  "code": 404,
				  "message": "User And Password Is Not Found"
				}




	@http.route("/signin_original/",auth='none',csrf=False, type='json')
	def signInOriginal(self,**values):

		resUsersModel = request.env['res.users']

		body = request.jsonrequest
		username = body['username']
		password = body['password']

		if(self.check_empty_input_user(username)):
			return {
					'code': 404,
					'message': 'Username Can Not Be Empty'
				}

		if(self.check_empty_input_user(password)):
			return {
					'code': 404,
					'message': 'Password Can Not Be Empty'
				}


		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')


		dbname = ''
		if request.session.db:
			dbname = request.session.db
			uid = request.session.uid
		elif dbname is None:
			dbname = db_monodb()


		uid = resUsersModel.authenticate(dbname, username, password, None)
		uid = resUsersModel.sudo().browse(uid)


		if(uid):

			if(self.check_app_token(headerToken)):


				dataUser = resUsersModel.sudo().search([('id','=',uid.id)],limit=1,order="id desc")
				if(dataUser):

					listAvatar = []
					listAvatar.append(str("data:image/png;base64,"))
					listAvatar.append(str(uid.image))
					outAvatar = ''.join(listAvatar)
					
					return{
						"username": username,
						"name": uid.name,
						"avatar": outAvatar,
						"code" : 200,
						"message" : "OK",
					}
					
				else:

					return {
							  "code": 404,
							  "message": "User Is Not Found"
							}
			else:

				return {
					  "code": 404,
					  "message": "API Key Is Not Same"
					}

		else:

			return {
				  "code": 404,
				  "message": "User And Password Is Not Found"
				}