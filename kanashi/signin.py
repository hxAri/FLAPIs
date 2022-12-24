#!/usr/bin/env python

#
# @author Ari Setiawan
# @create 23.05-2022
# @github https://github.com/hxAri/Kanashi
#
# Kanashi Copyright (c) 2022 - Ari Setiawan <ari160824@gmail.com>
# Kanashi Licence under GNU General Public Licence v3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Kanashi is not affiliated with or endorsed, endorsed at all by
# Instagram or any other party, if you use the main account to use this
# tool we as Coders and Developers are not responsible for anything that
# happens to that account, use it at your own risk, and this is Strictly
# not for SPAM.
#

from datetime import datetime
from random import randint
from time import sleep

from kanashi.context import Context
from kanashi.error import Alert, Error
from kanashi.object import Object
from kanashi.utils import JSON, JSONError, Util

#[kanashi.SignInError]
class SignInError( Error ):
	
	# Login Detected as Spam.
	# If Spam has detected please wait for 24 hours.
	SPAM_DETECTED = 85181
	
	# User Notfound.
	USER_NOTFOUND = 85283
	
	# Invalid Password
	USER_PASSWORD = 85392
	
#[kanashi.SignIn2FAInvalidCode]
class SignIn2FAInvalidCode( SignInError ):
	pass
	
#[kanashi.SignIn2FARequired]
class SignIn2FARequired( Object ):
	pass
	
#[kanashi.SignInCheckpoint]
class SignInCheckpoint( Object ):
	pass
	
#[kanashi.SignInSuccess]
class SignInSuccess( Object ):
	pass
	

#[kanashi.BaseSignIn]
class BaseSignIn( Context ):
	
	#[BaseSignIn( Object app )]
	def __init__( self, app ):
		
		# Copy Request and Session instance.
		self.request = app.request
		self.session = app.session
		
		# Call parent constructor.
		super().__init__( app )
		
	#[BaseSignIn.cookie( String csrftoken, String sessionid, String datr, String dpr, String ds_user_id, String ig_did, String mid, String rur, String shbid, String shbts, String uagent )]
	def cookie( self, csrftoken, sessionid, datr, dpr, ds_user_id, ig_did, mid, rur, shbid, shbts, uagent ):
		pass
	
	#[BaseSignIn.csrftoken()]
	def csrftoken( self ):
		self.err = None
		try:
			self.app.session.headers.update({
				"Origin": "https://www.instagram.com",
				"Referer": "https://www.instagram.com/"
			})
			resp = self.app.request.get( "https://i.instagram.com/api/v1/si/fetch_headers", timeout=10 )
			if resp:
				return( dict( resp.cookies )['csrftoken'] )
			if self.app.request.err:
				self.err = self.app.request.err
		except KeyError:
			self.err = Error( "Csrftoken prelogin is not available" )
		return( False )
		
	#[BaseSignIn.password( String username, String password )]
	def password( self, username, password, csrftoken ):
		self.app.session.headers.update({
			"Origin": "https://www.instagram.com",
			"Referer": "https://www.instagram.com/",
			"X-CSRFToken": csrftoken
		})
		resp = self.app.request.post( "https://www.instagram.com/accounts/login/ajax/", allow_redirects=True, data={
			"username": username,
			"enc_password": "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format( int( datetime.now().timestamp() ), password ),
			"queryParams": {},
			"optIntoOneTap": "false"
		})
		
	#[BaseSignIn.verify( SignIn2FARequired info, Int method )]
	def verify( self, info, method ):
		try:
			self.output( "verify", "Enter the verification code" if method == 1 else "Enter the backup code" )
			code = self.input( "code", number=True )
			self.app.session.headers.update({
				"Origin": "https://www.instagram.com",
				"Referer": "https://www.instagram.com/accounts/login/two_factor?next=%2F"
			})
			resp = self.app.request.post( "https://www.instagram.com/accounts/login/two_factor/", allow_redirects=True, timeout=10, data={
				"identifier": info.identifier,
				"trust_signal": "true",
				"username": info.username,
				"verificationCode": code,
				"verification_method": method,
				"queryParams": {
					"next":"/"
				}
			})
			if resp:
				json = resp.json()
				print( json )
				exit()
			if self.app.request.err:
				self.err = self.app.request.err
		except AttributeError as e:
			self.err = e
		return( False )
	

#[kanashi.SignIn]
class SignIn( BaseSignIn, Util ):
	
	#[SignIn.cookie( String csrftoken, String sessionid, String datr, String dpr, String ds_user_id, String ig_did, String mid, String rur, String shbid, String shbts, String uagent )]
	def cookie( self, csrftoken=None, sessionid=None, datr=None, dpr=None, ds_user_id=None, ig_did=None, mid=None, rur=None, shbid=None, shbts=None, uagent=None ):
		cookies = {
			"csrftoken": csrftoken or self.input( "csrftoken" ),
			"sessionid": sessionid or self.input( "sessionid" ),
			"datr": datr or self.input( "datr" ),
			"dpr": dpr or self.input( "dpr" ),
			"ds_user_id": ds_user_id or self.input( "ds_user_id", number=True ),
			"ig_did": ig_did or self.input( "ig_did" ),
			"mid": mid or self.input( "mid" ),
			"rur": rur or self.input( "rur" ),
			"shbid": shbid or self.input( "shbid" ),
			"shbts": shbts or self.input( "shbts" )
		}
		if uagent == None:
			if self.input( "Use default User-Agent [Y/n]", default=[ "Y", "y", "N", "n" ] ).upper() == "N":
				uagent = self.input( "User-Agent" )
			else:
				uagent = self.app.config.browser.default
		pass
		
	#[SignIn.csrftoken()]
	def csrftoken( self ):
		csrftoken = BaseSignIn.csrftoken( self )
		if csrftoken:
			return( csrftoken )
		else:
			self.emit( self.err )
			if self.input( "Try again [Y/n]", default=[ "Y", "y", "N", "n" ] ).upper() == "Y":
				return( self.csrftoken() )
		return( False )
		
	#[SignIn.password( String username, String password )]
	def password( self, username=None, password=None, csrftoken=None ):
		if csrftoken == None:
			csrftoken = self.csrftoken()
			sleep( 1 )
		if csrftoken:
			if username == None:
				username = self.input( "username" )
			if password == None:
				password = self.getpass( "password" )
			#signin = BaseSignIn.password( self, username, password, csrftoken )
			self.app.session.headers.update({
				"Origin": "https://www.instagram.com",
				"Referer": "https://www.instagram.com/",
				"X-CSRFToken": csrftoken
			})''
			signin = self.app.request.post( "https://www.instagram.com/accounts/login/ajax/", allow_redirects=True, data={
				"username": username,
				"enc_password": "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format( int( datetime.now().timestamp() ), password ),
				"queryParams": {},
				"optIntoOneTap": "false"
			})
			print( signin )
			print( self.app.request.err )
			print( self.app.request.response )
		else:
			self.app.main()
		
	#[SignIn.switch()]
	def switch( self ):
		pass
		
	#[SignIn.verify( SignIn2FARequired info, Int method )]
	def verify( self, info, method ):
		pass
	
