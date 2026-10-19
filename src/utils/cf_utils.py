import os

from cloudflare import Cloudflare
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def prompt_cloudflare_api_key():
    print(
        """You Cloudflare API key will be used to obtain TLS certs by.
 The API key must have the permission to edit `DNS` and `SSL and Certificates` zones."""
    )
    cf_api_key = input("\nEnter your Cloudflare API key: ")
    while not cf_api_key:
        print("\nInvalid API key!")
        cf_api_key = input("Enter your Cloudflare API key: ")

    return cf_api_key


def generate_csr_and_key(domain):
    print("Generating private key and CSR locally...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])).sign(key, hashes.SHA256())

    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    csr_pem = csr.public_bytes(serialization.Encoding.PEM)

    return key_pem, csr_pem

def request_cloudflare_origin_certs(api_token: str, main_domain: str, cert_dir: str):
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    if os.path.exists(os.path.join(cert_dir, f"{main_domain}.key")):
        print(f"Cert files for the given domains already exist in {cert_dir}")
        return

    client = Cloudflare(api_token=api_token)
    key_pem, csr_pem = generate_csr_and_key(main_domain)

    try:
        print(f"Requesting Origin CA certificate for {main_domain} and *.{main_domain} via SDK...")
        response = client.origin_ca_certificates.create(
            csr=csr_pem.decode("utf-8"),
            hostnames=[main_domain, f"*.{main_domain}"],
            request_type="origin-rsa",
            requested_validity=5475
        )

        if response:
            certificate_pem = response.certificate
            if certificate_pem:
                with open(os.path.join(cert_dir, f"{main_domain}.key"), "wb") as f:
                    f.write(key_pem)

                with open(os.path.join(cert_dir, f"{main_domain}.crt"), "w") as f:
                    f.write(certificate_pem)

                print(f"Success! Files saved in {cert_dir}")
                print(f"Validity: {response.requested_validity} days")

    except Exception as e:
        print(f"An error occurred when trying to fetch origin ca certs: {e}")
