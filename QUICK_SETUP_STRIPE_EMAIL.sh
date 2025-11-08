#!/bin/bash
# Quick setup script for Stripe and Email
# Usage: ./QUICK_SETUP_STRIPE_EMAIL.sh

echo "🔧 Stripe & Email Setup Helper"
echo "================================"
echo ""

# Check current setup
echo "📊 Текущо състояние:"
echo ""

# Check Stripe
if grep -q "STRIPE_SECRET_KEY" .env 2>/dev/null; then
    echo "✅ Stripe Secret Key: SET"
else
    echo "❌ Stripe Secret Key: NOT SET"
fi

if grep -q "STRIPE_PUBLISHABLE_KEY" .env 2>/dev/null; then
    echo "✅ Stripe Publishable Key: SET"
else
    echo "❌ Stripe Publishable Key: NOT SET"
fi

if grep -q "STRIPE_WEBHOOK_SECRET" .env 2>/dev/null; then
    echo "✅ Stripe Webhook Secret: SET"
else
    echo "⚠️  Stripe Webhook Secret: NOT SET (добави от Stripe Dashboard)"
fi

echo ""

# Check Email
if grep -q "EMAIL_HOST" .env 2>/dev/null; then
    EMAIL_HOST=$(grep "EMAIL_HOST" .env | cut -d '=' -f2)
    if [[ "$EMAIL_HOST" == *"mailtrap"* ]]; then
        echo "⚠️  Email Host: Mailtrap Sandbox (за тестване)"
        echo "   → За production използвай Gmail/SendGrid"
    else
        echo "✅ Email Host: $EMAIL_HOST"
    fi
else
    echo "❌ Email Host: NOT SET"
fi

if grep -q "EMAIL_HOST_USER" .env 2>/dev/null; then
    echo "✅ Email User: SET"
else
    echo "❌ Email User: NOT SET"
fi

echo ""
echo "================================"
echo ""
echo "📚 За пълни инструкции виж:"
echo "   - SETUP_STRIPE_EMAIL.md"
echo "   - CHECK_CURRENT_SETUP.md"
echo ""

