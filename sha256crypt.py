from hashlib import sha256
from random import SystemRandom

pw = "toomanysecrets"
rounds = 5000

r = SystemRandom()
pwlen = len(pw)
itoa64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
salt = "".join(r.choice(itoa64) for i in xrange(16))
quot, rem = divmod(rounds, 42)

# Ensure min and max limits for rounds
if rounds < 1000: rounds = 1000
if rounds > 999999999: rounds = 999999999

# Start digest "a"
da = sha256(pw + salt)

# Create digest "b"
db = sha256(pw + salt + pw).digest()

# Update digest "a" by repeating digest "b", providing "pwlen" bytes:
i = pwlen
while i > 0:
    da.update(db if i > 32 else db[:i])
    i -= 32

# Upate digest "a" by adding either a NULL or the first char from "pw"
i = pwlen
while i:
    da.update(db if i & 1 else pw)
    i >>= 1

da = da.digest()

# Create digest "p". For every char in "pw, add "pw" to digest "p"
dp = sha256(pw * len(pw)).digest()

# Produce byte sequence "p" of the same length as "pw"
i = pwlen
tmp = ""
while i > 0:
    tmp += dp if i > 32 else dp[:i]
    i -= 32
dp = tmp

# Create digest "s"
ds = sha256(salt * (16 + ord(da[0]))).digest()[:len(salt)]

p = dp
pp = dp+dp
ps = dp+ds
psp = dp+ds+dp
sp = ds+dp
spp = ds+dp+dp

permutations = [
    (p , psp), (spp, pp), (spp, psp), (pp, ps ), (spp, pp), (spp, psp),
    (pp, psp), (sp , pp), (spp, psp), (pp, psp), (spp, p ), (spp, psp),
    (pp, psp), (spp, pp), (sp , psp), (pp, psp), (spp, pp), (spp, ps ),
    (pp, psp), (spp, pp), (spp, psp)
]
# Optimize!
while quot:
    for i, j in permutations:
        da = sha256(j + sha256(da + i).digest()).digest()
    quot -= 1

if rem:
    half_rem = rem >> 1
    for i, j in permutations[:half_rem]:
        da = sha256(j + sha256(da + i).digest()).digest()
    if rem & 1:
        da = sha256(da + permutations[half_rem][0]).digest()

# convert 3 8-bit words to 4 6-bit words while mixing
final = ""
for x,y,z in ((0,10,20),(21,1,11),(12,22,2),(3,13,23),(24,4,14),
              (15,25,5),(6,16,26),(27,7,17),(18,28,8),(9,19,29)):
    v = ord(da[x]) << 16 | ord(da[y]) << 8 | ord(da[z])
    for i in range(4):
        final += itoa64[v & 63]
        v >>= 6
v = ord(da[31]) << 8 | ord(da[30])
for i in range(3):
    final += itoa64[v & 63]
    v >>= 6

# output the result
if rounds == 5000:
    result = "$5${0}${1}".format(salt, final)
else:
    result = "$5$rounds={0}${1}${2}".format(rounds, salt, final)
print result
