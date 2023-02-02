import tkinter
import customtkinter
from classes import *

width = 1400
height = 700

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")



class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
     
        self.geometry(f"{width}x{height}")
        self.title("JWealth5")
           
        self.lblFont = customtkinter.CTkFont(family="Pacifico", size=72)
        self.lblMainWindow= customtkinter.CTkLabel(master=self, text="JWealth5", text_color="red", font =self.lblFont)
        self.lblMainWindow.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

        self.lblFont = customtkinter.CTkFont(family="Dancing Script", size=35)
        self.lblMainWindow= customtkinter.CTkLabel(master=self, text="Clothes, accessories and more", text_color="yellow", font =self.lblFont)
        self.lblMainWindow.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        
        menu_bar = MenuBar(self)


    def __del__(self):
        database.commit()
        dbcursor.close()
        database.close()
    


if __name__ == "__main__":
    main_window = MainWindow()

    main_window.mainloop()

  
