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


import os
from random import SystemRandom
import binascii


APPTOKEN = 'Project Transhybrid Ekadata'
DEFAULT_ENTROPY = 32

class TranshybridSignInApi(http.Controller):


	def token_bytes(self,nbytes=None):
		if(nbytes is None):
			nbytes = DEFAULT_ENTROPY

		return os.urandom(nbytes)

	def token_hex(self, nbytes=None):
		return binascii.hexlify(self.token_bytes(nbytes)).decode('ascii')


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

		headers = {'Content-Type': 'application/json','Status':400}
		resUsersModel = request.env['res.users']
		resUserTokenModel = request.env['res.users.token']

		body = request.jsonrequest

		'''
		haduh = request.httprequest
		print " ===========",haduh
		print(type(haduh))
		print(haduh.status_code)
		'''

		try:
			username = body['username']
			password = body['password']
		except:
			
			output = {
				'code': 401,
				'status':401,
				'message':'Username And Password Can Not Be Empty',
			}

			Response.status = "400"
			return output
			#return output
			#return Response(json.dumps(output),headers=headers)



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

				tokenNumber = self.token_hex()
				tokenNumber = str(tokenNumber)
				
				dataUserToken = resUserTokenModel.sudo().search([('res_id','=',int(dataUser.id))],limit=1,order="id desc")
				if(dataUserToken):
					# JIKA SUDAH ADA MAKA UPDATE
					for outTokenNumber in dataUserToken:
						outTokenNumber.token_data = tokenNumber

				else:
					# JIKA BELUM ADA INPUT BARU
					resUserTokenModel.sudo().create({'res_id':dataUser.id,'token_data':tokenNumber})


				listAvatar = []
				listAvatar.append(str("data:image/png;base64,"))
				listAvatar.append(str(uid.image))
				outAvatar = ''.join(listAvatar)
				
				Response.status = "200"
				return{
					"username": username,
					"name": uid.name,
					"token":tokenNumber,
					"avatar": outAvatar,
					"code" : 200,
					"message" : "OK",
				}
				
			else:
				Response.status = "404"
				return {
						  "code": 404,
						  "message": "User Is Not Found"
						}
			

		else:

			Response.status = "404"
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