import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector

current_mode = None
current_entries = {}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dellenter@06",
        database="judetrade_db",
        port=3306
    )

BG = "#F0FDF4"
DARK = "#166534"
BTN_GREEN = "#166534"
BTN_BLUE = "#1d4ed8"
BTN_RED = "#8B0000"
BTN_TEAL = "#0f766e"
FRAME_3D = "#d1d5db"
PLACEHOLDER = "#9CA3AF"
BUTTON = "#22C55E"

def fetch_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, client_name, wallet_balance FROM client")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_client(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT client_name, mobile, email, pan,
               demat_acc, depository, trading_acc,
               nominee, nominee_pan
        FROM client
        WHERE client_id = %s
    """, (client_id,))

    row = cursor.fetchone()
    conn.close()
    return row


def fetch_stocks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id, stock_name, sector, current_price FROM stock")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_stock(stock_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stock_name, sector, current_price,
               high_price, low_price, face_value,
               outstanding_shares
        FROM stock
        WHERE stock_id = %s
    """, (stock_id,))

    row = cursor.fetchone()
    conn.close()
    return row


def fetch_holdings(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT h.stock_id, s.stock_name, s.sector,
           h.quantity, h.avg_buy_price, s.current_price
    FROM holdings h
    JOIN stock s ON h.stock_id = s.stock_id
    WHERE h.client_id = %s
    """
    cursor.execute(query, (client_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def client_has_holdings(client_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM holdings WHERE client_id = %s",
        (client_id,)
    )

    count = cur.fetchone()[0]
    conn.close()

    return count > 0

def validate_fields(field_names):
    for f in field_names:
        value = current_entries[f].get()
        if not value or str(value).strip() == "":
            return False
    return True


def record_exists(table, key_column, key_value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {key_column}=%s",
        (key_value,)
    )
    exists = cur.fetchone()[0] > 0
    conn.close()
    return exists


def fetch_existing_record(table, key_column, key_value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM {table} WHERE {key_column}=%s",
        (key_value,)
    )
    row = cur.fetchone()
    conn.close()
    return row




def calculate_portfolio_from_db(client_id):
    data = fetch_holdings(client_id)


    if not data:
        current_value_lbl.config(text="Current Value : ₹ 0")
        invested_value_lbl.config(text="Invested Value : ₹ 0")
        returns_lbl.config(text="Total Returns : ₹ 0")
        stock_count_lbl.config(text="No. of Stocks : 0")
        stock_types_lbl.config(text="Stock Types : --")
        shares_lbl.config(text="Shares per Stock :\n--")
        return

    invested = 0.0
    current = 0.0
    sectors = set()
    shares_list = []

    for _, stock_name, sector, qty, avg_buy, curr_price in data:

        qty = int(qty)
        avg_buy = float(avg_buy)
        curr_price = float(curr_price)

        invested += qty * avg_buy
        current += qty * curr_price

        sectors.add(sector)
        shares_list.append(f"{stock_name} : {qty}")

    returns = current - invested


    current_value_lbl.config(
        text=f"Current Value : ₹ {current:,.2f}"
    )

    invested_value_lbl.config(
        text=f"Invested Value : ₹ {invested:,.2f}"
    )

    returns_lbl.config(
        text=f"Total Returns : ₹ {returns:,.2f}"
    )

    stock_count_lbl.config(
        text=f"No. of Stocks : {len(data)}"
    )

    stock_types_lbl.config(
        text="Stock Types : " + ", ".join(sectors)
    )

    shares_lbl.config(
        text="Shares per Stock :\n" + "\n".join(shares_list)
    )



root = tk.Tk()
root.title("Login")
root.state("zoomed")
root.configure(bg=BG)

def login():
    users = {"ezekiel06": "362506", "jenita03": "pass369"}
    if entry_user.get() in users and users[entry_user.get()] == entry_pass.get():
        messagebox.showinfo("Success", "Welcome Admin!")
        root.destroy()
        open_main_window()
    else:
        messagebox.showerror("Error", "Invalid login")

def clear_user(e):
    if entry_user.get() == "Username":
        entry_user.delete(0, tk.END)
        entry_user.config(fg=DARK)

def clear_pass(e):
    if entry_pass.get() == "Password":
        entry_pass.delete(0, tk.END)
        entry_pass.config(show="*", fg=DARK)


logo_frame = tk.Frame(root, bg=BG)
logo_frame.pack(pady=30)

img = Image.open(r"c:\users\DELL\Desktop\Intern\logo.png")
img = img.resize((450, 450))
logo = ImageTk.PhotoImage(img)
tk.Label(logo_frame, image=logo, bg=BG).pack()
logo_frame.image = logo


login_frame = tk.Frame(root, bg=BG)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

entry_user = tk.Entry(login_frame, width=30, font=("Inter", 14), fg=PLACEHOLDER)
entry_user.insert(0, "Username")
entry_user.bind("<FocusIn>", clear_user)
entry_user.pack(pady=8)

entry_pass = tk.Entry(login_frame, width=30, font=("Inter", 14), fg=PLACEHOLDER)
entry_pass.insert(0, "Password")
entry_pass.bind("<FocusIn>", clear_pass)
entry_pass.pack(pady=8)

tk.Button(
    login_frame, text="LOGIN", width=25, height=2,
    bg=BUTTON, fg="white",
    font=("Inter", 12, "bold"),
    command=login
).pack(pady=16)


def open_main_window():
    main = tk.Tk()
    main.title("JUDETRADE – Brokerage Management System")
    main.state("zoomed")
    main.configure(bg=BG)


    header = tk.Frame(main, bg=DARK, bd=8, relief="ridge")
    header.pack(side="top", fill="x")

    img = Image.open(r"c:\users\DELL\Desktop\Intern\logo.png")
    img = img.resize((450, 130))
    logo = ImageTk.PhotoImage(img)
    tk.Label(header, image=logo, bg=BG).pack(pady=10)
    header.image = logo


    container = tk.Frame(main, bg=FRAME_3D, bd=8, relief="ridge")
    container.pack(fill="both", expand=True, padx=10, pady=5)


    left_panel = tk.LabelFrame(container, text="Details",
                               font=("Arial", 12, "bold"),
                               bg=BG, bd=6, relief="ridge")
    left_panel.place(x=10, y=10, width=900, height=420)

    right_panel = tk.LabelFrame(container, text="Portfolio / Analysis",
                                font=("Arial", 12, "bold"),
                                bg=BG, bd=6, relief="ridge")
    right_panel.place(x=920, y=10, width=580, height=420)


    button_frame = tk.Frame(container, bg=FRAME_3D, bd=6, relief="ridge")
    button_frame.place(x=10, y=440, width=1490, height=70)

    for i in range(7):
        button_frame.grid_columnconfigure(i, weight=1)

    btn = {"font": ("Arial", 12, "bold"), "fg": "white", "height": 2}

    # ================= HELPER FUNCTIONS =================



    # ================= ADD RECORD =================

    def add_record():
        if current_mode == "CLIENT":

            required = [
                "Client ID", "Client Name", "Mobile", "Email",
                "PAN", "Demat Acc", "Depository",
                "Trading Acc", "Nominee", "Nominee PAN"
            ]

            if not validate_fields(required):
                messagebox.showwarning(
                    "Missing Data",
                    "Please fill ALL client details before adding."
                )
                return

            cid = current_entries["Client ID"].get()

            if record_exists("client", "client_id", cid):
                messagebox.showerror(
                    "Duplicate Client",
                    "Client ID already exists!"
                )
                return

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO client
                (client_id, client_name, mobile, email, pan,
                 demat_acc, depository, trading_acc,
                 nominee, nominee_pan, wallet_balance)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)
            """, (
                cid,
                current_entries["Client Name"].get(),
                current_entries["Mobile"].get(),
                current_entries["Email"].get(),
                current_entries["PAN"].get(),
                current_entries["Demat Acc"].get(),
                current_entries["Depository"].get(),
                current_entries["Trading Acc"].get(),
                current_entries["Nominee"].get(),
                current_entries["Nominee PAN"].get()
            ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Client added successfully")


        elif current_mode == "STOCK":

            required = [
                "Stock ID", "Stock Name", "Sector",
                "Current Price", "High Price", "Low Price",
                "Face Value", "Outstanding Shares"
            ]

            if not validate_fields(required):
                messagebox.showwarning(
                    "Missing Data",
                    "Please fill ALL stock details before adding."
                )
                return

            sid = current_entries["Stock ID"].get()

            if record_exists("stock", "stock_id", sid):
                messagebox.showerror(
                    "Duplicate Stock",
                    "Stock ID already exists!"
                )
                return

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO stock
                (stock_id, stock_name, sector, current_price,
                 high_price, low_price, face_value, outstanding_shares)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                sid,
                current_entries["Stock Name"].get(),
                current_entries["Sector"].get(),
                current_entries["Current Price"].get(),
                current_entries["High Price"].get(),
                current_entries["Low Price"].get(),
                current_entries["Face Value"].get(),
                current_entries["Outstanding Shares"].get()
            ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stock added successfully")

    def update_record():
        if current_mode == "CLIENT":

            required = [
                "Client ID", "Client Name", "Mobile", "Email",
                "PAN", "Demat Acc", "Depository",
                "Trading Acc", "Nominee", "Nominee PAN"
            ]

            if not validate_fields(required):
                messagebox.showwarning(
                    "Missing Data",
                    "Please fill ALL client details before updating."
                )
                return

            cid = current_entries["Client ID"].get()

            if not record_exists("client", "client_id", cid):
                messagebox.showerror(
                    "Not Found",
                    "Client does not exist!"
                )
                return

            old = fetch_existing_record("client", "client_id", cid)

            new = (
                cid,
                current_entries["Client Name"].get(),
                current_entries["Mobile"].get(),
                current_entries["Email"].get(),
                current_entries["PAN"].get(),
                current_entries["Demat Acc"].get(),
                current_entries["Depository"].get(),
                current_entries["Trading Acc"].get(),
                current_entries["Nominee"].get(),
                current_entries["Nominee PAN"].get()
            )

            if old[0:10] == new:
                messagebox.showinfo(
                    "No Changes",
                    "No changes detected.\nNothing to update."
                )
                return

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE client SET
                client_name=%s, mobile=%s, email=%s, pan=%s,
                demat_acc=%s, depository=%s, trading_acc=%s,
                nominee=%s, nominee_pan=%s
                WHERE client_id=%s
            """, (
                new[1], new[2], new[3], new[4],
                new[5], new[6], new[7], new[8], new[9], new[0]
            ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Client updated successfully")


        elif current_mode == "STOCK":

            required = [
                "Stock ID", "Stock Name", "Sector",
                "Current Price", "High Price", "Low Price",
                "Face Value", "Outstanding Shares"
            ]

            if not validate_fields(required):
                messagebox.showwarning(
                    "Missing Data",
                    "Please fill ALL stock details before updating."
                )
                return

            sid = current_entries["Stock ID"].get()

            if not record_exists("stock", "stock_id", sid):
                messagebox.showerror(
                    "Not Found",
                    "Stock does not exist!"
                )
                return

            old = fetch_existing_record("stock", "stock_id", sid)

            new = (
                sid,
                current_entries["Stock Name"].get(),
                current_entries["Sector"].get(),
                current_entries["Current Price"].get(),
                current_entries["High Price"].get(),
                current_entries["Low Price"].get(),
                current_entries["Face Value"].get(),
                current_entries["Outstanding Shares"].get()
            )

            if old[0:8] == new:
                messagebox.showinfo(
                    "No Changes",
                    "No changes detected.\nNothing to update."
                )
                return

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE stock SET
                stock_name=%s, sector=%s, current_price=%s,
                high_price=%s, low_price=%s,
                face_value=%s, outstanding_shares=%s
                WHERE stock_id=%s
            """, (
                new[1], new[2], new[3],
                new[4], new[5], new[6], new[7], new[0]
            ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stock updated successfully")

    def delete_record():
        if current_mode == "CLIENT":
            cid = current_entries["Client ID"].get()

            if client_has_holdings(cid):
                messagebox.showwarning(
                    "Cannot Delete",
                    "Client has active investments.\n"
                    "Please sell all stocks before deleting."
                )
                return

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM client WHERE client_id = %s", (cid,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Client deleted successfully")

    def reset_form():
        for widget in current_entries.values():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)

        if current_mode == "CLIENT":
            current_value_lbl.config(text="Current Value : ₹ --")
            invested_value_lbl.config(text="Invested Value : ₹ --")
            returns_lbl.config(text="Total Returns : ₹ --")
            stock_count_lbl.config(text="No. of Stocks : --")
            stock_types_lbl.config(text="Stock Types : --")
            shares_lbl.config(text="Shares per Stock :\n--")

        elif current_mode == "STOCK":
            market_cap_lbl.config(text="Market Cap : ₹ --")
            bv_lbl.config(text="Book Value : ₹ --")
            pe_lbl.config(text="P/E Ratio : --")

    def load_client_and_portfolio(entry_widgets):
        client_id = entry_widgets["Client ID"].get()

        if not client_id:
            return


        data = fetch_client(client_id)

        if data:
            (
                name, mobile, email, pan,
                demat, depo, trading,
                nominee, nominee_pan
            ) = data

            entry_widgets["Client Name"].delete(0, tk.END)
            entry_widgets["Client Name"].insert(0, name)

            entry_widgets["Mobile"].delete(0, tk.END)
            entry_widgets["Mobile"].insert(0, mobile)

            entry_widgets["Email"].delete(0, tk.END)
            entry_widgets["Email"].insert(0, email)

            entry_widgets["PAN"].delete(0, tk.END)
            entry_widgets["PAN"].insert(0, pan)

            entry_widgets["Demat Acc"].delete(0, tk.END)
            entry_widgets["Demat Acc"].insert(0, demat)

            entry_widgets["Depository"].set(depo)

            entry_widgets["Trading Acc"].delete(0, tk.END)
            entry_widgets["Trading Acc"].insert(0, trading)

            entry_widgets["Nominee"].delete(0, tk.END)
            entry_widgets["Nominee"].insert(0, nominee)

            entry_widgets["Nominee PAN"].delete(0, tk.END)
            entry_widgets["Nominee PAN"].insert(0, nominee_pan)


        calculate_portfolio_from_db(client_id)

    def load_stock_details(entry_widgets):
        stock_id = entry_widgets["Stock ID"].get()

        if not stock_id:
            return

        data = fetch_stock(stock_id)

        if not data:
            return

        (
            name, sector, price,
            high, low, face,
            shares
        ) = data


        entry_widgets["Stock Name"].delete(0, tk.END)
        entry_widgets["Stock Name"].insert(0, name)

        entry_widgets["Sector"].set(sector)

        entry_widgets["Current Price"].delete(0, tk.END)
        entry_widgets["Current Price"].insert(0, price)

        entry_widgets["High Price"].delete(0, tk.END)
        entry_widgets["High Price"].insert(0, high)

        entry_widgets["Low Price"].delete(0, tk.END)
        entry_widgets["Low Price"].insert(0, low)

        entry_widgets["Face Value"].delete(0, tk.END)
        entry_widgets["Face Value"].insert(0, face)

        entry_widgets["Outstanding Shares"].delete(0, tk.END)
        entry_widgets["Outstanding Shares"].insert(0, shares)


        price=float(price)
        shares=int(shares)
        face=float(face)
        market_cap = price * shares
        book_value = face * shares

        market_cap_lbl.config(text=f"Market Cap : ₹ {market_cap:,.2f}")
        bv_lbl.config(text=f"Book Value : ₹ {book_value:,.2f}")


        eps = face * 0.15
        pe = price / eps if eps != 0 else 0

        pe_lbl.config(text=f"P/E Ratio : {pe:.2f}")


    def load_client_form():
        global current_mode, current_entries
        current_mode = "CLIENT"


        global current_value_lbl, invested_value_lbl
        global returns_lbl, stock_count_lbl
        global stock_types_lbl, shares_lbl

        left_panel.config(text="Client Details")
        for w in left_panel.winfo_children():
            w.destroy()


        entry_widgets = {}


        fields = [
            "Client ID", "Client Name", "Mobile",
            "Email", "PAN", "Demat Acc", "Depository",
            "Trading Acc", "Nominee", "Nominee PAN"
        ]

        depository_options = ["NSDL", "CDSL"]

        for i, f in enumerate(fields):

            tk.Label(
                left_panel,
                text=f,
                bg=BG,
                font=("Arial", 11, "bold")
            ).grid(row=i, column=0, sticky="w", pady=6, padx=10)


            if f == "Client ID":
                entry = tk.Entry(left_panel, width=30)
                entry.grid(row=i, column=1, pady=6)
                entry_widgets[f] = entry

                entry.bind(
                    "<KeyRelease>",
                    lambda e: load_client_and_portfolio(entry_widgets)
                )


            elif f == "Depository":
                cb = ttk.Combobox(
                    left_panel,
                    values=depository_options,
                    state="readonly",
                    width=28
                )
                cb.grid(row=i, column=1, pady=6)
                entry_widgets[f] = cb

            
            else:
                entry = tk.Entry(left_panel, width=30)
                entry.grid(row=i, column=1, pady=6)
                entry_widgets[f] = entry


        tk.Label(
            left_panel,
            text="Portfolio Metrics",
            font=("Arial", 13, "bold"),
            fg=DARK,
            bg=BG
        ).grid(row=0, column=2, padx=30, sticky="w")

        current_value_lbl = tk.Label(
            left_panel, text="Current Value : ₹ --",
            font=("Arial", 11), bg=BG
        )
        current_value_lbl.grid(row=1, column=2, padx=30, sticky="w")

        invested_value_lbl = tk.Label(
            left_panel, text="Invested Value : ₹ --",
            font=("Arial", 11), bg=BG
        )
        invested_value_lbl.grid(row=2, column=2, padx=30, sticky="w")

        returns_lbl = tk.Label(
            left_panel, text="Total Returns : ₹ --",
            font=("Arial", 11), bg=BG
        )
        returns_lbl.grid(row=3, column=2, padx=30, sticky="w")

        stock_count_lbl = tk.Label(
            left_panel, text="No. of Stocks : --",
            font=("Arial", 11), bg=BG
        )
        stock_count_lbl.grid(row=4, column=2, padx=30, sticky="w")

        stock_types_lbl = tk.Label(
            left_panel, text="Stock Types : --",
            font=("Arial", 11), bg=BG, wraplength=300, justify="left"
        )
        stock_types_lbl.grid(row=5, column=2, padx=30, sticky="w")

        shares_lbl = tk.Label(
            left_panel, text="Shares per Stock :\n--",
            font=("Arial", 11), bg=BG, justify="left"
        )
        shares_lbl.grid(row=6, column=2, padx=30, sticky="w")
        current_entries=entry_widgets


    def load_stock_form():
        global current_mode, current_entries
        current_mode = "STOCK"


        global pe_lbl, bv_lbl, market_cap_lbl

        left_panel.config(text="Stock Details")
        for w in left_panel.winfo_children():
            w.destroy()

        entry_widgets = {}

        fields = [
            "Stock ID", "Stock Name", "Sector",
            "Current Price", "High Price", "Low Price",
            "Face Value", "Outstanding Shares"
        ]

        sector_options = [
            "IT", "Banking", "Finance", "Pharma",
            "FMCG", "Energy", "Automobile", "Others"
        ]

        for i, f in enumerate(fields):
            tk.Label(
                left_panel,
                text=f,
                bg=BG,
                font=("Arial", 11, "bold")
            ).grid(row=i, column=0, sticky="w", pady=6, padx=10)


            if f == "Stock ID":
                entry = tk.Entry(left_panel, width=30)
                entry.grid(row=i, column=1, pady=6)
                entry_widgets[f] = entry

                entry.bind(
                    "<KeyRelease>",
                    lambda e: load_stock_details(entry_widgets)
                )


            elif f == "Sector":
                cb = ttk.Combobox(
                    left_panel,
                    values=sector_options,
                    state="readonly",
                    width=28
                )
                cb.grid(row=i, column=1, pady=6)
                entry_widgets[f] = cb

            else:
                entry = tk.Entry(left_panel, width=30)
                entry.grid(row=i, column=1, pady=6)
                entry_widgets[f] = entry


        tk.Label(
            left_panel,
            text="Stock Metrics",
            font=("Arial", 13, "bold"),
            fg=DARK,
            bg=BG
        ).grid(row=0, column=2, padx=30, sticky="w")

        market_cap_lbl = tk.Label(
            left_panel, text="Market Cap : ₹ --",
            font=("Arial", 11), bg=BG
        )
        market_cap_lbl.grid(row=1, column=2, padx=30, sticky="w")

        pe_lbl = tk.Label(
            left_panel, text="P/E Ratio : --",
            font=("Arial", 11), bg=BG
        )
        pe_lbl.grid(row=2, column=2, padx=30, sticky="w")

        bv_lbl = tk.Label(
            left_panel, text="Book Value : ₹ --",
            font=("Arial", 11), bg=BG
        )
        bv_lbl.grid(row=3, column=2, padx=30, sticky="w")
        current_entries=entry_widgets

        # ---------- TABLE FRAME (FIXED) ----------

    global tree  # Add this so functions can see it
    table_frame = tk.Frame(container, bg=FRAME_3D, bd=6, relief="ridge")
    table_frame.place(x=10, y=520, width=1490, height=240)

    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(table_frame, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scroll_y.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scroll_y.set)

    # 2. NOW DEFINE THE FUNCTIONS THAT USE 'tree'
    def load_stocks_into_tree():
        tree.delete(*tree.get_children())
        cols = ("Stock ID", "Stock Name", "Sector", "Current Price", "High", "Low")
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=200)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT stock_id, stock_name, sector, current_price, high_price, low_price FROM stock")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def load_clients_into_tree():
        tree.delete(*tree.get_children())
        cols = ("Client ID", "Client Name", "Mobile", "Email", "PAN", "Depository", "Wallet Balance")
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=180)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT client_id, client_name, mobile, email, pan, depository, wallet_balance FROM client")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
    tk.Button(
        button_frame, text="👤 CLIENT",
        bg=BTN_TEAL,
        command=lambda: (load_client_form(), load_clients_into_tree()),
        **btn
    ).grid(row=0, column=0, sticky="nsew", padx=5)

    tk.Button(
        button_frame, text="📈 STOCK",
        bg=BTN_BLUE,
        command=lambda: (load_stock_form(), load_stocks_into_tree()),
        **btn
    ).grid(row=0, column=1, sticky="nsew", padx=5)

    tk.Button(button_frame, text="➕ ADD",
              bg=BTN_GREEN, command=add_record, **btn)\
        .grid(row=0, column=2, sticky="nsew", padx=5)

    tk.Button(button_frame, text="✏️ UPDATE",
              bg=BTN_GREEN,command=update_record, **btn)\
        .grid(row=0, column=3, sticky="nsew", padx=5)

    tk.Button(button_frame, text="🗑️ DELETE",
              bg=BTN_GREEN,command=delete_record, **btn)\
        .grid(row=0, column=4, sticky="nsew", padx=5)

    tk.Button(button_frame, text="♻️ RESET",
              bg=BTN_GREEN,command=reset_form, **btn)\
        .grid(row=0, column=5, sticky="nsew", padx=5)

    tk.Button(button_frame, text="⛔ EXIT",
              bg=BTN_RED, command=main.destroy, **btn)\
        .grid(row=0, column=6, sticky="nsew", padx=5)



    load_client_form()
    main.mainloop()


root.mainloop()
