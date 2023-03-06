######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Zulema25Bruh.'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
isLoggedIn = False
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from registeredUser")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from registeredUser")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return 
	user = User()
	user.id = email
	#cursor = mysql.connect().cursor()
	#cursor.execute("SELECT password FROM registeredUser WHERE email = '{0}'".format(email))
	#data = cursor.fetchall()
	#pwd = str(data[0][0] )
	#user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	
	#check if email is registered
	if cursor.execute("SELECT password FROM registeredUser WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress=True)

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		fName = request.form.get('fName')
		lName = request.form.get('lName')
		date = request.form.get('DOB')
		fullName = fName + ' ' + lName
		gender = request.form.get('gender')
		hometown = request.form.get('hometown')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO registeredUser (email, password, fName, lName, DOB, fullName, gender, hometown, contributionScore) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}', '{7}', '{8}')".format(email, password, fName, lName, date, fullName, gender, hometown, 0)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=fullName, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return render_template('register.html', supress=False)

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=getFullNameFromEmail(flask_login.current_user.id), message="Here's your profile")

@app.route('/browsePhotos')
def photoBrowsing():
	try:
		return render_template('photoBrowsing.html', name= getFullNameFromEmail(flask_login.current_user.id), photos = getAllPhotos(), base64=base64)
	except:
		return render_template('photoBrowsing.html', name= "anonymous", photos = getAllPhotos(), base64=base64)
	#if(not email):
	#	return render_template('photoBrowsing.html', name= "anonymous", photos = getAllPhotos(), base64=base64)
	#else:
	#	return render_template('photoBrowsing.html', name= getFullNameFromEmail(flask_login.current_user.id), photos = getAllPhotos(), base64=base64)
		
#useful methods here
def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photoBinary, pID, caption FROM photo_in_album WHERE userID = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM registeredUser WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM registeredUser WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
	
def getFullNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fullName FROM registeredUser WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT photoBinary, caption, userID, albumID FROM photo_in_album")
	photos =cursor.fetchall()
	photos = list(photos)
	newPhotos = list()
	for photo in photos:
		uid = photo[2]
		fullName = (getFullNameFromUserID(uid),)
		albumID = (photo[3])
		albumName = (getAlbumNameFromID(albumID, uid),)
		new = photo + fullName
		new = new + albumName
		newPhotos.append(new)
	return newPhotos


def getPhotosInAlbumForUser(albumName, userID):
	cursor = conn.cursor()
	albumID = getAlbumIDfromName(albumName, userID)
	cursor.execute("SELECT photoBinary, pID, caption FROM photo_in_album where albumID = '{0}' and userID = '{1}'".format(albumID, userID))
	photos =cursor.fetchall()
	return list(photos)

def getAlbumsForUser(userID):
	cursor = conn.cursor()
	cursor.execute("Select albumID, albumName from albums where ownerID = '{0}'".format(userID))
	albums = cursor.fetchall()
	return albums

def getAlbumIDfromName(albumName, userID):
	cursor = conn.cursor()
	cursor.execute("Select albumID from albums where albumName = '{0}' and ownerID = '{1}'".format(albumName, userID))
	albumID = cursor.fetchone()[0]
	return albumID
def getAlbumNameFromID(albumID, userID):
	cursor = conn.cursor()
	cursor.execute("Select albumName from albums where albumID = '{0}' and ownerID = '{1}'".format(albumID, userID))
	albumID = cursor.fetchone()[0]
	return albumID

def setUserContScore(userID, amount):
	#amount is how much to increase by. pass in a negative amount to decrease
	cursor = conn.cursor()
	newScore = int(getContributionScore(userID)) + amount
	cursor.execute("Update registeredUser set contributionScore= ('{0}') where userID = '{1}'".format(newScore, userID))
	conn.commit()

def getNumPhotosInAlbum(userID, albumID):
	cursor = conn.cursor()
	cursor.execute("Select count(*) from albums where albumID = '{0}' and ownerID = '{1}'".format(albumID, userID))
	numPhotos = cursor.fetchone()[0]
	return numPhotos
	
def getContributionScore(userID):
	cursor = conn.cursor()
	cursor.execute("Select contributionScore from registeredUser where userID = '{0}'".format(userID))
	contributionScore = cursor.fetchone()[0]
	return contributionScore
	
def getFullNameFromUserID(userID):
	cursor = conn.cursor()
	cursor.execute("SELECT fullName FROM registeredUser WHERE userID = '{0}'".format(userID))
	return cursor.fetchone()[0]

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	if request.method == 'POST':
		if (getAlbumsForUser(uid)):
			imgfile = request.files['photo']
			caption = request.form.get('caption')
			photo_data =imgfile.read()	
			selectedAlbum = request.form.get('albumName')
			selectedAlbumID = getAlbumIDfromName(selectedAlbum,uid)
			cursor.execute('''INSERT INTO photo_in_album (photoBinary, userID, caption, albumID) VALUES (%s, %s, %s, %s )''', (photo_data, uid, caption, selectedAlbumID))
			setUserContScore(uid, 1)
			conn.commit()
			
			return render_template('hello.html', name=getFullNameFromEmail(flask_login.current_user.id), message='Photo uploaded! to album: ' + selectedAlbum, photos=getUsersPhotos(uid), base64=base64)
		else:
			#albumName = request.form.get('albumName')
			#cursor.execute('''INSERT INTO albums (albumName, ownerID) VALUES (%s, %s)''', (albumName, uid))
			#conn.commit()
			return render_template('upload.html', album=False)
	else:
		if(getAlbumsForUser(uid)):

			return render_template('upload.html', album=True)
		else:
			#albumName = request.form.get('albumName')
			#cursor.execute('''INSERT INTO albums (albumName, ownerID) VALUES (%s, %s)''', (albumName, uid))
			#conn.commit()
			return render_template('upload.html', album=False)
		

			#user needs to make an album first
	#The method is GET so we return a  HTML form to upload the a photo.
	
@app.route('/photoDeletion', methods=['GET','POST'])
@flask_login.login_required
def photoDeletion():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	fullName = getFullNameFromUserID(uid)
	if request.method == 'GET':
		photos = getUsersPhotos(uid)
		return render_template('photoDeletion.html', name = fullName, photos = photos,base64=base64)
	else:
		try:
			pID = request.form.get('pID')
		except:
			return render_template('hello.html', name = fullName, message = 'Something went wrong')
		cursor = conn.cursor()
			#this assumes that each user only makes one album with a certain name
		cursor.execute("Delete from photo_in_album where pID = '{0}' and userID = '{1}' ".format(pID, uid))
		setUserContScore(uid, -1)
		conn.commit()
		return render_template('hello.html', name = fullName, message = 'photo successfully deleted')

#end photo uploading code
@app.route('/albumSelection', methods=['GET', 'POST'])
@flask_login.login_required
def albumSelection():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	fullName = getFullNameFromUserID(uid)
	if request.method == 'GET':
		
		albums = getAlbumsForUser(uid)
		
		if (albums):
			return render_template('albumSelection.html', albums = albums, name = fullName)
		else:
			return render_template('albumSelection.html', albums = False, name = fullName)
	else:
		action = request.form.get('action')
		albumName = request.form.get('albumList')
		print(albumName)
		print(action)
		print(uid)			
		if(action == 'Upload Photos'):
			return render_template('upload.html', album = True)
		elif(action == 'Delete Photos'):
			return render_template('photoDeletion.html', photos = getUsersPhotos(uid), name = fullName, base64=base64)
		elif(action == 'Delete Album'):
			albumID = getAlbumIDfromName(albumName, uid)
			numPhotos = -1 * int(getNumPhotosInAlbum(uid, albumID))
			cursor = conn.cursor()
			#this assumes that each user only makes one album with a certain name
			cursor.execute("Delete from albums where albumName = '{0}' and ownerID = '{1}' ".format(albumName, uid))
			conn.commit()
			#lowers the contribution score by the number of photos deleted.
			setUserContScore(uid, numPhotos)
			
			return render_template('hello.html', name = fullName, message = 'album successfully deleted!')
		elif(action == 'View Album'):
			return render_template('albumViewing.html', photos = getPhotosInAlbumForUser(albumName, uid), base64=base64, albumName = albumName)
		elif(action == 'Create Album'):
			return render_template('albumCreation.html')
		else:
			return render_template('hello.html', message = "something failed")

			#display all the photos with their photoID, probably inside of the specific album they are in.
			#have the user submit the photoID of the photo they wish to delete
			#use that pID to delete their photo


@app.route('/albumCreation', methods=['GET', 'POST'])
@flask_login.login_required
def albumCreation():
	if(request.method == 'GET'):
		return render_template('albumCreation.html')
	else:
		ownerID = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		albumName = request.form.get('albumName')
		cursor.execute('''INSERT INTO albums (albumName, ownerID) VALUES (%s, %s)''', (albumName, ownerID))
		conn.commit()
		return render_template('hello.html', name =flask_login.current_user.id, message = "album " + albumName + " has been created!")




#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
