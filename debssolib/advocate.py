# coding: utf-8
from debssolib.cli import Command
from debssolib.certs import Certs
import requests
import sys
import email
import email.utils
import re
import sys

class Advocate(Command):
    """
    Read a signed statement and post it as an advocacy message
    """
    def argument_parser(self):
        parser = super().argument_parser()
        parser.add_argument("file", nargs="?", help="File with the signed statement (default: stdin)")
        parser.add_argument("-p", "--process", type=int, default=None, help="Process number (default: autodetected from mail headers, if input is an email)")
        return parser

    def run(self):
        parser = self.argument_parser()
        args = parser.parse_args()
        if args.file:
            with open(args.file, "rb") as infd:
                data = infd.read()
        else:
            data = sys.stdin.buffer.read()

        if args.process is not None:
            self.submit(args.process, data)
            return

        if data.strip().startswith(b"-----BEGIN PGP SIGNED MESSAGE-----"):
            raise RuntimeError("Please use --process when sending clearsigned statements")

        # Infer process from email headers
        process = self.infer_process_from_email(data)
        if process is None:
            raise RuntimeError("Cannot find archive-nn@nm.debian.org address in headers: please use --process")
        self.submit(process, data)

    def infer_process_from_email(self, data):
        """
        Infer process number from email headers
        """
        mail = email.message_from_bytes(data)
        dests = []
        dests.extend(mail.get_all("To", failobj=()))
        dests.extend(mail.get_all("Cc", failobj=()))
        re_archive = re.compile(r"^archive-(\d+)@nm.debian.org$")
        for name, addr in email.utils.getaddresses(dests):
            mo = re_archive.match(addr)
            if mo: return int(mo.group(1))
        return None

    def submit(self, process, data):
        certs = Certs.from_browser()
        with certs.tempfiles() as files:
            cert_args = { "cert": (files.crt_pathname, files.key_pathname) }
            session = requests.session()
            url = "https://nm.debian.org/process/{}/advocate/statement/create".format(process)
            res = session.get(url, **cert_args)
            res.raise_for_status()
            res = session.post(url,
                            allow_redirects=False,
                            headers={
                                "Referer": url,
                                "X-CSRFToken": res.cookies["csrftoken"],
                            },
                            data={
                                "csrfmiddlewaretoken": res.cookies["csrftoken"],
                                "statement": data,
                            }, **cert_args)
            res.raise_for_status()
            if res.status_code == 200:
                from lxml.html import document_fromstring
                page = document_fromstring(res.content)
                for el in page.iter("ul"):
                    _class = el.attrib.get("class", None)
                    if _class is None: continue
                    if "errorlist" not in _class: continue
                    for li in el.iter("li"):
                        print(li.text, file=sys.stderr)
                    sys.exit(1)
