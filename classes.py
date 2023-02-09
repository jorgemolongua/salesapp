import tkinter
import customtkinter
import hashlib
import sqlite3
from tkinter import ttk

width = 1400
height = 700
currentUser = ""

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

database = sqlite3.connect("JWdatabase.db")
dbcursor = database.cursor()

class SellProducts:
    def __init__(self, parent, cashier):
        self.parent = parent
        self.cashier = cashier
        self.productNumberStringVar = customtkinter.StringVar(self.parent, value="Product #")
        self.productDescriptionStringVar = customtkinter.StringVar(self.parent, value="Product Description")
        self.quantityStringVar = customtkinter.StringVar(self.parent)
        self.salePricerDoubleVar = customtkinter.DoubleVar(self.parent)
        self.subTotalDoubleVar = customtkinter.DoubleVar(self.parent)
        self.totalDoubleVar = customtkinter.DoubleVar(self.parent)
        self.basket = []
        
        self.cashierUsernameLabel = customtkinter.CTkLabel(parent, text=f"Cashier: {self.cashier}")
        self.productNumberEntry = customtkinter.CTkEntry(self.parent, placeholder_text="Product #", width=100, textvariable=self.productNumberStringVar)
        self.productDescriptionEntry = customtkinter.CTkEntry(master=self.parent, placeholder_text="Product description", width=300, textvariable=self.productDescriptionStringVar)
        self.quantity = customtkinter.CTkEntry(master=self.parent, placeholder_text="Quantity", textvariable=self.quantityStringVar, width=100)
        self.salePriceEntry = customtkinter.CTkEntry(master=self.parent, placeholder_text="Unit price", textvariable=self.salePricerDoubleVar, state='normal', width=100)
        self.subTotal = customtkinter.CTkEntry(master=self.parent, placeholder_text="sub Total", textvariable=self.subTotalDoubleVar, state='normal', width=100)
        self.addButton = customtkinter.CTkButton(self.parent, text="Add to cart", command=self.addToCart)

        self.productNumberEntry.bind('<Return>', self.productNumberSearch)
        self.productDescriptionEntry.bind('<Return>', self.productDescriptionSearch)
        self.quantity.bind('<Return>', self.processQuantityChange)
                
        self.cashierUsernameLabel.place(x=40, y=30)
        self.productNumberEntry.place(x=40, y=100)
        self.productDescriptionEntry.place(x=145, y=100)
        self.quantity.place(x=450, y=100)
        self.salePriceEntry.place(x=555, y=100)
        self.subTotal.place(x=660, y=100)
        self.addButton.place(x=765, y=100)

    def addToCart(self, *args):    
        self.basket.append([self.productDescriptionStringVar.get(), self.quantityStringVar.get(), self.salePricerDoubleVar.get(), self.subTotalDoubleVar.get()])
        self.totalDoubleVar.set(self.totalDoubleVar.get() + self.subTotalDoubleVar.get())
        print(self.basket, self.totalDoubleVar)
        print(self.totalDoubleVar.get())

    def processQuantityChange(self, *args):
        self.subTotalDoubleVar.set(self.salePricerDoubleVar.get()*int(self.quantityStringVar.get()))           
    

    def productDescriptionSearch(self, *args):
        self.record = (self.productDescriptionStringVar.get(),)
        print(self.record[0])
        try:
            dbcursor.execute(f"SELECT productNumber, productName, productDescription, salePrice FROM products WHERE productName like '%{self.record[0]}%' OR  productDescription like '%{self.record[0]}%'")
            database.commit()
            rows = dbcursor.fetchall()
            if (rows):
                columnNames = ("productNumber", "productDescription", "salePrice")
                treeView = ttk.Treeview(self.parent, columns=columnNames)
                myStyle=ttk.Style()
                myStyle.configure(".", font=("Helvetica", 12))
                myStyle.configure("Treeview", font=("Helvetica", 12))
                myStyle.configure("Treeview.Heading", font=("Helvetica", 15), background="blue")

                treeView.heading("#0", text="")
                treeView.heading("productNumber", text="Product #", anchor="w")
                treeView.heading("productDescription", text="Description", anchor="w")
                treeView.heading("salePrice", text="Price", anchor="w")

                for row in rows:
                    treeView.insert(parent='', index=tkinter.END, values=(row[0], row[2], row[3]))
                
                # treeView.bind("<<TreeviewSelect>>", self.itemSelected)
                treeView.bind("<<TreeviewSelect>>", lambda *args : self.selectedRow(treeView))

                # treeView.pack()
                treeView.place(x=40, y=170)
        except Exception as e:
            print("Error in fetching in the database: ", e)

    def selectedRow(self, tree):
        record = (tree.item(tree.selection()))['values']
        self.productNumberStringVar.set(record[0])
        self.productDescriptionStringVar.set(record[1])
        self.quantityStringVar.set(1)
        self.salePricerDoubleVar.set(record[2])
        self.processQuantityChange()
        # self.subTotalDoubleVar.set(self.salePricerDoubleVar.get()*int(self.quantityStringVar.get())) 
        tree.destroy()


    def productNumberSearch(self, *args):
        self.record = (self.productNumberStringVar.get(),)
        try:
            dbcursor.execute(f"SELECT productDescription, salePrice FROM products WHERE productNumber = ?", self.record)
            database.commit()
            row = dbcursor.fetchone()
            if (row):
                self.productDescriptionStringVar.set(row[0])    
                self.quantity.focus()
                self.quantityStringVar.set(1)
                self.salePricerDoubleVar.set(row[1])
                self.subTotalDoubleVar.set(self.salePricerDoubleVar.get()*int(self.quantityStringVar.get()))
        except Exception as e:
            print("Error: ", e)     



 
class Products(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x375")
        self.title("Products Entry")

        self.productNumberEntry = customtkinter.CTkEntry(self, placeholder_text="Enter product number", width=200)
        self.productNameEntry = customtkinter.CTkEntry(master=self, placeholder_text="Enter product name", width=200)
        self.productDescriptionEntry = customtkinter.CTkEntry(master=self, placeholder_text="Enter a description", width=200)
        self.unitsEntry = customtkinter.CTkEntry(master=self, placeholder_text="Quantity of this unit", width=200)
        self.locationEntry = customtkinter.CTkEntry(master=self, placeholder_text="Location kept", width=200)
        self.costPriceEntry = customtkinter.CTkEntry(master=self, placeholder_text="Cost price", width=200)
        self.salePriceEntry = customtkinter.CTkEntry(master=self, placeholder_text="Sale price", width=200)
        self.postProductButton = customtkinter.CTkButton(self, text="Post product", width=200, command=self.validate)
        self.lblMessage = customtkinter.CTkLabel(self, width=200, text="", text_color="red")
        
        self.productNumberEntry.place(x=50, y=30)
        self.productNameEntry.place(x=50, y=65)
        self.productDescriptionEntry.place(x=50, y=100)
        self.unitsEntry.place(x=50, y=135)    
        self.locationEntry.place(x=50, y=170)
        self.costPriceEntry.place(x=50, y=205)
        self.salePriceEntry.place(x=50, y=240)
        self.postProductButton.place(x=50, y=275)
        self.lblMessage.place(x=50, y=345)

    def validate(self):
        self.productNumber = self.productNumberEntry.get()
        self.productName = self.productNameEntry.get()
        self.productDescription	= self.productDescriptionEntry.get()
        self.units = self.unitsEntry.get()
        self.location = self.locationEntry.get()
        self.costPrice = self.costPriceEntry.get()
        self.salePrice = self.salePriceEntry.get()     

        if(self.productNumber and self.productName and self.productDescription and self.units 
           and self.location and self.costPrice and self.salePrice): 
            self.record = (self.productNumber, self.productName, self.productDescription, self.units, self.location, self.costPrice, self.salePrice)       
            # database = sqlite3.connect("JWdatabase.db")
            # dbcursor = database.cursor()
            try:
                dbcursor.execute("""INSERT INTO products 
                (productNumber, productName, productDescription, units, location, costPrice, salePrice) 
                VALUES (?,?,?,?,?,?,?)""",  self.record)
                database.commit()
            except:
                self.lblMessage.configure(text="Error posting into database")
        else:
            self.lblMessage.configure(text="All fields must be entered")


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
        self.parent = parent
 
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
        self.username = self.usernameEntry.get()
        self.password = self.passwordEntry.get()
        if(self.username and self.password):
            try:
                self.password = hashlib.sha256(self.password.encode()).hexdigest()
                self.record = (self.username, self.password)
                # database = sqlite3.connect("JWdatabase.db")
                # dbcursor = database.cursor()
                dbcursor.execute("SELECT * FROM users WHERE userName = ? AND password = ?", self.record)
                database.commit()
                if (dbcursor.fetchall()):
                    self.destroy()
                    sellproducts = SellProducts(self.parent, self.username)               
            except:
                    self.lblMessage.configure(text="Wrong credentials or user does not exist")
        else:
            self.lblMessage.configure(text="Both username and password fields must be entered")

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
        self.menubar.add_cascade(label="Options", font=("",13),  menu=self.optionsMenu)
        self.optionsMenu.add_command(label="Log In", font=("",13), command= lambda : self.logIn(self.parent))
        self.optionsMenu.add_command(label="Input Products", font=("",13), command= lambda : self.inputProducts(self.parent))
        self.optionsMenu.add_command(label="Inventory", font=("",13), command=self.inventoryReport)
        self.optionsMenu.add_command(label="User Administration", font=("",13), command=lambda : self.userAdministration(self.parent))


    def logIn(self, parent):
        self.login = LogInWindow(parent)   

    def inputProducts(self, parent):
        self.login = Products(parent) 

    def inventoryReport(self):
        print("implement Inventory report")

    def userAdministration(self, parent):
        self.login= AdminWindow(parent)


  
