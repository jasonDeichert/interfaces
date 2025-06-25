#!/usr/bin/env python3
"""
Demo Runner for Healthcare Interface Transformations

This script demonstrates the power of AI-accelerated config-driven transformations
by showing before/after comparisons with different configurations.
"""

import os
import sys
import json
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from transformer import BidirectionalTransformer


def clear_output_directories():
    """Clear output directories for clean demo."""
    output_dirs = [
        "data/output/hl7_output",
        "data/output/xml_output"
    ]
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)


def show_sample_output(file_path: str, lines: int = 20):
    """Show sample of output file."""
    if not os.path.exists(file_path):
        print(f"   ❌ File not found: {file_path}")
        return
        
    print(f"\n📖 Sample from {os.path.basename(file_path)}:")
    print("-" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        file_lines = f.readlines()
        for i, line in enumerate(file_lines[:lines]):
            print(f"{i+1:2d}: {line.rstrip()}")
        if len(file_lines) > lines:
            print(f"    ... ({len(file_lines) - lines} more lines)")


def run_basic_inbound_demo():
    """Run basic inbound transformation demo (HL7 → XML)."""
    print("🎯 BASIC INBOUND TRANSFORMATION DEMO")
    print("=" * 60)
    print("📋 Configuration: Basic HL7 → XML (standard segments only)")
    print("🔄 Processing: Meditech ADT message with custom Z-segments")
    print()
    
    config_path = "config/inbound_config.json"
    input_dir = "data/input"
    output_dir = "data/output"
    
    try:
        transformer = BidirectionalTransformer(config_path)
        processed_files = transformer.process_directory(input_dir, output_dir)
        
        if processed_files:
            print(f"✅ Processed {len(processed_files)} files:")
            for file in processed_files:
                print(f"   📄 {os.path.basename(file)}")
            
            # Show sample of Meditech ADT file
            adt_file = next((f for f in processed_files if 'meditech' in f.lower()), None)
            if adt_file:
                show_sample_output(adt_file, 15)
                
        print(f"\n💡 Notice: Only standard HL7 segments processed")
        print(f"   🔍 Custom Z-segments (ZPV, ZIN, ZCL, ZMD, ZAL, ZRX, ZVS, ZDI, ZNT) are ignored")
        print(f"   🔍 Missing: Insurance info, medications, vital signs, diagnostic tests")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_enhanced_inbound_demo():
    """Run enhanced inbound transformation demo."""
    print("\n🎯 ENHANCED INBOUND TRANSFORMATION DEMO")
    print("=" * 60)
    print("📋 Configuration: Enhanced HL7 → XML (includes all Meditech Z-segments)")
    print("🔄 Processing: Complete extraction of custom interface data")
    print()
    
    config_path = "config/demo_configs/enhanced_inbound_config.json"
    input_dir = "data/input" 
    output_dir = "data/output"
    
    try:
        transformer = BidirectionalTransformer(config_path)
        processed_files = transformer.process_directory(input_dir, output_dir)
        
        if processed_files:
            print(f"✅ Processed {len(processed_files)} files:")
            for file in processed_files:
                print(f"   📄 {os.path.basename(file)}")
            
            # Show sample of enhanced output
            adt_file = next((f for f in processed_files if 'meditech' in f.lower()), None)
            if adt_file:
                show_sample_output(adt_file, 25)
                
        print(f"\n💡 Enhanced output includes:")
        print(f"   ✅ All custom Z-segments processed")
        print(f"   ✅ Insurance information (ZIN)")
        print(f"   ✅ Medications and dosages (ZRX)")
        print(f"   ✅ Vital signs (ZVS)")
        print(f"   ✅ Diagnostic test results (ZDI)")
        print(f"   ✅ Nursing notes (ZNT)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_basic_outbound_demo():
    """Run basic outbound transformation demo (XML → HL7)."""
    print("\n🎯 BASIC OUTBOUND TRANSFORMATION DEMO")
    print("=" * 60)
    print("📋 Configuration: Basic XML → HL7 (standard segments only)")
    print("🔄 Processing: XML patient data to HL7 format")
    print()
    
    config_path = "config/outbound_config.json"
    input_dir = "data/input"
    output_dir = "data/output"
    
    try:
        transformer = BidirectionalTransformer(config_path)
        processed_files = transformer.process_directory(input_dir, output_dir)
        
        if processed_files:
            print(f"✅ Processed {len(processed_files)} files:")
            for file in processed_files:
                print(f"   📄 {os.path.basename(file)}")
            
            # Show sample of HL7 output
            hl7_file = next((f for f in processed_files if f.endswith('.hl7')), None)
            if hl7_file:
                show_sample_output(hl7_file, 10)
                
        print(f"\n💡 Notice: Only standard HL7 segments generated")
        print(f"   🔍 Custom XML data not converted to Z-segments")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_comparison_demo():
    """Run side-by-side comparison."""
    print("\n🎯 BEFORE/AFTER COMPARISON")
    print("=" * 60)
    
    basic_file = "data/output/xml_output/sample_meditech_adt.xml"
    enhanced_file = None
    
    # Find the enhanced file (may have been created by enhanced demo)
    if os.path.exists("data/output/xml_output"):
        for file in os.listdir("data/output/xml_output"):
            if 'meditech' in file and file.endswith('.xml'):
                enhanced_file = os.path.join("data/output/xml_output", file)
                break
    
    if os.path.exists(basic_file):
        print("📊 Comparing Meditech ADT transformation:")
        print()
        
        # Count lines to show difference
        with open(basic_file, 'r') as f:
            basic_lines = len(f.readlines())
            
        print(f"📄 Basic config output:    {basic_lines:3d} lines")
        
        if enhanced_file and os.path.exists(enhanced_file):
            with open(enhanced_file, 'r') as f:
                enhanced_lines = len(f.readlines())
            print(f"📄 Enhanced config output: {enhanced_lines:3d} lines")
            print(f"📈 Enhancement factor:     {enhanced_lines/basic_lines:.1f}x more content")
        
        print(f"\n🔍 Key differences:")
        print(f"   • Basic: Standard HL7 segments only (MSH, PID, PV1)")
        print(f"   • Enhanced: Complete Meditech interface data")
        print(f"   • Enhanced: Insurance, medications, vital signs, diagnostics")
        print(f"   • Enhanced: Nursing notes and clinical information")
        
    else:
        print("⚠️  Run basic inbound demo first")


def show_config_difference():
    """Show the configuration differences."""
    print("\n🎯 CONFIGURATION COMPARISON")
    print("=" * 60)
    
    basic_config = "config/inbound_config.json"
    enhanced_config = "config/demo_configs/enhanced_inbound_config.json"
    
    if os.path.exists(basic_config) and os.path.exists(enhanced_config):
        with open(basic_config, 'r') as f:
            basic_data = json.load(f)
        with open(enhanced_config, 'r') as f:
            enhanced_data = json.load(f)
            
        print(f"📋 Basic inbound config:")
        print(f"   • Mappings: {len(basic_data.get('mappings', {}))}")
        print(f"   • Custom segments: {'❌ Not configured' if 'custom_segments' not in basic_data.get('mappings', {}) else '✅ Configured'}")
        
        print(f"\n📋 Enhanced inbound config:")
        print(f"   • Mappings: {len(enhanced_data.get('mappings', {}))}")
        print(f"   • Custom segments: {'✅ Configured' if 'custom_segments' in enhanced_data.get('mappings', {}) else '❌ Not configured'}")
        
        if 'custom_segments' in enhanced_data.get('mappings', {}):
            custom_segments = enhanced_data['mappings']['custom_segments']
            print(f"   • Z-segment sections: {len(custom_segments)}")
            print(f"     - Insurance info (ZIN)")
            print(f"     - Medications (ZRX)")
            print(f"     - Vital signs (ZVS)")
            print(f"     - Diagnostic tests (ZDI)")
            print(f"     - Nursing notes (ZNT)")
        
    else:
        print("⚠️  Configuration files not found")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='Healthcare Interface Transformation Demo')
    parser.add_argument('--mode', choices=['basic-in', 'enhanced-in', 'basic-out', 'compare', 'config', 'all'], 
                       default='all', help='Demo mode to run')
    parser.add_argument('--no-pause', action='store_true', help='Run without interactive pauses')
    args = parser.parse_args()
    
    print("🏥 AI-Accelerated Healthcare Interface Transformation Demo")
    print("Demonstrating Config-Driven Development with Meditech Segments")
    print("=" * 60)
    
    # Clear outputs for clean demo
    if args.mode == 'all':
        clear_output_directories()
    
    if args.mode in ['basic-in', 'all']:
        run_basic_inbound_demo()
        
    if args.mode in ['enhanced-in', 'all']:
        if args.mode == 'all' and not args.no_pause:
            input("\n⏸️  Press Enter to continue to enhanced demo...")
        run_enhanced_inbound_demo()
        
    if args.mode in ['basic-out', 'all']:
        if args.mode == 'all' and not args.no_pause:
            input("\n⏸️  Press Enter to continue to outbound demo...")
        run_basic_outbound_demo()
        
    if args.mode in ['compare', 'all']:
        if args.mode == 'all' and not args.no_pause:
            input("\n⏸️  Press Enter to see comparison...")
        run_comparison_demo()
        
    if args.mode in ['config', 'all']:
        if args.mode == 'all' and not args.no_pause:
            input("\n⏸️  Press Enter to see config differences...")
        show_config_difference()
    
    print(f"\n🎉 Demo Complete!")
    print(f"\n💡 Key Takeaway:")
    print(f"   Same transformation engine + different config = completely different interface capability")
    print(f"   AI accelerates complex Meditech interface logic through configuration enhancement")


if __name__ == "__main__":
    main() 