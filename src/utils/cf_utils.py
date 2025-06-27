

def prompt_cloudflare_api_key():
    print(
        """You Cloudflare API key will be used by Certbot to obtain TLS certs by
verifying DNS-01 challenges. The API key must have the permission to edit DNS Zones."""
    )
    cf_api_key = input("\nEnter your Cloudflare API key: ")
    while not cf_api_key:
        print("\nInvalid API key!")
        cf_api_key = input("Enter your Cloudflare API key: ")

    return cf_api_key

def insert_cloudflare_api_key(cf_secrets_file: str, api_key: str):
    """
    Inserts and overwrites the Cloudflare API key to enable Certbot obtain certs through DNS challenges

    :param cf_secrets_file: Path to the .ini file
    :param api_key: The string to write as the key
    """
    with open(cf_secrets_file, 'w') as file:
        file.write(f"dns_cloudflare_api_token = {api_key}\n")