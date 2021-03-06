#!/usr/bin/python

# Released to the public domain
#
# Exit codes:
#   0: Successful execution
#   1: Wrong salt length
#   2: Invalid cost parameter
#   3: Wrong salt format
#   4: Unknown crypt format
#   5: bcrypt password longer than 72 bytes
#
# Requires passlib >= 1.7

import os
import click
import string
import random
from passlib.exc import PasswordTruncateError
from passlib import hash as ph

@click.command()
@click.option("--apache", is_flag=1, help="Apache md5crypt password variant.")
@click.option("--bcrypt", is_flag=1, help="OpenBSD bcrypt hash, truncated to 72 bytes.")
@click.option("--bcrypt_sha256", is_flag=1, help="bcrypt prehashed with SHA-256 and base64, unlimited length.")
@click.option("--cisco", is_flag=1, help="Cisco md5crypt variant, salt limited to 4 characters.")
@click.option("--des", is_flag=1, help="Unix 3DES crypt, truncated to 8 characters.")
@click.option("--md5", is_flag=1, help="FreeBSD md5crypt hash, limited to 1,000 rounds.")
@click.option("--mysql", is_flag=1, help="MySQL 4.1 hashing algorithm.")
@click.option("--sha256", is_flag=1, help="GNU libc sha256crypt hash.")
@click.option("--sha512", is_flag=1, help="GNU libc sha512crypt hash.")
@click.option("--cost", type=int, help="Password hashing cost, if applicable.")
@click.option("--salt", type=str, help="Password salt in the character set [A-Za-z0-9./], if applicable.")
@click.option("--check", type=str, help="Check a password hash. Must be wrapped in single quotes.")
@click.password_option(help="User-supplied password in cleartext.")
def main(check, password, apache, mysql, des, md5, cisco, bcrypt, bcrypt_sha256, sha256, sha512, cost, salt):
    sr = random.SystemRandom()
    chars = string.ascii_letters + string.digits + "/."

    if apache and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(8))
        if len(salt) > 8:
            salt = salt[:8]
        print(ph.apr_md5_crypt.using(salt=salt).hash(password))

    if mysql and not check:
        print(ph.mysql41.hash(password))

    if des and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(2))
        if len(salt) != 2:
            print("Salt must be exactly 2 characters long.")
            os.sys.exit(1)
        print(ph.des_crypt.using(salt=salt).hash(password))

    if md5 and not check:
        if not salt:
            if cisco:
                salt = "".join(sr.choice(chars) for i in range(4))
            else:
                salt = "".join(sr.choice(chars) for i in range(8))
        if len(salt) > 8:
            if cisco:
                salt = salt[:4]
            else:
                salt = salt[:8]
        print(ph.md5_crypt.using(salt=salt).hash(password))

    if bcrypt and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(22))
            salt = salt[:-1] + sr.choice(".Oeu")
        elif salt[-1:] not in [".", "O", "e", "u"]:
            print("Salt must end in '.', 'O', 'e', or 'u'.")
            print("See https://bitbucket.org/ecollins/passlib/issues/25")
            os.sys.exit(3)
        if len(salt) != 22:
            print("Salt must be exactly 22 characters long.")
            os.sys.exit(1)
        if not cost:
            cost = 5
        if cost < 4 or cost > 31:
            print("Cost must be between 4 and 31.")
            os.sys.exit(2)
        try:
            print(ph.bcrypt.using(rounds=cost, salt=salt, truncate_error=1).hash(password))
        except PasswordTruncateError:
            print("bcrypt truncates passwords to 72 bytes. Truncate your password, or use --bcrypt_sha256 instead.")
            os.sys.exit(5)

    if bcrypt_sha256 and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(22))
            salt = salt[:-1] + sr.choice(".Oeu")
        elif salt[-1:] not in [".", "O", "e", "u"]:
            print("Salt must end in '.', 'O', 'e', or 'u'.")
            print("See https://bitbucket.org/ecollins/passlib/issues/25")
            os.sys.exit(3)
        if len(salt) != 22:
            print("Salt must be exactly 22 characters long.")
            os.sys.exit(1)
        if not cost:
            cost = 5
        if cost < 4 or cost > 31:
            print("Cost must be between 4 and 31.")
            os.sys.exit(2)
        print(ph.bcrypt_sha256.using(rounds=cost, salt=salt).hash(password))

    if sha256 and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(16))
        if len(salt) > 16:
            salt = salt[:16]
        if not cost:
            cost = 5000
        if cost < 1000 or cost > 999999999:
            print("Cost must be between 1000 and 999999999.")
            os.sys.exit(2)
        print(ph.sha256_crypt.using(rounds=cost, salt=salt).hash(password))

    if sha512 and not check:
        if not salt:
            salt = "".join(sr.choice(chars) for i in range(16))
        if len(salt) > 16:
            salt = salt[:16]
        if not cost:
            cost = 5000
        if cost < 1000 or cost > 999999999:
            print("Cost must be between 1000 and 999999999.")
            os.sys.exit(2)
        print(ph.sha512_crypt.using(rounds=cost, salt=salt).hash(password))

    if check:
        ret = 0
        try:
            magic = check.split("$")[1]
            if magic == "apr1":
                ret = ph.apr_md5_crypt.verify(password, check)
            elif magic == "1":
                ret = ph.md5_crypt.verify(password, check)
            elif magic == "2b":
                ret = ph.bcrypt.verify(password, check)
            elif magic == "bcrypt-sha256":
                ret = ph.bcrypt_sha256.verify(password, check)
            elif magic == "5":
                ret = ph.sha256_crypt.verify(password, check)
            elif magic == "6":
                ret = ph.sha512_crypt.verify(password, check)
            else:
                print("Unknown hash format.")
                os.sys.exit(4)
        except IndexError:
            if len(check) == 8:
                ret = ph.des_crypt.verify(password, check)
            elif len(check) == 41 and check[0] == "*":
                ret = ph.mysql41.verify(password, check)
            else:
                print("Unknown hash format.")
                os.sys.exit(4)
        else:
            if ret:
                print("\033[92m\033[1mPassword matches crypt.\033[0m")
            else:
                print("\033[91m\033[1mPassword does not match crypt.\033[0m")
        
if __name__ == '__main__':
    main()
