#!/bin/bash

# S3 Migration Setup Script
# This script sets up everything needed for S3 storage migration

set -e  # Exit on error

echo "=========================================="
echo "🚀 S3 Storage Migration Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 1: Checking AWS CLI configuration...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    echo "Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if aws sts get-caller-identity &> /dev/null; then
    echo -e "${GREEN}✅ AWS credentials configured${NC}"
    aws sts get-caller-identity
else
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "\n${YELLOW}Step 2: Installing Python dependencies...${NC}"
cd backend
pip install boto3 pandas joblib scikit-learn --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "\n${YELLOW}Step 3: Verifying S3 buckets...${NC}"
# List of required buckets
BUCKETS=(
    "climate-health-raw-data-sharvaj"
    "climate-health-processed-data-sharvaj"
    "climate-health-models-use1-457151800683"
)

for bucket in "${BUCKETS[@]}"; do
    if aws s3 ls "s3://$bucket" &> /dev/null; then
        echo -e "${GREEN}✅ Bucket exists: $bucket${NC}"
    else
        echo -e "${RED}❌ Bucket not found: $bucket${NC}"
        echo "Please create the bucket or update the bucket name in app/utils/s3_storage.py"
        exit 1
    fi
done

echo -e "\n${YELLOW}Step 4: Creating directory structure...${NC}"
mkdir -p app/services
mkdir -p app/utils
mkdir -p models
mkdir -p data/raw
mkdir -p data/processed
echo -e "${GREEN}✅ Directories created${NC}"

echo -e "\n${YELLOW}Step 5: Checking for data files...${NC}"
if [ -f "data/raw/climate_data.csv" ]; then
    echo -e "${GREEN}✅ Found: climate_data.csv${NC}"
else
    echo -e "${YELLOW}⚠️  climate_data.csv not found in data/raw/${NC}"
fi

if [ -f "data/raw/health_data.csv" ]; then
    echo -e "${GREEN}✅ Found: health_data.csv${NC}"
else
    echo -e "${YELLOW}⚠️  health_data.csv not found in data/raw/${NC}"
fi

if [ -f "data/raw/hospital_data.csv" ]; then
    echo -e "${GREEN}✅ Found: hospital_data.csv${NC}"
else
    echo -e "${YELLOW}⚠️  hospital_data.csv not found in data/raw/${NC}"
fi

if [ -f "data/raw/locations.csv" ]; then
    echo -e "${GREEN}✅ Found: locations.csv${NC}"
else
    echo -e "${YELLOW}⚠️  locations.csv not found in data/raw/${NC}"
fi

echo -e "\n${YELLOW}Step 6: Saving models...${NC}"
if [ -f "save_enhanced_models.py" ]; then
    echo "Running save_enhanced_models.py..."
    python save_enhanced_models.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Models saved successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Model saving had issues (this is okay if models already exist)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  save_enhanced_models.py not found${NC}"
fi

echo -e "\n${YELLOW}Step 7: Running data migration to S3...${NC}"
if [ -f "migrate_data_to_s3.py" ]; then
    echo "Uploading data to S3..."
    python migrate_data_to_s3.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Data migration completed${NC}"
    else
        echo -e "${RED}❌ Data migration failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ migrate_data_to_s3.py not found${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 8: Testing S3 integration...${NC}"
if [ -f "test_s3_integration.py" ]; then
    echo "Running integration tests..."
    python test_s3_integration.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some tests failed - check the output above${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  test_s3_integration.py not found${NC}"
fi

echo -e "\n=========================================="
echo -e "${GREEN}🎉 S3 Migration Setup Complete!${NC}"
echo "=========================================="

echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo "1. Review the test results above"
echo "2. Update your application code to use:"
echo "   - app.services.data_service"
echo "   - app.services.model_service"
echo "3. Test your API endpoints"
echo "4. Monitor AWS CloudWatch logs"

echo -e "\n${YELLOW}📚 Documentation:${NC}"
echo "- S3 Migration Guide: ../S3_MIGRATION_GUIDE.md"
echo "- Code Examples: ./S3_MIGRATION_EXAMPLES.py"

echo -e "\n${YELLOW}🔍 Useful Commands:${NC}"
echo "# List S3 bucket contents:"
echo "  aws s3 ls s3://climate-health-raw-data-sharvaj/raw/"
echo ""
echo "# Check bucket sizes:"
echo "  aws s3 ls s3://climate-health-raw-data-sharvaj --recursive --summarize"
echo ""
echo "# Download a file:"
echo "  aws s3 cp s3://climate-health-raw-data-sharvaj/raw/climate_data.csv ./local_file.csv"
echo ""

cd ..
