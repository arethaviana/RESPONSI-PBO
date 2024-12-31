import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

# Koneksi ke database MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ganti dengan password MySQL Anda
        database="toko"
    )

# Fungsi untuk menambah produk
def add_product():
    nama_produk = entry_nama_produk.get()
    harga_produk = entry_harga_produk.get()
    
    if nama_produk and harga_produk:
        try:
            harga_produk = float(harga_produk)
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produk (nama_produk, harga_produk) VALUES (%s, %s)", (nama_produk, harga_produk))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Produk berhasil ditambahkan")
            entry_nama_produk.delete(0, tk.END)
            entry_harga_produk.delete(0, tk.END)
            load_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "Semua field harus diisi")

def load_products():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id_produk, nama_produk FROM produk")
        products = cursor.fetchall()
        conn.close()

        # Update nilai ComboBox
        combo_produk['values'] = [f"{prod[1]} (ID: {prod[0]})" for prod in products]

        if products:
            combo_produk.set('')  # Kosongkan ComboBox untuk mencegah salah parsing
        else:
            combo_produk.set('')
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan saat memuat produk: {str(e)}")

def load_product_details(event):
    selected_product = combo_produk.get()
    if selected_product:
        try:
            # Parsing id_produk dengan aman
            product_id = int(selected_product.split(" (ID: ")[1][:-1])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT nama_produk, harga_produk FROM produk WHERE id_produk = %s", (product_id,))
            product = cursor.fetchone()
            conn.close()
            
            if product:
                entry_nama_produk.delete(0, tk.END)
                entry_nama_produk.insert(0, product[0])
                entry_harga_produk.delete(0, tk.END)
                entry_harga_produk.insert(0, product[1])
        except ValueError:
            messagebox.showerror("Error", "ID produk tidak valid")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

def delete_product():
    selected_product = combo_produk.get()
    if selected_product:
        try:
            # Parsing id_produk dengan aman
            product_id = int(selected_product.split(" (ID: ")[1][:-1])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transaksi WHERE id_produk = %s", (product_id,))
            cursor.execute("DELETE FROM produk WHERE id_produk = %s", (product_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", "Produk berhasil dihapus")

            # Refresh ComboBox dan tabel transaksi
            load_products()
            load_transactions()
        except ValueError:
            messagebox.showerror("Error", "ID produk tidak valid")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Pilih produk yang ingin dihapus")

# Fungsi untuk mengupdate produk
def update_product():
    selected_product = combo_produk.get()
    if not selected_product:
        messagebox.showwarning("Warning", "Pilih produk yang ingin diupdate")
        return

    try:
        # Ambil id_produk dari teks pilihan
        product_id = int(selected_product.split(" (ID: ")[1][:-1])

        # Ambil data dari form
        nama_produk = entry_nama_produk.get().strip()
        harga_produk = entry_harga_produk.get().strip()

        if not nama_produk or not harga_produk:
            messagebox.showwarning("Warning", "Semua field harus diisi")
            return

        # Validasi harga produk
        try:
            harga_produk = float(harga_produk)
        except ValueError:
            messagebox.showerror("Error", "Harga Produk harus berupa angka")
            return

        # Update produk di database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE produk SET nama_produk = %s, harga_produk = %s WHERE id_produk = %s",
            (nama_produk, harga_produk, product_id),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Produk berhasil diupdate")

        # Bersihkan form dan refresh data
        entry_nama_produk.delete(0, tk.END)
        entry_harga_produk.delete(0, tk.END)
        combo_produk.set('')
        load_products()

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")


# Fungsi untuk mencatat transaksi
def record_transaction():
    selected_product = combo_produk.get()
    jumlah_produk = entry_jumlah_produk.get()
    
    if selected_product and jumlah_produk:
        try:
            jumlah_produk = int(jumlah_produk)
            product_id = int(selected_product.split(" (ID: ")[1][:-1])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT harga_produk FROM produk WHERE id_produk = %s", (product_id,))
            harga_produk = cursor.fetchone()[0]
            total_harga = harga_produk * jumlah_produk
            
            cursor.execute("INSERT INTO transaksi (id_produk, jumlah_produk, total_harga, tanggal_transaksi) VALUES (%s, %s, %s, %s)",
                           (product_id, jumlah_produk, total_harga, datetime.now().date()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Transaksi berhasil dicatat")
            entry_jumlah_produk.delete(0, tk.END)
            load_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "Sem ua field harus diisi")

# Fungsi untuk memuat transaksi
def load_transactions():
    for row in tree.get_children():
        tree.delete(row)
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nama_produk, t.jumlah_produk, t.total_harga, t.tanggal_transaksi
        FROM transaksi t
        JOIN produk p ON t.id_produk = p.id_produk
    """)
    transactions = cursor.fetchall()
    conn.close()
    
    for transaction in transactions:
        tree.insert("", tk.END, values=transaction)

# GUI
root = tk.Tk()
root.title("Aplikasi Toko")

# Form Produk
frame_produk = tk.Frame(root)
frame_produk.pack(pady=10)

tk.Label(frame_produk, text="Nama Produk:").grid(row=0, column=0)
entry_nama_produk = tk.Entry(frame_produk)
entry_nama_produk.grid(row=0, column=1)

tk.Label(frame_produk, text="Harga Produk:").grid(row=1, column=0)
entry_harga_produk = tk.Entry(frame_produk)
entry_harga_produk.grid(row=1, column=1)

btn_tambah_produk = tk.Button(frame_produk, text="Tambah Produk", command=add_product)
btn_tambah_produk.grid(row=2, columnspan=2)

btn_update_produk = tk.Button(frame_produk, text="Update Produk", command=update_product)
btn_update_produk.grid(row=3, columnspan=2)

btn_hapus_produk = tk.Button(frame_produk, text="Hapus Produk", command=delete_product)
btn_hapus_produk.grid(row=4, columnspan=2)

# Form Transaksi
# Form Transaksi
frame_transaksi = tk.Frame(root)
frame_transaksi.pack(pady=10)

tk.Label(frame_transaksi, text="Pilih Produk:").grid(row=0, column=0)
combo_produk = ttk.Combobox(frame_transaksi)
combo_produk.grid(row=0, column=1)
combo_produk.bind("<<ComboboxSelected>>", load_product_details)

tk.Label(frame_transaksi, text="Jumlah Produk:").grid(row=1, column=0)
entry_jumlah_produk = tk.Entry(frame_transaksi)
entry_jumlah_produk.grid(row=1, column=1)

btn_catat_transaksi = tk.Button(frame_transaksi, text="Catat Transaksi", command=record_transaction)
btn_catat_transaksi.grid(row=2, columnspan=2)


# Tabel Transaksi
frame_tabel = tk.Frame(root)
frame_tabel.pack(pady=10)

tree = ttk.Treeview(frame_tabel, columns=("Nama Produk", "Jumlah", "Total Harga", "Tanggal"), show='headings')
tree.heading("Nama Produk", text="Nama Produk")
tree.heading("Jumlah", text="Jumlah")
tree.heading("Total Harga", text="Total Harga")
tree.heading("Tanggal", text="Tanggal")

tree.pack()

load_products()
load_transactions()

root.mainloop()