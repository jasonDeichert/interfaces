"""
HL7 ↔ XML Bidirectional Transformer

This module provides a flexible transformation engine that can convert between
HL7 and XML formats based on JSON mapping configurations. Designed to demonstrate
AI-accelerated development of healthcare interface transformations.
"""

import json
import os
import glob
from typing import Dict, Optional, Any, cast, List
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring
from xml.dom import minidom
from datetime import datetime
import sys

from hl7_parser import HL7Parser, HL7Message


class TransformationError(Exception):
    """Custom exception for transformation errors."""
    pass


class BidirectionalTransformer:
    """Main transformer class for converting between HL7 and XML formats."""
    
    def __init__(self, mapping_config_path: str):
        """
        Initialize transformer with mapping configuration.
        
        Args:
            mapping_config_path: Path to JSON mapping configuration file
        """
        self.mapping_config = self._load_mapping_config(mapping_config_path)
        self.mappings = self.mapping_config.get('mappings', {})
        self.input_format = self.mapping_config.get('input_format', 'hl7')
        self.output_format = self.mapping_config.get('output_format', 'xml')
    
    def _load_mapping_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate mapping configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config: Dict[str, Any] = json.load(file)
            return config
        except FileNotFoundError:
            raise TransformationError(f"Mapping configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise TransformationError(f"Invalid JSON in mapping configuration: {e}")
    
    def process_directory(self, input_base_dir: str, output_base_dir: str) -> List[str]:
        """
        Process all files in input directory structure and generate outputs.
        
        Args:
            input_base_dir: Base directory containing hl7/ and xml/ subdirectories
            output_base_dir: Base directory for hl7_output/ and xml_output/ subdirectories
            
        Returns:
            List of processed file paths
        """
        # Ensure output directories exist
        hl7_output_dir = os.path.join(output_base_dir, 'hl7_output')
        xml_output_dir = os.path.join(output_base_dir, 'xml_output')
        os.makedirs(hl7_output_dir, exist_ok=True)
        os.makedirs(xml_output_dir, exist_ok=True)
        
        processed_files: List[str] = []
        
        # Process HL7 files (input_base_dir/hl7/*.hl7 -> output_base_dir/xml_output/*.xml)
        hl7_input_dir = os.path.join(input_base_dir, 'hl7')
        if os.path.exists(hl7_input_dir):
            hl7_pattern = os.path.join(hl7_input_dir, '*.hl7')
            hl7_files = glob.glob(hl7_pattern)
            
            for input_file in hl7_files:
                try:
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    output_file = os.path.join(xml_output_dir, f"{base_name}.xml")
                    
                    if self.input_format.lower() == 'hl7' and self.output_format.lower() == 'xml':
                        self._transform_hl7_to_xml(input_file, output_file)
                        processed_files.append(output_file)
                    
                except Exception as e:
                    print(f"Error processing {input_file}: {e}")
                    continue
        
        # Process XML files (input_base_dir/xml/*.xml -> output_base_dir/hl7_output/*.hl7)
        xml_input_dir = os.path.join(input_base_dir, 'xml')
        if os.path.exists(xml_input_dir):
            xml_pattern = os.path.join(xml_input_dir, '*.xml')
            xml_files = glob.glob(xml_pattern)
            
            for input_file in xml_files:
                try:
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    output_file = os.path.join(hl7_output_dir, f"{base_name}.hl7")
                    
                    if self.input_format.lower() == 'xml' and self.output_format.lower() == 'hl7':
                        self._transform_xml_to_hl7(input_file, output_file)
                        processed_files.append(output_file)
                    
                except Exception as e:
                    print(f"Error processing {input_file}: {e}")
                    continue
        
        return processed_files
    
    def transform_file(self, input_file_path: str, output_file_path: str) -> None:
        """
        Transform single file from input format to output format.
        
        Args:
            input_file_path: Path to input file
            output_file_path: Path to output file
        """
        try:
            if self.input_format.lower() == 'hl7' and self.output_format.lower() == 'xml':
                self._transform_hl7_to_xml(input_file_path, output_file_path)
            elif self.input_format.lower() == 'xml' and self.output_format.lower() == 'hl7':
                self._transform_xml_to_hl7(input_file_path, output_file_path)
            else:
                raise TransformationError(f"Unsupported transformation: {self.input_format} to {self.output_format}")
                
            print(f"✓ Transformed: {os.path.basename(input_file_path)} → {os.path.basename(output_file_path)}")
            
        except Exception as e:
            raise TransformationError(f"Failed to transform {input_file_path}: {e}")
    
    def _transform_hl7_to_xml(self, input_file_path: str, output_file_path: str) -> None:
        """Transform HL7 file to XML."""
        # Parse HL7 message
        hl7_message = HL7Parser.parse_from_file(input_file_path)
        
        # Validate message
        errors = HL7Parser.validate_message(hl7_message)
        if errors:
            print(f"⚠️  Validation warnings: {', '.join(errors)}")
        
        # Transform to XML
        xml_element = self._hl7_to_xml_element(hl7_message)
        xml_string = self._format_xml(xml_element)
        
        # Write to output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(xml_string)
    
    def _transform_xml_to_hl7(self, input_file_path: str, output_file_path: str) -> None:
        """Transform XML file to HL7."""
        # Parse XML
        with open(input_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        xml_element = fromstring(xml_content)
        
        # Transform to HL7
        hl7_content = self._xml_to_hl7_string(xml_element)
        
        # Write to output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(hl7_content)
    
    def _hl7_to_xml_element(self, hl7_message: HL7Message) -> Element:
        """Convert HL7 message to XML Element."""
        # Create root XML element
        root = Element("HealthcareMessage")
        root.set("version", "1.0")
        root.set("timestamp", datetime.now().isoformat())
        root.set("transformation_config", self.mapping_config.get('config_name', 'default'))
        
        # Process each section in the mapping
        for section_name, section_config in self.mappings.items():
            if section_name == "message_header":
                self._process_message_header(root, hl7_message, section_config)
            elif section_name == "patient":
                self._process_patient(root, hl7_message, section_config)
            elif section_name == "visit":
                self._process_visit(root, hl7_message, section_config)
            elif section_name == "custom_segments":
                self._process_custom_segments(root, hl7_message, section_config)
            elif section_config.get('source') == 'OBX':
                self._process_obx_section(root, hl7_message, section_name, section_config)
            elif section_name == "allergies":
                self._process_array_section(root, hl7_message, section_name, section_config)
            elif section_name == "diagnoses":
                self._process_array_section(root, hl7_message, section_name, section_config)
        
        return root
    
    def _xml_to_hl7_string(self, xml_element: Element) -> str:
        """Convert XML Element to HL7 string."""
        # This is a simplified reverse transformation
        # In a real system, this would be much more complex
        
        lines: List[str] = []
        
        # Generate MSH segment
        msh_line = "MSH|^~\\&|DEMO|SYSTEM|TARGET|SYSTEM|" + \
                  datetime.now().strftime("%Y%m%d%H%M") + "||ADT^A01^ADT_A01|" + \
                  str(hash(xml_element.get('timestamp', '')) % 10000) + "|P|2.5"
        lines.append(msh_line)
        
        # Extract patient info
        patient = xml_element.find("Patient")
        if patient is not None:
            pid_parts: List[str] = ["PID", "1", ""]
            
            # Patient ID
            patient_id = patient.find("PatientId")
            pid_parts.append(patient_id.text if patient_id is not None and patient_id.text else "")
            pid_parts.append("")
            
            # Patient name
            last_name = patient.find("LastName")
            first_name = patient.find("FirstName")
            if last_name is not None and first_name is not None and last_name.text and first_name.text:
                name = f"{last_name.text}^{first_name.text}"
            else:
                name = ""
            pid_parts.append(name)
            
            lines.append("|".join(pid_parts))
        
        return "\n".join(lines)
    
    def _process_custom_segments(self, parent: Element, hl7_message: HL7Message, config: Dict[str, Any]) -> None:
        """Process custom Z-segments (Meditech-style segments)."""
        custom_elem = SubElement(parent, "CustomSegments")
        
        for section_name, section_config in config.items():
            section_elem = SubElement(custom_elem, self._camel_case(section_name))
            
            for field_name, field_config in section_config.items():
                field_config = cast(Dict[str, Any], field_config)
                value = self._extract_field_value(hl7_message, field_config)
                if value or field_config.get('required', False):
                    field_elem = SubElement(section_elem, self._camel_case(field_name))
                    field_elem.text = value or ""
    
    def _process_message_header(self, parent: Element, hl7_message: HL7Message, config: Dict[str, Any]) -> None:
        """Process message header section."""
        header_elem = SubElement(parent, "MessageHeader")
        
        for field_name, field_config in config.items():
            field_config = cast(Dict[str, Any], field_config)
            value = self._extract_field_value(hl7_message, field_config)
            if value or field_config.get('required', False):
                field_elem = SubElement(header_elem, self._camel_case(field_name))
                field_elem.text = value or ""
    
    def _process_patient(self, parent: Element, hl7_message: HL7Message, config: Dict[str, Any]) -> None:
        """Process patient information section."""
        patient_elem = SubElement(parent, "Patient")
        
        for field_name, field_config in config.items():
            field_config = cast(Dict[str, Any], field_config)
            if 'source' in field_config:
                # Simple field
                value = self._extract_field_value(hl7_message, field_config)
                if value or field_config.get('required', False):
                    field_elem = SubElement(patient_elem, self._camel_case(field_name))
                    field_elem.text = value or ""
            else:
                # Nested object (like address)
                nested_elem = SubElement(patient_elem, self._camel_case(field_name))
                for nested_field, nested_config in field_config.items():
                    nested_config = cast(Dict[str, Any], nested_config)
                    if 'source' in nested_config:
                        value = self._extract_field_value(hl7_message, nested_config)
                        if value or nested_config.get('required', False):
                            nested_field_elem = SubElement(nested_elem, self._camel_case(nested_field))
                            nested_field_elem.text = value or ""
    
    def _process_visit(self, parent: Element, hl7_message: HL7Message, config: Dict[str, Any]) -> None:
        """Process visit information section."""
        visit_elem = SubElement(parent, "Visit")
        
        for field_name, field_config in config.items():
            field_config = cast(Dict[str, Any], field_config)
            if 'source' in field_config:
                # Simple field
                value = self._extract_field_value(hl7_message, field_config)
                if value or field_config.get('required', False):
                    field_elem = SubElement(visit_elem, self._camel_case(field_name))
                    field_elem.text = value or ""
            else:
                # Nested object (like location or attending_doctor)
                nested_elem = SubElement(visit_elem, self._camel_case(field_name))
                for nested_field, nested_config in field_config.items():
                    nested_config = cast(Dict[str, Any], nested_config)
                    if 'source' in nested_config:
                        value = self._extract_field_value(hl7_message, nested_config)
                        if value or nested_config.get('required', False):
                            nested_field_elem = SubElement(nested_elem, self._camel_case(nested_field))
                            nested_field_elem.text = value or ""
    
    def _process_array_section(self, parent: Element, hl7_message: HL7Message, section_name: str, config: Dict[str, Any]) -> None:
        """Process array sections like allergies and diagnoses."""
        section_elem = SubElement(parent, self._camel_case(section_name))
        
        segment_type = config.get('source')
        if not segment_type:
            return
        
        segments = hl7_message.get_segments(segment_type)
        
        for segment in segments:
            item_elem = SubElement(section_elem, self._camel_case(section_name[:-1]))  # Remove 's' for singular
            
            fields_config = config.get('fields', {})
            for field_name, field_config in fields_config.items():
                field_config = cast(Dict[str, Any], field_config)
                if 'source' in field_config:
                    # Extract value from current segment
                    field_reference = cast(str, field_config['source'])
                    # Replace segment type with current segment data
                    segment_fields = segment.fields
                    field_parts = field_reference.split('.')
                    
                    if len(field_parts) >= 2:
                        field_index = int(field_parts[1])
                        component_index = int(field_parts[2]) if len(field_parts) > 2 else 1
                        
                        if field_index <= len(segment_fields):
                            field_value = segment_fields[field_index - 1] if field_index > 0 else ""
                            if component_index > 1 and field_value:
                                components = field_value.split('^')
                                field_value = components[component_index - 1] if component_index <= len(components) else ""
                            
                            if field_value:
                                field_elem = SubElement(item_elem, self._camel_case(field_name))
                                field_elem.text = field_value
    
    def _process_obx_section(self, parent: Element, hl7_message: HL7Message, section_name: str, config: Dict[str, Any]) -> None:
        """Process OBX segments with filtering based on observation IDs."""
        section_elem = SubElement(parent, self._camel_case(section_name))
        
        obx_segments = hl7_message.get_segments('OBX')
        filter_config = config.get('filter', {})
        observation_ids = filter_config.get('observation_id', [])
        
        for segment in obx_segments:
            # Check if this OBX segment matches our filter
            if len(segment.fields) > 3:
                observation_id = segment.fields[3].split('^')[0] if segment.fields[3] else ""
                
                if not observation_ids or observation_id in observation_ids:
                    item_elem = SubElement(section_elem, self._camel_case(section_name[:-1]) if section_name.endswith('s') else self._camel_case(section_name))
                    
                    fields_config = config.get('fields', {})
                    for field_name, field_config in fields_config.items():
                        field_config = cast(Dict[str, Any], field_config)
                        if 'source' in field_config:
                            field_reference = cast(str, field_config['source'])
                            field_parts = field_reference.split('.')
                            
                            if len(field_parts) >= 2:
                                field_index = int(field_parts[1])
                                component_index = int(field_parts[2]) if len(field_parts) > 2 else 1
                                
                                if field_index <= len(segment.fields):
                                    field_value = segment.fields[field_index - 1] if field_index > 0 else ""
                                    if component_index > 1 and field_value:
                                        components = field_value.split('^')
                                        field_value = components[component_index - 1] if component_index <= len(components) else ""
                                    
                                    if field_value:
                                        field_elem = SubElement(item_elem, self._camel_case(field_name))
                                        field_elem.text = field_value
    
    def _extract_field_value(self, hl7_message: HL7Message, field_config: Dict[str, Any]) -> Optional[str]:
        """Extract field value from HL7 message based on field configuration."""
        source = field_config.get('source')
        if not source:
            return None
        
        value = hl7_message.get_field_value(source)
        if not value:
            return None
        
        # Apply formatting based on field type
        field_type = field_config.get('type', 'string')
        field_format = field_config.get('format')
        
        if field_type == 'date' and field_format:
            return HL7Parser.format_date(value, field_format)
        elif field_type == 'datetime' and field_format:
            return HL7Parser.format_date(value, field_format)
        
        return value
    
    def _camel_case(self, snake_str: str) -> str:
        """Convert snake_case to CamelCase."""
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    def _format_xml(self, xml_element: Element) -> str:
        """Format XML with proper indentation."""
        xml_string = tostring(xml_element, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")
    
    def get_transformation_summary(self, output_base_dir: str) -> Dict[str, Any]:
        """Get summary of transformation results."""
        hl7_output_dir = os.path.join(output_base_dir, 'hl7_output')
        xml_output_dir = os.path.join(output_base_dir, 'xml_output')
        
        hl7_files = glob.glob(os.path.join(hl7_output_dir, '*')) if os.path.exists(hl7_output_dir) else []
        xml_files = glob.glob(os.path.join(xml_output_dir, '*')) if os.path.exists(xml_output_dir) else []
        
        summary = {
            'files_processed': len(hl7_files) + len(xml_files),
            'hl7_files': len(hl7_files),
            'xml_files': len(xml_files),
            'output_format': self.output_format,
            'input_format': self.input_format,
            'config_name': self.mapping_config.get('config_name', 'default'),
            'timestamp': datetime.now().isoformat(),
            'output_files': [os.path.basename(f) for f in hl7_files + xml_files]
        }
        
        return summary


def main() -> None:
    """Main function to run the transformer."""
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    config_path = os.path.join(project_root, 'config', 'inbound_config.json')
    input_dir = os.path.join(project_root, 'data', 'input')
    output_dir = os.path.join(project_root, 'data', 'output')
    
    try:
        # Create transformer
        transformer = BidirectionalTransformer(config_path)
        
        print("🔄 Healthcare Interface Transformation Demo")
        print("=" * 50)
        print(f"Input Format:  {transformer.input_format.upper()}")
        print(f"Output Format: {transformer.output_format.upper()}")
        print(f"Config:        {transformer.mapping_config.get('config_name', 'default')}")
        print()
        
        # Process all files in input directory
        processed_files = transformer.process_directory(input_dir, output_dir)
        
        if processed_files:
            print(f"✅ Successfully processed {len(processed_files)} files:")
            for file in processed_files:
                print(f"   📄 {os.path.basename(file)}")
            
            # Get and display summary
            summary = transformer.get_transformation_summary(output_dir)
            print(f"\n📊 Transformation Summary:")
            print(f"   Files processed: {summary['files_processed']}")
            print(f"   Configuration: {summary['config_name']}")
            print(f"   Completed: {summary['timestamp']}")
            
        else:
            print("⚠️  No files were processed. Check input directory and file formats.")
        
    except TransformationError as e:
        print(f"❌ Transformation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 