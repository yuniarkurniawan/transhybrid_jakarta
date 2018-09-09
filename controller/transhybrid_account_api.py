from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha512,pbkdf2_sha256
import base64
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

import os
import email
import email.encoders
import smtplib
import re
import urllib2
import json

import hashlib
import sys
import pydoc
import datetime
import time
import random
a_month_ago = datetime.datetime.today() - datetime.timedelta(days=30)
first_day_of_month = datetime.datetime.today().replace(day=1)

APPTOKEN = 'Project Transhybrid Ekadata'


class TranshybridAccountApi(http.Controller):
	

	def check_app_token(self,paramAppToken):

		appToken = hashlib.md5()
		appToken.update(APPTOKEN)
		appToken = appToken.hexdigest()

		if(str(paramAppToken)==str(appToken)):
			return True
		else:
			return False


	def get_user_token(self,paramUserToken,paramDataPool):

		kondisi = False
		resUserTokenModel = request.env['res.users.token']
		if(paramDataPool):
			for dataUser in paramDataPool:
				dataUserToken = resUserTokenModel.sudo().search([('res_id','=',dataUser.id)],limit=1,order="id desc")
				if(dataUserToken):
					if(dataUserToken.token_data==int(paramUserToken)):
						kondisi = True

		
		return kondisi


	def get_time_token_configuration(self):

		listTimeTokenConfiguration = []

		timeTokenConfigurationModel = request.env['transhybrid.configuration']
		timeTokenConfigurationPool = timeTokenConfigurationModel.sudo().search([('is_time_token_configuration','=',True)])

		if(timeTokenConfigurationPool):
			for outData in timeTokenConfigurationPool:

				new_dict = {}
				
				new_dict['time_expired'] = outData.time_expired

				listTimeTokenConfiguration.append(new_dict)


		return listTimeTokenConfiguration


	def get_email_server_configuration(self):

		listEmailConfiguration = []
		configurationModel = request.env['transhybrid.configuration']
		configurationPool = configurationModel.sudo().search([('is_email_server_configuration','=',True)])

		if(configurationPool):
			for outData in configurationPool:
				
				new_dict={}

				new_dict['email_host'] = outData.email_host
				new_dict['email_port'] = outData.email_port
				
				new_dict['email_sender'] = outData.email_sender
				new_dict['email_password'] = outData.email_password
					
				listEmailConfiguration.append(new_dict)
		
		
		return listEmailConfiguration


	def check_empty_input_user(self,paramInputUser):

		kondisi = False
		tmpParamInputUser = paramInputUser
		tmpParamInputUser = str(tmpParamInputUser)
		tmpParamInputUser = tmpParamInputUser.strip()

		if(len(tmpParamInputUser)==0):
			kondisi = True

		return kondisi


	@http.route("/account/check_username/", auth='none',csrf=False, type='json')
	def check_username(self,**values):

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		
		body = request.jsonrequest
		email = body['email']

		if(self.check_empty_input_user(email)):
			return {
					'code': 404,
					'message': 'Email Can Not Be Empty'
				}


		if(self.check_app_token(headerToken)):

			resUserModel = request.env['res.users']
			

			validEmailUser = resUserModel.sudo().search([
								('login', '=', email)
								])

			if(validEmailUser):

				return {
					'code' : 200,
					'message' : 'OK',
					'is_registered': True
				}			
			else:
				return {
					'code': 404,
					'message': 'User Is Not Found'
				}
		else:

			return {
					'code': 404,
					'message': 'API Key Is Not Same'
				}

	
	@http.route("/account/request_otp/", auth='none',csrf=False, type='json')
	def request_otp(self,**values):

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')

		tmpHostEmail = ""
		tmpPortEmail = ""
		
		tmpPengirimEmail = ""
		tmpPasswordEmail = ""		

		TIME_OTP = 0
		listTimeTokenConfiguration = []
		listTimeTokenConfiguration = self.get_time_token_configuration()
		if(len(listTimeTokenConfiguration)<=0):

			return {
					'code': 404,
					'message': 'Time Token Expired Configuratioin Is Not Found'
				}
		else:

			for outDataTimeToken in listTimeTokenConfiguration:
				TIME_OTP = outDataTimeToken['time_expired']


			if(TIME_OTP<=0):
				return {
					'code': 404,
					'message': 'Time Token Expired Can Not Be 0'
				}


		listEmailconfiguration = []
		listEmailconfiguration = self.get_email_server_configuration()
		if(len(listEmailconfiguration)<=0):

			return {
					'code': 404,
					'message': 'Email Server Is Not Found'
				}
		else:

			for outDataEmail in listEmailconfiguration:

				tmpHostEmail = outDataEmail['email_host']
				tmpPortEmail = outDataEmail['email_port']
				
				tmpPengirimEmail = outDataEmail['email_sender']
				tmpPasswordEmail = outDataEmail['email_password']



			if(tmpHostEmail==False or tmpPortEmail==False or tmpPengirimEmail==False or tmpPasswordEmail==False):
				return {
						'code': 404,
						'message': 'Email Server Has Not Been Configured'
					}



		if(self.check_app_token(headerToken)):

			resUserModel = request.env['res.users']
			resUserTokenModel = request.env['res.users.token']

			body = request.jsonrequest
			phone = body['phone']
			
			phone = str(phone)
			tmpCheck = phone.isdigit()

			dataPool = False
			dataPhonePool = resUserModel.sudo().search([('partner_id.phone','=',phone)])
			if(dataPhonePool):
				dataPool = dataPhonePool
			else:
				dataPool = resUserModel.sudo().search([('login','=',phone)])


			if(dataPool):

				for dataUser in dataPool:

					r = random.randint(1111,9999)
					tokenNumber = "%04d" % r

					# --------- begin email

					tmpMessageEmail = "Your token number is " + tokenNumber
					

					msg = MIMEMultipart()
					msg['From'] = tmpPengirimEmail
					msg['To'] = ''.join(dataUser.login)
					msg['Date'] = email.Utils.formatdate(localtime=True)
					msg['Subject'] = "Token Number"
					msg.attach(MIMEText(tmpMessageEmail)) 

					
					try:

						# ---------- begin email
						tmpPesan = "Your token number is " + tokenNumber
						server = smtplib.SMTP(tmpHostEmail, int(tmpPortEmail))

						server.ehlo()
						server.starttls()
						server.login(tmpPengirimEmail, tmpPasswordEmail)
						 
						server.sendmail(tmpPengirimEmail, dataUser.login, msg.as_string())
						server.quit()

						# --------- end email

						resUserTokenModel.sudo().create({'res_id':dataUser.id,'token_data':tokenNumber})
						
						return {
							'code':200,
							'message':'OK',
							'expired_time': TIME_OTP,
						}

					except:

						return {
							'code':404,
							'message':'Email Is Not Valid'
						}
					
			else:

				return {
					'code': 404,
					'message': 'User Is Not Found'
				}
		else:

			return {
					'code': 404,
					'message': 'API Key Is Not Same'
				}
		
	
	@http.route("/account/verify/",auth='none',csrf=False, type='json')		
	def verify_otp(self,**values):

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		
		body = request.jsonrequest
		phone = body['phone']
		otp = body['otp']


		if(self.check_empty_input_user(phone)):
			return {
					'code': 404,
					'message': 'Phone Can Not Be Empty'
				}

		if(self.check_empty_input_user(otp)):
			return {
					'code': 404,
					'message': 'Phone Can Not Be Empty'
				}



		TIME_OTP = 0
		listTimeTokenConfiguration = []
		listTimeTokenConfiguration = self.get_time_token_configuration()
		if(len(listTimeTokenConfiguration)<=0):

			return {
					'code': 404,
					'message': 'Time Token Expired Configuratioin Is Not Found'
				}
		else:

			for outDataTimeToken in listTimeTokenConfiguration:
				TIME_OTP = outDataTimeToken['time_expired']
				

			if(TIME_OTP<=0):
				return {
					'code': 404,
					'message': 'Time Token Expired Can Not Be 0'
				}



		if(self.check_app_token(headerToken)):

			resUserModel = request.env['res.users']
			resUserTokenModel = request.env['res.users.token']
			
			dataPool = False
			dataPhonePool = resUserModel.sudo().search([('partner_id.phone','=',phone)])
			if(dataPhonePool):
				dataPool = dataPhonePool
			else:
				dataPool = resUserModel.sudo().search([('login','=',phone)])


			if(dataPool):

				for dataUser in dataPool:
					dataUserToken = resUserTokenModel.sudo().search([('res_id','=',dataUser.id)],limit=1,order="id desc")
					
					if(dataUserToken):
						
						dateOne = datetime.datetime.strptime(dataUserToken.time_token,"%Y-%m-%d %H:%M:%S")
						temp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
						dateTwo = datetime.datetime.strptime(temp,"%Y-%m-%d %H:%M:%S")

						totalSecond = dateTwo - dateOne
						totalSecond = totalSecond.seconds

						if(dataUserToken.token_data==int(otp)):
							
							
							if(totalSecond<=TIME_OTP):		

								return {
								  'code': 200,
								  'message': 'Token Verify Success'
								}
							else:
								
								# dikembalikan ke login screen
								return {
									'code': 400,
									'message': 'Has Timed Out After 3 Minutes'
								}

						else:

							if(totalSecond<=TIME_OTP):

								# masih dihalaman yang sama
								return {
										'code': 403,
										'message': 'Token Is Not Valid'
									}

							else:

								# dikembalikan ke login screen
								return {
										'code': 400,
										'message': 'Token Is Not Valid'
									}
					else:

						return {
							'code':400,
							'message': 'Token Is Not Valid'
						}
						
			else:

				return {
					'code': 404,
					'message': 'User Is Not Found'
				}
		else:

			return {
					'code': 404,
					'message': 'API Key Is Not Same'
				}

	@http.route("/account/resetPassword/",auth='none',csrf=False,type='json')
	def reset_password(self,**values):

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		
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


		if(self.check_app_token(headerToken)):

			resUserModel = request.env['res.users']
			changePasswordUserModel = request.env['change.password.user']
			
			

			if(len(password)<5):
				return {
					"code": 422,
					"message":"Password Minimum Length Must Be 5 Characters"
				}


			dataUser = resUserModel.sudo().search([
								('login', '=', username)
								])


			if(dataUser):
				dataUser.sudo(dataUser.id).password = password
				
				return{
					"code": 200,
					"message": "Reset Password Success"
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


	def get_position_employee(self,paramUid):

		resGroupsModel = request.env['res.groups']
		dataGroupPool = resGroupsModel.sudo().search([('users','=',paramUid),('name', 'ilike', 'transhybrid')],limit=1) 

		tmpPosition = ""
		for outData in dataGroupPool:
			tmpPosition = outData.name
			
		return tmpPosition


	@http.route("/account/edit/",auth='none',csrf=False,type='json')
	def edit_profile(self,**values):

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		headerTokenUser = headerData.get('token')
		
		resUserModel = request.env['res.users']
		body = request.jsonrequest
		name = body['name']
		user_phone = body['phone']
		user_address = body['address']
		

		if(self.check_empty_input_user(name)):
			return {
					'code': 404,
					'message': 'Name Can Not Be Empty'
				}

		if(self.check_empty_input_user(user_phone)):
			return {
					'code': 404,
					'message': 'Phone Can Not Be Empty'
				}

		if(self.check_empty_input_user(user_address)):
			return {
					'code': 404,
					'message': 'Address Can Not Be Empty'
				}



		if(body.has_key('avatar')):
			image = body['avatar']
			

		resUserTokenModel = request.env['res.users.token']
		resUserModel = request.env['res.users']

		if(self.check_app_token(headerToken)):		
			
			todays = datetime.datetime.today()
			tokenDataPool = resUserTokenModel.sudo().search([('token_data','=',headerTokenUser)],limit=1,order="id desc")
		
			if(tokenDataPool):
				for outData in tokenDataPool:
					
					dataUser = resUserModel.sudo(outData.res_id.id).search([('id','=',outData.res_id.id)])
					if(dataUser):
						listImageAddres = []
						for outUser in dataUser:
							
							outUser.sudo(outUser.id).name = name
							outUser.sudo(outUser.id).user_phone = user_phone
							
							outUser.sudo(outUser.id).partner_id.phone = user_phone
							outUser.sudo(outUser.id).partner_id.mobile = user_phone

							outUser.sudo(outUser.id).user_address = user_address
							outUser.sudo(outUser.id).partner_id.street = user_address

							if(body.has_key('avatar')):
								outUser.sudo(outUser.id).image = image

							
							listAvatar = []
							listAvatar.append(str("data:image/png;base64,"))
							listAvatar.append(str(outUser.image))
							outAvatar = ''.join(listAvatar)



						return {
						  "name": name,
						  "avatar": outAvatar,
						  "phone": user_phone,
						  "email":dataUser.email,
						  "address": user_address,
						  "position": self.get_position_employee(dataUser.id),
						  "code":200,
						  "message":"Update Data Success"
						}

					else:

						return {
						  'code': 404,
						  'message': 'User Is Not Found'
						}

			else:

				return {
				  'code': 404,
				  'message': 'Token Is Not Valid'
				}


		else:

			return {
				  'code': 404,
				  'message': 'API Key Is Not Same'
				}



	@http.route("/account/changePassword/",auth='none',csrf=False,type='json')
	def change_password(self,**values):

		resUserModel = request.env['res.users']

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		headerTokenUser = headerData.get('token')
		
		resUserModel = request.env['res.users']
		body = request.jsonrequest
		username = body['username']
		oldPassword = body['oldPassword']
		newPassword = body['newPassword']


		if(self.check_empty_input_user(username)):
			return {
					'code': 404,
					'message': 'Username Can Not Be Empty'
				}

		if(self.check_empty_input_user(oldPassword)):
			return {
					'code': 404,
					'message': 'Old Password Can Not Be Empty'
				}

		if(self.check_empty_input_user(newPassword)):
			return {
					'code': 404,
					'message': 'New Password Can Not Be Empty'
				}


		dataPool = resUserModel.sudo().search([
								('login', '=', username)
								])

		if(len(newPassword)<5):
			return {
				"code": 422,
				"message":"Password Minimum Length Must Be 5 Characters"
			}

		
		if(self.check_app_token(headerToken) and self.get_user_token(headerTokenUser,dataPool)):

			if(dataPool):

				dataUser = resUserModel.browse(int(dataPool.id))
				
				#print "Data User : ", dataUser.id
				try:
					dataUser.sudo(dataUser.id).change_password(oldPassword,newPassword)
					return {
					  "code": 200,
					  "message": "Password Has Been Change"
					}
				except:
					return{
						"code":400,
						"message":"Old Password Is Wrong"
					}
				
			else:

				return{
					"code": 404,
					"message": "User Is Not Found"
				}

		else:

			return {
				  "code": 404,
				  "message": "API Key And User Is Not Valid"
				}
		