"""
Sensor Credentials - Certificate and Private Key
Self-signed certificate and private key in PEM format for IoT sensor authentication
"""

# Self-signed X.509 Certificate in PEM format
# Valid for 1 year from 2026-06-11
# Subject: CN=iot-sensor-sensor_001, OU=IoT Devices, O=IoT Sensors Inc, L=Stockholm, ST=Stockholm, C=SE
SENSOR_CERTIFICATE_PEM = """-----BEGIN CERTIFICATE-----
MIID1jCCAr6gAwIBAgIUYW3w8egt8leUvsFPv3egVcpLowAwDQYJKoZIhvcNAQEL
BQAwgYUxCzAJBgNVBAYTAlNFMRIwEAYDVQQIDAlTdG9ja2hvbG0xEjAQBgNVBAcM
CVN0b2NraG9sbTEYMBYGA1UECgwPSW9UIFNlbnNvcnMgSW5jMRQwEgYDVQQLDAtJ
b1QgRGV2aWNlczEeMBwGA1UEAwwVaW90LXNlbnNvci1zZW5zb3JfMDAxMB4XDTI2
MDYxMTEwNTA0NFoXDTI3MDYxMTEwNTA0NFowgYUxCzAJBgNVBAYTAlNFMRIwEAYD
VQQIDAlTdG9ja2hvbG0xEjAQBgNVBAcMCVN0b2NraG9sbTEYMBYGA1UECgwPSW9U
IFNlbnNvcnMgSW5jMRQwEgYDVQQLDAtJb1QgRGV2aWNlczEeMBwGA1UEAwwVaW90
LXNlbnNvci1zZW5zb3JfMDAxMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC
AQEAuC7YS+t3RtN6PHrgoLEyrDuPrVU+pHV660zh1eij/CLwFf+7hKgQKsPVE5pU
WGTA9alKRoYwpntakjK396BiEnzAy0Mo6yUU7pVgwbMZx/djtHLH8cocOunPUjk4
IqaGai2Rfwf2XvFJEysnAYuXUe0dWgx7gqwwPfiY7lUSt/dgqKNdAUUsZ0bSMjWo
bOu27pWfJETLS4nMRQTWtt+ZOyPwiXxsvYB1rj71zC4N2VYjKcWj1vgUw0x+VK+w
Qr1UAqJLxp2EjhqLBIlSN0vlML7plfYfPlREfzyCC1v233CoRvbP94jK7GHwngLb
Auqcwoo1lfxOl5hcTceUaamIaQIDAQABozwwOjA4BgNVHREEMTAvghdzZW5zb3It
c2Vuc29yXzAwMS5sb2NhbIIUc2Vuc29yXzAwMS5pb3QubG9jYWwwDQYJKoZIhvcN
AQELBQADggEBAI2gDuqWeMVRyylJUyDENRfGRyIP4OWET09on4URmYHCTU0D/Nyj
t2sQrN58iF6nD111pqjzkKAsXQt9R//ZvZyA6InIodRaZ323F/VMb3x7XrugtPiG
YILFUKLvveTryI4i1SbpTMyn75fW78wvZTTVNyarqASDDZPUPbUuE9gSjSBCbyZp
K7ySQypoS9kkg1tuhmXvVDH2l4jqQ7dOWdsJcyypJI1lyi67ThWwMtW7cdGvhAjw
YtRoNN+lLVczmVDF6y4sta1mkSqxkiIut9o/q69K5gbcL3/J9uEuKr7epTRbTDNc
DdvsAdfFGmHMcMRXoOj5tjDm0RAmpCym+t4=
-----END CERTIFICATE-----"""

# RSA Private Key in PEM format (2048-bit)
# IMPORTANT: Keep this private key secure!
# In production, store in a secure key management system or hardware security module (HSM)
SENSOR_PRIVATE_KEY_PEM = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAuC7YS+t3RtN6PHrgoLEyrDuPrVU+pHV660zh1eij/CLwFf+7
hKgQKsPVE5pUWGTA9alKRoYwpntakjK396BiEnzAy0Mo6yUU7pVgwbMZx/djtHLH
8cocOunPUjk4IqaGai2Rfwf2XvFJEysnAYuXUe0dWgx7gqwwPfiY7lUSt/dgqKNd
AUUsZ0bSMjWobOu27pWfJETLS4nMRQTWtt+ZOyPwiXxsvYB1rj71zC4N2VYjKcWj
1vgUw0x+VK+wQr1UAqJLxp2EjhqLBIlSN0vlML7plfYfPlREfzyCC1v233CoRvbP
94jK7GHwngLbAuqcwoo1lfxOl5hcTceUaamIaQIDAQABAoIBABE/jtE2SwBindoD
2l0mFwQe3E7L0r7ZQyJ9u9D51UCPn4r53NxYllIA7qeELoWsIs9mtA5ccvomR2Y1
UnnhxslrLi1i29ZAjeAldE8TeBS8T9WmYZ/csO3Z90jAk8eX73LKU2uxadK8lx6w
zfl0sn4xPcxQ6rCjMi3dhenc5PC+FN0Dig4fBUqc0sGLgqkIjiA1qvSmMjEXwnYB
41yOG/qcRwN/9p+hOlQZYc7sf0VmJK1JG2X06QWkFJk+FFidQbgEuUgR42ojSmGV
qshOfjXMP48HRLI2CrCHXtxDgmJW7KcH9AUwskTx3V4UGrjrKBWCNGMOWdgRG+cN
SeEUyJECgYEA3bFcmwWv+bXU/mnrkz6CmDYD6pXUjAOFgOhYGoOtKVdU6qLONpcA
Y3vFeit/FUm/FoZuYIdhqdnzKDXS4m95z2XRMmTrmCtkH+1JQPJr6DIrDR4HW04d
jD3BpEMbWxAVybNuD2anbGUQMqgoI7pFIzmfYaqRRIA7YjcVx5E6YhECgYEA1K97
+prVrsJFP4txHG6cizexqkg4lEcQjNaRU12HxGohXfleSBp2VUmBmC/4mXkdwljt
BrDXTmJC9A2uKVZ1TXf+NqKjXzN12mX5SHsQAhI1uVieohcW6d5sNuttCn+FinDI
swDwqIOR8a9nkZ9Wsm2G2sUx82X52GJXT0R96NkCgYEA16Jm0xrrGla1QGnCjExn
NqqDkLAAN9hNCR/2YoPl8KpTnI6TSiICbMG9SaH5ULmUttI3lojYhB/NFjWUVE/e
Cc+ddgkX58F8+FkTwaqLLyVtHqswuKz4rKp9KctkVmUE7FYtHanZ++MpqDxMHsRV
73djAdqoxhp8qIGwG5e1VCECgYEAjlnFyT3It2cfoiBaXIVMEYH9T9N2yweldB5I
tltre3LtUlCNYgUUHpFMQ+gXo+EEogeS3V+PO89YsLBXWSOc73TYmQjR/+4Ze0u1
RWXYmQpHGv7Nbf+2PmG4XCnGmbgwUTCbo/OFH8Sv8etMjpLvHA1irRo/DIG8b6+i
cFOPUkECgYAYAP4qGhuMGIgrDKC8ac+SpYcXg7GalTHdSgN6peOUiVH0qJfs/b4I
PJTMaDy9J3mBZ8Y98ZBLFKuoPiaXRtFY/u7+uyeqh09UHPisu3iCObesNOc5Mtna
kbjlTPiH8KrbMknVLTJdqK+KbNAdyKNoB422bvguDPYUeEdCVOzOHA==
-----END RSA PRIVATE KEY-----"""

# Certificate information
CERTIFICATE_INFO = {
    "subject": {
        "country": "SE",
        "state": "Stockholm",
        "locality": "Stockholm",
        "organization": "IoT Sensors Inc",
        "organizational_unit": "IoT Devices",
        "common_name": "iot-sensor-sensor_001"
    },
    "subject_alternative_names": [
        "sensor-sensor_001.local",
        "sensor_001.iot.local"
    ],
    "valid_from": "2026-06-11T10:50:44Z",
    "valid_until": "2027-06-11T10:50:44Z",
    "key_size": 2048,
    "algorithm": "RSA",
    "signature_algorithm": "SHA256"
}

# Made with Bob