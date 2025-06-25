#!/usr/bin/env python3
"""
Demo Setup Script

This script prepares and demonstrates the current state of our HL7 transformation
system and shows what we'll enhance during the live demo.
"""

import os
import sys
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from transformer import HL7ToXMLTransformer

def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n--- {title} ---")

def show_current_system() -> None:
    """Demonstrate the current working system."""
    print_header("Current HL7 to XML Transformation System")
    print("✅ WORKING: Basic field mapping with JSON configuration")
    print("✅ WORKING: Type-aware transformations (dates, strings)")
    print("✅ WORKING: Nested XML structure generation")
    print("✅ WORKING: Comprehensive test coverage (17 tests passing)")
    
    print_section("Current Capabilities")
    
    # Show current config structure
    with open("config/mapping.json", 'r') as f:
        config = json.load(f)
    
    print("Current mapping structure:")
    patient_fields = list(config['mappings']['patient'].keys())[:5]
    for field in patient_fields:
        field_config = config['mappings']['patient'][field]
        if isinstance(field_config, dict) and 'source' in field_config:
            print(f"  {field:15} -> {field_config['source']:10} ({field_config.get('type', 'string')})") #type: ignore[arg-type]
    print("  ... and more")
    
    print_section("Sample Transformation")
    
    # Run current transformation
    transformer = HL7ToXMLTransformer("config/mapping.json")
    transformer.transform_file(
        "data/input/sample_adt_a01.hl7", 
        "data/output/current_demo.xml"
    )
    
    # Show sample output
    with open("data/output/current_demo.xml", 'r') as f:
        lines = f.readlines()
    
    print("Generated XML (first 15 lines):")
    for i, line in enumerate(lines[:15], 1):
        print(f"{i:2d}: {line.rstrip()}")
    print("...")

def show_demo_scenarios() -> None:
    """Show what we'll implement during the live demo."""
    print_header("Live Demo Scenarios - What We'll Add")
    
    print_section("Scenario 1: Multi-Panel Lab Processing")
    print("🎯 GOAL: Process 16 lab results, group by panels")
    print("📝 REQUEST: 'Group OBX results by test panels (CBC, BMP, Lipid)'")
    print("⚙️  IMPLEMENTATION: Add repeating segment handling")
    print("🧪 TEST: 3 panels with proper result grouping")
    print()
    print("Data: ORU^R01 message with 16 lab results")
    print("- CBC: WBC, RBC, HGB, HCT, PLT")
    print("- BMP: Glucose, BUN, Creatinine, Electrolytes")  
    print("- Lipid: Total Chol, HDL, LDL, Triglycerides")
    
    print_section("Scenario 2: Critical Value Detection")
    print("🎯 GOAL: Intelligent alerts for critical lab values")
    print("📝 REQUEST: 'Flag critical values with severity scoring'")
    print("⚙️  IMPLEMENTATION: Custom Python functions + business rules")
    print("🧪 TEST: Critical thresholds (WBC >30/<1, Glucose >400/<40)")
    print()
    print("Features: Severity scoring, immediate notification flags")
    
    print_section("Scenario 3: Clinical Interpretation Engine")
    print("🎯 GOAL: Generate cardiovascular & diabetes risk assessments")
    print("📝 REQUEST: 'Clinical interpretations from lab panels'")
    print("⚙️  IMPLEMENTATION: Multi-field calculations + narrative generation")
    print("🧪 TEST: HIGH cardiovascular risk, HIGH diabetes risk")
    print()
    print("Algorithms: Cardiovascular risk scoring, diabetes assessment")

def show_failing_tests() -> None:
    """Show the tests that will pass once we implement features."""
    print_header("Pre-Written Tests (Currently Failing)")
    print("We've written tests for features that don't exist yet.")
    print("During the demo, we'll implement the features and watch tests turn green!")
    
    print_section("Running Demo Scenario Tests")
    
    # Run the failing tests
    os.system("python -m pytest tests/test_demo_scenarios.py -v --tb=short")

def show_documentation():
    """Show the configuration rules documentation."""
    print_header("Enhanced Configuration Documentation")
    print("📖 See CONFIG_RULES.md for complete documentation of new features")
    
    with open("CONFIG_RULES.md", 'r') as f:
        lines = f.readlines()
    
    # Show first part of documentation
    print("\nDocumentation preview:")
    for line in lines[:20]:
        print(line.rstrip())
    print("... (see CONFIG_RULES.md for complete documentation)")

def main():
    """Main demo setup function."""
    print_header("HL7 Interface Configuration Demo Setup")
    print("This demo shows how AI assistance transforms interface development")
    print("from hours/days of work into minutes of configuration changes.")
    
    show_current_system()
    show_demo_scenarios()
    show_failing_tests()
    show_documentation()
    
    print_header("Demo Ready!")
    print("🎬 LIVE DEMO PLAN:")
    print("   1. Show current working system")
    print("   2. Take 'change requests' from audience")
    print("   3. Implement features live with AI assistance")
    print("   4. Watch tests turn green")
    print("   5. Show immediate business value")
    
    print("\n🚀 Key Message: What used to take hours now takes minutes")
    print("💡 AI doesn't replace expertise - it amplifies it")

if __name__ == "__main__":
    main() 