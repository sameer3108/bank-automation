import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import csv
import os

BATCH_FILE = "batch_number.txt"

# Open last batch number
def get_batch_number():
    if not os.path.exists(BATCH_FILE):
        with open(BATCH_FILE, "w") as f:
            f.write("0248")               # Company wanted it to start at 248, could be anything
        return 248 
    with open(BATCH_FILE, "r") as f:
        try:
            return int(f.read())
        except:
            return 248

# Increment batch number
def increment_batch_number(current):
    new_batch = current + 1
    with open(BATCH_FILE, "w") as f:
        f.write(str(new_batch).zfill(4))
    return new_batch

# Batch number
batch_number = get_batch_number()

# GUI 
class EFTConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EFT 80 Byte File Converter")
        
        # Today's Date
        today = datetime.now().strftime('%d/%m/%y')
        tk.Label(root, text=f"Today's Date: {today}").grid(row=0, column=0, columnspan=3, pady=5)
        
        # Payment Date
        tk.Label(root, text="Payment Date (ddmmyy):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.payment_date_entry = tk.Entry(root)
        self.payment_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Batch Number
        tk.Label(root, text="Batch Number:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.batch_label = tk.Label(root, text=str(batch_number).zfill(4))
        self.batch_label.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Choose File
        tk.Label(root, text="Choose CSV File:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(root, textvariable=self.file_path_var, width=40)
        self.file_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.choose_file).grid(row=3, column=2, padx=5, pady=5)
        
        # Options Button
        tk.Button(root, text="Options", command=self.open_options).grid(row=4, column=0, columnspan=3, pady=5)
        
        # Convert Button
        tk.Button(root, text="Convert", command=self.convert_to_dat).grid(row=5, column=0, columnspan=3, pady=10)
        
        # Options fields
        self.institution_number = ""
        self.transit_number = ""
        self.account_number = ""
    
    def choose_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.file_path_var.set(file)
    
    def open_options(self):
        # Second window
        options_window = tk.Toplevel(self.root)
        options_window.title("Bank Information")
        
        tk.Label(options_window, text="Institution Number:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.institution_entry = tk.Entry(options_window)
        self.institution_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(options_window, text="Transit Number:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.transit_entry = tk.Entry(options_window)
        self.transit_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(options_window, text="Account Number:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.account_entry = tk.Entry(options_window)
        self.account_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(options_window, text="Save", command=lambda: self.save_options(options_window)).grid(row=3, column=0, columnspan=2, pady=10)
    
    def save_options(self, window):
        self.institution_number = self.institution_entry.get().zfill(4) if self.institution_entry.get() else " " * 4
        self.transit_number = self.transit_entry.get().zfill(5) if self.transit_entry.get() else " " * 5
        self.account_number = self.account_entry.get().ljust(12) if self.account_entry.get() else " " * 12
        window.destroy()
    
    def convert_to_dat(self):
        global batch_number
        csv_file = self.file_path_var.get()
        payment_date = self.payment_date_entry.get()
        institution = self.institution_number if self.institution_number else " " * 4
        transit = self.transit_number if self.transit_number else " " * 5
        account = self.account_number if self.account_number else " " * 12
        
        # Validate inputs
        if not csv_file:
            messagebox.showerror("Error", "Please choose a CSV file.")
            return
        if not payment_date or len(payment_date) != 6 or not payment_date.isdigit():
            messagebox.showerror("Error", "Please enter a valid payment date in ddmmyy format.")
            return
        
        try:
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
            
            if not rows:
                messagebox.showerror("Error", "CSV file is empty.")
                return
            
            # Output location
            output_file = os.path.splitext(csv_file)[0] + ".dat"
            
            # Totals
            num_transactions = len(rows)
            total_value = 0
            dat_content = []
            
            # Header Line
            header = (
                "H" 
                "TPABK12345"  # 10 char
                "C"  # Credit/Debit indicator
                "C460"  # CPA Code 3 char
                f"{payment_date}"  # 6 char
                f"{' ' * 15}"  # 15 spaces
                f"{institution}"  # 4 char
                f"{transit}"  # 5 char
                f"{account} "  # 12 char + space
                f"{str(batch_number).zfill(4)}"  # 4 char
                f"{' ' * 19}"  # Remaining spaces to reach 80 characters
            )
            header = header.ljust(80)
            dat_content.append(header)
            
            # Detail Lines
            for row in rows:
                if len(row) < 3:
                    continue
                amount_str, bank_info, payee_name = row
                try:
                    amount = int(float(amount_str) * 100)
                except:
                    amount = 0
                total_value += amount
                
                # Parse bank_info coming from csv as #010*00003*68371234
                institution_num = " " * 4
                transit_num = " " * 5
                account_num = " " * 12
                if bank_info.startswith("#"):
                    parts = bank_info[1:].split("*")
                    if len(parts) == 3:
                        inst = parts[0].zfill(4)[:4]
                        transit = parts[1].zfill(5)[:5]
                        account = parts[2].ljust(12)[:12]
                        institution_num = inst
                        transit_num = transit
                        account_num = account
                # Format fields
                payee_name_formatted = payee_name[:23].ljust(23)
                reference_name = payee_name[:13].ljust(13)
                amount_formatted = str(amount).zfill(10)
                
                detail = (
                    "D" 
                    f"{payee_name_formatted}"  # 23 char
                    f"{payment_date}"  # 6 char
                    f"{reference_name}"  # 13 char
                    f"{' ' * 6}"  # 6 spaces
                    f"{institution_num}"  # 4 char
                    f"{transit_num}"  # 5 char
                    f"{account_num}"  # 12 char
                    f"{amount_formatted}"  # 10 char
                    f"{' ' * (80 - 1 - 23 - 6 - 13 - 6 - 4 - 5 - 12 - 10)}"  # Remaining spaces
                )
                detail = detail[:80]
                dat_content.append(detail)
            
            # Trailer Line
            total_value_str = str(total_value).zfill(14)
            trailer = (
                "T" 
                f"{str(num_transactions).zfill(6)}"
                f"{total_value_str}"  # (14 char)
                f"{' ' * (80 - 6 - 14)}"  # 80 char limit
            )
            trailer = trailer.ljust(80)
            dat_content.append(trailer)
            
            with open(output_file, "w", encoding='utf-8') as f:
                f.write("\n".join(dat_content))
            
            # Unique batch number, incremented from previous run
            batch_number = increment_batch_number(batch_number)
            self.batch_label.config(text=str(batch_number).zfill(4))
            
            messagebox.showinfo("Success", f"Conversion successful! Output saved to {output_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# GUI
root = tk.Tk()
app = EFTConverterApp(root)
root.mainloop()