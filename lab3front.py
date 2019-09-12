# Kristi Luu & Amir Alaj
# Lab 3 -- CIS41B

# This program will display a GUI and interacts with a database.
import sqlite3
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import matplotlib.pyplot as plt
import numpy as np

class DisplayWin(tk.Toplevel):
    '''class that will display the listbox'''
    def __init__(self, master, b_degree, m_degree, certification, a_degree, choice, degree):
        '''constructor for listbox display window'''
        super().__init__(master)
        self._bachJobs = b_degree
        self._mastJobs = m_degree
        self._certJobs = certification
        self._assocJobs = a_degree
        self._userChoice = choice
        self._title = degree
        self.geometry("+100+100")
        
        self.LB = tk.Listbox(self, selectmode=tk.SINGLE, width=35, height=10)
        self.LB.grid()
        self.title('Minimum Degree: ' + self._title)
        
        if self._userChoice == 1:
            self.LB.insert(tk.END, *self._mastJobs)
        elif self._userChoice == 2:
            self.LB.insert(tk.END, *sorted(self._bachJobs))
        elif self._userChoice == 3:
            self.LB.insert(tk.END, *self._certJobs)
        else:
            self.LB.insert(tk.END, *self._assocJobs)


class DialogWin(tk.Toplevel):
    '''dialog window with radiobuttons'''
    def __init__(self,master, educationlevels):
        '''constructor for radiobutton dialog window'''
        super().__init__(master)
        self.geometry("+100+100")
        self._educationlevel = educationlevels
        self.title('Choose Entry Degree')
        
        self._control_var = tk.IntVar() 

        for val, level in enumerate(self._educationlevel):
            tk.Radiobutton(self, text=level[1], padx = 20, 
                    variable=self._control_var, value=level[0],
                    command=self.getChoice).grid(padx=20, sticky='w')
                    
        tk.Button(self, text="OK", command=self._close).grid(padx=20)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.transient(master)
    def getChoice(self):
        '''getter for user's choice when selecting a radio button (key/number)'''
        self._choice = self._control_var.get()
        return self._choice
    def getDegree(self):
        '''getter for user's choice degree (name)'''
        for items in self._educationlevel:
            if self._choice == items[0]:
                self._degree = items[1]
        return self._degree
    def _close(self):
        '''closes the window'''
        self.destroy()

class PlotWin(tk.Toplevel):
    '''class that plots data from a database in horizontal bar graphs'''
    def __init__(self, master, plotFct, *args, **kwargs):
        '''constructor for plots'''
        super().__init__(master)
        self.geometry("+200+200")
        self.transient(master)
        fig = plt.figure(figsize=(9,6))
        plotFct(*args, **kwargs)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid()
        canvas.draw()

class MainWin(tk.Tk):
    '''main GUI class'''
    def __init__(self):
        '''constructor for the master GUI class'''
        super().__init__()
        self.title('High Tech Jobs')
        self._F = tk.Frame(self)
        self._F.grid()
        self._conn = sqlite3.connect('occupation.db')
        self._cur = self._conn.cursor()

        tk.Button(self._F, text='By Salary', fg='blue', command= lambda: PlotWin(self, self.plot, 'salary')).grid(row=0, column=0, padx=20, pady=20)
        tk.Button(self._F, text='By Growth Rate', fg='blue', command= lambda: PlotWin(self, self.plot, 'rate')).grid(row=0, column=1, padx=20, pady=20)
        tk.Button(self._F, text='By Degree', fg='blue', command= self.radio).grid(row=0, column=2, padx=20, pady=20)

    def plot(self, choice):
        '''selects data from database, puts it in a list, and plots the data'''
    
        self._cur.execute('''SELECT * FROM OccupationFields''')
        getField = self._cur.fetchone()

        if choice == 'salary':
            self._cur.execute('''SELECT Median_Pay FROM JobData ORDER BY Median_Pay ASC''')
            medianPay = [pay[0] for pay in self._cur.fetchall()]   
            
            self._cur.execute('''SELECT Job_Title FROM JobData ORDER BY Median_Pay ASC''')
            job = [job[0] for job in self._cur.fetchall()]
            
            y_pos = np.arange(len(job))
            plt.title(getField[0])
            plt.barh(y_pos, medianPay, align="center")
            plt.xlabel("Dollar")
        else:
            self._cur.execute('''SELECT Growth_Rate FROM JobData ORDER BY Growth_Rate ASC''')
            growthRate = [rate[0] for rate in self._cur.fetchall()] 
            
            self._cur.execute('''SELECT Job_Title FROM JobData ORDER BY Growth_Rate ASC''')
            job = [job[0] for job in self._cur.fetchall()]
            
            y_pos = np.arange(len(job))
            plt.title(getField[5])
            plt.barh(y_pos, growthRate, align="center")
            plt.xlabel("Percentage")
        plt.ylabel("Job Title")
        plt.yticks(y_pos, job, wrap=True, fontsize=6, verticalalignment='center')        

    def radio(self):
        '''selects data from database and passes it to dialog and display window'''
        self._cur.execute('''SELECT * FROM Majors''')
        major = [maj for maj in self._cur.fetchall()]
        dialog = DialogWin(self, major)
        self.wait_window(dialog)
        choice = dialog.getChoice()
        degree = dialog.getDegree()

        self._cur.execute('''SELECT Job_Title FROM JobData WHERE Education LIKE 2''') #selects all Bachelor degree jobs
        bach = [b[0] for b in self._cur.fetchall()]
        self._cur.execute('''SELECT Job_Title FROM JobData WHERE Education LIKE 1''') #selects all Master degree jobs
        mast = [m[0] for m in self._cur.fetchall()]
        self._cur.execute('''SELECT Job_Title FROM JobData WHERE Education LIKE 3''') #selects all certifcation jobs
        cert = [c[0] for c in self._cur.fetchall()]
        self._cur.execute('''SELECT Job_Title FROM JobData WHERE Education LIKE 4''') #selects all Associate degree jobs
        assoc = [a[0] for a in self._cur.fetchall()]

        display = DisplayWin(self, bach, mast, cert, assoc, choice, degree)
        self.wait_window(display)

app = MainWin()
app.mainloop()

