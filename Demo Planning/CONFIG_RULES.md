# Interface Configuration Rules & Capabilities

## Overview
This document describes the enhanced configuration capabilities for our HL7 to XML transformation engine, including Python function injection, filtering, and advanced field mapping.

## Basic Field Mapping
```json
"field_name": {
  "source": "PID.6.1",
  "type": "string",
  "required": true
}
```

## Python Function Injection
You can inject Python code directly into field mappings for custom transformations:

```json
"formatted_name": {
  "source": "PID.6.1",
  "type": "string",
  "python_transform": "value.title() if value else None",
  "required": false
}
```

### Available Variables in Python Context:
- `value`: The extracted field value
- `message`: The full HL7Message object
- `field_config`: The current field configuration

### Common Python Transformations:
```json
// Age calculation from date of birth
"age": {
  "source": "PID.8",
  "type": "integer", 
  "python_transform": "calculate_age(value) if value else None"
}

// Conditional field based on patient class
"insurance_required": {
  "source": "PV1.2",
  "type": "boolean",
  "python_transform": "value == 'I'"  // Inpatient only
}

// Name formatting with suffix handling
"full_name": {
  "source": "PID.6",
  "type": "string",
  "python_transform": "format_patient_name(value)"
}
```

## Source-Level Filtering
Filter records at the source level before transformation. If a source is filtered out, the system moves to the next available source.

```json
"mappings": {
  "patient": {
    "source_filters": [
      {
        "field": "PID.4.1",
        "condition": "not_starts_with",
        "value": "TEST"
      },
      {
        "field": "PID.8", 
        "condition": "date_age_greater_than",
        "value": 18
      }
    ],
    "fields": {
      // ... field mappings
    }
  }
}
```

### Available Filter Conditions:
- `equals`, `not_equals`
- `starts_with`, `not_starts_with`
- `contains`, `not_contains`
- `greater_than`, `less_than`
- `date_age_greater_than`, `date_age_less_than`
- `regex_match`, `regex_not_match`

## Global Filters
Apply filters across all transformations:

```json
"global_filters": [
  {
    "field": "MSH.3",
    "condition": "not_equals", 
    "value": "TEST_SYSTEM"
  }
]
```

## Conditional Field Mapping
Include/exclude fields based on conditions:

```json
"ssn": {
  "source": "PID.20",
  "type": "string",
  "required": false,
  "include_if": {
    "field": "PV1.2",
    "condition": "equals",
    "value": "I"  // Only for inpatients
  }
}
```

## Multiple Source Fallback
Define fallback sources if primary source is unavailable:

```json
"patient_id": {
  "sources": [
    "PID.4.1",    // Primary: Medical Record Number
    "PID.3.1",    // Fallback: Patient Account Number  
    "PID.2.1"     // Last resort: Patient ID
  ],
  "type": "string",
  "required": true
}
```

## Validation Rules
Add validation to ensure data quality:

```json
"phone_number": {
  "source": "PID.14.1",
  "type": "string",
  "validation": {
    "regex": "^\\(\\d{3}\\)\\d{3}-\\d{4}$",
    "error_message": "Phone must be in format (XXX)XXX-XXXX"
  }
}
```

## Custom Python Functions
Define reusable functions in the configuration:

```json
"custom_functions": {
  "calculate_age": "lambda dob: (datetime.now() - datetime.strptime(dob, '%Y%m%d')).days // 365 if dob else None",
  "format_patient_name": "lambda name_field: ' '.join([comp.title() for comp in name_field.split('^') if comp]) if name_field else None",
  "is_test_patient": "lambda patient_id: patient_id and patient_id.upper().startswith('TEST')"
}
```

## Error Handling
Configure how to handle transformation errors:

```json
"error_handling": {
  "on_missing_required": "error",     // "error", "warn", "skip"
  "on_validation_fail": "warn",       // "error", "warn", "skip" 
  "on_python_error": "skip",          // "error", "warn", "skip"
  "log_level": "info"
}
```

## Usage Examples

### Example 1: Adult Inpatient Insurance Processing
```json
"insurance_info": {
  "source_filters": [
    {"field": "PV1.2", "condition": "equals", "value": "I"},
    {"field": "PID.8", "condition": "date_age_greater_than", "value": 18}
  ],
  "fields": {
    "policy_number": {"source": "IN1.2.1", "type": "string"},
    "carrier_name": {"source": "IN1.4.1", "type": "string"}
  }
}
```

### Example 2: Smart Name Formatting
```json
"patient_name": {
  "source": "PID.6",
  "type": "string", 
  "python_transform": "format_patient_name(value)",
  "validation": {
    "min_length": 2,
    "error_message": "Patient name must be at least 2 characters"
  }
}
```

This configuration system allows for complex business logic while maintaining readability and maintainability. 