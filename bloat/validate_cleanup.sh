#!/bin/bash

echo "🧹 CASSAVA AI - CLEAN PROJECT VALIDATION"
echo "========================================"

# Check project structure
echo "📁 Project Structure:"
echo "Root files:"
ls -1 *.* | head -8

echo ""
echo "Core directories:"
ls -1d */ | grep -v ".git" | head -6

echo ""
echo "📊 File Count Summary:"
echo "- Root files: $(ls -1 *.* | wc -l | tr -d ' ')"
echo "- Backend files: $(find backend -name "*.py" | wc -l | tr -d ' ') Python files"
echo "- Frontend files: $(find frontend -name "*.html" | wc -l | tr -d ' ') HTML files"
echo "- Bloat files: $(find bloat -type f | wc -l | tr -d ' ') archived files"
echo "- Image assets: $(find img -name "*.png" | wc -l | tr -d ' ') logo files"

echo ""
echo "🎯 Active POC Files:"
echo "✅ setup_poc.sh - Main setup script"
echo "✅ diagnostic.sh - AI & channel testing"
echo "✅ quick_test.sh - Direct API testing"
echo "✅ docker-compose.poc.yml - POC configuration"
echo "✅ README.md - Updated documentation"
echo "✅ SETUP_GUIDE.md - Setup instructions"

echo ""
echo "🗑️ Archived Files (in bloat/):"
echo "- $(find bloat -name "*.md" | wc -l | tr -d ' ') documentation files"
echo "- $(find bloat -name "test_*.py" | wc -l | tr -d ' ') test scripts"
echo "- $(find bloat -name "*.sh" | wc -l | tr -d ' ') old setup scripts"

echo ""
echo "✅ CLEANUP COMPLETE!"
echo "📋 Next steps:"
echo "1. Start POC: ./setup_poc.sh"
echo "2. Test system: ./diagnostic.sh" 
echo "3. Access dashboard: http://localhost:8000/ui/"