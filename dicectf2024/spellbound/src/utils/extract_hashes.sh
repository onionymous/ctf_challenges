#!/bin/bash

# `extract_hashes.sh *.apk`

help() {
    "echo `extract_hashes.sh <your.apk>`"
}

TMP=$(mktemp -d)
trap 'rm -r $TMP' EXIT

APK=$1
PEM="$TMP/cert.pem"

RSA_FILE=$(unzip -l "$APK" "META-INF/*.[R|D]SA" | grep -o "[-a-zA-Z0-9]*.RSA")
if [[ -z "$RSA_FILE" ]]; then
    echo "APK has no signature"
    exit 1
fi

RSA="$TMP/$RSA_FILE"
unzip -jq "$APK" "META-INF/*.[R|D]SA" -d "$TMP/"
openssl pkcs7 -inform DER -in "$RSA" -print_certs -out "$PEM"

echo ""
echo "Certificate information"
openssl x509 -in "$PEM" -noout -subject -issuer -dates -fingerprint -md5
openssl x509 -in "$PEM" -noout -fingerprint -sha256
openssl x509 -in "$PEM"

echo ""
echo "hash"

base64UrlEncode() {
    echo "$1" | sed 's%=%%g' | sed 's%+%-%g' | sed 's%/%_%g'
}

DER="$TMP/cert.cer"
openssl x509 -inform PEM -in "$PEM" -outform DER -out "DER"
echo "--------"
SHA256=$(openssl dgst -sha256 -binary < "$DER" | openssl base64)
echo "sha256: $(base64UrlEncode "$SHA256")"
echo "android signature hex:"
xxd -p -g 0 -c 30 $DER
echo "--------"