import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import pydicom
import os

class DicomTagEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Tag Editor")
        self.files = []
        self.current_ds = None
        self.current_file = None

        # File selection
        self.file_frame = ttk.Frame(root)
        self.file_frame.pack(fill=tk.X, padx=10, pady=5)
        self.select_btn = ttk.Button(self.file_frame, text="Select DICOM Files", command=self.select_files)
        self.select_btn.pack(side=tk.LEFT)
        self.file_list = tk.Listbox(self.file_frame, height=4)
        self.file_list.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.file_list.bind('<<ListboxSelect>>', self.on_file_select)

        # Tag display
        self.tag_frame = ttk.Frame(root)
        self.tag_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tag_tree = ttk.Treeview(self.tag_frame, columns=("Tag", "Name", "Value"), show="headings")
        self.tag_tree.heading("Tag", text="Tag")
        self.tag_tree.heading("Name", text="Name")
        self.tag_tree.heading("Value", text="Value")
        self.tag_tree.pack(fill=tk.BOTH, expand=True)
        self.tag_tree.bind('<Double-1>', self.edit_tag)

        # Add Tag to Series button
        self.add_tag_btn = ttk.Button(root, text="Add Tag to Series", command=self.add_tag_to_series)
        self.add_tag_btn.pack(pady=5)

        # Save button
        self.save_btn = ttk.Button(root, text="Save Changes", command=self.save_changes)
        self.save_btn.pack(pady=5)
    def add_tag_to_series(self):
        if not self.files:
            messagebox.showinfo("Info", "No DICOM files loaded.")
            return
        tag_str = simpledialog.askstring("Add Tag", "Enter tag (group,element) in hex, e.g. 0010,0020:")
        if not tag_str:
            return
        try:
            group, element = [int(x, 16) for x in tag_str.replace('(','').replace(')','').split(',')]
            tag_tuple = (group, element)
        except Exception:
            messagebox.showerror("Error", "Invalid tag format. Use hex, e.g. 0010,0020")
            return
        value = simpledialog.askstring("Add Tag", f"Enter value for tag {tag_str}:")
        if value is None:
            return
        # Try to look up VR from pydicom dictionary
        from pydicom.datadict import dictionary_VR
        vr = dictionary_VR(tag_tuple)
        if vr is None:
            vr = simpledialog.askstring("Add Tag", "VR (Value Representation) not found. Enter VR (e.g. PN, LO, SH):")
            if not vr:
                messagebox.showerror("Error", "VR is required for unknown tags.")
                return
        updated = 0
        for file_path in self.files:
            try:
                ds = pydicom.dcmread(file_path)
                from pydicom.dataelem import DataElement
                ds[tag_tuple] = DataElement(tag_tuple, vr, value)
                ds.save_as(file_path)
                updated += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add tag to {os.path.basename(file_path)}:\n{e}")
        messagebox.showinfo("Done", f"Added tag {tag_str} to {updated} files.")
        # Refresh current file's tags if needed
        if self.current_ds and self.current_file:
            self.populate_tags(self.current_ds)

    def select_files(self):
        files = filedialog.askopenfilenames(title="Select DICOM files", filetypes=[("DICOM files", "*.*")])
        if files:
            self.files = list(files)
            self.file_list.delete(0, tk.END)
            for f in self.files:
                self.file_list.insert(tk.END, os.path.basename(f))
            self.current_ds = None
            self.current_file = None
            self.tag_tree.delete(*self.tag_tree.get_children())

    def on_file_select(self, event):
        selection = self.file_list.curselection()
        if not selection:
            return
        idx = selection[0]
        file_path = self.files[idx]
        try:
            ds = pydicom.dcmread(file_path)
            self.current_ds = ds
            self.current_file = file_path
            self.populate_tags(ds)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read DICOM file:\n{e}")

    def populate_tags(self, ds):
        self.tag_tree.delete(*self.tag_tree.get_children())
        for elem in ds:
            tag_str = f"({elem.tag.group:04X},{elem.tag.element:04X})"
            name = elem.name
            value = str(elem.value)[:100]  # Truncate long values
            self.tag_tree.insert('', 'end', values=(tag_str, name, value))

    def edit_tag(self, event):
        selected = self.tag_tree.selection()
        if not selected or not self.current_ds:
            return
        item = self.tag_tree.item(selected[0])
        tag_str, name, value = item['values']
        tag_tuple = tuple(int(x, 16) for x in tag_str[1:-1].split(','))
        new_value = simpledialog.askstring("Edit Tag", f"Enter new value for {name} ({tag_str}):", initialvalue=value)
        if new_value is not None:
            try:
                self.current_ds[tag_tuple].value = new_value
                self.populate_tags(self.current_ds)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update tag:\n{e}")

    def save_changes(self):
        if not self.current_ds or not self.current_file:
            messagebox.showinfo("Info", "No file selected.")
            return
        try:
            self.current_ds.save_as(self.current_file)
            messagebox.showinfo("Success", f"Changes saved to {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DicomTagEditor(root)
    root.mainloop()
