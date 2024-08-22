from web3 import Web3
import json
import logging
from colorama import init, Fore, Style
import pyfiglet
import os
import time  # Import time module untuk jeda

def print_banner(text, font="slant"):
    try:
        ascii_banner = pyfiglet.figlet_format(text, font=font)
        print(ascii_banner)
    except Exception as e:
        print(Fore.RED + f"Error displaying banner: {e}")

print_banner("Murup Neverdie", "slant")

init()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

rpc_url = config['rpc_url']
web3 = Web3(Web3.HTTPProvider(rpc_url))

if not web3.is_connected():
    logger.error(Fore.RED + "Gagal Konek ke RPC URL")
    exit()

gas_price = web3.to_wei(config['gas_price_gwei'], 'gwei')
gas_limit = config['gas_limit']
jumlah_eth = config['min_eth']

def muat_private_keys(filename='private_keys.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            private_keys = json.load(file)
    else:
        logger.error(Fore.RED + f"File {filename} tidak ditemukan.")
        exit()
    return private_keys

private_keys = muat_private_keys()

def kirim_eth(ke_alamat, jumlah_eth, private_key):
    try:
        account = web3.eth.account.from_key(private_key)
        my_address = account.address
        nonce = web3.eth.get_transaction_count(my_address)

        transaksi = {
            'nonce': nonce,
            'to': ke_alamat,
            'value': web3.to_wei(jumlah_eth, 'ether'),
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': config['chain_id']
        }

        transaksi_ditandatangani = web3.eth.account.sign_transaction(transaksi, private_key)
        tx_hash = web3.eth.send_raw_transaction(transaksi_ditandatangani.rawTransaction)
        return tx_hash.hex()
    except Exception as e:
        logger.error(Fore.RED + f"Gagal kirim {config['coin_symbol']} ke {ke_alamat}: {str(e)}")
        raise  # Re-raise the exception to be handled by the caller

def muat_recept(filename='recept.txt'):
    with open(filename, 'r') as file:
        lines = file.read().strip().split('\n')
    return lines

def print_separator(color):
    print(color + "-"*60)

def main():
    print(Style.BRIGHT + Fore.CYAN + "Pilih opsi:")
    print("1. " + Fore.GREEN + "Kirim ke 1 wallet")
    print("2. " + Fore.MAGENTA + "Kirim ke 100 wallet")
    pilihan = input(Fore.WHITE + "Masukkan pilihan (1/2): ")

    if pilihan == '1':
        wallet_addresses = muat_recept()
        if wallet_addresses:
            alamat_penerima = wallet_addresses[0]
            print_separator(Fore.BLUE)
            for private_key in private_keys:
                try:
                    hash_transaksi = kirim_eth(alamat_penerima, jumlah_eth, private_key)
                    tx_url = f"https://testnet-explorer.elosys.io/tx/{hash_transaksi}"
                    logger.info(Fore.YELLOW + f"Berhasil kirim {jumlah_eth} {config['coin_symbol']} ke {alamat_penerima}. {tx_url}")
                    print(Fore.YELLOW + f"Berhasil kirim {jumlah_eth} {config['coin_symbol']} ke {alamat_penerima}. {tx_url}")
                    print_separator(Fore.BLUE)
                    break
                except Exception as e:
                    print(Fore.RED + f"Gagal kirim {config['coin_symbol']} ke {alamat_penerima}.")
                    logger.error(Fore.RED + f"Gagal kirim {config['coin_symbol']} ke {alamat_penerima}: {str(e)}")
                    print_separator(Fore.BLUE)
    elif pilihan == '2':
        wallet_addresses = muat_recept()
        for alamat_penerima in wallet_addresses[:100]:
            print_separator(Fore.BLUE)
            for private_key in private_keys:
                try:
                    hash_transaksi = kirim_eth(alamat_penerima, jumlah_eth, private_key)
                    tx_url = f"https://testnet-explorer.elosys.io/tx/{hash_transaksi}"
                    logger.info(Fore.YELLOW + f"Berhasil kirim {jumlah_eth} {config['coin_symbol']} ke {alamat_penerima}. {tx_url}")
                    print(Fore.YELLOW + f"Berhasil kirim {jumlah_eth} {config['coin_symbol']} ke {alamat_penerima}. {tx_url}")
                    print_separator(Fore.BLUE)
                    time.sleep(5)  # Jeda 5 detik antar transaksi
                    break
                except Exception as e:
                    print(Fore.RED + f"Gagal kirim {config['coin_symbol']} ke {alamat_penerima}.")
                    logger.error(Fore.RED + f"Gagal kirim {config['coin_symbol']} ke {alamat_penerima}: {str(e)}")
                    print_separator(Fore.BLUE)
    else:
        logger.warning(Fore.RED + "Pilihan tidak valid. Silakan jalankan ulang program dan pilih opsi yang benar.")
        print(Fore.RED + "Pilihan tidak valid. Silakan jalankan ulang program dan pilih opsi yang benar.")

if __name__ == "__main__":
    main()
