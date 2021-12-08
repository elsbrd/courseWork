from flask import Flask, render_template, flash, request, redirect, url_for, session, jsonify, json
from flask_mysqldb import MySQL,MySQLdb
import bcrypt

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'coursework'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute("SELECT * FROM selectWork ")
    # selectWorklist = cur.fetchall()
    # cur.execute("SELECT * FROM technology ")
    # technologylist = cur.fetchall()
    # return render_template('buyingWork.html', selectWorklist=selectWorklist, technologylist=technologylist)
    return redirect(url_for('register'))





@app.route("/insert", methods=["POST", "GET"])
def insert():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        fullname = request.form['name']
        email = request.form['email']
        selectWork = request.form['selectWork']
        technology = request.form['technology']
        expireTime = request.form['expireTime']
        price = request.form['price']
        try:
            cur.execute("INSERT INTO tbl_user (fullname,email, selectWork, technology, expireTime, price) VALUES (%s,%s,%s,%s,%s,%s)", [fullname, email, selectWork, technology, expireTime, price])

        except Exception as e:
            # #print
            # "Error code:", e.errno  # error number
            # print
            # "SQLSTATE value:", e.sqlstate  # SQLSTATE value
            # print
            # "Error message:", e.msg  # error message
            # print
            # "Error:", e  # errno, sqlstate, msg values
            s = str(e)
            response = app.response_class(response=json.dumps(s), status=201, mimetype='application/json')
            #print(s)
            # print
            # "Error:", s
            return response
        #data = {"message": 'New Records added successfully'}
        #response = app.response_class(response=json.dumps(data), status=201, mimetype='application/json')
        mysql.connection.commit()
        cur.close()
        return jsonify('New Records added successfully')


@app.route('/buyWork',methods=["GET"])
def buyWork():
    if request.method == 'GET':
        print(session)
        if len(session) != 0:
            #if session role == admin:
                #render_template("...")
            #else:
                #...
            return render_template("buyingWork.html")
        else:
            return redirect(url_for('login'))

@app.route('/seeorders')
def seeorders():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # order by a specific full name
    # fullname = request.form['fullname']
    # cur.execute('SELECT * FROM tbl_user WHERE email=%s', fullname)
    cur.execute('SELECT * FROM tbl_user')
    data = cur.fetchall()
    cur.execute("SELECT * FROM selectWork ")
    selectWorklist = cur.fetchall()
    cur.execute("SELECT * FROM technology ")
    technologylist = cur.fetchall()
    return render_template('index.html', employee=data, selectWorklist=selectWorklist, technologylist=technologylist)

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
        cur.close()
        print(user)
        if user is not None:

        #if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = user['role']
                if user['role'] == 'basic':
                    return redirect("/buyWork")
                if user['role'] == 'admin':
                    return redirect("/seeorders")
            else:
                return render_template('login.html', error = {"message": "Error password and email not match"})
                #return "Error password and email not match"
        else:
            #return "Error user not found"
            return render_template('login.html',error = {"message": "Error password and email not match"})
    else:
        return render_template("login.html", error = {})


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("buyingWork.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
        mysql.connection.commit()
        #session['name'] = name
        #session['email'] = email
        return redirect(url_for('login'))

@app.route('/add_contact', methods=['POST'])
def add_employee():
    #conn = mysql.connect()
    #cur = conn.cursor(pymysql.cursors.DictCursor)
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        selectWork = request.form['selectWork']
        technology = request.form['technology']
        expireTime = request.form['expireTime']
        price = request.form['price']
        cur.execute("INSERT INTO tbl_user (fullname, email, selectWork, technology, expireTime, price) VALUES (%s,%s,%s, %s,%s,%s)",
                    (fullname, email,  selectWork, technology, expireTime, price))
        #conn.commit()
        #mysql.connection.commit()
        mysql.connection.commit()
        cur.close()
        flash('New order successfully added')
        return redirect("/seeorders")


@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_employee(id):
    #conn = mysql.connect()
    #cur = conn.cursor(pymysql.cursors.DictCursor)
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM tbl_user WHERE userid = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', employee=data[0])


@app.route('/update/<id>', methods=['POST'])
def update_employee(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        selectWork = request.form['selectWork']
        technology = request.form['technology']
        expireTime = request.form['expireTime']
        price = request.form['price']
        #conn = mysql.connect()
        #cur = conn.cursor(pymysql.cursors.DictCursor)
        cur = mysql.connection.cursor()

        cur.execute("""
            UPDATE tbl_user
            SET fullname = %s,
                email = %s,
                selectWork = %s,
                technology = %s,
                expireTime = %s,
                price = %s
            WHERE userid = %s
        """, (fullname, email,  selectWork, technology, expireTime, price, id))
        flash('Order Updated Successfully')
        #conn.commit()
        mysql.connection.commit()
        cur.close()
        return redirect("/seeorders")


@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_employee(id):
    #conn = mysql.connect()
    #cur = conn.cursor(pymysql.cursors.DictCursor)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('DELETE FROM tbl_user WHERE userid = {0}'.format(id))
    #conn.commit()
    mysql.connection.commit()
    flash('Order Removed Successfully')
    return redirect("/seeorders")

if __name__ == '__main__':
    app.secret_key = "caircocoders-ednalan"
    app.run(debug=True)