# Generate key pair
[Generate key pair in pkcs8 format](https://kb.vander.host/security/how-to-generate-rsa-public-and-private-key-pair-in-pkcs8-format/)

openssl genrsa -out keypair.pem 2048 
openssl rsa -in keypair.pem -pubout -out publickey.crt 
openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key