import tkinter
import customtkinter
import hashlib
import sqlite3

width = 1400
height = 700

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


database = sqlite3.connect("JWdatabase.db")
dbcursor = database.cursor()



class AdminWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x400")
        self.title("User Administration")
   
        self.firstnameEntry = customtkinter.CTkEntry(self, placeholder_text="Enter Firstname", width=200)
        self.lastnameEntry = customtkinter.CTkEntry(self, placeholder_text="Enter Lastname", width=200)
        self.usernameEntry = customtkinter.CTkEntry(self, placeholder_text="Enter Username", width=200)
        self.password1Entry = customtkinter.CTkEntry(self, placeholder_text="Enter Password", show="*", width=200)
        self.password2Entry = customtkinter.CTkEntry(self, placeholder_text="Confirm Password", show="*", width=200)
        self.entryLevel = customtkinter.CTkEntry(self, placeholder_text="Level (1-user, 2-supvc, 3-admin)", width=200) 
        self.userAddButton = customtkinter.CTkButton(self, text="Add User", width=200, text_color="black", command=self.addUser)
        self.userRemoveButton = customtkinter.CTkButton(self, text="Remove User", fg_color="red", text_color="black", width=200, command=self.removeUser)
        self.changePasswordButton = customtkinter.CTkButton(self, text="Change Password", fg_color="yellow", text_color="black", width=200, command=self.changePassword)
        self.lblMessage = customtkinter.CTkLabel(self, width=200, text="", text_color="red")

        self.firstnameEntry.place(x=50, y=30)
        self.lastnameEntry.place(x=50, y=67)
        self.usernameEntry.place(x=50, y=104)
        self.password1Entry.place(x=50, y=141)
        self.password2Entry.place(x=50, y=178)
        self.entryLevel.place(x=50, y=215)
        self.userAddButton.place(x=50, y=252)
        self.userRemoveButton.place(x=50, y=289)
        self.changePasswordButton .place(x=50, y=326)
        self.lblMessage.place(x=10, y=363)


    def addUser(self):
               
        self.firstname =  self.firstnameEntry.get()
        self.lastname = self.lastnameEntry.get()
        self.username = self.usernameEntry.get()
        self.password1 = self.password2Entry.get()
        self.password2 = self.password2Entry.get()
        self.level = self.entryLevel.get()

        if (self.firstname and self.lastname and self.username and self.password1 and self.password2):
            if(self.password1 == self.password2):
                self.password = hashlib.sha256(self.password1.encode()).hexdigest()
                record = (self.firstname, self.lastname, self.username, self.password, self.level)
                dbcursor.execute("INSERT INTO users (firstName, lastName, userName, password, level) VALUES (?,?,?,?,?)", record)
                database.commit() 
                            
                self.firstnameEntry.configure(placeholder_text="Enter Firstname")
                self.lastnameEntry.configure(placeholder_text="Enter Lastname")
                self.usernameEntry.configure(placeholder_text="Enter Username")
                self.password1Entry.configure(placeholder_text="Enter Password")
                self.password2Entry.configure(placeholder_text="Confirm Password")
                self.entryLevel.configure(placeholder_text="Level (1-user, 2-supvc, 3-admin)")
                self.lblMessage.configure(text="")
            else:
                self.lblMessage.configure(text="The two passwords must be the same")
        else:
            self.lblMessage.configure(text="All fields must be filled")

    def removeUser(self):
        self.firstname = self.firstnameEntry.get()
        self.lastname = self.lastnameEntry.get()
        self.username = self.usernameEntry.get()

        if ((self.firstname and self.lastname) or self.username):
            record = (self.firstname, self.lastname, self.username)
            dbcursor.execute("DELETE from users where firstname = ? and lastname = ? or username = ?", record)
            database.commit() 


    def changePassword(self):
        
        self.firstname =  self.firstnameEntry.get()
        self.lastname = self.lastnameEntry.get()
        self.username = self.usernameEntry.get()
        self.password1 = self.password2Entry.get()
        self.password2 = self.password2Entry.get()

        if (self.firstname and self.lastname or self.username):
            if(self.password1 == self.password2):
                self.password = hashlib.sha256(self.password1.encode()).hexdigest()
                record = (self.password, self.firstname, self.lastname, self.username)
                dbcursor.execute("""
                    UPDATE users 
                    SET password = ?
                    WHERE firstname = ? and lastname = ? or username = ?""", record)
                database.commit() 
            else:
                self.lblMessage.configure(text="The two passwords must be the same")
        else:
            self.lblMessage.configure(text="Enter firstname and lastname OR username")




class LogInWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x375")
        self.title("Login")

        self.usernameEntry = customtkinter.CTkEntry(self, placeholder_text="Enter Username", width=200)
        self.passwordEntry = customtkinter.CTkEntry(master=self, placeholder_text="Enter Password",show="*", width=200)
        self.loginButton = customtkinter.CTkButton(self, text="Log In", width=200, command=self.validate)
        self.loginAlternativeLabel = customtkinter.CTkLabel(self, text="Or Log In with", text_color="blue")
        self.loginGoogleButton = customtkinter.CTkButton(self, text="Google", width=200, fg_color="red", command=self.logInGoogleUser)
        self.loginFacebookButton = customtkinter.CTkButton(self, text="Facebook", width=200, command=self.logInFacebookUser)
        self.lblMessage = customtkinter.CTkLabel(self, width=200, text="", text_color="red")
        
        self.usernameEntry.place(x=50, y=30)
        self.passwordEntry.place(x=50, y=67)
        self.loginButton.place(x=50, y=105)
        self.loginAlternativeLabel.place(x=10, y=180)    
        self.loginGoogleButton.place(x=50, y=255)
        self.loginFacebookButton.place(x=50, y=290)

    def validate(self):
        # global usernameEntry, passwordEntry, credentialsDialog
        self.username = self.usernameEntry.get()
        self.password = self.passwordEntry.get()
        # if(usernameEntry and passwordEntry):
        if(self.username and self.password):
            self.password = hashlib.sha256(self.password.encode()).hexdigest()
            self.record = (self.username, self.password)
            database = sqlite3.connect("JWdatabase.db")
            dbcursor = database.cursor()
            dbcursor.execute("SELECT * FROM users WHERE userName = ? AND password = ?", self.record)
            database.commit()
            if (dbcursor.fetchall()):
                self.destroy()
                print("Credentials are OK. Proceed")
            else:
                print("Wrong credentials or user does not exist")
        else:
            print("Both username and password fields must be entered")

    def logInGoogleUser(self):
        pass

    def logInFacebookUser(self):
        pass


class MenuBar:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.menubar = tkinter.Menu(self.parent)
        parent.config(menu=self.menubar)
        self.optionsMenu = tkinter.Menu(self.menubar, tearoff=0)
        self.optionsMenu.add_command(label="Log In", command= lambda : self.logIn(self.parent))
        self.optionsMenu.add_command(label="Inventory", command=self.inventoryReport)
        self.optionsMenu.add_command(label="User Administration", command=lambda : self.userAdministration(self.parent))
        self.menubar.add_cascade(label="Options", menu=self.optionsMenu)

    def logIn(self, parent):
        self.login = LogInWindow(parent) 

    def inventoryReport(self):
        print("implement Inventory report")

    def userAdministration(self, parent):
        self.login= AdminWindow(parent)


  
