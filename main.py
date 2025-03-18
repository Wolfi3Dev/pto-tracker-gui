import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union

class PTOManager:
    def __init__(self, data_file="pto_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file or create default structure if it doesn't exist."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {self.data_file}, creating new data structure.")
        
        # Default data structure
        return {
            "yearly_pto_hours": 0,
            "used_pto_hours": 0,
            "pto_requests": []
        }
    
    def _save_data(self) -> None:
        """Save data to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _validate_date(self, date_str: str) -> Optional[str]:
        """Validate and normalize date string in MM-DD-YY format."""
        try:
            # Parse the MM-DD-YY format
            date_obj = datetime.strptime(date_str, "%m-%d-%y")
            # Store as ISO format for consistent sorting (YYYY-MM-DD)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    def _format_date_for_display(self, iso_date: str) -> str:
        """Convert ISO date (YYYY-MM-DD) to display format (MM-DD-YY)."""
        try:
            date_obj = datetime.strptime(iso_date, "%Y-%m-%d")
            return date_obj.strftime("%m-%d-%y")
        except ValueError:
            return iso_date  # Return as is if there's an error
        
    def set_yearly_pto_hours(self, hours: float) -> None:
        """Set the total yearly PTO hours available."""
        self.data["yearly_pto_hours"] = hours
        self._save_data()
        print(f"Yearly PTO hours set to {hours}.")
    
    def add_pto_request(self, date: str, is_half_day: bool = False, note: str = "") -> None:
        """Add a new PTO request."""
        # Validate and normalize date
        normalized_date = self._validate_date(date)
        if not normalized_date:
            print("Invalid date format. Please use MM-DD-YY.")
            return
        
        # Check if date already exists
        for request in self.data["pto_requests"]:
            if request["date"] == normalized_date:
                display_date = self._format_date_for_display(normalized_date)
                print(f"A PTO request for {display_date} already exists. Use edit instead.")
                return
        
        hours = 4 if is_half_day else 8
        
        # Create new request
        new_request = {
            "date": normalized_date,
            "is_half_day": is_half_day,
            "hours": hours,
            "note": note
        }
        
        self.data["pto_requests"].append(new_request)
        
        # Sort requests by date
        self.data["pto_requests"].sort(key=lambda x: x["date"])
        
        # Update used hours
        self.data["used_pto_hours"] += hours
        
        self._save_data()
        display_date = self._format_date_for_display(normalized_date)
        print(f"Added PTO request for {display_date}.")
    
    def edit_pto_request(self, date: str, new_date: Optional[str] = None, 
                        is_half_day: Optional[bool] = None, note: Optional[str] = None) -> None:
        """Edit an existing PTO request."""
        # Validate and normalize the lookup date
        normalized_date = self._validate_date(date)
        if not normalized_date:
            print("Invalid date format for lookup date. Please use MM-DD-YY.")
            return
            
        # Validate and normalize the new date if provided
        normalized_new_date = None
        if new_date:
            normalized_new_date = self._validate_date(new_date)
            if not normalized_new_date:
                print("Invalid date format for new date. Please use MM-DD-YY.")
                return
        
        for i, request in enumerate(self.data["pto_requests"]):
            if request["date"] == normalized_date:
                # Update the used hours count
                old_hours = request["hours"]
                
                if normalized_new_date is not None:
                    request["date"] = normalized_new_date
                
                if is_half_day is not None:
                    request["is_half_day"] = is_half_day
                    request["hours"] = 4 if is_half_day else 8
                
                if note is not None:
                    request["note"] = note
                
                # Update the total used hours
                self.data["used_pto_hours"] = self.data["used_pto_hours"] - old_hours + request["hours"]
                
                # Sort requests by date
                self.data["pto_requests"].sort(key=lambda x: x["date"])
                
                self._save_data()
                display_date = self._format_date_for_display(normalized_date)
                print(f"Updated PTO request for {display_date}.")
                return
        
        display_date = self._format_date_for_display(normalized_date)
        print(f"No PTO request found for {display_date}.")
    
    def remove_pto_request(self, date: str) -> None:
        """Remove a PTO request."""
        # Validate and normalize date
        normalized_date = self._validate_date(date)
        if not normalized_date:
            print("Invalid date format. Please use MM-DD-YY.")
            return
            
        for i, request in enumerate(self.data["pto_requests"]):
            if request["date"] == normalized_date:
                # Update the used hours count
                self.data["used_pto_hours"] -= request["hours"]
                
                # Remove the request
                self.data["pto_requests"].pop(i)
                
                self._save_data()
                display_date = self._format_date_for_display(normalized_date)
                print(f"Removed PTO request for {display_date}.")
                return
        
        display_date = self._format_date_for_display(normalized_date)
        print(f"No PTO request found for {display_date}.")
    
    def list_pto_requests(self) -> None:
        """List all PTO requests."""
        if not self.data["pto_requests"]:
            print("No PTO requests found.")
            return
        
        print("\nCurrent PTO Requests:")
        print("=" * 50)
        for request in self.data["pto_requests"]:
            day_type = "Half Day" if request["is_half_day"] else "Full Day"
            display_date = self._format_date_for_display(request["date"])
            note_str = f" - Note: {request['note']}" if request["note"] else ""
            print(f"{display_date} - {day_type} ({request['hours']} hours){note_str}")
        print("=" * 50)
    
    def show_summary(self) -> None:
        """Display a summary of PTO information."""
        remaining = self.data["yearly_pto_hours"] - self.data["used_pto_hours"]
        
        print("\nPTO Summary:")
        print("=" * 50)
        print(f"Total Yearly PTO: {self.data['yearly_pto_hours']} hours")
        print(f"Used PTO: {self.data['used_pto_hours']} hours")
        print(f"Remaining PTO: {remaining} hours")
        print("=" * 50)

def run_gui():
    """Run a simple GUI for the PTO manager using tkinter."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, simpledialog
    except ImportError:
        print("Tkinter not available. Please install it or use the terminal interface.")
        import sys
        sys.exit(1)
    
    pto = PTOManager()
    
    # Main window
    root = tk.Tk()
    root.title("PTO Manager")
    root.geometry("700x500")
    
    # Style
    style = ttk.Style()
    style.configure("TButton", padding=6, relief="flat")
    style.configure("TFrame", padding=10)
    
    # Frame for summary info
    summary_frame = ttk.Frame(root, padding="10")
    summary_frame.pack(fill=tk.X, padx=10, pady=5)
    
    yearly_pto_var = tk.StringVar()
    used_pto_var = tk.StringVar()
    remaining_pto_var = tk.StringVar()
    
    # Summary labels
    ttk.Label(summary_frame, text="Yearly PTO Hours:").grid(row=0, column=0, sticky=tk.W, padx=5)
    ttk.Label(summary_frame, textvariable=yearly_pto_var).grid(row=0, column=1, sticky=tk.W, padx=5)
    
    ttk.Label(summary_frame, text="Used PTO Hours:").grid(row=1, column=0, sticky=tk.W, padx=5)
    ttk.Label(summary_frame, textvariable=used_pto_var).grid(row=1, column=1, sticky=tk.W, padx=5)
    
    ttk.Label(summary_frame, text="Remaining PTO Hours:").grid(row=2, column=0, sticky=tk.W, padx=5)
    ttk.Label(summary_frame, textvariable=remaining_pto_var).grid(row=2, column=1, sticky=tk.W, padx=5)
    
    # PTO Requests List
    list_frame = ttk.Frame(root, padding="10")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    ttk.Label(list_frame, text="PTO Requests:").pack(anchor=tk.W)
    
    # Treeview for PTO requests
    columns = ("Date", "Type", "Hours", "Note")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings")
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    tree.column("Date", width=150)
    tree.column("Type", width=100)
    tree.column("Hours", width=80)
    tree.column("Note", width=250)
    
    tree.pack(fill=tk.BOTH, expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Buttons frame
    btn_frame = ttk.Frame(root, padding="10")
    btn_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def update_display():
        """Update the display with current data."""
        # Clear current tree items
        for item in tree.get_children():
            tree.delete(item)
        
        # Update summary variables
        yearly_pto_var.set(f"{pto.data['yearly_pto_hours']} hours")
        used_pto_var.set(f"{pto.data['used_pto_hours']} hours")
        remaining = pto.data['yearly_pto_hours'] - pto.data['used_pto_hours']
        remaining_pto_var.set(f"{remaining} hours")
        
        # Add PTO requests to tree
        for request in pto.data["pto_requests"]:
            day_type = "Half Day" if request["is_half_day"] else "Full Day"
            display_date = pto._format_date_for_display(request["date"])
            tree.insert("", tk.END, values=(
                display_date,
                day_type,
                f"{request['hours']} hrs",
                request["note"]
            ))
    
    def set_yearly_pto():
        """Set the yearly PTO hours."""
        hours = simpledialog.askfloat("Yearly PTO", "Enter yearly PTO hours:", 
                                     minvalue=0, initialvalue=pto.data["yearly_pto_hours"])
        if hours is not None:
            pto.set_yearly_pto_hours(hours)
            update_display()
    
    def add_pto():
        """Add a new PTO request."""
        add_window = tk.Toplevel(root)
        add_window.title("Add PTO Request")
        add_window.geometry("400x200")
        add_window.transient(root)

        add_window.columnconfigure(0, weight=0)  # Label column stays fixed width
        add_window.columnconfigure(1, weight=1)  # Entry column expands to fill space
        
        ttk.Label(add_window, text="Date (MM-DD-YY):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = ttk.Entry(add_window, width=20)
        date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        is_half_day_var = tk.BooleanVar()
        ttk.Checkbutton(add_window, text="Half Day", variable=is_half_day_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(add_window, text="Note:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        note_entry = ttk.Entry(add_window, width=30)
        note_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        def submit():
            date = date_entry.get().strip()
            is_half_day = is_half_day_var.get()
            note = note_entry.get().strip()
            
            normalized_date = pto._validate_date(date)
            if normalized_date:
                pto.add_pto_request(date, is_half_day, note)
                add_window.destroy()
                update_display()
            else:
                messagebox.showerror("Error", "Invalid date format. Please use MM-DD-YY.")
        
        ttk.Button(add_window, text="Add", command=submit).grid(
            row=3, column=0, columnspan=2, pady=15)
    
    def edit_pto():
        """Edit a selected PTO request."""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a PTO request to edit.")
            return
        
        # Get the date from the selected item
        item_values = tree.item(selected[0], "values")
        display_date = item_values[0]
        
        # Convert to ISO format to find in the data
        orig_date_obj = datetime.strptime(display_date, "%m-%d-%y")
        iso_date = orig_date_obj.strftime("%Y-%m-%d")
        
        # Find the request data
        request_data = None
        for req in pto.data["pto_requests"]:
            if req["date"] == iso_date:
                request_data = req
                break
        
        if not request_data:
            messagebox.showerror("Error", "Could not find request data.")
            return
        
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit PTO Request")
        edit_window.geometry("400x200")
        edit_window.transient(root)

        edit_window.columnconfigure(0, weight=0)  # Label column stays fixed width
        edit_window.columnconfigure(1, weight=1)  # Entry column expands to fill space
        
        ttk.Label(edit_window, text="Date (MM-DD-YY):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = ttk.Entry(edit_window, width=20)
        date_entry.insert(0, display_date)
        date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        is_half_day_var = tk.BooleanVar(value=request_data["is_half_day"])
        ttk.Checkbutton(edit_window, text="Half Day", variable=is_half_day_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Note:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        note_entry = ttk.Entry(edit_window, width=30)
        note_entry.insert(0, request_data["note"])
        note_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        def submit():
            new_date = date_entry.get().strip()
            is_half_day = is_half_day_var.get()
            note = note_entry.get().strip()
            
            if pto._validate_date(new_date):
                pto.edit_pto_request(display_date, new_date, is_half_day, note)
                edit_window.destroy()
                update_display()
            else:
                messagebox.showerror("Error", "Invalid date format. Please use MM-DD-YY.")
        
        ttk.Button(edit_window, text="Update", command=submit).grid(
            row=3, column=0, columnspan=2, pady=15)
    
    def remove_pto():
        """Remove a selected PTO request."""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a PTO request to remove.")
            return
        
        # Get the date from the selected item
        item_values = tree.item(selected[0], "values")
        display_date = item_values[0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove the PTO request for {display_date}?"):
            pto.remove_pto_request(display_date)
            update_display()
    
    # Create buttons
    ttk.Button(btn_frame, text="Set Yearly PTO", command=set_yearly_pto).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Add PTO", command=add_pto).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Edit PTO", command=edit_pto).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Remove PTO", command=remove_pto).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Refresh", command=update_display).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Exit", command=root.destroy).pack(side=tk.RIGHT, padx=5)
    
    # Initial display update
    update_display()
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    # Check if GUI mode is requested
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--gui", "-g"]:
        run_gui()
    else:
        print("PTO Manager starting in terminal mode.")
        print("To use GUI mode, restart with --gui or -g flag.")
        run_terminal_interface()