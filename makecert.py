import os
import subprocess
import argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import requests

def generate_ssl_cert(domain, output_dir):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Save private key to a file
    private_key_path = os.path.join(output_dir, f"{domain}.key")
    with open(private_key_path, "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    csr = subprocess.check_output(
        ["openssl", "req", "-new", "-key", private_key_path, "-subj", f"/CN={domain}"],
        universal_newlines=True
    )

    # Save CSR to a file
    csr_path = os.path.join(output_dir, f"{domain}.csr")
    with open(csr_path, "w") as csr_file:
        csr_file.write(csr)

    acme_tiny_url = "https://raw.githubusercontent.com/diafygi/acme-tiny/master/acme_tiny.py"
    acme_tiny_path = os.path.join(output_dir, "acme_tiny.py")
    response = requests.get(acme_tiny_url)
    with open(acme_tiny_path, "w") as acme_tiny_file:
        acme_tiny_file.write(response.text)

    # Run the acme-tiny script to get the signed certificate
    signed_cert_path = os.path.join(output_dir, f"{domain}-signed.crt")
    subprocess.run([
        "python", acme_tiny_path,
        "--account-key", "account.key",
        "--csr", csr_path,
        "--acme-dir", "/var/www/html/.well-known/acme-challenge",
        "--output", signed_cert_path
    ])

    intermediate_cert_url = "https://letsencrypt.org/certs/lets-encrypt-r3.pem"
    intermediate_cert_path = os.path.join(output_dir, "lets-encrypt-r3.pem")
    response = requests.get(intermediate_cert_url)
    with open(intermediate_cert_path, "w") as intermediate_cert_file:
        intermediate_cert_file.write(response.text)
    fullchain_path = os.path.join(output_dir, f"{domain}-fullchain.crt")
    subprocess.run([
        "cat", signed_cert_path, intermediate_cert_path, ">", fullchain_path
    ])

    print(f"SSL certificate generated successfully for {domain}")

def main():
    parser = argparse.ArgumentParser(description="Generate SSL certificate for a domain")
    parser.add_argument("-d", "--domain", required=True, help="Domain name for the SSL certificate")
    args = parser.parse_args()

    output_dir = args.domain
    os.makedirs(output_dir, exist_ok=True)

    generate_ssl_cert(args.domain, output_dir)

if __name__ == "__main__":
    main()
