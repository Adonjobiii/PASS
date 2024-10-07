import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os

class AssemblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Two Pass Assemblers")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Initialize file paths
        self.input_file = "input.txt"
        self.optab_file = "optab.txt"
        self.symtab_file = "symtab.txt"
        self.intermediate_file = "intermediate.txt"
        self.length_file = "length.txt"
        self.output_file = "output.txt"
        self.objcode_file = "objcode.txt"

        self.create_widgets()
        self.create_menu()
        self.create_heading()

    def create_heading(self):
        heading_frame = ttk.Frame(self.root)
        heading_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

        heading_label = ttk.Label(heading_frame, text="Two Pass Assemblers", font=("Arial", 16, "bold"))
        heading_label.pack()

        copyright_label = ttk.Label(heading_frame, text="© ADON JOBI", font=("Arial", 10))
        copyright_label.pack()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.pass1_button = ttk.Button(buttons_frame, text="Run Pass 1", command=self.pass_one)
        self.pass1_button.grid(row=0, column=0, padx=5)

        self.pass2_button = ttk.Button(buttons_frame, text="Run Pass 2", command=self.pass_two)
        self.pass2_button.grid(row=0, column=1, padx=5)

        self.run_both_button = ttk.Button(buttons_frame, text="Run Both Passes", command=self.run_both_passes)
        self.run_both_button.grid(row=0, column=2, padx=5)

        content_frame = ttk.LabelFrame(main_frame, text="Output")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=("Arial", 10))
        self.content_text.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Input File", command=self.select_input_file)
        file_menu.add_command(label="Select OPTAB File", command=self.select_optab_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Pass 1", command=self.pass_one)
        run_menu.add_command(label="Run Pass 2", command=self.pass_two)
        run_menu.add_command(label="Run Both Passes", command=self.run_both_passes)
        menubar.add_cascade(label="Run", menu=run_menu)

        self.root.config(menu=menubar)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.input_file = file_path
            self.status_var.set(f"Selected input file: {os.path.basename(file_path)}")

    def select_optab_file(self):
        file_path = filedialog.askopenfilename(title="Select OPTAB File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.optab_file = file_path
            self.status_var.set(f"Selected OPTAB file: {os.path.basename(file_path)}")

    def pass_one(self):
        try:
            with open(self.input_file, "r") as fp1, \
                 open(self.optab_file, "r") as fp2, \
                 open(self.symtab_file, "w") as fp3, \
                 open(self.intermediate_file, "w") as fp4, \
                 open(self.length_file, "w") as fp5:

                line = fp1.readline().strip().split()
                if len(line) < 3:
                    messagebox.showerror("Error", "Invalid input file format.")
                    return
                
                label, opcode, operand = line

                if opcode == "START":
                    start = int(operand, 16)
                    locctr = start
                    fp4.write(f"{locctr:04X}\t{label}\t{opcode}\t{operand}\n")
                    line = fp1.readline().strip().split()
                    if line:
                        label, opcode, operand = line
                    else:
                        messagebox.showerror("Error", "Invalid input file format.")
                        return
                else:
                    locctr = 0

                while opcode != "END":
                    fp4.write(f"{locctr:04X}\t{label}\t{opcode}\t{operand}\n")

                    if label != "**":
                        fp3.write(f"{label}\t{locctr:04X}\n")

                    fp2.seek(0)
                    optab = fp2.readlines()
                    found = False
                    for entry in optab:
                        optab_opcode, _ = entry.strip().split()
                        if opcode == optab_opcode:
                            locctr += 3
                            found = True
                            break

                    if not found:
                        if opcode == "WORD":
                            locctr += 3
                        elif opcode == "RESW":
                            locctr += 3 * int(operand)
                        elif opcode == "BYTE":
                            if operand.startswith("C'") and operand.endswith("'"):
                                locctr += len(operand) - 3
                            elif operand.startswith("X'") and operand.endswith("'"):
                                locctr += (len(operand) - 3) // 2
                            else:
                                messagebox.showerror("Error", f"Invalid BYTE operand: {operand}")
                                return
                        elif opcode == "RESB":
                            locctr += int(operand)
                        else:
                            messagebox.showerror("Error", f"Invalid opcode: {opcode}")
                            return

                    line = fp1.readline().strip().split()
                    if line:
                        label, opcode, operand = line
                    else:
                        break

                fp4.write(f"{locctr:04X}\t{label}\t{opcode}\t{operand}\n")  # Output for the final record
                length = locctr - start
                fp5.write(f"{length:04X}\n")

            self.status_var.set("Pass 1 completed successfully!")
            self.display_content()

        except FileNotFoundError as e:
            messagebox.showerror("File Error", f"File not found: {e.filename}")
            self.status_var.set("Pass 1 failed due to missing file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Pass 1 failed due to an error.")

    def pass_two(self):
        try:
            # Class-level constants for opcodes and their corresponding machine codes
            MNEMONIC_CODES = {
                "LDA": "33", "STA": "44", "LDCH": "53", "STCH": "57"
            }

            # Load symbol table into memory for fast lookup
            symtab = {}
            with open(self.symtab_file, "r") as symtab_fp:
                for line in symtab_fp:
                    symbol, address = line.strip().split()
                    symtab[symbol] = address

            with open(self.output_file, "w") as output_fp, \
                 open(self.intermediate_file, "r") as intermediate_fp, \
                 open(self.objcode_file, "w") as objcode_fp:

                lines = intermediate_fp.readlines()

                # Process the first line
                first_line = lines[0].split()
                if len(first_line) < 3:
                    messagebox.showerror("Error", "Invalid intermediate file format.")
                    return

                label, opcode, operand = first_line[:3]

                # Write header record for object code file if opcode is START
                if opcode == "START":
                    output_fp.write(f"\t{label}\t{opcode}\t{operand}\n")
                    start_address = operand
                    objcode_fp.write(f"H^{label}^00{start_address}^00\n")  # Add final address later
                    next_line = lines[1].split()
                    start = int(next_line[0], 16)
                else:
                    start = 0

                # Begin writing text records for object code
                for line in lines[1:]:
                    tokens = line.strip().split()

                    if len(tokens) < 4:
                        continue

                    address = tokens[0]
                    label = tokens[1]
                    opcode = tokens[2]
                    operand = tokens[3]

                    # Handle BYTE operand object code generation
                    if opcode == "BYTE":
                        if operand.startswith("C'") and operand.endswith("'"):
                            obj_code = ''.join(f"{ord(c):02X}" for c in operand[2:-1])
                        elif operand.startswith("X'") and operand.endswith("'"):
                            obj_code = operand[2:-1]
                        output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\t{obj_code}\n")
                        objcode_fp.write(f"^{obj_code}")

                    # Handle WORD operand object code generation
                    elif opcode == "WORD":
                        obj_code = f"{int(operand):06X}"
                        output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\t{obj_code}\n")
                        objcode_fp.write(f"^{obj_code}")

                    # Handle RESW and RESB (no object code is generated, just addresses)
                    elif opcode in ["RESB", "RESW"]:
                        output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\n")

                    # Handle normal opcodes from MNEMONIC_CODES
                    elif opcode in MNEMONIC_CODES:
                        obj_code = MNEMONIC_CODES[opcode]

                        # If the operand is not COPY, find its address in the symbol table
                        if operand != "COPY":
                            if operand in symtab:
                                symbol_address = symtab[operand]
                                output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\t{obj_code}{symbol_address}\n")
                                objcode_fp.write(f"^{obj_code}{symbol_address}")
                            else:
                                messagebox.showerror("Error", f"Undefined symbol: {operand}")
                                self.status_var.set("Pass 2 failed due to undefined symbol.")
                                return
                        else:
                            # Handle the COPY case with a fixed address (0000)
                            output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\t{obj_code}0000\n")
                            objcode_fp.write(f"^{obj_code}0000")

                    # Handle the END opcode correctly
                    elif opcode == "END":
                        output_fp.write(f"{address}\t{label}\t{opcode}\t{operand}\n")
                        objcode_fp.write(f"\nE^{start:02X}")
                        break  # Exit the loop after processing END

                    else:
                        messagebox.showerror("Error", f"Undefined opcode: {opcode}")
                        self.status_var.set("Pass 2 failed due to undefined opcode.")
                        return

                self.status_var.set("Pass 2 completed successfully!")
                self.display_content()

        except FileNotFoundError as e:
            messagebox.showerror("File Error", f"File not found: {e.filename}")
            self.status_var.set("Pass 2 failed due to missing file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Pass 2 failed due to an error.")

    def display_content(self):
        self.content_text.delete(1.0, tk.END)
        try:
            if os.path.exists(self.input_file):
                with open(self.input_file, "r") as fp1:
                    self.content_text.insert(tk.END, "\nContents of Input File:\n\n" + fp1.read())

            if os.path.exists(self.intermediate_file):
                with open(self.intermediate_file, "r") as fp2:
                    self.content_text.insert(tk.END, "\nContents of Intermediate File:\n\n" + fp2.read())

            if os.path.exists(self.symtab_file):
                with open(self.symtab_file, "r") as fp3:
                    self.content_text.insert(tk.END, "\nContents of Symbol Table:\n\n" + fp3.read())

            if os.path.exists(self.output_file):
                with open(self.output_file, "r") as fp4:
                    self.content_text.insert(tk.END, "\nContents of Output File:\n\n" + fp4.read())

            if os.path.exists(self.objcode_file):
                with open(self.objcode_file, "r") as fp5:
                    self.content_text.insert(tk.END, "\nContents of Object Code File:\n\n" + fp5.read())
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying content: {e}")

    def run_both_passes(self):
        self.pass_one()
        if self.status_var.get() == "Pass 1 completed successfully!":
            self.pass_two()

def main():
    root = tk.Tk()
    app = AssemblerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

