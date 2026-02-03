import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_FILE = Path("data.json")

saldo: float = 0.0
transactions: List[Dict[str, Any]] = []


def _safe_write_json(path: Path, data: dict) -> None:
    """Tulis file JSON secara atomik (tulis ke file sementara lalu pindahkan)."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        # Jika gagal, hapus file sementara jika ada
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def load_data() -> None:
    """Muat data dari `data.json` dan lakukan sanitasi sederhana.

    Jika file rusak, file akan direset (tetap aman untuk dijalankan).
    Transaksi yang tidak valid akan diabaikan dan jumlah yang valid akan dikonversi ke float.
    """
    global saldo, transactions
    if not DATA_FILE.exists():
        saldo = 0.0
        transactions = []
        return

    try:
        with DATA_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        print("File data rusak — data direset.")
        saldo = 0.0
        transactions = []
        return

    # Ambil saldo dengan aman
    try:
        saldo = float(data.get("saldo", 0.0))
    except (TypeError, ValueError):
        saldo = 0.0

    # Sanitasi transaksi
    raw_tx = data.get("transactions", [])
    sane: List[Dict[str, Any]] = []
    skipped = 0
    if isinstance(raw_tx, list):
        for t in raw_tx:
            if not isinstance(t, dict):
                skipped += 1
                continue
            ttype = t.get("type")
            if ttype not in ("pemasukan", "pengeluaran"):
                skipped += 1
                continue
            try:
                amount = float(t.get("amount", 0))
            except (TypeError, ValueError):
                skipped += 1
                continue
            time_str = t.get("time") or datetime.now().isoformat()
            # Pastikan number ter-round dua desimal
            sane.append({"type": ttype, "amount": round(amount, 2), "time": time_str})
    else:
        skipped = len(raw_tx) if raw_tx is not None else 0

    transactions = sane
    if skipped:
        print(f"Beberapa entri transaksi tidak valid diabaikan: {skipped}")


def save_data() -> None:
    """Simpan saldo dan transaksi ke `data.json` secara aman."""
    try:
        _safe_write_json(DATA_FILE, {"saldo": round(saldo, 2), "transactions": transactions})
    except Exception:
        print("Gagal menyimpan data.")


def _input_amount(prompt: str) -> Optional[float]:
    """Baca input angka dari user dan kembalikan sebagai float, atau None jika dibatalkan."""
    try:
        raw = input(prompt).strip()
        if raw == "":
            print("Dibatalkan.")
            return None
        val = float(raw)
        if val <= 0:
            print("Jumlah harus lebih dari 0.")
            return None
        return round(val, 2)
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return None


def tambah_pemasukan() -> None:
    global saldo, transactions
    jumlah = _input_amount("Masukkan jumlah pemasukan: ")
    if jumlah is None:
        return
    saldo += jumlah
    transactions.append({"type": "pemasukan", "amount": jumlah, "time": datetime.now().isoformat()})
    save_data()
    print(f"✅ Pemasukan Rp {jumlah:,.2f} ditambahkan. Saldo sekarang: Rp {saldo:,.2f}")


def tambah_pengeluaran() -> None:
    global saldo, transactions
    jumlah = _input_amount("Masukkan jumlah pengeluaran: ")
    if jumlah is None:
        return
    if jumlah > saldo:
        print("⚠️  Saldo tidak cukup.")
        return
    saldo -= jumlah
    transactions.append({"type": "pengeluaran", "amount": jumlah, "time": datetime.now().isoformat()})
    save_data()
    print(f"✅ Pengeluaran Rp {jumlah:,.2f} dikurangkan. Saldo sekarang: Rp {saldo:,.2f}")


def _format_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_str


def lihat_saldo() -> None:
    """Tampilkan saldo saat ini dengan format yang rapi."""
    print(f"Saldo saat ini: Rp {saldo:,.2f}")


def lihat_laporan() -> None:
    """Tampilkan rekap dan daftar transaksi dengan format lebih ramah pengguna."""
    if not transactions:
        print("Belum ada transaksi.")
        return
    total_in = sum(t["amount"] for t in transactions if t.get("type") == "pemasukan")
    total_out = sum(t["amount"] for t in transactions if t.get("type") == "pengeluaran")

    print("=== Laporan Rekap ===")
    print(f"Total pemasukan : Rp {total_in:,.2f}")
    print(f"Total pengeluaran: Rp {total_out:,.2f}")
    print(f"Saldo saat ini   : Rp {saldo:,.2f}")
    print(f"Saldo dari rekap : Rp {(total_in - total_out):,.2f}")
    print("")
    print("Daftar transaksi:")
    for i, t in enumerate(transactions, start=1):
        waktu = _format_time(t.get("time", "-"))
        tipe = t.get("type", "-")
        amt = t.get("amount", 0)
        print(f"{i:>3}. {waktu} | {tipe:<10} | Rp {amt:,.2f}")


def menu() -> None:
    print("\n=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Lihat laporan")
    print("5. Keluar (atau Ctrl+C)")


def main() -> None:
    load_data()
    print("Selamat datang! Ketik nomor menu untuk memilih, atau Ctrl+C untuk keluar.")
    try:
        while True:
            menu()
            pilihan = input("Pilih menu: ").strip()

            if pilihan == "1":
                tambah_pemasukan()
            elif pilihan == "2":
                tambah_pengeluaran()
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
