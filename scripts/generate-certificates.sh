#!/bin/bash
# SSL Certificate Generation Script
# Generates self-signed certificates for local development
# For production, use Let's Encrypt with certbot

set -e

CERT_DIR="./nginx/certs"
DAYS_VALID=365

echo "🔐 CIAF SSL Certificate Generation"
echo "=================================="
echo ""

# Create certificate directory
mkdir -p "$CERT_DIR"

# Generate self-signed certificate for development
if [ ! -f "$CERT_DIR/key.pem" ] || [ ! -f "$CERT_DIR/cert.pem" ]; then
    echo "📝 Generating self-signed certificate for development..."
    echo "   Valid for $DAYS_VALID days"
    echo ""

    openssl req -x509 \
        -newkey rsa:4096 \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days $DAYS_VALID \
        -nodes \
        -subj "/C=US/ST=Development/L=Local/O=CIAF/CN=localhost"

    echo "✅ Certificate generated successfully!"
    echo ""
    echo "📂 Certificate location: $CERT_DIR"
    echo "   - Private key: $CERT_DIR/key.pem"
    echo "   - Certificate: $CERT_DIR/cert.pem"
    echo ""
    echo "⚠️  WARNING: This is a self-signed certificate for development only"
    echo "            Your browser will show a security warning"
    echo "            For production, use Let's Encrypt certificates"
else
    echo "✅ Certificate already exists at $CERT_DIR"
    echo "   - Private key: $CERT_DIR/key.pem"
    echo "   - Certificate: $CERT_DIR/cert.pem"
fi

echo ""
echo "📖 PRODUCTION SETUP:"
echo "==================="
echo "For production deployments, use Let's Encrypt with certbot:"
echo ""
echo "1. Run docker-compose with production profile:"
echo "   docker-compose --profile production up -d"
echo ""
echo "2. Certbot will automatically:"
echo "   - Generate certificates from Let's Encrypt"
echo "   - Renew certificates automatically"
echo "   - Update nginx configuration"
echo ""
echo "3. Update your docker-compose.yml with production domain"
echo ""
