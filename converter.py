import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os

# hardcoded need to fix
batch_number = 248

def increment_batch_number():
    global batch_number
    batch_number += 1

def generate_dat_file(csv_file, payment_date, institution, transit, account):
    try:
        with open(csv_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            rows = list(csv_reader)
        
        output_file = os.path.join(os.path.dirname(csv_file), "output.dat")
        
        num_transactions = len(rows)
        total_value = sum(int(float(row[0]) * 100) for row in rows)
        
        # .dat file
        with open(output_file, 'w') as datfile:
            #header record
            header = f"H{'TPABK54201':<10}C46{payment_date:6}{'':15}{institution:0>4}{transit:0>5}{account:<12} {batch_number:04}{'':19}\n"
            datfile.write(header)

            for row in rows:
                amount = int(float(row[0]) * 100)
                bank_info = row[1].replace('#', '').replace('*', '').split()
                payee_name = row[2][:23].ljust(23)
                institution_number = bank_info[0].zfill(4)
                transit_number = bank_info[1].zfill(5)
                account_number = bank_info[2].ljust(12)
                
                detail = f"D{payee_name}{payment_date:6}{payee_name[:19]:<19}{'':6}{institution_number}{transit_number}{account_number:<12}{amount:011}\n"
                datfile.write(detail)
                
            trailer = f"T{num_transactions:08}{total_value:014}{'':57}\n"
            datfile.write(trailer)
        
        increment_batch_number()
        messagebox.showinfo("Success", f".dat file created successfully at: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_path_var.set(file_path)

# GUI setup
root = tk.Tk()
root.title("CSV to .DAT Converter")

tk.Label(root, text="Today's Date:").grid(row=0, column=0, sticky="e")
tk.Label(root, text="Payment Date (DDMMYY):").grid(row=1, column=0, sticky="e")
tk.Label(root, text="Choose File:").grid(row=2, column=0, sticky="e")
tk.Label(root, text="Batch Number:").grid(row=3, column=0, sticky="e")

today_label = tk.Label(root, text="20241114")  
today_label.grid(row=0, column=1, sticky="w")

payment_date_entry = tk.Entry(root)
payment_date_entry.grid(row=1, column=1)

file_path_var = tk.StringVar()
file_path_entry = tk.Entry(root, textvariable=file_path_var, width=40)
file_path_entry.grid(row=2, column=1)
file_button = tk.Button(root, text="Browse", command=open_file)
file_button.grid(row=2, column=2)

batch_number_label = tk.Label(root, text=str(batch_number))
batch_number_label.grid(row=3, column=1, sticky="w")

def open_options():
    options_window = tk.Toplevel(root)
    options_window.title("Enter Bank Details")
    
    tk.Label(options_window, text="Institution Number:").grid(row=0, column=0, sticky="e")
    tk.Label(options_window, text="Transit Number:").grid(row=1, column=0, sticky="e")
    tk.Label(options_window, text="Account Number:").grid(row=2, column=0, sticky="e")

    institution_entry = tk.Entry(options_window)
    institution_entry.grid(row=0, column=1)
    
    transit_entry = tk.Entry(options_window)
    transit_entry.grid(row=1, column=1)
    
    account_entry = tk.Entry(options_window)
    account_entry.grid(row=2, column=1)
    
    def save_options():
        institution_var.set(institution_entry.get())
        transit_var.set(transit_entry.get())
        account_var.set(account_entry.get())
        options_window.destroy()
    
    save_button = tk.Button(options_window, text="Save", command=save_options)
    save_button.grid(row=3, column=1, pady=10)

institution_var = tk.StringVar()
transit_var = tk.StringVar()
account_var = tk.StringVar()

options_button = tk.Button(root, text="Options", command=open_options)
options_button.grid(row=4, column=0, columnspan=2)

def convert():
    csv_file = file_path_var.get()
    payment_date = payment_date_entry.get()
    institution = institution_var.get()
    transit = transit_var.get()
    account = account_var.get()
    
    if csv_file and payment_date and institution and transit and account:
        generate_dat_file(csv_file, payment_date, institution, transit, account)
    else:
        messagebox.showwarning("Warning", "Please complete all fields before converting.")

convert_button = tk.Button(root, text="Convert", command=convert)
convert_button.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()