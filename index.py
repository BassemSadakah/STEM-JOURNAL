import os
import mysql.connector
from flask import *
from sqlalchemy import *
from sqlalchemy.orm import *
global idd
app = Flask(__name__)
# engine=create_engine('mysql://root:183256179482165817349261@localhost:3306/journals')
engine=create_engine(os.getenv('database'))
db= scoped_session(sessionmaker(bind=engine))

try:
	db.execute('Select * from users;')
except Exception as e:
	db.execute("create table users (Name TEXT NOT NULL , ID INT NOT NULL , Email VARCHAR(255) UNIQUE NOT NULL,password TEXT NOT NULL, Secret_Number INT);")
	db.commit()
	db.execute("insert into users (name,email,id,password) VALUES (\'admin\', \'admin\', 0, \'Stemalex.J\')")
	db.commit()

try:
	db.execute('Select * from questions;')
except Exception as e:
	db.execute("create table questions (question1 Text,question2 Text,question3 Text,question4 Text);")
	db.commit()
	db.execute("insert into questions(question1,question2,question3,question4) VALUES (\"\",\"\",\"\",\"\");")
	db.commit()

try:
	db.execute('Select * from journals;')
except Exception as e:
	db.execute("create table journals (journal_id INT auto_increment,journal_date DATE NOT NULL,PRIMARY KEY(journal_id));")
	db.commit()



table=db.execute("SELECT * FROM users").fetchall()
#db.execute("INSERT INTO new (name) VALUES ('lsse');")

@app.route("/")
def index():
	username=request.cookies.get('user')
	password=request.cookies.get('password')
	if 'user' in request.cookies and 'password' in request.cookies:
		username=request.cookies.get('user')
		password=request.cookies.get('password')
		response = redirect(url_for('journal'))
		return response
	else:
		return render_template("index.html")


@app.route("/journal", methods=["POST",'GET'] )
def journal():
	if request.method=='GET':
		global username
		global password
		username=request.cookies.get('user')
		password=request.cookies.get('password')
		app.logger.info(username)
	else:
		username = request.form.get("username")
		password = request.form.get("password")


	global u_data
	u_data=db.execute("SELECT * FROM users WHERE email=:email and password=:password;",{'email':username,'password':password}).fetchall()
	j_data=db.execute("SELECT * FROM questions").fetchall()
	question1=j_data[0][0]
	question2=j_data[0][1]
	question3=j_data[0][2]
	question4=j_data[0][3]

	if len(u_data)==0:
		response=redirect(url_for('index'))
		response.set_cookie('user', '', expires=0)
		response.set_cookie('password', '', expires=0)
		return response
		# return "Wrong Username OR Password"
	if u_data[0][1]==0 and len(u_data)!=0:
		# if j_data
		# db.refresh_all()
		if j_data[0][0] == "" and j_data[0][1]== "":

			# return render_template("journal_admin.html")
			journals=db.execute("select * from journals").fetchall()
			response=make_response(render_template("journal_admin.html",journals=journals))
			response.set_cookie('user', username)
			response.set_cookie('password', password)
			return response
			# return str(journals)
		else:

			journals=db.execute("select * from journals").fetchall()
			journal_id=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]
			query=" select count(*) from journal%s;"%journal_id
			n_responses=db.execute(query).fetchall()[0][0]
			response=make_response(render_template("journal_admin_2.html",n_responses=n_responses,journals=journals))
			response.set_cookie('user', username)
			response.set_cookie('password', password)
			return response
		 # return "j_data "+str(j_data)
	else:
		# db.refresh()
		if j_data[0][0] == "" and j_data[0][1]== "":

			response=make_response(render_template("journal_students.html",id=u_data[0][1],question1=question1,question2=question2,question3=question3,question4=question4,journal_running=False))
			response.set_cookie('user', username)
			response.set_cookie('password', password)
			return response
		else:
			journal_id=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]
			query="select count(*) from journal%s Where Email=\'%s\'" %(journal_id,u_data[0][2])
			x=db.execute(query).fetchall()[0][0]
			app.logger.info(x,'xxxxxxxxxxxxxxxxxxxxxxxxxx')

			global already_submit
			if x==1:
				already_submit=1
			else:
				already_submit=0
			response=make_response(render_template("journal_students.html",id=u_data[0][1],question1=question1,question2=question2,question3=question3,question4=question4,journal_running=True,already_submit=already_submit,status="Another Respone has already submitted by this E-Mail"))
			response.set_cookie('user', username)
			response.set_cookie('password', password)
			return response


@app.route("/journal_edited",methods=["POST"])
def new_journal():
	question1=request.form.get('question1')
	question2=request.form.get('question2')
	question3=request.form.get('question3')
	question4=request.form.get('question4')
	question1_sql= db.execute('select * from questions').fetchall()[0][0]
	if(question1_sql!=''):
		return "STOP CURRENT JOURNAL FIRST"

	# db.execute("delete from responses where True;")
	db.execute("update questions set question1=:question1, question2=:question2, question3=:question3, question4=:question4;",{'question1':question1,'question2':question2,'question3':question3,'question4':question4})

	# **************************
	db.execute("insert into journals (journal_date) VALUES (NOW());")
	db.commit()
	journal_id=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]
	journal_name='journal'+str(journal_id)
	app.logger.info(journal_name)
	query="create table %s (Name varchar(255),Email varchar(255) NOT NULL,ID INT UNIQUE NOT NULL,Secret_Number INT UNIQUE,question1 TEXT ,question2 TEXT ,question3 TEXT ,question4 TEXT);" % journal_name
	db.execute(query)
	# db.execute("create table :table_name (Name varchar(255),email varchar(255) NOT NULL,id INT UNIQUE NOT NULL,Secret_Number INT UNIQUE,question1 TEXT ,question2 TEXT ,question3 TEXT ,question4 TEXT);",{'table_name': journal_name})
	db.commit();
	# query2="INSERT INTO journal%s (name,id,email,Secret_Number,question1,question2,question3,question4) VALUES (\'Name\',\'ID\',\'email\',\'Secret_Number\',\'Question 1\',\'Question 2\',\'Question 3\',\'Question 4\');" %journal_id
	# db.execute(query2)
	# db.commit()
	journal_id=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]
	query=" select count(*) from journal%s;"%journal_id
	n_responses=db.execute(query).fetchall()[0][0]
	journals=db.execute("select * from journals").fetchall()

	return render_template("journal_admin_2.html",n_responses=n_responses,journals=journals)

@app.route("/signup")
def sign_up():
	return render_template("sign_up.html")


@app.route("/", methods=["POST"])
def submit_sign_up():
	name=request.form.get('name')
	id=request.form.get('id')
	Secret_Number=request.form.get('Secret_Number')
	email=request.form.get('email')
	password_a=request.form.get('password_a')
	password_b=request.form.get('password_b')
	if password_a != password_b:
		return 'passwords didn\'t match'
	try:
		db.execute("INSERT INTO users (name,id,email,password,Secret_Number) VALUES (:name,:id,:email,:password,:Secret_Number);",{'name':name,'id':id,'email':email,'password':password_a,'Secret_Number':Secret_Number})
		db.commit()
	except Exception as e:
		return '<li>Username OR Email is already taken</li> <li>Your ID isn\'t a number</li>  <li> Your Email has more than 255 characters</li>'
		# return e
	db.commit()

	return render_template("index.html")

@app.route("/done",methods=['POST'])
def submit_journal():
	question1=request.form.get('question1')
	question2=request.form.get('question2')
	question3=request.form.get('question3')
	question4=request.form.get('question4')
	username=request.cookies.get('user')
	password=request.cookies.get('password')
	global u_data
	u_data=db.execute("SELECT * FROM users WHERE email=:email and password=:password;",{'email':username,'password':password}).fetchall()

	try:
		journal_id=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]
		query="INSERT INTO journal%s (name,id,email,Secret_Number,question1,question2,question3,question4) VALUES (:name,:id,:email,:Secret_Number,:question1,:question2,:question3,:question4);" %journal_id
		app.logger.info(u_data[0],'ddddddddddddddddddd	dddddd')

		db.execute(query,{'name':u_data[0][0],'id':u_data[0][1],'email':u_data[0][2],'Secret_Number':u_data[0][4],'question1':question1, 'question2':question2, 'question3':question3,'question4':question4})
		db.commit()
	except Exception as e:

		response=make_response(render_template("journal_students.html",id=u_data[0][1],question1=question1,question2=question2,question3=question3,question4=question4,journal_running=True,already_submit=1,status="Another Respone has already submitted by this E-Mail"))
		response.set_cookie('user', username)
		response.set_cookie('password', password)
		# return response
		return e
		# return "Another Respone has already submitted by this E-Mail"
	response=make_response(render_template("journal_students.html",id=u_data[0][1],question1=question1,question2=question2,question3=question3,question4=question4,journal_running=True,already_submit=1,status="Thanks for submitting"))
	response.set_cookie('user', username)
	response.set_cookie('password', password)
	return response
	# return "Thanks for submitting Journal 1"
@app.route("/download", methods=['POST'])
def download():
	# os.remove("/var/lib/mysql-files/journal_responses.xlsx")
	checkbox_name=request.form.get('checkbox_name')
	checkbox_email=request.form.get('checkbox_email')
	checkbox_id=request.form.get('checkbox_id')
	checkbox_secret=request.form.get('checkbox_secret')
	select=request.form.get('select')
	app.logger.info(select,'d')
	global x
	x=''
	y=''
	i=0
	if checkbox_name=='Name' :
		x+='Name,'
		y+='\'Name\','
		i+=1
	if checkbox_id=='ID' :
		x+='ID,'
		y+='\'ID\','
		i+=1
	if checkbox_email=='Email' :
		x+='Email,'
		y+='\'Email\','
		i+=1
	if checkbox_secret=='Secret_Number' :
		x+='Secret_Number,'
		y+='\'Secret_Number\','
		i+=1


	# db.execute("select :checkbox_name :checkbox_email :checkbox_id :checkbox_secret INTO OUTFILE \"/var/lib/mysql-files/journal_responses.xlsx\" FROM responses;")
	if(select=='0'):
		select=db.execute("select * from journals ORDER BY journal_id DESC LIMIT 1;").fetchall()[0][0]

	location=db.execute('SELECT @@GLOBAL.secure_file_priv').fetchall()[0][0]+'journal_responses.xls'
	query="SELECT %s 'Question1','Question2','Question3','Question4' UNION ALL SELECT %s question1,question2,question3,question4 FROM journal%s  INTO OUTFILE \"%s\" " %(y,x,select,location)
	app.logger.info(query,'ffffffffffffffffffffffffffff')

	# query="select %s question1,question2,question3,question4 INTO OUTFILE \"/var/lib/mysql-files/journal_responses.xls\" FROM journal%s ;" %(x,select)
	db.execute(query)
	cwd=os.getcwd()+'/Journal_Responses.xls'
	os.rename(location,cwd)

	return send_file('Journal_Responses.xls',as_attachment=True)

@app.route("/stop", methods=['POST'])
def stop():
	# os.remove("/var/lib/mysql-files/journal_responses.xlsx")
	# db.execute("select * INTO OUTFILE \"/var/lib/mysql-files/journal_responses.xlsx\" FROM responses;")
	# os.rename("/var/lib/mysql-files/journal_responses.xlsx","/home/toor/Documents/Web Development/STEM_JOURNAL/Journal_Responses.xlsx")
	db.execute("update questions set question1=\"\", question2=\"\", question3=\"\", question4=\"\";")
	# db.execute("delete from responses where True;")
	db.commit()
	journals=db.execute("select * from journals").fetchall()
	return render_template("journal_admin.html",journals=journals)
@app.route("/logout")
def logout():
	# return 'rr'
	response=redirect(url_for('index'))
	response.set_cookie('user', '', expires=0)
	response.set_cookie('password', '', expires=0)
	return response



@app.route("/fonts.css", methods=["GET"])
def fonts():
	return send_file('fonts.css');
@app.route("/fonts/1.woff2", methods=["GET"])
def fonts1():
	return send_file('fonts/1.woff2');
@app.route("/fonts/2.woff2", methods=["GET"])
def fonts2():
	return send_file('fonts/2.woff2');
@app.route("/fonts/3.woff2", methods=["GET"])
def fonts3():
	return send_file('fonts/3.woff2');
@app.route("/fonts/4.woff2", methods=["GET"])
def fonts4():
	return send_file('fonts/4.woff2');
@app.route("/fonts/5.woff2", methods=["GET"])
def fonts5():
	return send_file('fonts/5.woff2');
