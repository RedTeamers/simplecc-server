import os, pathlib, datetime
from typing import Optional
from uvicorn import run as uvicorn_run

# ---- Paramètres via env (avec valeurs par défaut) ----
HOST         = os.getenv("C2_HOST", "0.0.0.0")
PORT         = int(os.getenv("C2_PORT", "8000"))
CERT_DIR     = pathlib.Path(os.getenv("C2_CERT_DIR", "."))
CERT_FILE    = CERT_DIR / os.getenv("C2_CERT_FILE", "cert.pem")
KEY_FILE     = CERT_DIR / os.getenv("C2_KEY_FILE", "key.pem")
CERT_CN      = os.getenv("C2_CERT_CN", "localhost")            # CN du cert
CERT_DAYS    = int(os.getenv("C2_CERT_DAYS", "365"))
APP_IMPORT   = os.getenv("C2_APP", "simplec2.main:app")        # import FastAPI

# ---- Génération du certificat auto-signé via cryptography ----
def generate_self_signed_cert(
    cert_path: pathlib.Path,
    key_path: pathlib.Path,
    common_name: str = "localhost",
    valid_days: int = 365,
):
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    import ipaddress

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"DZ"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Algeria"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Algiers"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"RedTeamers"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"Tested"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(minutes=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=valid_days))
    )

    # SAN: CN, localhost, 127.0.0.1
    alt_names = [
        x509.DNSName(common_name),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]
    try:
        # Si le CN est une IP v4/v6 valide, l’ajouter
        alt_names.append(x509.IPAddress(ipaddress.ip_address(common_name)))
    except ValueError:
        pass

    builder = builder.add_extension(
        x509.SubjectAlternativeName(alt_names), critical=False
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    )

    cert = builder.sign(private_key=key, algorithm=hashes.SHA256(), backend=default_backend())

    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    with open(key_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def ensure_certs():
    need_gen = not (CERT_FILE.exists() and KEY_FILE.exists())
    if not need_gen:
        # Optionnel: vérifier l’expiration et régénérer si proche
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            with open(CERT_FILE, "rb") as cf:
                cert = x509.load_pem_x509_certificate(cf.read(), default_backend())
            if (cert.not_valid_after - datetime.datetime.utcnow()) < datetime.timedelta(days=7):
                need_gen = True
        except Exception:
            need_gen = True

    if need_gen:
        print(f"[*] Génération d’un certificat auto-signé → {CERT_FILE} / {KEY_FILE}")
        generate_self_signed_cert(CERT_FILE, KEY_FILE, common_name=CERT_CN, valid_days=CERT_DAYS)

def main():
    ensure_certs()
    # Lancer Uvicorn en HTTPS
    uvicorn_run(
        APP_IMPORT,
        host=HOST,
        port=PORT,
        ssl_keyfile=str(KEY_FILE),
        ssl_certfile=str(CERT_FILE),
    )

if __name__ == "__main__":
    main()
