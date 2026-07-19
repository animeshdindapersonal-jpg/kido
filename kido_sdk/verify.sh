#!/bin/bash

echo "============================================================"
echo "🧒 KIDO SDK Verification"
echo "============================================================"
echo ""

# Check executable
echo "📦 Checking executable..."
if [ -f "dist/kido" ]; then
    echo "  ✅ Executable exists: $(ls -lh dist/kido | awk '{print $5}')"
    VERSION=$(./dist/kido version 2>&1 | head -1)
    echo "  ✅ Version: $VERSION"
else
    echo "  ❌ Executable not found"
fi
echo ""

# Check examples
echo "📚 Checking examples..."
EXAMPLE_COUNT=$(ls examples/*.kd 2>/dev/null | wc -l)
echo "  ✅ $EXAMPLE_COUNT example programs available"
echo ""

# Run a test
echo "🧪 Running test program..."
./dist/kido run examples/hello.kd > /tmp/kido_test_output.txt 2>&1
if [ $? -eq 0 ]; then
    echo "  ✅ Test program executed successfully"
    echo "  Output preview:"
    head -3 /tmp/kido_test_output.txt | sed 's/^/    /'
else
    echo "  ❌ Test program failed"
fi
echo ""

# Check documentation
echo "📄 Checking documentation..."
for doc in README.md INSTALL.md QUICKSTART.md SUMMARY.md; do
    if [ -f "$doc" ]; then
        echo "  ✅ $doc exists"
    else
        echo "  ❌ $doc missing"
    fi
done
echo ""

# Check build system
echo "🔨 Checking build system..."
for script in build.py build_unix.sh install.sh; do
    if [ -f "$script" ]; then
        echo "  ✅ $script exists"
    else
        echo "  ❌ $script missing"
    fi
done
echo ""

# Check distribution package
echo "📦 Checking distribution package..."
if [ -f "kido-linux.tar.gz" ]; then
    echo "  ✅ Distribution package exists: $(ls -lh kido-linux.tar.gz | awk '{print $5}')"
else
    echo "  ⚠️  Distribution package not built (run build_unix.sh to create)"
fi
echo ""

echo "============================================================"
echo "✅ Verification complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Test: ./dist/kido run examples/hello.kd"
echo "  2. Install: sudo ./install.sh"
echo "  3. Read: cat QUICKSTART.md"
echo ""

rm -f /tmp/kido_test_output.txt
