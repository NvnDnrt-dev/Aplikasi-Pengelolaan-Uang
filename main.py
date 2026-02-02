import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data.json")

saldo = 0
transactions = []

def load_data():
    global saldo, transactions
    try:
        with DATA_FILE.open() as f:
            data = json.load(f)
            saldo = float(data.get("saldo", 0))
            transactions = data.get("transactions", [])
    except FileNotFoundError:
        saldo = 0
        transactions = []
    except (json.JSONDecodeError, ValueError):
        print("File data rusak — data direset.")
        saldo = 0
        transactions = []

def save_data():
    try:
        DATA_FILE.write_text(json.dumps({"saldo": round(saldo, 2), "transactions": transactions}, indent=2))
    except OSError:
        print("Gagal menyimpan data.")

def tambah_pemasukan():
    global saldo, transactions
    try:
        jumlah = float(input("Masukkan jumlah pemasukan: "))
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return
    saldo += jumlah
    transactions.append({"type": "pemasukan", "amount": jumlah, "time": datetime.now().isoformat()})
    save_data()
    print(f"Pemasukan sebesar {jumlah:.2f} berhasil ditambahkan. Saldo sekarang: {saldo:.2f}")

def tambah_pengeluaran():
    global saldo, transactions
    try:
        jumlah = float(input("Masukkan jumlah pengeluaran: "))
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return
    if jumlah > saldo:
        print("Saldo tidak cukup.")
        return
    saldo -= jumlah
    transactions.append({"type": "pengeluaran", "amount": jumlah, "time": datetime.now().isoformat()})
    save_data()
    print(f"Pengeluaran sebesar {jumlah:.2f} berhasil dikurangkan. Saldo sekarang: {saldo:.2f}")

def lihat_saldo():
    """Menampilkan saldo saat ini dengan format rapi.

    Contoh output: "Saldo saat ini: Rp 1,234.56"
    """
    # Tampilkan dengan pemisah ribuan dan dua angka desimal
    print(f"Saldo saat ini: Rp {saldo:,.2f}")

def lihat_laporan():
    """Menampilkan rekap pemasukan dan pengeluaran serta daftar transaksi."""
    if not transactions:
        print("Belum ada transaksi.")
        return
    total_in = sum(t["amount"] for t in transactions if t.get("type") == "pemasukan")
    total_out = sum(t["amount"] for t in transactions if t.get("type") == "pengeluaran")
    print("=== Laporan Rekap ===")
    print(f"Total pemasukan : Rp {total_in:,.2f}")
    print(f"Total pengeluaran: Rp {total_out:,.2f}")
    print(f"Saldo bersih     : Rp {(total_in - total_out):,.2f}")
    print("\nDaftar transaksi:")
    for t in transactions:
        waktu = t.get("time", "-")
        tipe = t.get("type", "-")
        amt = t.get("amount", 0)
        print(f"- {waktu} | {tipe} | Rp {amt:,.2f}")

def menu():
    print("=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Lihat laporan")
    print("5. Keluar")

if __name__ == "__main__":
    load_data()
    while True:
        menu()
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_pemasukan()
        elif pilihan == "2":
            tambah_pengeluaran()
        elif pilihan == "3":
            lihat_saldo()
        elif pilihan == "4":
            lihat_laporan()
        elif pilihan == "5":
            save_data()
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid")