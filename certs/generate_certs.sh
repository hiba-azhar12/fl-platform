#!/bin/bash
# Genere tous les certificats mTLS X.509 pour le cluster FL Finance
# Usage : bash generate_certs.sh

set -e
cd "$(dirname "$0")"

echo "Generation de la Certificate Authority (CA)..."
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 \
    -out ca.crt -subj '/CN=FL-Finance-CA'

echo "Certificat du serveur agregateur..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj '/CN=fl-server'
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days 365 -sha256

echo "Certificats des 4 banques..."
for bank in bank_a bank_b bank_c bank_d; do
    openssl genrsa -out ${bank}.key 2048
    openssl req -new -key ${bank}.key -out ${bank}.csr \
        -subj "/CN=${bank}"
    openssl x509 -req -in ${bank}.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out ${bank}.crt -days 365 -sha256
    rm ${bank}.csr
    echo "  ${bank}.crt OK"
done

rm server.csr
echo ""
echo "Certificats generes :"
ls -la *.crt *.key
