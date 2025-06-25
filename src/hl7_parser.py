"""
HL7 Message Parser Utility

This module provides utilities for parsing HL7 v2 messages and extracting
field values based on segment.field.component notation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class HL7Field:
    """Represents an HL7 field with its components and repetitions."""
    
    def __init__(self, value: str, field_separator: str = '^'):
        self.value = value
        self.field_separator = field_separator
        self.components = self._parse_components()
    
    def _parse_components(self) -> List[str]:
        """Parse field components separated by the field separator."""
        if not self.value:
            return []
        return self.value.split(self.field_separator)
    
    def get_component(self, index: int) -> Optional[str]:
        """Get component by 1-based index."""
        if index < 1 or index > len(self.components):
            return None
        return self.components[index - 1] if self.components[index - 1] else None


class HL7Segment:
    """Represents an HL7 segment with its fields."""
    
    def __init__(self, segment_line: str, field_separator: str = '|'):
        self.segment_line = segment_line.strip()
        self.field_separator = field_separator
        self.fields = self._parse_fields()
        self.segment_type = self.fields[0] if self.fields else ""
    
    def _parse_fields(self) -> List[str]:
        """Parse segment fields separated by the field separator."""
        return self.segment_line.split(self.field_separator)
    
    def get_field(self, index: int) -> Optional[HL7Field]:
        """Get field by 1-based index."""
        if index < 1 or index > len(self.fields):
            return None
        field_value = self.fields[index - 1] if index <= len(self.fields) else ""
        return HL7Field(field_value)


class HL7Message:
    """Represents a complete HL7 message with all its segments."""
    
    def __init__(self, message_text: str):
        self.message_text = message_text
        self.segments: Dict[str, List[HL7Segment]] = {}
        self.field_separator = '|'
        self.component_separator = '^'
        self.repetition_separator = '~'
        self.escape_character = '\\'
        self.subcomponent_separator = '&'
        self._parse_message()
    
    def _parse_message(self) -> None:
        """Parse the complete HL7 message into segments."""
        lines = [line.strip() for line in self.message_text.split('\n') if line.strip()]
        
        for line in lines:
            if not line:
                continue
                
            segment = HL7Segment(line, self.field_separator)
            segment_type = segment.segment_type
            
            if segment_type not in self.segments:
                self.segments[segment_type] = []
            
            self.segments[segment_type].append(segment)
            
            # Extract encoding characters from MSH segment
            if segment_type == 'MSH' and len(segment.fields) > 1:
                encoding_chars = segment.fields[1]
                if len(encoding_chars) >= 4:
                    self.component_separator = encoding_chars[0]
                    self.repetition_separator = encoding_chars[1]
                    self.escape_character = encoding_chars[2]
                    self.subcomponent_separator = encoding_chars[3]
    
    def get_segments(self, segment_type: str) -> List[HL7Segment]:
        """Get all segments of a specific type."""
        return self.segments.get(segment_type, [])
    
    def get_segment(self, segment_type: str, index: int = 0) -> Optional[HL7Segment]:
        """Get a specific segment by type and index (0-based)."""
        segments = self.get_segments(segment_type)
        if index < len(segments):
            return segments[index]
        return None
    
    def get_field_value(self, field_reference: str) -> Optional[str]:
        """
        Get field value using HL7 field reference notation (e.g., 'PID.5.1').
        
        Args:
            field_reference: Field reference in format 'SEGMENT.FIELD.COMPONENT'
        
        Returns:
            Field value as string or None if not found
        """
        parts = field_reference.split('.')
        if len(parts) < 2:
            return None
        
        segment_type = parts[0]
        field_index = int(parts[1])
        component_index = int(parts[2]) if len(parts) > 2 else 1
        
        segment = self.get_segment(segment_type)
        if not segment:
            return None
        
        field = segment.get_field(field_index)
        if not field:
            return None
        
        if len(parts) > 2:
            return field.get_component(component_index)
        else:
            return field.value
    
    def get_all_segments_values(self, segment_type: str) -> List[Dict[str, Any]]:
        """Get all segments of a type as a list of dictionaries."""
        segments = self.get_segments(segment_type)
        result: List[Dict[str, Any]] = []
        
        for segment in segments:
            segment_data = {
                'segment_type': segment.segment_type,
                'fields': segment.fields
            }
            result.append(segment_data)
        
        return result


class HL7Parser:
    """Main parser class for HL7 messages."""
    
    @staticmethod
    def parse(message_text: str) -> HL7Message:
        """Parse an HL7 message from text."""
        return HL7Message(message_text)
    
    @staticmethod
    def parse_from_file(file_path: str) -> HL7Message:
        """Parse an HL7 message from a file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return HL7Parser.parse(file.read())
    
    @staticmethod
    def format_date(date_string: str, input_format: str = "YYYYMMDD") -> Optional[str]:
        """Format HL7 date string to ISO format."""
        if not date_string:
            return None
        
        try:
            if input_format == "YYYYMMDD" and len(date_string) == 8:
                dt = datetime.strptime(date_string, "%Y%m%d")
                return dt.strftime("%Y-%m-%d")
            elif input_format == "YYYYMMDDHHMM" and len(date_string) == 12:
                dt = datetime.strptime(date_string, "%Y%m%d%H%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            else:
                return date_string
        except ValueError:
            return date_string
    
    @staticmethod
    def validate_message(message: HL7Message) -> List[str]:
        """Validate HL7 message structure and return list of errors."""
        errors: List[str] = []
        
        # Check for required MSH segment
        if not message.get_segment('MSH'):
            errors.append("Missing required MSH segment")
        
        # Check for required PID segment for ADT messages
        msh = message.get_segment('MSH')
        if msh:
            message_type = msh.get_field(9)
            if message_type and 'ADT' in message_type.value:
                if not message.get_segment('PID'):
                    errors.append("Missing required PID segment for ADT message")
        
        return errors 