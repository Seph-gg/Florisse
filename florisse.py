import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path("florisse.db")
STARTER_STOCK = 40


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with closing(connect()) as conn:
        with conn:
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('customer', 'admin'))
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 40,
                    discount REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS premade_bouquets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series TEXT NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    price REAL NOT NULL,
                    discount REAL NOT NULL DEFAULT 0.0
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS bouquet_contents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bouquet_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    qty INTEGER NOT NULL,
                    FOREIGN KEY (bouquet_id) REFERENCES premade_bouquets(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    label TEXT NOT NULL,
                    bouquet_id INTEGER,
                    product_id INTEGER,
                    qty INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    custom_notes TEXT,
                    materials_spec TEXT,
                    FOREIGN KEY (bouquet_id) REFERENCES premade_bouquets(id) ON DELETE SET NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)

            cur.execute("""
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES ('admin', 'password', 'admin')
            """)

            for cat_name in ["Main Flowers", "Fillers", "Ribbon"]:
                cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat_name,))

            seed_catalog(conn)


def category_id_by_name(conn, name):
    row = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()
    return row["id"] if row else None


def product_id_by_name(conn, name):
    row = conn.execute("SELECT id FROM products WHERE name = ?", (name,)).fetchone()
    return row["id"] if row else None


def seed_catalog(conn):
    cur = conn.cursor()
    existing = cur.execute("SELECT COUNT(*) AS cnt FROM products").fetchone()["cnt"]
    if existing > 0:
        return

    main_cat = category_id_by_name(conn, "Main Flowers")
    filler_cat = category_id_by_name(conn, "Fillers")
    ribbon_cat = category_id_by_name(conn, "Ribbon")

    items = [
        # Main Flowers
        (main_cat, "Lily / Tiger Lily", 65.0, STARTER_STOCK),
        (main_cat, "Tulips", 60.0, STARTER_STOCK),
        (main_cat, "Blooming Tulips", 70.0, STARTER_STOCK),
        (main_cat, "Big Daisy", 65.0, STARTER_STOCK),
        (main_cat, "Carnation", 75.0, STARTER_STOCK),
        (main_cat, "Gerbera", 70.0, STARTER_STOCK),
        (main_cat, "Poppy", 70.0, STARTER_STOCK),
        (main_cat, "Mini Sunflower", 70.0, STARTER_STOCK),
        (main_cat, "Medium Sunflower", 85.0, STARTER_STOCK),
        (main_cat, "Big Sunflower", 100.0, STARTER_STOCK),
        (main_cat, "Rose Ver 1.", 75.0, STARTER_STOCK),
        (main_cat, "Rose Ver 2.", 65.0, STARTER_STOCK),
        (main_cat, "Chrysanthemum", 75.0, STARTER_STOCK),
        (main_cat, "Mini Tangled Stargazer", 95.0, STARTER_STOCK),
        (main_cat, "Medium Tangled Stargazer", 120.0, STARTER_STOCK),
        (main_cat, "Hibiscus", 125.0, STARTER_STOCK),
        (main_cat, "Peonies Ver 1.", 150.0, STARTER_STOCK),
        (main_cat, "Peonies Ver 2.", 165.0, STARTER_STOCK),
        (main_cat, "Small Stargazer", 95.0, STARTER_STOCK),
        (main_cat, "Medium Stargazer", 175.0, STARTER_STOCK),
        (main_cat, "Big Stargazer", 190.0, STARTER_STOCK),
        (main_cat, "Stargazer Buds", 60.0, STARTER_STOCK),
        (main_cat, "Mini Tulip Bundle", 85.0, STARTER_STOCK),
        # Fillers
        (filler_cat, "Mini Daisy", 15.0, STARTER_STOCK),
        (filler_cat, "Baby's Breath", 15.0, STARTER_STOCK),
        (filler_cat, "Medium Leaf", 12.0, STARTER_STOCK),
        (filler_cat, "Small Leaf", 12.0, STARTER_STOCK),
        (filler_cat, "Eucalyptus", 12.0, STARTER_STOCK),
        (filler_cat, "Sprout", 12.0, STARTER_STOCK),
        (filler_cat, "Lavender", 20.0, STARTER_STOCK),
        # Ribbon
        (ribbon_cat, "Fishtail Ribbon", 15.0, STARTER_STOCK),
        (ribbon_cat, "Plain Ribbon", 10.0, STARTER_STOCK),
    ]

    for cat_id, name, price, qty in items:
        cur.execute(
            """
            INSERT OR IGNORE INTO products (category_id, name, price, quantity, discount)
            VALUES (?, ?, ?, ?, 0.0)
            """,
            (cat_id, name, price, qty),
        )

    grand_bouquets = [
        (
            "Beatriz's Thumbelina",
            700,
            [
                ("Medium Sunflower", 1),
                ("Chrysanthemum", 1),
                ("Gerbera", 2),
                ("Tulips", 1),
                ("Rose Ver 1.", 1),
                ("Poppy", 1),
                ("Medium Leaf", 1),
                ("Sprout", 2),
                ("Baby's Breath", 2),
                ("Mini Daisy", 3),
            ],
        ),
        (
            "Hiyasmin in Bloom",
            850.0,
            [
                ("Peonies Ver 2.", 1),
                ("Lily / Tiger Lily", 1),
                ("Tulips", 2),
                ("Chrysanthemum", 1),
                ("Bloomed Rose", 2),
                ("Lavender", 3),
                ("Mini Daisy", 5),
                ("Medium Leaf", 1),
            ],
        ),
        (
            "Jasmine's Daydream",
            350.0,
            [
                ("Medium Sunflower", 1),
                ("Rose Ver 2.", 1),
                ("Medium Leaf", 1),
                ("Mini Daisy", 6),
            ],
        ),
        (
            "Jessamin's Embrace",
            650.0,
            [
                ("Carnation", 5),
                ("Medium Leaf", 3),
                ("Eucalyptus", 3),
            ],
        ),
        (
            "Carlita's Charm",
            375.0,
            [
                ("Tulips", 4),
                ("Mini Sunflower", 1),
                ("Lavender", 2),
                ("Mini Daisy", 3),
            ],
        ),
        (
            "Jennie's Serenade",
            375.0,
            [
                ("Mini Daisy", 25),
            ],
        ),
        (
            "Alivia's Golden Hour",
            450.0,
            [
                ("Medium Sunflower", 1),
                ("Rose Ver 2.", 3),
                ("Baby's Breath", 4),
            ],
        ),
        (
            "Eleanor's Elegance",
            300,
            [
                ("Big Stargazer", 1),
                ("Sprout", 1),
            ],
        ),
        (
            "Cynthia's Grace",
            200,
            [
                ("Tulips", 1),
                ("Medium Leaf", 1),
                ("Mini Daisy", 3),
                ("Mini Tulip Bundle", 1),
            ],
        ),
        (
            "Edelia's Tangled Romance",
            250,
            [
                ("Mini Tangled Stargazer", 1),
                ("Mini Daisy", 6),
                ("Medium Leaf", 2),
            ],
        ),
    ]

    for b_name, fixed_price, parts in grand_bouquets:
        if fixed_price is not None:
            b_price = fixed_price
        else:
            total = 0.0
            for part_name, qty in parts:
                row = cur.execute("SELECT price FROM products WHERE name = ?", (part_name,)).fetchone()
                if row:
                    total += row["price"] * qty
            b_price = round(total, 2)

        cur.execute(
            """
            INSERT OR IGNORE INTO premade_bouquets (series, name, price, discount)
            VALUES ('The Grand Series', ?, ?, 0.0)
            """,
            (b_name, b_price),
        )
        b_row = cur.execute("SELECT id FROM premade_bouquets WHERE name = ?", (b_name,)).fetchone()
        if not b_row:
            continue
        b_id = b_row["id"]

        has_parts = cur.execute(
            "SELECT COUNT(*) AS cnt FROM bouquet_contents WHERE bouquet_id = ?", (b_id,)
        ).fetchone()["cnt"]
        if has_parts == 0:
            for part_name, qty in parts:
                pid = product_id_by_name(conn, part_name)
                if pid:
                    cur.execute(
                        "INSERT INTO bouquet_contents (bouquet_id, product_id, qty) VALUES (?, ?, ?)",
                        (b_id, pid, qty),
                    )

    cur.execute(
        """
        INSERT OR IGNORE INTO premade_bouquets (series, name, price, discount)
        VALUES ('The Mini Series', 'Risse Petite Bouquet', 0.0, 0.0)
        """
    )


def price_after_discount(price, discount_pct):
    disc = float(discount_pct or 0.0)
    return round(float(price) * (1.0 - disc / 100.0), 2)


def get_int(prompt, min_val=None, max_val=None):
    while True:
        raw = input(prompt).strip()
        try:
            num = int(raw)
            if min_val is not None and num < min_val:
                print(f"Enter a number of at least {min_val}.")
                continue
            if max_val is not None and num > max_val:
                print(f"Enter a number of at most {max_val}.")
                continue
            return num
        except ValueError:
            print("Enter a whole number.")


def get_float(prompt, min_val=0.0, max_val=None):
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
            if val < min_val:
                print(f"Enter a value of at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Enter a value of at most {max_val}.")
                continue
            return val
        except ValueError:
            print("Enter a valid number.")


def max_grand_available(conn, bouquet_id):
    rows = conn.execute(
        """
        SELECT bc.qty, p.quantity
        FROM bouquet_contents bc
        JOIN products p ON bc.product_id = p.id
        WHERE bc.bouquet_id = ?
        """,
        (bouquet_id,),
    ).fetchall()
    if not rows:
        return 0
    return min(r["quantity"] // r["qty"] for r in rows if r["qty"] > 0)


# ---------- AUTH & START ----------


def register_user():
    print("\n--- Register Customer ---")
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    if username.lower() == "admin":
        print("Username 'admin' cannot be registered.")
        return

    password = input("Password: ").strip()
    if not password:
        print("Password cannot be empty.")
        return

    with closing(connect()) as conn:
        try:
            with conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'customer')",
                    (username, password),
                )
            print(f"Account created for '{username}'.")
        except sqlite3.IntegrityError:
            print("That username is already taken.")


def login():
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    with closing(connect()) as conn:
        user = conn.execute(
            "SELECT username, role FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()

    if not user:
        print("Invalid username or password.")
        return

    if user["role"] == "admin":
        admin_menu()
    else:
        customer_menu(user["username"])


def main():
    init_db()
    while True:
        print("\n====================================================")
        print("Florisse - A bouquet shop made from fuzzy wire")
        print("====================================================")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")


# ---------- CUSTOMER MENU ----------


def customer_menu(username):
    while True:
        print(f"\n--- Customer Menu ({username}) ---")
        print("1. Buy")
        print("2. View Cart")
        print("3. Check Out")
        print("4. Logout")
        choice = input("Choose: ").strip()

        if choice == "1":
            buy_menu(username)
        elif choice == "2":
            view_cart(username)
        elif choice == "3":
            checkout(username)
        elif choice == "4":
            break
        else:
            print("Invalid option.")


def buy_menu(username):
    print("\n--- Buy ---")
    print("1. Choose from available products")
    print("2. Customized")
    choice = input("Choose: ").strip()

    if choice == "1":
        premade_menu(username)
    elif choice == "2":
        customized_bouquet(username)
    else:
        print("Invalid option.")


def premade_menu(username):
    print("\n--- Pre-made Bouquets ---")
    print("1. The Mini Series")
    print("2. The Grand Series")
    choice = input("Choose series: ").strip()

    if choice == "1":
        risse_petite(username)
    elif choice == "2":
        grand_series(username)
    else:
        print("Invalid series.")


def risse_petite(username):
    print("\n--- Risse Petite Bouquet ---")
    print("Choose 1 main flower under P80 and 4 fillers.")

    with closing(connect()) as conn:
        mains = conn.execute(
            """
            SELECT * FROM products
            WHERE category_id = (SELECT id FROM categories WHERE name = 'Main Flowers')
              AND price < 80.0
              AND quantity >= 1
            ORDER BY name
            """
        ).fetchall()

        fillers = conn.execute(
            """
            SELECT * FROM products
            WHERE category_id = (SELECT id FROM categories WHERE name = 'Fillers')
              AND quantity >= 1
            ORDER BY name
            """
        ).fetchall()

        petite = conn.execute(
            "SELECT * FROM premade_bouquets WHERE name = 'Risse Petite Bouquet'"
        ).fetchone()

    if not mains or not fillers:
        print("Not enough materials in stock for Risse Petite Bouquet.")
        return

    print("\nMain Flowers (under P80):")
    for idx, m in enumerate(mains, 1):
        price = price_after_discount(m["price"], m["discount"])
        print(f"  {idx}. {m['name']} - P{price:.2f} (Stock: {m['quantity']})")
    m_pick = get_int("Choose 1 main flower: ", 1, len(mains))
    chosen_main = mains[m_pick - 1]

    print("\nFillers (pick 4):")
    for idx, f in enumerate(fillers, 1):
        price = price_after_discount(f["price"], f["discount"])
        print(f"  {idx}. {f['name']} - P{price:.2f} (Stock: {f['quantity']})")

    needed = {chosen_main["id"]: 1}
    picked_fillers = []
    for n in range(1, 5):
        f_pick = get_int(f"Filler #{n}: ", 1, len(fillers))
        f_item = fillers[f_pick - 1]
        next_qty = needed.get(f_item["id"], 0) + 1
        if next_qty > f_item["quantity"]:
            print(f"Only {f_item['quantity']} left for '{f_item['name']}'.")
            return
        needed[f_item["id"]] = next_qty
        picked_fillers.append(f_item)

    max_bouquets = min(
        chosen_main["quantity"] // needed[chosen_main["id"]],
        *(
            next(f["quantity"] for f in fillers if f["id"] == pid) // cnt
            for pid, cnt in needed.items()
            if pid != chosen_main["id"]
        ),
    )

    qty = get_int(f"Quantity (max {max_bouquets}): ", 1, max_bouquets)

    unit_price = round(
        (price_after_discount(petite["price"], petite["discount"]) if petite else 0.0)
        + price_after_discount(chosen_main["price"], chosen_main["discount"])
        + sum(price_after_discount(f["price"], f["discount"]) for f in picked_fillers),
        2,
    )

    filler_names = ", ".join(f["name"] for f in picked_fillers)
    notes = f"Main: {chosen_main['name']} | Fillers: {filler_names}"
    materials_spec = ";".join(f"{pid}:{cnt}" for pid, cnt in needed.items())

    with closing(connect()) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO cart
                    (username, label, bouquet_id, product_id, qty, unit_price, custom_notes, materials_spec)
                VALUES (?, ?, ?, NULL, ?, ?, ?, ?)
                """,
                (
                    username,
                    f"Risse Petite Bouquet ({chosen_main['name']})",
                    petite["id"] if petite else None,
                    qty,
                    unit_price,
                    notes,
                    materials_spec,
                ),
            )

    print(f"Added {qty}x Risse Petite Bouquet to cart (P{unit_price:.2f} each).")


def grand_series(username):
    with closing(connect()) as conn:
        bouquets = conn.execute(
            """
            SELECT * FROM premade_bouquets
            WHERE series = 'The Grand Series'
            ORDER BY id
            """
        ).fetchall()

        available = []
        print("\n--- The Grand Series ---")
        for b in bouquets:
            can_make = max_grand_available(conn, b["id"])
            if can_make <= 0:
                continue
            parts = conn.execute(
                """
                SELECT bc.qty, p.name
                FROM bouquet_contents bc
                JOIN products p ON bc.product_id = p.id
                WHERE bc.bouquet_id = ?
                ORDER BY bc.id
                """,
                (b["id"],),
            ).fetchall()
            inc_str = ", ".join(f"{r['qty']} {r['name']}" for r in parts)
            price = price_after_discount(b["price"], b["discount"])
            available.append((b, can_make))
            print(f"{len(available)}. {b['name']} - P{price:.2f} (Available: {can_make})")
            print(f"   Includes: {inc_str}")

    if not available:
        print("No Grand Series bouquets available based on current inventory.")
        return

    pick = get_int("Select bouquet (0 to cancel): ", 0, len(available))
    if pick == 0:
        return

    chosen, max_qty = available[pick - 1]
    qty = get_int(f"Quantity (up to {max_qty}): ", 1, max_qty)
    unit_price = price_after_discount(chosen["price"], chosen["discount"])

    with closing(connect()) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO cart
                    (username, label, bouquet_id, product_id, qty, unit_price, custom_notes, materials_spec)
                VALUES (?, ?, ?, NULL, ?, ?, NULL, NULL)
                """,
                (username, chosen["name"], chosen["id"], qty, unit_price),
            )

    print(f"Added {qty}x {chosen['name']} to cart.")


def customized_bouquet(username):
    print("\n--- Customized Bouquet ---")
    sizes = ["Small", "Medium", "Large", "Grand"]
    size_fees = {"Small": 50.0, "Medium": 80.0, "Large": 120.0, "Grand": 180.0}

    print("Bouquet Size:")
    for idx, s in enumerate(sizes, 1):
        print(f"  {idx}. {s} (+P{size_fees[s]:.2f})")
    s_pick = get_int("Choose bouquet size: ", 1, len(sizes))
    size = sizes[s_pick - 1]

    with closing(connect()) as conn:
        mains = conn.execute(
            """
            SELECT * FROM products
            WHERE category_id = (SELECT id FROM categories WHERE name = 'Main Flowers')
              AND quantity > 0
            ORDER BY name
            """
        ).fetchall()
        fillers = conn.execute(
            """
            SELECT * FROM products
            WHERE category_id = (SELECT id FROM categories WHERE name = 'Fillers')
              AND quantity > 0
            ORDER BY name
            """
        ).fetchall()
        ribbons = conn.execute(
            """
            SELECT * FROM products
            WHERE category_id = (SELECT id FROM categories WHERE name = 'Ribbon')
              AND quantity > 0
            ORDER BY name
            """
        ).fetchall()

    if not mains or not fillers or not ribbons:
        print("Some materials are out of stock.")
        return

    print("\nMain Flowers:")
    for idx, m in enumerate(mains, 1):
        price = price_after_discount(m["price"], m["discount"])
        print(f"  {idx}. {m['name']} - P{price:.2f} (Stock: {m['quantity']})")
    m_pick = get_int("Select main flower: ", 1, len(mains))
    main_flower = mains[m_pick - 1]
    main_qty = get_int(f"Quantity of {main_flower['name']} (max {main_flower['quantity']}): ", 1, main_flower["quantity"])
    main_color = input("Main flower color: ").strip() or "Default"

    print("\nFillers:")
    for idx, f in enumerate(fillers, 1):
        price = price_after_discount(f["price"], f["discount"])
        print(f"  {idx}. {f['name']} - P{price:.2f} (Stock: {f['quantity']})")
    f_pick = get_int("Select filler: ", 1, len(fillers))
    filler = fillers[f_pick - 1]
    filler_qty = get_int(f"Quantity of {filler['name']} (max {filler['quantity']}): ", 0, filler["quantity"])
    filler_color = input("Filler color: ").strip() or "Default"

    wrap_color = input("Wrapping color: ").strip() or "Default"

    print("\nRibbon Type:")
    for idx, r in enumerate(ribbons, 1):
        price = price_after_discount(r["price"], r["discount"])
        print(f"  {idx}. {r['name']} - P{price:.2f} (Stock: {r['quantity']})")
    r_pick = get_int("Select ribbon type: ", 1, len(ribbons))
    ribbon = ribbons[r_pick - 1]
    ribbon_color = input("Ribbon color: ").strip() or "Default"

    notes = input("Notes or image link for inspiration: ").strip() or "None"

    total_price = round(
        size_fees[size]
        + price_after_discount(main_flower["price"], main_flower["discount"]) * main_qty
        + price_after_discount(filler["price"], filler["discount"]) * filler_qty
        + price_after_discount(ribbon["price"], ribbon["discount"]),
        2,
    )

    details = (
        f"Size: {size} | Main: {main_qty}x {main_flower['name']} ({main_color}) | "
        f"Filler: {filler_qty}x {filler['name']} ({filler_color}) | "
        f"Wrap: {wrap_color} | Ribbon: {ribbon['name']} ({ribbon_color}) | "
        f"Notes/Link: {notes}"
    )

    parts = [(main_flower["id"], main_qty), (ribbon["id"], 1)]
    if filler_qty > 0:
        parts.append((filler["id"], filler_qty))
    materials_spec = ";".join(f"{pid}:{amt}" for pid, amt in parts)

    with closing(connect()) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO cart
                    (username, label, bouquet_id, product_id, qty, unit_price, custom_notes, materials_spec)
                VALUES (?, ?, NULL, NULL, 1, ?, ?, ?)
                """,
                (username, f"Customized {size} Bouquet", total_price, details, materials_spec),
            )

    print(f"Customized bouquet added to cart (Total: P{total_price:.2f}).")


def view_cart(username):
    print(f"\n--- {username}'s Cart ---")
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM cart WHERE username = ? ORDER BY id",
            (username,),
        ).fetchall()

    if not rows:
        print("Your cart is empty.")
        return

    grand_total = 0.0
    for idx, row in enumerate(rows, 1):
        subtotal = round(row["qty"] * row["unit_price"], 2)
        grand_total = round(grand_total + subtotal, 2)
        print(f"{idx}. {row['label']} x{row['qty']} @ P{row['unit_price']:.2f} = P{subtotal:.2f}")
        if row["custom_notes"]:
            print(f"   {row['custom_notes']}")

    print(f"------------------------------------\nTotal Price: P{grand_total:.2f}")


def checkout(username):
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM cart WHERE username = ? ORDER BY id",
            (username,),
        ).fetchall()

        if not rows:
            print("Your cart is empty.")
            return

        deductions = {}
        total_paid = 0.0

        for row in rows:
            total_paid = round(total_paid + row["qty"] * row["unit_price"], 2)

            if row["bouquet_id"] is not None and not row["materials_spec"]:
                mats = conn.execute(
                    "SELECT product_id, qty FROM bouquet_contents WHERE bouquet_id = ?",
                    (row["bouquet_id"],),
                ).fetchall()
                for m in mats:
                    deductions[m["product_id"]] = deductions.get(m["product_id"], 0) + m["qty"] * row["qty"]

            elif row["materials_spec"]:
                for entry in row["materials_spec"].split(";"):
                    if not entry:
                        continue
                    pid_str, per_unit_str = entry.split(":")
                    pid = int(pid_str)
                    per_unit = int(per_unit_str)
                    deductions[pid] = deductions.get(pid, 0) + per_unit * row["qty"]

            elif row["product_id"] is not None:
                deductions[row["product_id"]] = deductions.get(row["product_id"], 0) + row["qty"]

        for pid, needed in deductions.items():
            prod = conn.execute("SELECT name, quantity FROM products WHERE id = ?", (pid,)).fetchone()
            avail = prod["quantity"] if prod else 0
            if avail < needed:
                name = prod["name"] if prod else f"Item #{pid}"
                print(f"Insufficient stock for '{name}' (need {needed}, have {avail}). Checkout canceled.")
                return

        with conn:
            for pid, needed in deductions.items():
                conn.execute(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (needed, pid),
                )
            conn.execute("DELETE FROM cart WHERE username = ?", (username,))

    print(f"\nChecked out! Total Price: P{total_paid:.2f}. Stock updated.")


# ---------- ADMIN MENU ----------


def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. View products")
        print("2. Manage stocks")
        print("3. Logout")
        choice = input("Choose: ").strip()

        if choice == "1":
            view_products()
        elif choice == "2":
            manage_stocks()
        elif choice == "3":
            break
        else:
            print("Invalid option.")


def view_products():
    print("\n--- Products ---")
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT p.id, c.name AS category, p.name, p.quantity, p.price, p.discount
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE c.name IN ('Main Flowers', 'Fillers', 'Ribbon')
            ORDER BY c.id, p.id
            """
        ).fetchall()

    if not rows:
        print("No products found.")
        return

    for r in rows:
        final_price = price_after_discount(r["price"], r["discount"])
        disc_text = f"{r['discount']:.0f}% (P{final_price:.2f})" if r["discount"] > 0 else "0%"
        print(
            f"[{r['id']}] Category: {r['category']} | Product: {r['name']} "
            f"| Quantity: {r['quantity']} | Price: P{r['price']:.2f} | Discount: {disc_text}"
        )


def manage_stocks():
    while True:
        print("\n--- Manage Stocks ---")
        print("1. Add a product")
        print("2. Remove a product")
        print("3. Edit a product")
        print("4. Back")
        choice = input("Choose: ").strip()

        if choice == "1":
            add_product()
        elif choice == "2":
            remove_product()
        elif choice == "3":
            edit_product()
        elif choice == "4":
            break
        else:
            print("Invalid option.")


def add_product():
    with closing(connect()) as conn:
        cats = conn.execute("SELECT id, name FROM categories ORDER BY id").fetchall()

    if not cats:
        print("No categories available.")
        return

    print("\nSelect Category:")
    for idx, c in enumerate(cats, 1):
        print(f"  {idx}. {c['name']}")
    c_pick = get_int("Category: ", 1, len(cats))
    cat = cats[c_pick - 1]

    name = input("Product Name: ").strip()
    if not name:
        print("Product name cannot be empty.")
        return

    qty = get_int("Quantity: ", 0)
    price = get_float("Price: ", 0.0)

    with closing(connect()) as conn:
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO products (category_id, name, price, quantity, discount)
                    VALUES (?, ?, ?, ?, 0.0)
                    """,
                    (cat["id"], name, price, qty),
                )
            print(f"Added '{name}' under '{cat['name']}'.")
        except sqlite3.IntegrityError:
            print("A product with that name already exists.")


def remove_product():
    view_products()
    prod_id = get_int("\nProduct ID to remove (0 to cancel): ", 0)
    if prod_id == 0:
        return

    with closing(connect()) as conn:
        with conn:
            cur = conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        print("Product removed." if cur.rowcount else "Product ID not found.")


def edit_product():
    view_products()
    prod_id = get_int("\nProduct ID to edit (0 to cancel): ", 0)
    if prod_id == 0:
        return

    with closing(connect()) as conn:
        prod = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
        if not prod:
            print("Product not found.")
            return

        print(
            f"\nEditing '{prod['name']}' "
            f"(Quantity: {prod['quantity']}, Price: P{prod['price']:.2f}, Discount: {prod['discount']:.0f}%)"
        )
        print("1. Add stock to existing product")
        print("2. Edit price")
        print("3. Set discount (%)")
        choice = input("Choose: ").strip()

        with conn:
            if choice == "1":
                add_qty = get_int("Quantity to add: ", 1)
                conn.execute(
                    "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                    (add_qty, prod_id),
                )
                print(f"Added {add_qty} to '{prod['name']}'.")
            elif choice == "2":
                new_price = get_float("New Price: ", 0.0)
                conn.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, prod_id))
                print("Price updated.")
            elif choice == "3":
                new_disc = get_float("Discount % (0-100): ", 0.0, 100.0)
                conn.execute("UPDATE products SET discount = ? WHERE id = ?", (new_disc, prod_id))
                print("Discount updated.")
            else:
                print("Invalid option.")


if __name__ == "__main__":
    main()