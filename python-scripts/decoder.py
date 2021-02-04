import base64

def bits_converter(x):
    index = 0
    bits = ""
    while x is not 0:
        bits += str(x & 1)
        x = x >> 1
        index+=1
    return bits[::-1]

def reverse(x):
    x = (((x & 0xaaaaaaaa) >> 1) | ((x & 0x55555555) << 1))
    x = (((x & 0xcccccccc) >> 2) | ((x & 0x33333333) << 2))
    x = (((x & 0xf0f0f0f0) >> 4) | ((x & 0x0f0f0f0f) << 4))
    x = (((x & 0xff00ff00) >> 8) | ((x & 0x00ff00ff) << 8))
    return ((x >> 16) | (x << 16))

def mydecode(encoded):
    print(reverse(encoded[0].getBytes()))
    decodedBytes = base64.b64decode(encoded)
    latitute = decodedBytes[2] << 16
    latitute += decodedBytes[3] << 8
    latitute += decodedBytes[4]
    latitute /= 10000

    longitute = decodedBytes[5] << 16
    longitute += decodedBytes[6] << 8
    longitute += decodedBytes[7]
    longitute /= 10000

    altitute = decodedBytes[8] << 16
    altitute += decodedBytes[9] << 8
    altitute += decodedBytes[10]
    altitute /= 100

    return latitute, longitute, altitute

if __name__ == "__main__":
    string = "QNo+ASaAvQAB4misriSdVAsIPLuJlEg+"
    decodedstring = mydecode(string)
    print(decodedstring)
