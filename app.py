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
from datetime import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'GUwsn1108!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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

def friend(userID, friendID):
	print(userID, friendID)
	if not is_friends(userID, friendID):
		#insert the user_id into the table
		cursor = conn.cursor()
		print(f"{userID} and {friendID} is what im trying to insert")
		print(type(userID), type(friendID))
		cursor.execute("INSERT INTO friendship (userID, friendID) VALUES ('{0}','{1}')".format(userID, friendID))
		conn.commit()
		print('it should have inserted')


def is_friends(userID,friendID):
	# print(userID, friendID)
	cursor = mysql.connect().cursor()
	print(userID, friendID, type(userID))
	cursor.execute("SELECT * FROM friendship WHERE ((userID = '{0}' AND friendID = '{1}') AND (userID = '{1}' AND friendID = '{0}')) AND (userID IS NOT NULL AND friendID IS NOT NULL)".format(userID, friendID))
	return_value = cursor.fetchall()
	print(return_value)
	if return_value:
		print("true")
		return True
	else:
		print("false")
		return False

def get_friends(userID):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT friendID FROM friendship WHERE userID = '{0}'".format(userID))
    results = cursor.fetchall()
    friendIDs = [result[0] for result in results]
    print(friendIDs)
    return friendIDs

def get_friend_info(friendIDs):
    cursor = mysql.connect().cursor()
    friend_info = []
    for friendID in friendIDs:
        cursor.execute("SELECT * FROM registeredUser WHERE userID = '{0}'".format(friendID))
        result = cursor.fetchone()
        friend_info.append(result)
    return friend_info





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
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM registeredUser WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
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

	

@app.route('/add_friend', methods=['GET','POST'])
@flask_login.login_required
def add_friend():
	if request.method == 'POST':
		userID = request.form.get('userID')
		friendID = request.form.get('friendID')
		if userID != None or friendID != None:
			userID = int(userID)
			friendID = int(friendID)
		print(f"the userID is {userID}")
		print(f"the friendID is {friendID}")
		print(type(userID))

		print("point reached")
		if not is_friends(userID, friendID):
			print("NOT FRIEND YET")
			friend(userID, friendID)
			print("wow they should be friends")

	return render_template('add_friend.html')


@app.route('/find_friend', methods=['GET', 'POST'])
@flask_login.login_required
def find_friend():
	if request.method == 'POST':
		friend_email = request.form.get('email')
		friendID = getUserIdFromEmail(friend_email)
		if friendID == -1:
			return render_template('find_friend.html', friendID = -1)
		return render_template('find_friend.html', friendID = friendID)
	return render_template('find_friend.html')


@app.route('/friends', methods=['GET','POST'])
@flask_login.login_required
def show_friends():
	if request.method == 'GET':
		userID = getUserIdFromEmail(flask_login.current_user.id)
		print(userID)
		friendIDs = get_friends(userID)
		friend_info = get_friend_info(friendIDs)
		return render_template('friends.html', friend_info = friend_info)
	
	return render_template('friends.html')

@app.route('/friend_recommendations', methods = ['GET', 'POST'])
@flask_login.login_required
def friend_recommendations():
	userID = getUserIdFromEmail(flask_login.current_user.id)
	friends = get_friends(userID)
	print(f"friends {friends}")
	friends_of_friends = []
	for friend in friends:
		friends_of_friends.append(get_friends(friend))
	print(f"friend of friends {friends_of_friends}")
	all_friends_of_friends = [friend for friends in friends_of_friends for friend in friends]

	print(f"all friend of friends {all_friends_of_friends}")
	friend_count = {}
	for fid in all_friends_of_friends:
		if fid not in friends and fid != userID:
			if fid in friend_count:
				friend_count[fid] += 1
			else:
				friend_count[fid] = 1
	

	friend_recommendations = sorted(friend_count.items(), key=lambda x: x[1], reverse=True)
	print(f"friend_recommendations {friend_recommendations}")
	print(type(friend_recommendations))

	return render_template('friend_recommendations.html', friend_recommendations = friend_recommendations)





@app.route('/display_uphotostag/<tagTitle>', methods=['GET', 'POST'])
@flask_login.login_required
def display_uphotostag(tagTitle):
	if request.method == 'GET':
		userID = getUserIdFromEmail(flask_login.current_user.id)
		
		photos = get_user_photos_by_tag(userID, tagTitle)
		return render_template('mytagphotos.html', photos=photos, base64=base64, tag=tagTitle)

@app.route('/display_allphotostag/<tagTitle>', methods=['GET', 'POST'])
@flask_login.login_required
def display_allphotostag(tagTitle):
	if request.method == 'GET':
		userID = getUserIdFromEmail(flask_login.current_user.id)
		
		photos = get_all_photos_by_tag(tagTitle)
		return render_template('mytagphotos.html', photos=photos, base64=base64, tag=tagTitle)


def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT photoBinary, pID, caption FROM photo_in_album")
	photos =cursor.fetchall()
	return photos


@app.route('/browsePhotos')
def photoBrowsing():
	try:
		
		return render_template('photoBrowsing.html', name= getFullNameFromEmail(flask_login.current_user.id), photos = getAllPhotos(), base64=base64)
	except:
		
		return render_template('photoBrowsing.html', name= "anonymous", photos = getAllPhotos(), base64=base64)

@app.route('/likes_photo', methods = ['POST'])

@flask_login.login_required
def user_like():
	if request.method == 'POST':
		pID = request.form.get('pID')
		userID =  getUserIdFromEmail(flask_login.current_user.id)
		
		userID = int(userID)
		pID= int(pID)
		cursor = conn.cursor()
		cursor.execute("UPDATE photo_in_album SET likes = likes + 1 WHERE pID = %s", (pID))
		likes = cursor.execute("SELECT likes FROM photo_in_album WHERE pID = %s", (pID))
		
		cursor.execute("INSERT INTO likesPhoto (userID, pID) VALUES (%s, %s)", (userID, pID))
		conn.commit()
		return render_template('photoBrowsing.html', name = getFullNameFromEmail(flask_login.current_user.id), photos = getAllPhotos(), likes=likes, base64=base64)
	return render_template('photoBrowsing.html', name = "anonymous", photos = getAllPhotos(), base64=base64)
	
@app.route('/likes/<int:pID>')
@flask_login.login_required
def photo_likes(pID):
	cursor = conn.cursor()
	cursor.execute("SELECT likes FROM photo_in_album WHERE pID = %s", (pID,))
	likes = cursor.fetchone()[0]
	cursor.execute("SELECT userID FROM likesPhoto WHERE pID = %s", (pID,))
	cursor.execute("SELECT registeredUser.email FROM likesPhoto JOIN registeredUser ON likesPhoto.userID = registeredUser.userID WHERE likesPhoto.pID = %s", (pID,))
	liked_emails = [row[0] for row in cursor.fetchall()]

	return render_template('photo_likes.html', likes=likes, liked_users=liked_emails)

@app.route('/commented', methods=['POST', 'GET'])
def left_comment():
	if request.method == 'POST':
		pID = request.form.get('pID')
		userID = request.form.get('userID')
		
		if userID == '':
			if flask_login.current_user.is_authenticated:
				userID =  getUserIdFromEmail(flask_login.current_user.id)
			else:
				userID = -1
		
		cursor = conn.cursor()
		cursor.execute("SELECT userID FROM photo_in_album WHERE pID = %s", (pID,))
		result = cursor.fetchone()
		ownerID = result[0]
		print(userID)
		print(ownerID)
		if ownerID == userID:
			return "You cannot comment on your own photo."


		contents = request.form.get('comment')
		commented_by_name = None

		if userID == -1:
			
			commented_by_name = "anonymous"
		else:
			commented_by_name = getFullNameFromEmail(get_email_from_userID(userID))
			print(commented_by_name)

		cursor = conn.cursor()
		 
		cursor.execute("INSERT INTO comments (contents, commentOwner) VALUES (%s, %s)", (contents, commented_by_name))

		cursor.execute("SELECT commentID FROM comments WHERE contents = %s ORDER BY commentID DESC LIMIT 1", (contents,))
		result = cursor.fetchone()

		commentID = result[0]
		print(commentID, pID)
		cursor.execute("INSERT INTO comment_under_photo (commentID, pID) VALUES (%s, %s)", (commentID ,pID) )

		
		
		conn.commit()



		cursor.execute("""
        SELECT comments.commentID, comments.contents, comments.commentOwner, comments.commentDate
        FROM comments
        JOIN comment_under_photo
        ON comments.commentID = comment_under_photo.commentID
        WHERE comment_under_photo.pID = %s;
        """, (pID,))

		comments = cursor.fetchall()

		return render_template('comment_display.html', comments = comments)

	return render_template('comment_display.html')



@app.route('/searchcomment', methods = ['GET', 'POST'])
def search_comment():
	if request.method == 'POST':
		comment = request.form.get('comment')
		return render_template('searchcomments.html', comment = comment )


@app.route('/display_allcomments/<comment>', methods=['GET', 'POST'])
@flask_login.login_required
def display_allcomments(comment):
	if request.method == 'GET':
		userID = getUserIdFromEmail(flask_login.current_user.id)
		
		comments = get_all_comments_by_comment(comment)
		print(comments)
	
		return render_template('matched_comments.html', comments = comments )

def get_all_comments_by_comment(comment):

	cursor = conn.cursor()

	cursor.execute("""
		SELECT commentOwner,COUNT(commentOwner) AS ccount FROM comments WHERE contents= %s GROUP BY commentOwner ORDER BY ccount DESC
	""", (comment,))

	comments = cursor.fetchall()
	

	return comments




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
	return render_template('register.html', supress='False')

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
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def get_user_photos_by_tag(userID, tagTitle):
	
	cursor = conn.cursor()
	cursor.execute("SELECT pi.photobinary, pi.pID, pi.caption, t.tagTitle FROM photo_in_album pi JOIN hasTag ht ON ht.pID = pi.pID JOIN tags t ON ht.tagTitle = t.tagTitle WHERE pi.userID = '{0}' AND t.tagTitle = '{1}'".format(userID, tagTitle))
	return cursor.fetchall()

def get_all_photos_by_tag(tagTitle):
	
	cursor = conn.cursor()
	cursor.execute("SELECT pi.photobinary, pi.pID, pi.caption, t.tagTitle FROM photo_in_album pi JOIN hasTag ht ON ht.pID = pi.pID JOIN tags t ON ht.tagTitle = t.tagTitle WHERE t.tagTitle = '{0}'".format(tagTitle))
	return cursor.fetchall()

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photobinary, pID, caption FROM photo_in_album WHERE userID = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	call =cursor.execute("SELECT userID FROM registeredUser WHERE email = '{0}'".format(email))
	if call == 0:
		return -1
	return cursor.fetchone()[0]

def get_email_from_userID(userID):
	curcor = conn.cursor()
	call = cursor.execute("SELECT email FROM registeredUser where userID = '{0}'".format(userID))
	return cursor.fetchone()[0]

def getFullNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fullName FROM registeredUser WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM registeredUser WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tags').split(',')
		
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO photo_in_album (photoBinary, userID, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption))
		photo_id = cursor.lastrowid
		for tag in tags:
			tag = tag.upper()
			cursor.execute('''INSERT IGNORE INTO tags (tagTitle) VALUES (%s)''', (tag))
			cursor.execute('''INSERT INTO hasTag (pID, tagTitle) VALUES (%s, %s)''', (photo_id, tag))
		
		conn.commit()
		
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		# Query the database for tags associated with the user's photos
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT DISTINCT t.tagTitle FROM tags t JOIN hasTag ht ON t.tagTitle=ht.tagTitle JOIN photo_in_album p ON ht.pID=p.pID WHERE p.userID=%s", (uid,))
		tags = [row[0] for row in cursor.fetchall()]
		for tag in tags:
			tag = tag.upper()

		# # Query the database for all existing tags
		# cursor = conn.cursor() THIS IS FOR
		# cursor.execute("SELECT tagTitle FROM tags")
		# tags = [row[0] for row in cursor.fetchall()]

		# return render_template('upload.html', tags=tags)
		return render_template('upload.html', tags=tags)
#end photo uploading code

@app.route('/all_taggedphotos', methods=['GET','POST'])
def all_taggedphotos():
		cursor = conn.cursor() 
		cursor.execute("SELECT tagTitle FROM tags")
		tags = [row[0] for row in cursor.fetchall()]
		return render_template('all_taggedphotos.html', tags=tags)

@app.route('/top_taggedphotos', methods=['GET','POST'])
def top_taggedphotos():
		cursor = conn.cursor() 
		cursor.execute("""
        SELECT tagTitle, COUNT(*) as tag_count
        FROM hastag
        GROUP BY tagTitle
        ORDER BY tag_count DESC
        LIMIT 3
    """)
		tags = [row[0] for row in cursor.fetchall()]
		print(type(tags))
		return render_template('top_taggedphotos.html', tags=tags)

@app.route('/searchtag', methods=['GET', 'POST'])
def search_tag():
	if request.method == 'POST':
		tags = request.form.get('tagsearch')
		if tags is not None and ' ' in tags:
			tags = tags.split(' ')
			for tag in tags:
				tag = tag.upper()
		else:
			tags = tags.upper()

	if type(tags) == str:
		return render_template('searchtags_string.html', tags = tags)
	else:
		return render_template('searchtags_list.html', tags = tags)
		




#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
