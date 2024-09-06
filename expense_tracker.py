import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker & Budget Planner")
        self.root.geometry("1366x720")

        self.expenses = []
        self.categories = ["Rent", "Food", "Entertainment", "Car", "Credit Cards"]
        self.monthly_budget = 0
        self.data_loaded = False
        self.unsaved_changes = False
        self.loaded_file_path = None  # Track the loaded file path for saving later

        # Display the home screen with two options: create or load
        self.show_home_screen()

    def show_home_screen(self):
        """Shows the initial home screen to choose between creating a new dashboard or loading one."""
        if self.unsaved_changes:
            save_prompt = messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you want to save before returning to the home screen?")
            if save_prompt:
                self.save_data()  # Save the data if the user chooses to save

        # Reset data if going back to the home screen
        self.reset_data()

        # Clear existing widgets before showing the home screen
        for widget in self.root.winfo_children():
            widget.destroy()

        # Home frame
        home_frame = ttk.Frame(self.root, padding="20")
        home_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        ttk.Label(home_frame, text="Welcome to the Expense Tracker", font=("Arial", 18)).grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky=tk.N)

        # Create new dashboard button
        ttk.Button(home_frame, text="Create New Dashboard", command=self.create_new_dashboard).grid(row=1, column=0, pady=10, padx=10, sticky=tk.N)

        # Load existing dashboard button
        ttk.Button(home_frame, text="Load Dashboard", command=self.load_data).grid(row=1, column=1, pady=10, padx=10, sticky=tk.N)

        # Centering horizontally and vertically
        home_frame.columnconfigure(0, weight=1)
        home_frame.columnconfigure(1, weight=1)
        home_frame.rowconfigure(0, weight=1)
        home_frame.rowconfigure(1, weight=1)

        # Center the home_frame in the root window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)



    def create_new_dashboard(self):
        """Clears the home screen and prompts the user to enter a budget and currency symbol, then creates a new dashboard."""
        self.reset_data()  # Reset data when creating a new dashboard

        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a centered frame for user inputs
        center_frame = ttk.Frame(self.root, padding="20")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Prompt user to enter a monthly budget
        ttk.Label(center_frame, text="Enter your monthly budget:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.budget_entry = ttk.Entry(center_frame)
        self.budget_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Prompt user to enter a currency symbol
        ttk.Label(center_frame, text="Enter your preferred currency symbol:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.currency_symbol_entry = ttk.Entry(center_frame)
        self.currency_symbol_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Create a button to confirm the inputs and proceed
        ttk.Button(center_frame, text="Create Dashboard", command=self.confirm_new_dashboard).grid(row=2, column=0, columnspan=2, pady=20)

        # Center the center_frame in the root window
        center_frame.columnconfigure(0, weight=1)
        center_frame.columnconfigure(1, weight=1)
        center_frame.rowconfigure(0, weight=1)
        center_frame.rowconfigure(1, weight=1)
        center_frame.rowconfigure(2, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def confirm_new_dashboard(self):
        """Confirms the creation of a new dashboard and initializes categories and other settings."""
        budget = self.budget_entry.get()
        if budget:
            self.monthly_budget = float(budget)
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid budget.")
            return

        currency_symbol = self.currency_symbol_entry.get()
        if currency_symbol:
            self.currency_symbol = currency_symbol
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid currency symbol.")
            return

        # Initialize default categories
        self.categories = ["Rent", "Food", "Entertainment", "Car", "Credit Cards"]
        self.create_widgets()  # Create the main widgets including the dropdown

    def get_currency_symbol(self):
        """Prompts the user to enter a currency symbol."""
        currency_symbol = simpledialog.askstring("Currency Symbol", "Enter your preferred currency symbol (e.g., $, €, ¥):")
        if currency_symbol:
            return currency_symbol
        else:
            if messagebox.askyesno("No Currency Symbol", "You haven't entered a currency symbol. Do you want to exit?"):
                self.root.quit()
                return None

    def reset_data(self):
        """Resets all data when creating a new dashboard or returning to the home screen."""
        self.expenses = []
        self.categories = []  # Reset categories
        self.monthly_budget = 0
        self.data_loaded = False
        self.unsaved_changes = False
        self.loaded_file_path = None

        # Reset additional fields if any
        self.additional_fields = {}

    def get_initial_budget(self):
        """Prompts the user to enter a monthly budget."""
        while True:
            budget = simpledialog.askfloat("Monthly Budget", "Enter your monthly budget:", minvalue=0.01)
            if budget is not None:
                return budget
            else:
                if messagebox.askyesno("No Budget", "You haven't entered a budget. Do you want to exit?"):
                    self.root.quit()
                    return 0
                
    def change_currency_symbol(self):
        """Prompts the user to change the currency symbol."""
        new_symbol = simpledialog.askstring("Change Currency Symbol", "Enter new currency symbol:", initialvalue=self.currency_symbol)

        if new_symbol is not None:  # Check if the user didn't cancel
            self.currency_symbol = new_symbol
            self.update_budget_info()
            self.update_expense_list()  # Refresh the expense list with the new symbol

            # Update the monthly budget display with the new currency symbol
            if hasattr(self, 'budget_label'):
                self.budget_label.config(text=f"Monthly Budget: {self.currency_symbol}{self.monthly_budget:.2f}")

    def create_widgets(self):
        """Creates the main interface for adding expenses and viewing the dashboard."""
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header Frame with Home and Currency Buttons
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)

        # Home Button
        ttk.Button(header_frame, text="Go Back Home", command=self.show_home_screen).pack(side=tk.LEFT, padx=2)

        # Currency Symbol Change Button
        ttk.Button(header_frame, text="Change Currency Symbol", command=self.change_currency_symbol).pack(side=tk.RIGHT, padx=2)

        # Budget Information Frame
        budget_info_frame = ttk.LabelFrame(main_frame, text="Budget Information", padding="5")
        budget_info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=(1, 1))

        # Font Size Adjustment
        font_size = ('Helvetica', 12)

        self.budget_label = ttk.Label(budget_info_frame, text=f"Monthly Budget: {self.currency_symbol}{self.monthly_budget:.2f}", font=font_size)
        self.budget_label.grid(row=0, column=0, sticky=tk.W, pady=1)

        self.total_expenses_label = ttk.Label(budget_info_frame, text=f"Total Expenses: {self.currency_symbol}0.00", font=font_size)
        self.total_expenses_label.grid(row=1, column=0, sticky=tk.W, pady=1)

        self.remaining_budget_label = ttk.Label(budget_info_frame, text=f"Remaining Budget: {self.currency_symbol}{self.monthly_budget:.2f}", font=font_size)
        self.remaining_budget_label.grid(row=2, column=0, sticky=tk.W, pady=1)

        # Expense Input Frame (Increased Height)
        input_frame = ttk.LabelFrame(main_frame, text="Add Expense", padding="5")
        input_frame.grid(row=2, column=0, padx=2, pady=2)

        # Font size for inputs
        input_font = ('Helvetica', 10)

        ttk.Label(input_frame, text="Date:", font=input_font).grid(row=0, column=0, sticky=tk.W)
        self.date_entry = DateEntry(input_frame, date_pattern='y-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=2, pady=1)

        ttk.Label(input_frame, text="Category:", font=input_font).grid(row=1, column=0, sticky=tk.W)
        self.category_combobox = ttk.Combobox(input_frame, values=self.categories, font=input_font)
        self.category_combobox.grid(row=1, column=1, padx=2, pady=1)

        ttk.Label(input_frame, text="Amount:", font=input_font).grid(row=2, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame, font=input_font)
        self.amount_entry.grid(row=2, column=1, padx=2, pady=1)

        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=2)

        # Category Management Frame
        category_frame = ttk.LabelFrame(main_frame, text="Manage Categories", padding="5")
        category_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)

        self.new_category_entry = ttk.Entry(category_frame)
        self.new_category_entry.grid(row=0, column=0, padx=2, pady=1)
        ttk.Button(category_frame, text="Add Category", command=self.add_category).grid(row=0, column=1, padx=2, pady=1)

        # Display Frame for Expenses and Budget
        display_frame = ttk.LabelFrame(main_frame, text="Expenses and Budget", padding="5")
        display_frame.grid(row=1, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=(5, 2))

        self.expense_tree = ttk.Treeview(display_frame, columns=('Date', 'Category', 'Amount'), show='headings')
        self.expense_tree.heading('Date', text='Date', command=lambda: self.sort_by_column('Date'))
        self.expense_tree.heading('Category', text='Category', command=lambda: self.sort_by_column('Category'))
        self.expense_tree.heading('Amount', text='Amount', command=lambda: self.sort_by_column('Amount'))
        self.expense_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.expense_tree.configure(yscrollcommand=scrollbar.set)

        # Generate Chart Frame
        chart_frame = ttk.LabelFrame(display_frame, text="Generate Chart", padding="5")
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)

        self.chart_type = tk.StringVar(value="pie")
        ttk.Radiobutton(chart_frame, text="Pie Chart", variable=self.chart_type, value="pie").pack(anchor=tk.W, padx=2)
        ttk.Radiobutton(chart_frame, text="Bar Graph", variable=self.chart_type, value="bar").pack(anchor=tk.W, padx=2)
        ttk.Radiobutton(chart_frame, text="Line Chart", variable=self.chart_type, value="line").pack(anchor=tk.W, padx=2)
        ttk.Button(chart_frame, text="Generate Chart", command=self.generate_chart).pack(pady=5)

        # Save Data Button (at the bottom-right corner of the display_frame)
        ttk.Button(display_frame, text="Save Data", command=self.save_data).grid(row=2, column=0, sticky=(tk.E, tk.S), padx=5, pady=(5, 2))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        display_frame.rowconfigure(1, weight=0)
        display_frame.rowconfigure(2, weight=0)

        # Increase height of input_frame
        input_frame.configure(height=150)  # Adjust this height value as needed 

        # Initialize sorting state
        self.sort_column = None
        self.sort_order = 1  # 1 for ascending, -1 for descending

    def sort_by_column(self, col):
        """Sort the treeview by a given column."""
        data = [(self.expense_tree.set(child, col), child) for child in self.expense_tree.get_children('')]
    
        # Determine if the column is numeric
        if col == 'Amount':
            data.sort(key=lambda x: float(x[0].replace(self.currency_symbol, '').replace(',', '')), reverse=(self.sort_order == -1))
        else:
            data.sort(key=lambda x: x[0], reverse=(self.sort_order == -1))
    
        # Rearrange items in the sorted order
        for index, (value, item) in enumerate(data):
            self.expense_tree.move(item, '', index)
    
        # Toggle sort order
        if self.sort_column == col:
            self.sort_order *= -1
        else:
            self.sort_column = col
            self.sort_order = 1
    
        # Update column header to reflect the current sort order
        self.expense_tree.heading(col, command=lambda: self.sort_by_column(col))


    def add_category(self):
        """Adds a new category to the list of categories."""
        new_category = self.new_category_entry.get().strip()
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.category_combobox['values'] = self.categories
            self.new_category_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Invalid Category", "Category is either empty or already exists.")

    def add_expense(self):
        """Adds an expense to the list."""
        date = self.date_entry.get_date()
        category = self.category_combobox.get()
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount.")
            return

        self.expenses.append({
            'date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': amount
        })

        self.update_expense_list()
        self.update_budget_info()
        self.unsaved_changes = True

    def update_budget_info(self):
        """Updates the budget information display."""
        total_expenses = sum(expense['amount'] for expense in self.expenses)
        remaining_budget = self.monthly_budget - total_expenses

        self.total_expenses_label.config(text=f"Total Expenses: {self.currency_symbol}{total_expenses:.2f}")
        self.remaining_budget_label.config(text=f"Remaining Budget: {self.currency_symbol}{remaining_budget:.2f}")

    def update_expense_list(self):
        """Updates the expense list display."""
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        for expense in self.expenses:
            self.expense_tree.insert('', 'end', values=(
                expense['date'],
                expense['category'],
                f"{self.currency_symbol}{expense['amount']:.2f}"
            ))

    def generate_chart(self):
        """Generates a chart based on selected chart type."""
        if not self.expenses:
            messagebox.showwarning("No Data", "No expenses to display.")
            return

        # Prepare data for charting
        expenses_by_category = {}
        expenses_by_date = {}
        dates = []
        amounts = []

        for expense in self.expenses:
            date = expense['date']
            category = expense['category']
            amount = expense['amount']

            if category not in expenses_by_category:
                expenses_by_category[category] = 0
            expenses_by_category[category] += amount

            if date not in expenses_by_date:
                expenses_by_date[date] = 0
            expenses_by_date[date] += amount

        # Sort data for line chart
        sorted_dates = sorted(expenses_by_date.keys())
        sorted_amounts = [expenses_by_date[date] for date in sorted_dates]

        # Convert string dates to datetime objects
        sorted_dates = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]

        chart_type = self.chart_type.get()

        plt.figure(figsize=(10, 6))
        if chart_type == "pie":
            plt.pie(expenses_by_category.values(), labels=expenses_by_category.keys(), autopct='%1.1f%%')
            plt.title('Expenses by Category (Pie Chart)')
        elif chart_type == "bar":
            plt.bar(expenses_by_category.keys(), expenses_by_category.values())
            plt.title('Expenses by Category (Bar Graph)')
            plt.xlabel('Category')
            plt.ylabel('Amount')
        elif chart_type == "line":
            plt.plot(sorted_dates, sorted_amounts, marker='o')
            plt.title('Expenses by Date (Line Chart)')
            plt.xlabel('Date')
            plt.ylabel('Amount')
            # Set date format for x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b, %Y'))
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        else:
            messagebox.showwarning("Invalid Chart Type", "Invalid chart type selected.")
            return

        plt.tight_layout()
        plt.show()

    def save_data(self):
        """Saves the data to a JSON file."""
        if not self.expenses:
            messagebox.showwarning("No Data", "No data to save.")
            return

        if not self.loaded_file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
            if not file_path:
                return
            self.loaded_file_path = file_path

        with open(self.loaded_file_path, 'w') as file:
            json.dump({
                'monthly_budget': self.monthly_budget,
                'currency_symbol': self.currency_symbol,
                'expenses': self.expenses,
                'categories': self.categories  # Save categories
            }, file, indent=4)

        self.unsaved_changes = False
        messagebox.showinfo("Save Data", "Data saved successfully.")

    def load_data(self):
        """Loads data from a JSON file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        with open(file_path, 'r') as file:
            data = json.load(file)
            self.monthly_budget = data.get('monthly_budget', 0)
            self.currency_symbol = data.get('currency_symbol', "$")
            self.expenses = data.get('expenses', [])
            self.categories = data.get('categories', ["Rent", "Food", "Entertainment", "Car", "Credit Cards"])  # Default categories if not present

        self.loaded_file_path = file_path
        self.data_loaded = True
        self.create_widgets()

        # Update the budget info and expense list with loaded data
        self.update_budget_info()
        self.update_expense_list()

    def run(self):
        """Runs the application."""
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    app.run()