# Debian Single Sign-On client

Prototype client script for services behind the
[Debian Single Sign-On](https://wiki.debian.org/DebianSingleSignOn).

At the moment this is just a proof of concept to see if it can be done, and it
looks promising.

The script tries to get Single Sign-On keys out of 
[the browser certificate storage](http://blog.avirtualhome.com/adding-ssl-certificates-to-google-chrome-linux-ubuntu/),
and connect to <https://nm.debian.org/api/whoami> using them.

The script needs to write the secret keys to a temporary directory, so make
sure `$TMPDIR` points to volatile or encrypted storage.

It requires `$DEBEMAIL` to be set to the Single Sign-On username.

Dependencies: `libnss3-tools`, `openssl`, `python3-requests`.


## TODO

This could become a lot of things:

 * a script to send signed statements to applications on `nm.debian.org`.
 * a script that negotiates new keys with sso.debian.org and pushes them into
   the browser, without the need for `<keygen>`.
 * a script that removes expired keys from the browser.
 * a command line front end to all sort of Debian services that require
   authentication.
