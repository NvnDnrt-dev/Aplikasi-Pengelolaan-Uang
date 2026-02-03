import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data.json")

saldo = 0.0
transactions = []


def load_data():
    """Muat data sederhana dari `data.json`.

    Jika file rusak atau tidak ada, program tetap berjalan dengan data kosong.
    """
    global saldo, transactions
    if not DATA_FILE.exists():
        return
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        print("File data rusak — data direset.")
        return

    try:
        saldo = float(data.get("saldo", 0))
    except Exception:
        saldo = 0.0

    raw = data.get("transactions", [])
    sane = []
    if isinstance(raw, list):
        for t in raw:
            if not isinstance(t, dict):
                continue
            ttype = t.get("type")
            if ttype not in ("pemasukan", "pengeluaran"):
                continue
            try:
                amt = round(float(t.get("amount", 0)), 2)
            except Exception:
                continue
            sane.append({"type": ttype, "amount": amt, "time": t.get("time") or datetime.now().isoformat()})
    transactions = sane


def save_data():
    try:
        DATA_FILE.write_text(json.dumps({"saldo": round(saldo, 2), "transactions": transactions}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        print("Gagal menyimpan data.")


def tambah_transaksi(tipe):
    """Satu fungsi untuk menambah pemasukan atau pengeluaran."""
    global saldo, transactions
    raw = input(f"Masukkan jumlah {tipe}: ").strip()
    if raw == "":
        print("Dibatalkan.")
        return
    try:
        jumlah = round(float(raw), 2)
    except Exception:
        print("Input tidak valid. Masukkan angka.")
        return
    if jumlah <= 0:
        print("Jumlah harus lebih dari 0.")
        return
    if tipe == "pengeluaran" and jumlah > saldo:
        print("⚠️  Saldo tidak cukup.")
        return
    saldo += jumlah if tipe == "pemasukan" else -jumlah
    transactions.append({"type": tipe, "amount": jumlah, "time": datetime.now().isoformat()})
    save_data()
    print(f"✅ {tipe.capitalize()} Rp {jumlah:,.2f} diproses. Saldo sekarang: Rp {saldo:,.2f}")


def lihat_saldo():
    print(f"Saldo saat ini: Rp {saldo:,.2f}")


def lihat_laporan():
    if not transactions:
        print("Belum ada transaksi.")
        return
    total_in = sum(t["amount"] for t in transactions if t["type"] == "pemasukan")
    total_out = sum(t["amount"] for t in transactions if t["type"] == "pengeluaran")
    print("=== Laporan Rekap ===")
    print(f"Total pemasukan : Rp {total_in:,.2f}")
    print(f"Total pengeluaran: Rp {total_out:,.2f}")
    print(f"Saldo saat ini   : Rp {saldo:,.2f}")
    print("")
    print("Daftar transaksi:")
    for i, t in enumerate(transactions, 1):
        print(f"{i:>3}. {t.get('time','-')} | {t['type']:<10} | Rp {t['amount']:,.2f}")


def menu():
    print("\n=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Lihat laporan")
    print("5. Keluar (atau Ctrl+C)")


def main():
    load_data()
    print("Selamat datang! Ketik nomor menu untuk memilih, atau Ctrl+C untuk keluar.")
    try:
        while True:
            menu()
            pilihan = input("Pilih menu: ").strip()
            if pilihan == "1":
                tambah_transaksi("pemasukan")
            elif pilihan == "2":
                tambah_transaksi("pengeluaran")
            elif pilihan == "3":
                lihat_saldo()
            elif pilihan == "4":
                lihat_laporan()
            elif pilihan in ("5", "q", "quit", "exit"):
                save_data()
                print("Terima kasih!")
                break
            else:
                print("Pilihan tidak valid")
    except (KeyboardInterrupt, EOFError):
        print("\nKeluar... menyimpan data.")
        save_data()


if __name__ == "__main__":
    main()
