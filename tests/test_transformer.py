"""
Unit Tests for HL7 to XML Transformer

This module contains comprehensive unit tests for the HL7 parser and transformer
components, ensuring reliability and correctness of the transformation process.
"""

import pytest
import os
import sys
import json
import tempfile
from typing import Dict, Any
from xml.etree.ElementTree import fromstring

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hl7_parser import HL7Parser, HL7Message, HL7Segment, HL7Field
from transformer import HL7ToXMLTransformer, TransformationError


class TestHL7Field:
    """Test cases for HL7Field class."""
    
    def test_field_creation(self):
        """Test basic field creation and component parsing."""
        field = HL7Field("DOE^JANE^MARIE")
        assert field.value == "DOE^JANE^MARIE"
        assert len(field.components) == 3
        assert field.components == ["DOE", "JANE", "MARIE"]
    
    def test_get_component(self):
        """Test getting components by index."""
        field = HL7Field("DOE^JANE^MARIE")
        assert field.get_component(1) == "DOE"
        assert field.get_component(2) == "JANE"
        assert field.get_component(3) == "MARIE"
        assert field.get_component(4) is None
        assert field.get_component(0) is None
    
    def test_empty_field(self):
        """Test handling of empty fields."""
        field = HL7Field("")
        assert field.value == ""
        assert field.components == []
        assert field.get_component(1) is None


class TestHL7Segment:
    """Test cases for HL7Segment class."""
    
    def test_segment_creation(self):
        """Test basic segment creation and field parsing."""
        segment_line = "PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F"
        segment = HL7Segment(segment_line)
        assert segment.segment_type == "PID"
        assert len(segment.fields) == 9
    
    def test_get_field(self):
        """Test getting fields by index."""
        segment_line = "PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F"
        segment = HL7Segment(segment_line)
        
        field_1 = segment.get_field(1)
        assert field_1 is not None
        assert field_1.value == "PID"
        
        field_6 = segment.get_field(6)
        assert field_6 is not None
        assert field_6.get_component(1) == "DOE"
        assert field_6.get_component(2) == "JANE"
        
        field_100 = segment.get_field(100)
        assert field_100 is None


class TestHL7Message:
    """Test cases for HL7Message class."""
    
    @pytest.fixture
    def sample_hl7_message(self) -> str:
        """Fixture providing a sample HL7 message."""
        return """MSH|^~\\&|EPIC|UCDMC|CERNER|UCDMC|202312151430||ADT^A01^ADT_A01|12345|P|2.5|||AL||||||
PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F||2106-3^White^HL70005|123 MAIN ST^^SACRAMENTO^CA^95814^USA||(916)555-1234|(916)555-5678|EN^English^HL70296|S^Single^HL70002|CHR^Christian^HL70006|||123-45-6789|||N^Not Hispanic or Latino^HL70189||||||||||202312151430|
PV1|1|I|ICU^101^A|E|||123456^JOHNSON^ROBERT^M^DR^MD|123456^JOHNSON^ROBERT^M^DR^MD|MED||||19|VIP|||123456^JOHNSON^ROBERT^M^DR^MD|INP|INS|||||||||||||||||||||202312151430|202312151600|1|
AL1|1||DRUG^Penicillin^L|MO^Moderate^HL70128|Rash|
DG1|1|I10|Z51.11^Encounter for antineoplastic chemotherapy^ICD10|Encounter for antineoplastic chemotherapy||W|"""
    
    def test_message_parsing(self, sample_hl7_message: str) -> None:
        """Test parsing of complete HL7 message."""
        message = HL7Message(sample_hl7_message)
        
        # Check segments are parsed correctly
        assert "MSH" in message.segments
        assert "PID" in message.segments
        assert "PV1" in message.segments
        assert "AL1" in message.segments
        assert "DG1" in message.segments
        
        assert len(message.segments["MSH"]) == 1
        assert len(message.segments["PID"]) == 1
        assert len(message.segments["AL1"]) == 1
    
    def test_get_field_value(self, sample_hl7_message: str) -> None:
        """Test field value extraction using dot notation."""
        message = HL7Message(sample_hl7_message)
        
        # Test simple field extraction
        assert message.get_field_value("PID.6.1") == "DOE"
        assert message.get_field_value("PID.6.2") == "JANE"
        assert message.get_field_value("PID.8") == "19850315"
        assert message.get_field_value("PID.9") == "F"
        
        # Test non-existent fields
        assert message.get_field_value("PID.999") is None
        assert message.get_field_value("XXX.1") is None
    
    def test_get_segments(self, sample_hl7_message: str) -> None:
        """Test getting segments by type."""
        message = HL7Message(sample_hl7_message)
        
        pid_segments = message.get_segments("PID")
        assert len(pid_segments) == 1
        assert pid_segments[0].segment_type == "PID"
        
        nonexistent_segments = message.get_segments("OBX")
        assert len(nonexistent_segments) == 0


class TestHL7Parser:
    """Test cases for HL7Parser class."""
    
    @pytest.fixture
    def sample_hl7_message(self) -> str:
        """Fixture providing a sample HL7 message."""
        return """MSH|^~\\&|EPIC|UCDMC|CERNER|UCDMC|202312151430||ADT^A01^ADT_A01|12345|P|2.5|||AL||||||
PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F||2106-3^White^HL70005|123 MAIN ST^^SACRAMENTO^CA^95814^USA||(916)555-1234|(916)555-5678|EN^English^HL70296|S^Single^HL70002|CHR^Christian^HL70006|||123-45-6789|||N^Not Hispanic or Latino^HL70189||||||||||202312151430|"""
    
    def test_parse_message(self, sample_hl7_message: str) -> None:
        """Test parsing HL7 message from string."""
        message = HL7Parser.parse(sample_hl7_message)
        assert isinstance(message, HL7Message)
        assert "MSH" in message.segments
        assert "PID" in message.segments
    
    def test_format_date(self):
        """Test date formatting functionality."""
        # Test YYYYMMDD format
        assert HL7Parser.format_date("19850315", "YYYYMMDD") == "1985-03-15"
        
        # Test YYYYMMDDHHMM format
        assert HL7Parser.format_date("202312151430", "YYYYMMDDHHMM") == "2023-12-15 14:30"
        
        # Test invalid date
        assert HL7Parser.format_date("invalid", "YYYYMMDD") == "invalid"
        
        # Test empty date
        assert HL7Parser.format_date("", "YYYYMMDD") is None
    
    def test_validate_message(self, sample_hl7_message: str) -> None:
        """Test message validation."""
        message = HL7Parser.parse(sample_hl7_message)
        errors = HL7Parser.validate_message(message)
        assert len(errors) == 0  # Should be valid
        
        # Test message without MSH
        invalid_message = HL7Message("PID|1||123456789")
        errors = HL7Parser.validate_message(invalid_message)
        assert "Missing required MSH segment" in errors


class TestHL7ToXMLTransformer:
    """Test cases for HL7ToXMLTransformer class."""
    
    @pytest.fixture
    def sample_mapping_config(self) -> Dict[str, Any]:
        """Fixture providing a sample mapping configuration."""
        return {
            "message_type": "ADT^A01",
            "output_format": "xml",
            "mappings": {
                "patient": {
                    "patient_id": {
                        "source": "PID.4.1",
                        "type": "string",
                        "required": True
                    },
                    "last_name": {
                        "source": "PID.6.1",
                        "type": "string",
                        "required": True
                    },
                    "first_name": {
                        "source": "PID.6.2",
                        "type": "string",
                        "required": True
                    },
                    "date_of_birth": {
                        "source": "PID.8",
                        "type": "date",
                        "format": "YYYYMMDD",
                        "required": True
                    }
                },
                "message_header": {
                    "sending_application": {
                        "source": "MSH.3",
                        "type": "string",
                        "required": True
                    },
                    "message_type": {
                        "source": "MSH.9.1",
                        "type": "string",
                        "required": True
                    }
                }
            }
        }
    
    @pytest.fixture
    def sample_hl7_message(self) -> str:
        """Fixture providing a sample HL7 message."""
        return """MSH|^~\\&|EPIC|UCDMC|CERNER|UCDMC|202312151430||ADT^A01^ADT_A01|12345|P|2.5|||AL||||||
PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F||2106-3^White^HL70005|123 MAIN ST^^SACRAMENTO^CA^95814^USA||(916)555-1234|(916)555-5678|EN^English^HL70296|S^Single^HL70002|CHR^Christian^HL70006|||123-45-6789|||N^Not Hispanic or Latino^HL70189||||||||||202312151430|"""
    
    def test_transformer_initialization(self, sample_mapping_config: Dict[str, Any]) -> None:
        """Test transformer initialization with config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_mapping_config, f)
            config_path = f.name
        
        try:
            transformer = HL7ToXMLTransformer(config_path)
            assert transformer.mapping_config == sample_mapping_config
            assert "patient" in transformer.mappings
            assert "message_header" in transformer.mappings
        finally:
            os.unlink(config_path)
    
    def test_transformer_invalid_config(self):
        """Test transformer with invalid configuration file."""
        with pytest.raises(TransformationError):
            HL7ToXMLTransformer("nonexistent_file.json")
    
    def test_transform_to_xml(self, sample_mapping_config: Dict[str, Any], sample_hl7_message: str) -> None:
        """Test transformation of HL7 message to XML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_mapping_config, f)
            config_path = f.name
        
        try:
            transformer = HL7ToXMLTransformer(config_path)
            hl7_message = HL7Parser.parse(sample_hl7_message)
            
            xml_element = transformer.transform(hl7_message)
            
            # Check root element
            assert xml_element.tag == "HealthcareMessage"
            assert xml_element.get("version") == "1.0"
            assert xml_element.get("timestamp") is not None
            
            # Convert to string and parse back to verify structure
            xml_string = transformer.transform_to_xml_string(hl7_message)
            assert "<HealthcareMessage" in xml_string
            assert "<Patient>" in xml_string
            assert "<MessageHeader>" in xml_string
            
            # Parse XML to verify content
            root = fromstring(xml_string.split('?>')[1])  # Remove XML declaration
            
            # Find patient section
            patient = root.find("Patient")
            assert patient is not None
            
            # Check patient fields
            patient_id = patient.find("PatientId")
            assert patient_id is not None
            assert patient_id.text == "123456789"
            
            last_name = patient.find("LastName")
            assert last_name is not None
            assert last_name.text == "DOE"
            
            first_name = patient.find("FirstName")
            assert first_name is not None
            assert first_name.text == "JANE"
            
        finally:
            os.unlink(config_path)
    
    def test_camel_case_conversion(self, sample_mapping_config: Dict[str, Any]) -> None:
        """Test snake_case to CamelCase conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_mapping_config, f)
            config_path = f.name
        
        try:
            transformer = HL7ToXMLTransformer(config_path)
            
            assert transformer._camel_case("patient_id") == "PatientId"  # type: ignore[misc]
            assert transformer._camel_case("last_name") == "LastName"  # type: ignore[misc]
            assert transformer._camel_case("message_header") == "MessageHeader"  # type: ignore[misc]
            assert transformer._camel_case("simple") == "Simple"  # type: ignore[misc]
            
        finally:
            os.unlink(config_path)
    
    def test_field_extraction(self, sample_mapping_config: Dict[str, Any], sample_hl7_message: str) -> None:
        """Test field value extraction with different types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_mapping_config, f)
            config_path = f.name
        
        try:
            transformer = HL7ToXMLTransformer(config_path)
            hl7_message = HL7Parser.parse(sample_hl7_message)
            
            # Test string field
            field_config = {"source": "PID.6.1", "type": "string"}
            value = transformer._extract_field_value(hl7_message, field_config)  # type: ignore[misc]
            assert value == "DOE"
            
            # Test date field
            field_config = {"source": "PID.8", "type": "date", "format": "YYYYMMDD"}
            value = transformer._extract_field_value(hl7_message, field_config)  # type: ignore[misc]
            assert value == "1985-03-15"
            
            # Test non-existent field
            field_config = {"source": "PID.999", "type": "string"}
            value = transformer._extract_field_value(hl7_message, field_config)  # type: ignore[misc]
            assert value is None
            
        finally:
            os.unlink(config_path)


class TestIntegration:
    """Integration tests for the complete transformation process."""
    
    def test_end_to_end_transformation(self) -> None:
        """Test complete end-to-end transformation process."""
        # Create sample HL7 message
        hl7_content = """MSH|^~\\&|EPIC|UCDMC|CERNER|UCDMC|202312151430||ADT^A01^ADT_A01|12345|P|2.5|||AL||||||
PID|1||123456789^^^UCDMC^MR||DOE^JANE^MARIE^||19850315|F||2106-3^White^HL70005|123 MAIN ST^^SACRAMENTO^CA^95814^USA||(916)555-1234|(916)555-5678|EN^English^HL70296|S^Single^HL70002|CHR^Christian^HL70006|||123-45-6789|||N^Not Hispanic or Latino^HL70189||||||||||202312151430|
PV1|1|I|ICU^101^A|E|||123456^JOHNSON^ROBERT^M^DR^MD|123456^JOHNSON^ROBERT^M^DR^MD|MED||||19|VIP|||123456^JOHNSON^ROBERT^M^DR^MD|INP|INS|||||||||||||||||||||202312151430|202312151600|1|
AL1|1||DRUG^Penicillin^L|MO^Moderate^HL70128|Rash|"""
        
        # Create mapping configuration
        mapping_config = {
            "message_type": "ADT^A01",
            "output_format": "xml",
            "mappings": {
                                    "patient": {
                        "patient_id": {"source": "PID.4.1", "type": "string", "required": True},
                        "last_name": {"source": "PID.6.1", "type": "string", "required": True},
                        "first_name": {"source": "PID.6.2", "type": "string", "required": True},
                        "date_of_birth": {"source": "PID.8", "type": "date", "format": "YYYYMMDD", "required": True}
                    },
                "allergies": {
                    "source": "AL1",
                    "type": "array",
                    "fields": {
                        "allergen": {"source": "AL1.3.2", "type": "string"},
                        "severity": {"source": "AL1.4.2", "type": "string"}
                    }
                }
            }
        }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hl7', delete=False) as hl7_file:
            hl7_file.write(hl7_content)
            hl7_path = hl7_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            json.dump(mapping_config, config_file)
            config_path = config_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as xml_file:
            xml_path = xml_file.name
        
        try:
            # Perform transformation
            transformer = HL7ToXMLTransformer(config_path)
            transformer.transform_file(hl7_path, xml_path)
            
            # Verify output file exists and contains expected content
            assert os.path.exists(xml_path)
            
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Verify XML structure
            assert "<HealthcareMessage" in xml_content
            assert "<Patient>" in xml_content
            assert "<PatientId>123456789</PatientId>" in xml_content
            assert "<LastName>DOE</LastName>" in xml_content
            assert "<FirstName>JANE</FirstName>" in xml_content
            assert "<DateOfBirth>1985-03-15</DateOfBirth>" in xml_content
            assert "<Allergies>" in xml_content
            assert "<Severity>Penicillin</Severity>" in xml_content
            
        finally:
            # Clean up temporary files
            for temp_file in [hl7_path, config_path, xml_path]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 