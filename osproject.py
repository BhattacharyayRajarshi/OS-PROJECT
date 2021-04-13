import boto3
import tqdm
import mysql.connector
import sys
from cryptography.fernet import Fernet
from PIL import Image
import os

global s3
s3 = boto3.client('s3')


def percent(part, total):
    return 100 * float(part) / float(total)


def WriteDataToFilePrompt(data, newline):
    filename = input("Filename: ")
    file = open(filename, 'w')
    location = 0
    while location < len(data):
        if newline == True:
            file.writelines(data[location] + "\n")
        else:
            file.writelines(data[location])
        location += 1
    file.close()


class Fibonacci():
    def __init__(self):
        pass

    def Single(self, n):  # Returns a single Fibonacci number
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return self.Single(n - 1) + self.Single(n - 2)

    def SetOfFibonacci(self, start, end):  # Returns a set of Fibonacci numbers from start to end.
        returnData = []
        location = start
        while location < end:
            returnData.append(str(self.Single(location)))
            location += 1
        return returnData


fib = Fibonacci()
encryptionList = fib.SetOfFibonacci(1, 11)


class FibonacciEncryption():
    def __init__(self):
        pass

    def Encrypt(self, textToEncrypt):
        location = 0
        encryptedText = []
        offsetIndex = 0
        while location < len(textToEncrypt):
            if offsetIndex < 9:  # Let's make sure we keep it in-bounds.
                offsetIndex += 1
            elif offsetIndex == 9:
                offsetIndex = 0
            charValue = ord(textToEncrypt[location])
            offsetValue = encryptionList[offsetIndex]
            finalValue = int(charValue) + int(offsetValue)
            encryptedText.append(str(finalValue))
            location += 1
        location = 0
        finalString = ""
        while location < len(encryptedText):
            finalString += str(encryptedText[location])
            if location != len(encryptedText):
                finalString += " "
            location += 1
        return finalString

    def Decrypt(self, textToDecrypt):  # Anything other than a string input will break this
        location = 0
        decryptedText = ""
        offsetIndex = 0
        nextwhitespace = 0
        while location < len(textToDecrypt):
            if offsetIndex < 9:
                offsetIndex += 1
            elif offsetIndex == 9:
                offsetIndex = 0
            nextwhitespace = textToDecrypt.find(" ", location)
            if nextwhitespace != -1:
                tempTextToDecrypt = textToDecrypt[location:nextwhitespace]
                offsetValue = encryptionList[offsetIndex]
                finalText = chr(int(tempTextToDecrypt) - int(offsetValue))
                decryptedText += finalText
            if nextwhitespace < location:
                return decryptedText
            else:
                location = nextwhitespace + 1


fibe = FibonacciEncryption()


class AESEncryption:

    def __init__(self, filename):  # Constructor
        self.filename = filename

    def encryption(self):  # Allows us to perform file operation

        try:
            original_information = open(self.filename, 'rb')

        except (IOError, FileNotFoundError):
            print('File with name {} is not found.'.format(self.filename))
            sys.exit(0)

        try:

            encrypted_file_name = 'cipher_' + self.filename
            encrypted_file_object = open(encrypted_file_name, 'wb')

            content = original_information.read()
            content = bytearray(content)

            key1 = 192
            print('Encryption Process is in progress...!')
            for i, val in tqdm(enumerate(content)):
                content[i] = val ^ key1

            encrypted_file_object.write(content)

        except Exception:
            print('Something went wrong with {}'.format(self.filename))
        finally:
            encrypted_file_object.close()
            original_information.close()


class AESDecryption:

    def __init__(self, filename):
        self.filename = filename

    def decryption(self):  # produces the original result

        try:
            encrypted_file_object = open(self.filename, 'rb')

        except (FileNotFoundError, IOError):
            print('File with name {} is not found'.format(self.filename))
            sys.exit(0)

        try:

            decrypted_file = input('Enter the filename for the Decryption file with extension:')  # Decrypted file as output

            decrypted_file_object = open(decrypted_file, 'wb')

            cipher_text = encrypted_file_object.read()

            key1 = 192

            cipher_text = bytearray(cipher_text)

            print('Decryption Process is in progress...!')

            for i, val in tqdm(enumerate(cipher_text)):
                cipher_text[i] = val ^ key1

            decrypted_file_object.write(cipher_text)

        except Exception:
            print('Some problem with Ciphertext unable to handle.')

        finally:
            encrypted_file_object.close()
            decrypted_file_object.close()


def genData(data):
    # list of binary codes
    # of given data
    newd = []

    for i in data:
        newd.append(format(ord(i), '08b'))
    return newd


# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] +
               imdata.__next__()[:3] +
               imdata.__next__()[:3]]

        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1

            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if (pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
                # pix[j] -= 1

        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if (pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):

        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1


def merge_file(f, ff, fff):
    data = data2 = data3 =""

    # Reading data from file1
    with open(f) as fp:
        data = fp.read()

        # Reading data from file2
    with open(ff) as fp:
        data2 = fp.read()

    with open(fff) as fp:
        data3 = fp.read()
        # Merging 3 files
    # To add the data of file2
    # from next line
    #data += "\n"
    data += data2
    #data += "\n"
    data += data3

    with open('final_project.txt', 'w') as fp:
        fp.write(data)


def decrypt_new(fileq, filea):
    with open(fileq) as f:
        with open(filea, "w") as f1:
            for line in f:
                f1.write(line)


# Encode data into image
def encode():
    global new_img_name
    img = input("Enter image name(with extension) : ")
    image = Image.open(img, 'r')

    data = input("Enter data to be encoded : ")
    if (len(data) == 0):
        raise ValueError('Data is empty')

    newimg = image.copy()
    encode_enc(newimg, data)

    new_img_name = input("Enter the name of new image(with extension) : ")
    newimg.save(new_img_name)


# Decode the data in the image
def decode():
    imgg = input("Enter image name(with extension) : ")
    image = Image.open(imgg, 'r')

    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                  imgdata.__next__()[:3] +
                  imgdata.__next__()[:3]]

        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            return data


def write_key():
    global key
    key = Fernet.generate_key()


# def load_key():


def encrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(str(filename.split(".")[0])+'FE.'+str(filename.split(".")[1]), "wb") as file1:
            file1.write(encrypted_data)
    print("")


def decrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
        # decrypt data
        decrypted_data = f.decrypt(encrypted_data)
        # write the original file
        with open(str("decrypt_"+filename.split(".")[0])+'.'+str(filename.split(".")[1]), "wb") as file7:
            file7.write(decrypted_data)


print("HELLO!! WELCOME TO 3 STEP SECURITY FILE STORAGE IN AWS")
print("1. LOGIN")
print("2. SIGN UP")
a = int(input("ENTER YOUR CHOICE: "))
os.system("cls")
if a == 2:
    name = input("ENTER YOUR NAME: ")
    passwd = input("ENTER YOUR PASSWORD: ")
    write_key()
    st = "INSERT INTO  file_sec(name,password,key_code) VALUES(%s,%s,%s);"
    record = (name, passwd, key)
    my_db = mysql.connector.connect(host="localhost", user="rajarshi", passwd="root", database="rajarshi",
                                    autocommit=True)
    cur = my_db.cursor()
    cur.execute(st, record)
    print("YOUR ACCOUNT IS ALL SET!! PLEASE COPY THE KEY BELOW")
    print(key)
    print("PLEASE PRESS 3 TO PROCEED FURTHER...")
    b = int(input())
    os.system("cls")
    if b == 3:
        print("WELCOME TO FINAL STEP OF SIGN UP PROCEDURE. KINDLY SELECT AN IMAGE AND PASTE UR KEY AS HIDDEN MESSAGE AND ENCODE IT.")
        encode()
        ss = "update file_sec set steg_file_name = %s where name = %s"
        rec = (new_img_name, name)
        cur.execute(ss, rec)
        print("YOU ARE ALL SET!!KINDLY EXIT AND RERUN FOR LOGIN BY PRESSING 4")
        q = int(input())
        if q == 4:
            os.system("exit")
    else :
        print("INVALID CHOICE")
else:
    uname = input("ENTER USERNAME : ")
    pas = input("ENTER PASSWORD : ")
    os.system("cls")
    print("IF U WANT TO SELECT A FILE FROM UR PC AND UPLOAD IT TO AWS USING 3SFS(PRESS1)")
    print("IF U WANT TO DOWNLOAD ENCRYPTED FILES FROM AWS AND DECRYPT THEM FOR VIEWING(PRESS 2)")
    fg = int(input())
    os.system("cls")
    if fg == 1:
        my_db = mysql.connector.connect(host="localhost", user="rajarshi", passwd="root", database="rajarshi",
                                        autocommit=True)
        cur = my_db.cursor()
        cur.execute("select key_code from file_sec where name = '"+uname+"';")
        for i in cur:
            res = i[0]
        print("WELCOME TO THE MAIN PAGE")
        print("PLEASE GIVE THE FILE NAME(WITH EXTENSION) WHICH YOU WANT TO STORE IN CLOUD: ")
        fname = input()
        nf1 = open(str(fname.split(".")[0])+'1.'+str(fname.split(".")[1]), "w")
        nf2 = open(str(fname.split(".")[0])+'2.'+str(fname.split(".")[1]), "w")
        nf3 = open(str(fname.split(".")[0])+'3.'+str(fname.split(".")[1]), "w")
        with open(fname, "r", encoding="utf8") as file:
            data = file.readlines()
            si = len(data)
            for i in range(si//3):
                nf1.write(data[i])
            for j in range(si//3,2*si//3):
                nf2.write(data[j])
            for k in range(2*si//3,si):
                nf3.write(data[k])
        encrypt(str(fname.split(".")[0])+'1.'+str(fname.split(".")[1]), res)
        print("FILE 1st SUBPART HAS BEEN SUCCESSFULLY ENCRYPTED USING AES ENCRYPTION")
        encrypt(str(fname.split(".")[0])+'2.'+str(fname.split(".")[1]), res)
        print("FILE 2nd SUBPART HAS BEEN SUCCESSFULLY ENCRYPTED USING FERNET ENCRYPTION")
        encrypt(str(fname.split(".")[0])+'3.'+str(fname.split(".")[1]), res)
        print("FILE 3rd SUBPART HAS BEEN SUCCESSFULLY ENCRYPTED USING CAESAR & FIBONACCI ENCRYPTION")
        s3.upload_file(str(fname.split(".")[0])+'1FE.'+str(fname.split(".")[1]), 'os-project',str(fname.split(".")[0])+'1FE.'+str(fname.split(".")[1]))
        print("FILE 1 UPLOADED SUCCESSFULLY")
        s3.upload_file(str(fname.split(".")[0]) + '2FE.' + str(fname.split(".")[1]), 'os-project',
                       str(fname.split(".")[0]) + '2FE.' + str(fname.split(".")[1]))
        print("FILE 2 UPLOADED SUCCESSFULLY")
        s3.upload_file(str(fname.split(".")[0]) + '3FE.' + str(fname.split(".")[1]), 'os-project',
                       str(fname.split(".")[0]) + '3FE.' + str(fname.split(".")[1]))
        print("FILE 3 UPLOADED SUCCESSFULLY")
        print("FILE HAS BEEN UPLOADED SECURELY USING 3SES. PLEASE PRESS 5 TO EXIT THE SYSTEM")
        h = int(input())
        if h == 5:
            os.system("exit")
        else:
            print("INVALID COMMAND")
    else:
        bname = input("ENTER THE NAME OF THE FILE THAT YOU ENCRYPTED : ")
        s3.download_file('os-project',str(bname.split(".")[0])+'1FE.'+str(bname.split(".")[1]),
                         str(bname.split(".")[0])+'1DE.'+str(bname.split(".")[1]))
        print("FILE 1 HAS BEEN SUCCESSFULLY DOWNLOADED FROM AWS")
        s3.download_file('os-project',str(bname.split(".")[0])+'2FE.'+str(bname.split(".")[1]),
                         str(bname.split(".")[0]) + '2DE.' + str(bname.split(".")[1]))
        print("FILE 2 HAS BEEN SUCCESSFULLY DOWNLOADED FROM AWS")
        s3.download_file('os-project',str(bname.split(".")[0]) + '3FE.' + str(bname.split(".")[1]),
                         str(bname.split(".")[0]) + '3DE.' + str(bname.split(".")[1]))
        print("FILE 3 HAS BEEN SUCCESSFULLY DOWNLOADED FROM AWS")
        my_db = mysql.connector.connect(host="localhost", user="rajarshi", passwd="root", database="rajarshi",
                                        autocommit=True)
        cur = my_db.cursor()
        cur.execute("select key_code from file_sec where name = '" + uname + "';")
        for i in cur:
            res1 = i[0]
        decrypt_new(str(bname.split(".")[0])+'1.'+str(bname.split(".")[1]),
                    str("decrypt_"+bname.split(".")[0])+'1.'+str(bname.split(".")[1]))
        print("SUCCESSFULLY DECRYPTED FILE No 1!!!")
        decrypt_new(str(bname.split(".")[0])+'2.'+str(bname.split(".")[1]),
                    str("decrypt_"+bname.split(".")[0])+'2.'+str(bname.split(".")[1]))
        print("SUCCESSFULLY DECRYPTED FILE No 2!!!")
        decrypt_new(str(bname.split(".")[0])+'3.'+str(bname.split(".")[1]),
                    str("decrypt_"+bname.split(".")[0])+'3.'+str(bname.split(".")[1]))
        print("SUCCESSFULLY DECRYPTED DILE No 3!!!")
        merge_file(str("decrypt_"+bname.split(".")[0])+'1.'+str(bname.split(".")[1]),
                   str("decrypt_"+bname.split(".")[0])+'2.'+str(bname.split(".")[1]),
                   str("decrypt_"+bname.split(".")[0])+'3.'+str(bname.split(".")[1]))
        print("FILE HAS BEEN SAVED IN UR SPECIFIED DIRECTORY.")

