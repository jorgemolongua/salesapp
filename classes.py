import tkinter
import customtkinter
import hashlib
import sqlite3
from tkinter import ttk
from tabulate import tabulate
from datetime import datetime
import os
import tempfile
import tkcalendar


width = 1400
height = 700
currentUser = ""

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

database = sqlite3.connect("JWdatabase.db")
dbcursor = database.cursor()


class SalesUpdate:
    def __init__(self, parent, cashier, presentTime, saleRecord ):
        self.parent = parent
        self.cashier = cashier
        self.presentTime = presentTime
        self.saleRecord = saleRecord
        
        try:
            for row in saleRecord:
                #reduce sale quantity from products table
                dbcursor.execute("UPDATE products SET units = units - ? WHERE productNumber=?", (row[2], row[0]))
                database.commit()

                #update sales table
                dbcursor.execute("""INSERT INTO sales 
                (productNumber, units, salePrice, date, user) 
                VALUES (?,?,?,?,?)""", (row[0], row[2], row[3], self.presentTime, self.cashier))
                database.commit()
        except Exception as e:
            print(f"Error: {e}")



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
        self.amountReceivedStringVar = customtkinter.StringVar(self.parent)
        self.customerChangeStringVar = customtkinter.StringVar(self.parent)
        self.presentTime = ""
        self.basket, self.saleRecord = [], []
        self.lineWidth = 60

        self.customerReceipt = tkinter.Text(self.parent, width=self.lineWidth)

        self.cashierUsernameLabel = customtkinter.CTkLabel(parent, text=f"Cashier: {self.cashier}")
        self.productNumberEntry = customtkinter.CTkEntry(self.parent, placeholder_text="Product #", width=100, textvariable=self.productNumberStringVar)
        self.productDescriptionEntry = customtkinter.CTkEntry(master=self.parent, placeholder_text="Product description", width=300, textvariable=self.productDescriptionStringVar)
        self.quantity = customtkinter.CTkEntry(master=self.parent, placeholder_text="Quantity", textvariable=self.quantityStringVar, width=100)
        self.salePriceEntry = customtkinter.CTkEntry(master=self.parent, placeholder_text="Unit price", textvariable=self.salePricerDoubleVar, state='normal', width=100)
        self.subTotal = customtkinter.CTkEntry(master=self.parent, placeholder_text="sub Total", textvariable=self.subTotalDoubleVar, state='normal', width=100)
        self.addButton = customtkinter.CTkButton(self.parent, text="Add to cart", command=self.addToCart)
        self.payButton = customtkinter.CTkButton(self.parent, text="Checkout", fg_color="green", hover_color="#49be25", command=self.processPayment)

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
        self.payButton.place(x=765, y=140)

    def completeSale(self):
        #print file
        tmpfile = tempfile.mktemp('.txt')
        open(tmpfile, "w").write(self.customerReceipt.get("0.0", tkinter.END))
        os.startfile(tmpfile, "print")

        # #close change dialog box and receipt
        self.checkoutDialog.destroy()
        self.customerReceipt.destroy()

        # Update sales database
        updateSales = SalesUpdate(self.parent, self.cashier, self.presentTime, self.saleRecord)

        # #clear search fields
        SellProducts.__init__(self, self.parent, self.cashier)

       

    def giveChange(self, *args):
        amountGiven = int(self.amountReceivedEntry.get().strip())
        totalBill= self.totalDoubleVar.get() 
        customerChange = amountGiven - totalBill        

        #update customer receipt
        tabulatedData = tabulate(self.basket, headers=["Item Desc", "Qty", "Price", "Sub Total"])
        numberOfRows = len(self.basket) + 11
        lineWidth = len(self.productDescriptionStringVar.get()) + len(self.quantityStringVar.get()) + len(str(self.salePricerDoubleVar.get())) + len(str(self.subTotalDoubleVar.get())) + 20
        if(lineWidth > self.lineWidth):
            self.lineWidth = lineWidth
        self.customerReceipt.delete("1.0", tkinter.END)
        self.customerReceipt.destroy()
        self.customerReceipt = tkinter.Text(self.parent, width=self.lineWidth, height=numberOfRows)
        self.customerReceipt.insert("0.0", f"Cashier: {self.cashier}\n")
        self.presentTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.customerReceipt.insert("end", f"{self.presentTime}\n\n")
        self.customerReceipt.insert("end", tabulatedData)
        totalLine = self.lineWidth - len("TOTAL") - len(str(self.subTotalDoubleVar.get())) - 4
        self.customerReceipt.insert("end", "\n\n")
        self.customerReceipt.insert("end", f"TOTAL{' '*totalLine}{self.totalDoubleVar.get()}")        
        self.customerReceipt.insert("end", "\n\n")
        self.customerReceipt.insert("end", f"Cash{' '*totalLine}{amountGiven}\n") 
        self.customerReceipt.insert("end", f"Change{' '*(totalLine-2)}{customerChange}") 
        self.customerReceipt.place(x=1150, y=100)

        self.customerChangeDisplay.configure(text=str(customerChange))


    def processPayment(self, *args): 
        self.checkoutDialog = customtkinter.CTkToplevel()
        self.checkoutDialog.title("Checkout")
        checkoutDialogOffsetX, checkoutDialogOffsetY = self.parent.winfo_x(), self.parent.winfo_y()
        padx=600
        pady=0
        self.giveChangeBooleanVar = customtkinter.BooleanVar(self.parent)
        self.completeSaleBooleanVar = customtkinter.BooleanVar(self.parent)
        self.giveChangeBooleanVar.set(False)
        self.completeSaleBooleanVar.set(False)
   
        self.checkoutDialog.geometry(f"250x125+{checkoutDialogOffsetX + padx}+{checkoutDialogOffsetY + pady}")
        self.amountReceivedLabel = customtkinter.CTkLabel(self.checkoutDialog, text="   Amount Paid: ")
        self.amountReceivedEntry = customtkinter.CTkEntry(self.checkoutDialog)
        self.totalBillLabel = customtkinter.CTkLabel(self.checkoutDialog, text="   Total Bill: ")
        self.totalBillDisplay = customtkinter.CTkLabel(self.checkoutDialog, text=str(self.totalDoubleVar.get()))
        self.customerChangelabel = customtkinter.CTkLabel(self.checkoutDialog, text="   Change: ")
        self.customerChangeDisplay = customtkinter.CTkLabel(self.checkoutDialog, text="0.0")
        self.OKbutton = customtkinter.CTkButton(self.checkoutDialog, text="OK", command=self.completeSale)
        
        self.amountReceivedLabel.grid(row=0, column=1, sticky='e')
        self.amountReceivedEntry.grid(row=0, column=2, sticky='e')
        self.totalBillLabel.grid(row=2, column=1, sticky='e')
        self.totalBillDisplay.grid(row=2, column=2, sticky='e')
        self.customerChangelabel.grid(row=4, column=1, sticky='e')
        self.customerChangeDisplay.grid(row=4, column=2, sticky='e')
        self.OKbutton.grid(row=6, columnspan=3, sticky='ew')    

        self.amountReceivedEntry.bind('<Return>', command=self.giveChange)

  
    def addToCart(self, *args):   
        self.processQuantityChange()
        self.saleRecord.append([self.productNumberStringVar.get(), self.productDescriptionStringVar.get(), self.quantityStringVar.get(), self.salePricerDoubleVar.get(), self.subTotalDoubleVar.get()])
        self.basket.append([self.productDescriptionStringVar.get(), self.quantityStringVar.get(), self.salePricerDoubleVar.get(), self.subTotalDoubleVar.get()])
        self.totalDoubleVar.set(self.totalDoubleVar.get() + self.subTotalDoubleVar.get())
        tabulatedData = tabulate(self.basket, headers=["Item Desc", "Qty", "Price", "Sub Total"])
        numberOfRows = len(self.basket) + 7
        self.customerReceipt.configure(height=numberOfRows)
        self.customerReceipt.delete("0.0", tkinter.END)
        self.customerReceipt.insert("0.0", f"Cashier: {self.cashier}\n")
        self.customerReceipt.insert("end", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "\n\n")
        self.customerReceipt.insert("end", tabulatedData)
        totalLine = self.lineWidth - len("TOTAL") - len(str(self.subTotalDoubleVar.get())) - 4
        self.customerReceipt.insert("end", "\n\n")
        self.customerReceipt.insert("end", f"TOTAL{' '*totalLine}{self.totalDoubleVar.get()}")        
        self.customerReceipt.place(x=1150, y=100)



    def processQuantityChange(self, *args):
        self.subTotalDoubleVar.set(self.salePricerDoubleVar.get()*int(self.quantityStringVar.get()))           
    

    def productDescriptionSearch(self, *args):
        self.record = (self.productDescriptionStringVar.get(),)
        try:
            dbcursor.execute(f"SELECT productNumber, productName, productDescription, salePrice FROM products WHERE productName like '%{self.record[0]}%' OR  productDescription like '%{self.record[0]}%'")
            database.commit()
            rows = dbcursor.fetchall()
            if (rows):
                columnNames = ("productNumber", "productDescription", "salePrice")
                treeView = ttk.Treeview(self.parent, columns=columnNames, height=10)
                myStyle=ttk.Style()
                myStyle.configure(".", font=("Helvetica", 12))
                myStyle.configure("Treeview", font=("Helvetica", 12))
                myStyle.configure("Treeview.Heading", font=("Helvetica", 15), background="blue", foreground="blue" )
                treeView.column("#0", width=0)
                treeView.heading("#0", text="")
                treeView.heading("productNumber", text="Product #", anchor="w")
                treeView.heading("productDescription", text="Description", anchor="w")
                treeView.heading("salePrice", text="Price", anchor="w")

                for row in rows:
                    treeView.insert(parent='', index=tkinter.END, values=(row[0], row[2], row[3]))

                treeView.bind("<<TreeviewSelect>>", lambda *args : self.selectedRow(treeView, yscrollbar))
                treeView.place(x=40, y=170)
                yscrollbar = tkinter.Scrollbar(self.parent, orient='vertical', command=treeView.yview)
                treeView.configure(yscrollcommand=yscrollbar.set)
                yscrollbar.place(x=640, y=170, height=225)

        except Exception as e:
            print("Error: ", e)

    def selectedRow(self, tree, scrollbar):
        record = (tree.item(tree.selection()))['values']
        self.productNumberStringVar.set(record[0])
        self.productDescriptionStringVar.set(record[1])
        self.quantityStringVar.set(1)
        self.salePricerDoubleVar.set(record[2])
        self.processQuantityChange()
        tree.destroy()
        scrollbar.destroy()


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


class ProductNew(customtkinter.CTkToplevel):
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
            try:
                dbcursor.execute("""INSERT INTO products 
                (productNumber, productName, productDescription, units, location, costPrice, salePrice) 
                VALUES (?,?,?,?,?,?,?)""",  self.record)
                database.commit()
            except Exception as e:
                self.lblMessage.configure(text=f"Error: {e}")      
        else:
            self.lblMessage.configure(text="All fields must be entered")


class ProductExisting(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x375")
        self.title("Products Entry")

        self.productNumberEntry = customtkinter.CTkEntry(self, placeholder_text="Enter product number", width=200)
        self.productNameEntry = customtkinter.CTkEntry(master=self, placeholder_text="Enter product name", width=200, state="disabled")
        self.productDescriptionEntry = customtkinter.CTkEntry(master=self, placeholder_text="Enter a description", width=200, state="disabled")
        self.unitsEntry = customtkinter.CTkEntry(master=self, placeholder_text="Quantity of this unit", width=200)
        self.locationEntry = customtkinter.CTkEntry(master=self, placeholder_text="Location kept", width=200, state="disabled")
        self.costPriceEntry = customtkinter.CTkEntry(master=self, placeholder_text="Cost price", width=200)
        self.salePriceEntry = customtkinter.CTkEntry(master=self, placeholder_text="Sale price", width=200)
        self.postProductButton = customtkinter.CTkButton(self, text="Update product", width=200, command=self.validate)
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

        if(self.productNumber and self.units and self.costPrice and self.salePrice): 
            self.record = (self.units, self.costPrice, self.salePrice, self.productNumber)       
            try:
                #increase quantity in products table
                dbcursor.execute("UPDATE products SET units = units + ?, costPrice = ?, salePrice = ? WHERE productNumber = ?", self.record)
                database.commit()
            except Exception as e:
                self.lblMessage.configure(text=f"Error: {e}")           
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
        self.lblMessage.place(x=30, y=325)

    def validate(self):
        self.username = self.usernameEntry.get()
        self.password = self.passwordEntry.get()
        if(self.username and self.password):
            try:
                self.password = hashlib.sha256(self.password.encode()).hexdigest()
                self.record = (self.username, self.password)
                dbcursor.execute("SELECT * FROM users WHERE userName = ? AND password = ?", self.record)
                database.commit()
                if (dbcursor.fetchall()):
                    self.destroy()
                    sellproducts = SellProducts(self.parent, self.username)  
                else:             
                    self.lblMessage.configure(text="Wrong credentials or user does not exist")
            except Exception as e:
                    self.lblMessage.configure(text=f"Error: {e}")
        else:
            self.lblMessage.configure(text="Enter both username and password fields")

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
        self.productsMenu = tkinter.Menu(self.menubar, tearoff=0)
        self.optionsMenu.add_cascade(label="Products", font=("",13), menu=self.productsMenu)
        self.productsMenu.add_command(label="Input Products", font=("",13), command= lambda : self.inputProducts(self.parent))
        self.productsMenu.add_command(label="Update Products", font=("",13), command= lambda : self.updateProducts(self.parent))
        self.optionsMenu.add_command(label="User Administration", font=("",13), command=lambda : self.userAdministration(self.parent))
        self.inventoryMenu = tkinter.Menu(self.menubar, tearoff=0)
        self.optionsMenu.add_cascade(label="Inventory", font=("",13), menu=self.inventoryMenu)
        self.inventoryMenu.add_command(label="Current Inventory", font=("",13), command=self.inventoryReport)
        self.inventoryMenu.add_command(label="Sales Between Dates", font=("",13), command=self.salesReport)


    def logIn(self, parent):
        self.login = LogInWindow(parent)   

    def inputProducts(self, parent):
        self.login = ProductNew(parent) 


    def updateProducts(self, parent):
        self.login = ProductExisting(parent) 

    def inventoryReport(self):
        try:
            dbcursor.execute("SELECT productNumber, ProductName, ProductDescription, units, costPrice, salePrice FROM products ")
            database.commit()
            rows = dbcursor.fetchall()
            if (rows):
                tabulatedData = tabulate(rows, headers=["Product Number", "Product Name", "Description", "Units", "Cost Price", "Sale Price"])
                print(tabulatedData)  

                tmpfile = tempfile.mktemp('.txt')
                open(tmpfile, "w").write(tabulatedData)
                os.startfile(tmpfile, "edit")             
            else:             
                print("No results returned")
        except Exception as e:
                print(f"Error: {e}")

    
    def getStartDates(self, cal, button, entry1, entry2):
        if(button=="date1"):
            entry1.delete(0, customtkinter.END)
            entry1.insert(0, cal.get_date())
  
        elif(button=="date2"):
            entry2.delete(0, customtkinter.END)
            entry2.insert(0, cal.get_date())

    def getDates(self):
        startDate = self.startDateEntry.get() + " 01:01:01"
        endDate = self.endDateEntry.get() + " 23:59:59"

        record = (startDate, endDate)
        print(record)
        try:
            dbcursor.execute("SELECT date, sales.productNumber, productName, productDescription, sales.units, costPrice, sales.salePrice, user FROM sales INNER JOIN products ON sales.productNumber = products.productNumber WHERE date >= ? and date <= ?", record)
            database.commit()
            rows = dbcursor.fetchall()
            if (rows):
                tabulatedData = tabulate(rows, headers=["Date", "Product Number", "Product Name", "Description", "Units", "Cost Price", "Sale Price", "Cashier"])
                print(tabulatedData)  

                tmpfile = tempfile.mktemp('.txt')
                open(tmpfile, "w").write(tabulatedData)
                os.startfile(tmpfile, "edit")
            
            else:             
                print("No results returned")
        except Exception as e:
                print(f"Error: {e}")

    def salesReport(self, *args):
        self.calendarWindow = customtkinter.CTkToplevel(self.parent)
        self.calendarWindow.title("Sales")
        self.cal = tkcalendar.Calendar(self.calendarWindow, selectmode="day",  date_pattern="dd/MM/yyyy") 
        self.startDateLabel = customtkinter.CTkLabel(self.calendarWindow, text="Start Date: ")
        self.startDateEntry = customtkinter.CTkEntry(self.calendarWindow)  
        self.startButton = customtkinter.CTkButton(self.calendarWindow, text="Select", command=lambda: self.getStartDates(self.cal, "date1", self.startDateEntry, self.endDateEntry))
        self.endDateLabel = customtkinter.CTkLabel(self.calendarWindow, text="End Date: ")
        self.endDateEntry = customtkinter.CTkEntry(self.calendarWindow)
        self.endButton = customtkinter.CTkButton(self.calendarWindow, text="Select", command=lambda: self.getStartDates(self.cal, "date2", self.startDateEntry, self.endDateEntry))
        self.OKbutton = customtkinter.CTkButton(self.calendarWindow, text="Post", fg_color="green", hover_color="green", command=self.getDates)
        
        self.cal.grid(row=1, columnspan=6, sticky='ew') 
        self.startDateLabel.grid(row=6, column=2, sticky='e')
        self.startDateEntry.grid(row=6, column=3, sticky='e')
        self.startButton.grid(row=6, column=4)
        self.endDateLabel.grid(row=8, column=2, sticky='e')
        self.endDateEntry.grid(row=8, column=3, sticky='e')
        self.endButton.grid(row=8, column=4)
        self.OKbutton.grid(row=10, columnspan=6, sticky='ew')    


    def userAdministration(self, parent):
        self.login= AdminWindow(parent)

  