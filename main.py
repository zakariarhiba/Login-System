# import necessary librairs 
# for application
import sys
from  PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QStackedWidget, QMessageBox
from PyQt5 import uic,QtGui

# for DB connection 
import info_DB as info
import psycopg2   as pg

# function for checking the connection with DB
def checkDbConnection():
    # connect to db
    try:
        pgconn = pg.connect(
                host = info.db_host,
                database = info.db_name,
                user = info.db_user,
                password = info.db_password
            )
    except :
        return False
    return True   

# for checking formula 
import re 

# function for checking email correct form
def check_email(email) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.match(regex, email)):
        return True
    else:
        return False
         
###### welcome pagge ###### this is the first widget that display when you run the app 
class WelcomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui',self)
        self.buttons()
    
    

    def buttons(self):
        self.pushButton_signin.clicked.connect(self.signin)
        self.pushButton_signup.clicked.connect(self.signup)

    def signin(self):
        widget.setCurrentIndex(1)

    def signup(self):
        widget.setCurrentIndex(2)

######## sign in widget #########################
class SigninApp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('signin.ui',self)
        self.buttons()
        print(checkDbConnection())


    def backtowelcome(self):
        self.lineEdit_username.setText("")
        self.lineEdit_password.setText("")
        widget.setCurrentIndex(0)
        # should delte all then back 
        
    def gotoffice(self):
        widget.setCurrentIndex(3)


    def buttons(self):
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_back.clicked.connect(self.backtowelcome)
        
    def login(self):
        if checkDbConnection():
            try:
                pgconn = pg.connect(
                    host = info.db_host,
                    database = info.db_name,
                    user = info.db_user,
                    password = info.db_password
                )
            except :
                pass
            else:
                self.checkacc(self.account(),pgconn)
        else:
            QMessageBox.warning(self,"Failed Connection","Failed Connect to database")
            self.backtowelcome()




    def checkacc(self,account,pgconn):
        username,password = account.split(" ") 
        try:
            cur = pgconn.cursor() 
            cur.execute("SELECT username,password FROM accounts WHERE username like %s AND password like %s", (username,password))
            accounts = cur.fetchall() 
            print("collect data succesluy")  
        except (Exception, pg.DatabaseError) as error:
            print(error)
            QMessageBox.warning(self,"Failed Connection",error)
        else:
            # the codee that check if are the same
            if len(accounts) == 0:
                QMessageBox.information(self,"Failed Connection","User Not Found")  
            elif len(accounts) > 0: 
                    for account in accounts:
                        if username == account[0] and password == account[1]:
                            QMessageBox.information(self,"Login successfully",f"Welcome {username}")
                            self.lineEdit_username.setText("")
                            self.lineEdit_password.setText("")
                            self.gotoffice()
                        else:
                            QMessageBox.warning(self,"Failed Connection","Wrong Username or  Password")    
            ################ end  ################""
            cur.close()
        finally:
            if pgconn is not None:
                pgconn.close()
            



    def account(self):
        username = self.lineEdit_username.text().strip().lower()
        password = self.lineEdit_password.text()
        acc = username + ' ' + password
        print(f"you write -> {acc}")
        return acc 
              
######## sign up widget #########################
class SignupApp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('signup.ui',self)
        self.buttons()

    
    def buttons(self):
        self.pushButton_back.clicked.connect(self.backtowelcome)
        self.pushButton_submit.clicked.connect(self.submit)

    def backtowelcome(self):
        self.lineEdit_firstname.setText("")
        self.LineEdit_lastname.setText("")
        self.lineEdit_email.setText("")
        self.lineEdit_username.setText("")
        self.lineEdit_password.setText("")
        self.lineEdit_repassword.setText("")
        widget.setCurrentIndex(0)

    def submit(self):
        info_in = self.collectinfo()
        if self.check_info(info_in):
            # push data to db 
            print("data collect check successfly")
            try:
                pgconn = pg.connect(
                    host = info.db_host,
                    database = info.db_name,
                    user = info.db_user, 
                    password = info.db_password
                )
                cur = pgconn.cursor() 
                cur.execute("INSERT INTO persons(first_name,second_name,email) VALUES(%s,%s,%s) RETURNING person_id;",(info_in[0],info_in[1],info_in[2]))
                person_id = cur.fetchone()[0]
                cur.execute("INSERT INTO accounts(person_id,username,password) VALUES(%s,%s,%s);",(person_id,info_in[3],info_in[4]))
            except (Exception, pg.DatabaseError) as error:
                print(error)
                QMessageBox.warning(self,"Submit Failed","Failed sumbmit data to database")
            else:
                # commit the changes to the database
                QMessageBox.information(self,"Submit success","your account is create")
                print("add sucessfly")
                pgconn.commit()
                cur.close()
                self.backtowelcome()
            finally:
                if pgconn is not None:
                    pgconn.close()


    def collectinfo(self) -> list:
        #########  fname,lname,email,usernam,pawrd,repassd
        info_in =  [None, None,None,None,None,None]
        firstname = self.lineEdit_firstname.text().strip().lower()
        lastname = self.LineEdit_lastname.text().strip().lower()
        email = self.lineEdit_email.text().strip().lower()
        username = self.lineEdit_username.text().lower()
        password = self.lineEdit_password.text()
        repassword = self.lineEdit_repassword.text()
        info_in = [firstname,lastname,email,username,password,repassword]
        return info_in

    
    def check_info(self,info_in:list) -> bool:
        check = True
        if '' in info_in:
            QMessageBox.warning(self,"Failed submit","Enter all the filed")
            check= False
        else:
            firstName,lastName,email,username,password,repassword = info_in[0] \
                ,info_in[1],info_in[2],info_in[3],info_in[4],info_in[5]
            if check_email(email) == False:
                QMessageBox.warning(self,"Failed submit","Invalid email")
                check= False
            if ' ' in username:
                QMessageBox.warning(self,"Failed submit","Username should not contain space")
                check= False
            if len(password) != 8:
                QMessageBox.warning(self,"Failed submit","password should have 8 char")
                check= False
            if password != repassword:
                QMessageBox.warning(self,"Failed submit","password not match with repassword")
                check= False
        return check

#####  when user log this intrface gonna show 
class officeApp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('office.ui',self)
        self.buttons()

    def buttons(self):
        self.pushButton_back.clicked.connect(self.backtowelcome)

    def backtowelcome(self):
        widget.setCurrentIndex(0)

##### set up for widget stack
def setUi(Widget):
        widget.setWindowTitle('   ZACK CLUB APP')
        Widget.setGeometry(450, 100, 440, 500)
        widget.setFixedSize(440,500)
        widget.setWindowIcon(QtGui.QIcon('icon.png'))

# main code 
if __name__=='__main__':
    app = QApplication(sys.argv)
    widget = QStackedWidget()
    welcome = WelcomeApp() # index 0
    widget.addWidget(welcome)
    Signin = SigninApp()   # index 1
    widget.addWidget(Signin)
    Signup = SignupApp()   # index 2
    widget.addWidget(Signup)
    office = officeApp()   # index 3
    widget.addWidget(office)
    setUi(widget)
    widget.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('closing window...')



