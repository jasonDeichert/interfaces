"""
Test for New Directory Structure and OBX Segments

This test verifies that the new directory structure works correctly
and that the enhanced config processes OBX segments properly.
"""

import os
import sys
import tempfile
from xml.etree.ElementTree import fromstring

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transformer import BidirectionalTransformer


def test_basic_inbound_config():
    """Test that basic inbound config works but ignores OBX segments."""
    config_path = "config/inbound_config.json"
    hl7_file = "data/input/hl7/sample_meditech_adt.hl7"
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        transformer = BidirectionalTransformer(config_path)
        transformer.transform_file(hl7_file, output_path)
        
        # Verify file was created
        assert os.path.exists(output_path), "Output file should exist"
        
        # Parse and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Remove XML declaration for parsing
        xml_body = xml_content.split('?>')[1] if '?>' in xml_content else xml_content
        root = fromstring(xml_body)
        
        # Should have basic sections
        assert root.find("MessageHeader") is not None, "Should have MessageHeader"
        assert root.find("Patient") is not None, "Should have Patient"
        assert root.find("Visit") is not None, "Should have Visit"
        
        # Should NOT have OBX-based sections (ignored by basic config)
        assert root.find("FinancialInformation") is None, "Should NOT have FinancialInformation with basic config"
        assert root.find("SogiInformation") is None, "Should NOT have SogiInformation with basic config"
        
        # Count lines - should be around 40 lines for basic output
        line_count = len(xml_content.strip().split('\n'))
        assert 35 <= line_count <= 45, f"Basic config should produce ~40 lines, got {line_count}"
        
        print("✅ Basic inbound config test passed")
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_enhanced_inbound_config():
    """Test that enhanced inbound config processes OBX segments."""
    config_path = "config/demo_configs/enhanced_inbound_config.json"
    hl7_file = "data/input/hl7/sample_meditech_adt.hl7"
    
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        transformer = BidirectionalTransformer(config_path)
        transformer.transform_file(hl7_file, output_path)
        
        # Verify file was created
        assert os.path.exists(output_path), "Output file should exist"
        
        # Parse and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Remove XML declaration for parsing
        xml_body = xml_content.split('?>')[1] if '?>' in xml_content else xml_content
        root = fromstring(xml_body)
        
        # Should have basic sections
        assert root.find("MessageHeader") is not None, "Should have MessageHeader"
        assert root.find("Patient") is not None, "Should have Patient"
        assert root.find("Visit") is not None, "Should have Visit"
        
        # Should HAVE OBX-based sections (processed by enhanced config)
        financial = root.find("FinancialInformation")
        assert financial is not None, "Should have FinancialInformation with enhanced config"
        
        sogi = root.find("SogiInformation")
        assert sogi is not None, "Should have SogiInformation with enhanced config"
        
        communication = root.find("CommunicationPreferences")
        assert communication is not None, "Should have CommunicationPreferences with enhanced config"
        
        # Check specific OBX values
        financial_items = financial.findall("FinancialInformation")
        assert len(financial_items) >= 3, "Should have at least 3 financial information items"
        
        # Check for specific financial data
        loan_interest = None
        for item in financial_items:
            value_elem = item.find("Value")
            if value_elem is not None and value_elem.text and "HOME_MORTGAGE" in value_elem.text:
                loan_interest = value_elem.text
                break
        assert loan_interest is not None, "Should have loan interest information"
        
        # Count lines - should be much more than basic (around 160+ lines)
        line_count = len(xml_content.strip().split('\n'))
        assert line_count >= 150, f"Enhanced config should produce 150+ lines, got {line_count}"
        
        print("✅ Enhanced inbound config test passed")
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_directory_structure():
    """Test that the new directory structure is correct."""
    # Check input directories
    assert os.path.exists("data/input/hl7"), "Should have data/input/hl7 directory"
    assert os.path.exists("data/input/xml"), "Should have data/input/xml directory"
    
    # Check that files are in correct locations
    assert os.path.exists("data/input/hl7/sample_meditech_adt.hl7"), "Should have Meditech HL7 file in hl7 directory"
    assert os.path.exists("data/input/xml/sample_patient_data.xml"), "Should have XML file in xml directory"
    
    # Check config structure
    assert os.path.exists("config/inbound_config.json"), "Should have inbound config"
    assert os.path.exists("config/outbound_config.json"), "Should have outbound config"
    assert os.path.exists("config/demo_configs"), "Should have demo configs directory"
    assert os.path.exists("config/demo_configs/enhanced_inbound_config.json"), "Should have enhanced config"
    
    # Check that sample file has OBX segments
    with open("data/input/hl7/sample_meditech_adt.hl7", 'r') as f:
        content = f.read()
        assert "OBX|" in content, "Sample file should contain OBX segments"
        assert "LOAN_INTEREST" in content, "Should have financial OBX data"
        assert "SOGI_" in content, "Should have SOGI OBX data"
    
    print("✅ Directory structure test passed")


def run_all_tests():
    """Run all tests."""
    print("🧪 Testing New Structure and OBX Segments")
    print("=" * 50)
    
    try:
        test_directory_structure()
        test_basic_inbound_config()
        test_enhanced_inbound_config()
        
        print("\n🎉 All tests passed!")
        print("✅ Directory structure is correct")
        print("✅ Basic config ignores OBX segments (as expected)")
        print("✅ Enhanced config processes OBX segments correctly")
        print("✅ Demo is ready for presentation!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests() 