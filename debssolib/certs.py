# coding: utf-8
import os
import subprocess

class Browser:
    def __init__(self):
        self.dbname = "sql:" + os.path.expanduser("~/.pki/nssdb")

    def run_certutil(self, args, input=None):
        cmd = ["certutil", "-d", self.dbname]
        cmd.extend(args)
        output = subprocess.check_output(cmd, universal_newlines=True, input=input)
        return output

    def run_pk12util(self, args, input=None):
        cmd = ["pk12util", "-d", self.dbname]
        cmd.extend(args)
        output = subprocess.check_output(cmd, universal_newlines=False, input=input)
        return output

    def get_key_nicks(self):
        output = self.run_certutil(["-L"])
        payload = output.split("\n\n")[1]
        for line in payload.splitlines():
            nick, flags = line.rsplit(None, 1)
            yield nick, flags

    def get_sso_cert_nickname(self):
        debemail = os.environ.get("DEBEMAIL", None)
        if debemail is None: raise RuntimeError("$DEBEMAIL is not set")
        for nick, flags in self.get_key_nicks():
            if flags != "u,u,u": continue
            if not nick.startswith(debemail): continue
            if not "SSO" in nick: continue
            return nick

    def get_key_pkcs12(self, nick):
        """
        Read the certificate and key for the slot with the given nick and
        return them in a single pkcs12 blob.
        """
        return self.run_pk12util(["-n", nick, "-o", "/dev/stdout", "-W", ""])


def pkcs12_to_pem(pkcs12):
    """
    Return PEM-encoded certificate and key from their pkcs12 version
    """
    import OpenSSL.crypto
    from OpenSSL.crypto import FILETYPE_PEM
    p = OpenSSL.crypto.load_pkcs12(pkcs12, "")
    return (
        OpenSSL.crypto.dump_certificate(FILETYPE_PEM, p.get_certificate()),
        OpenSSL.crypto.dump_privatekey(FILETYPE_PEM, p.get_privatekey()),
    )
    #pem_cert = subprocess.check_output(["openssl", "pkcs12", "-nodes", "-passin", "pass:", "-clcerts", "-nokeys"],
    #                                    input=pkcs12, stderr=open("/dev/null", "wb"))
    #pem_key = subprocess.check_output(["openssl", "pkcs12", "-nodes", "-passin", "pass:", "-nocerts"],
    #                                    input=pkcs12, stderr=open("/dev/null", "wb"))
    #return pem_cert, pem_key


class Certs:
    def extract_from_browser(self):
        """
        Return PEM-encoded (certificate, key) extracted from libnss3 key
        storage used by common web browsers.
        """
        # Try to get SSO keys out of the browser and connect to nm.debian.org with
        # them.
        # Requires $DEBEMAIL to be set.
        # Requires libnss3-tools, python3-openssl
        # Tested with chromium.
        browser = Browser()
        nick = browser.get_sso_cert_nickname()
        pkcs12 = browser.get_key_pkcs12(nick)
        return pkcs12_to_pem(pkcs12)

