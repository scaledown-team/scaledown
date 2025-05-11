#!/usr/bin/env python3
"""
Test script for ScaleDown package
"""

import sys
import os
import json

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import from the local modules
from scaledown.api import ScaleDown
from scaledown.templates import Template, TemplateManager, get_default_manager
from scaledown.styles import Style, StyleManager, get_default_style_manager

# Create the ScaleDown instance manually
sd = ScaleDown()


def print_separator(text=""):
    """Print a separator line with optional text."""
    width = 80
    if text:
        padding = (width - len(text) - 2) // 2
        print('=' * padding + f" {text} " + '=' * padding)
    else:
        print('=' * width)

def test_templates():
    """Test template functionality."""
    print_separator("TEMPLATES")
    
    # List all templates
    templates = sd.load("templates")
    print(f"Found {len(templates)} templates:")
    for i, template in enumerate(templates[:5]):  # Show first 5
        print(f"{i+1}. [{template['id']}] {template['title']}")
        print(f"   {template['description']}")
    
    if len(templates) > 5:
        print(f"... and {len(templates) - 5} more")
    
    print()
    
    # Select a template
    template_id = "writing-1"  # Blog Post Intro
    print(f"Selecting template: {template_id}")
    template = sd.sd.select_template(template_id)
    print(f"Selected: {template.title}")
    print(f"Template text: {template.template_text}")
    print(f"Placeholders: {template.placeholders}")
    
    # Set values
    values = {"topic": "AI prompt optimization"}
    print(f"\nSetting values: {json.dumps(values)}")
    sd.sd.set_values(values)
    
    # Render the template
    prompt = sd.sd.get_prompt()
    print(f"\nRendered prompt: {prompt}")

def test_styles():
    """Test style functionality."""
    print_separator("STYLES")
    
    # List all styles
    styles = sd.sd.load("styles")
    print(f"Found {len(styles)} styles:")
    for style in styles:
        print(f"[{style['id']}] {style['name']}: {style['description']}")
    
    print()
    
    # Test each style
    for style in styles:
        print(f"Testing style: {style['name']}")
        sd.sd.select_style(style['id'])
        prompt = sd.sd.get_prompt()
        print(f"Styled prompt: {prompt}")
        print()

def test_expert_mode():
    """Test expert mode functionality."""
    print_separator("EXPERT MODE")
    
    # List domains and roles
    domains = sd.sd.load("expert_domains")
    roles = sd.sd.load("expert_roles")
    
    print("Available Domains:")
    for domain in domains[:5]:  # Show first 5
        print(f"- {domain['name']}")
    
    print("\nAvailable Roles:")
    for role in roles[:5]:  # Show first 5
        print(f"- {role['name']}")
    
    # Create an expert style
    domain = "Technology"
    role = "Consultant"
    print(f"\nCreating expert style: {domain} {role}")
    
    expert_style = sd.sd.create_expert_style(domain, role, expertise_level=85)
    print(f"Created style: {expert_style.name}")
    print(f"Description: {expert_style.description}")
    print(f"Modifier: {expert_style.template_modifier}")
    
    # Get prompt with expert style
    prompt = sd.sd.get_prompt()
    print(f"\nExpert prompt: {prompt}")

def test_optimization():
    """Test mock optimization."""
    print_separator("MOCK OPTIMIZATION")
    
    # Try different templates and styles
    templates_to_test = [
        ("writing-1", {"topic": "AI prompt optimization"}, "standard"),
        ("business-1", {"subject": "Meeting request"}, "concise"),
        ("technical-1", {"code": "def hello_world():\n    print('Hello, world!')"}, "detailed"),
        ("creative-1", {"sentence": "The door creaked open slowly."}, "creative")
    ]
    
    for template_id, values, style_id in templates_to_test:
        print(f"Testing template '{template_id}' with style '{style_id}'")
        
        # Select template and set values
        sd.sd.select_template(template_id)
        sd.sd.set_values(values)
        sd.sd.select_style(style_id)
        
        # Get original prompt
        prompt = sd.sd.get_prompt()
        print(f"Original prompt: {prompt}")
        
        # Mock optimize
        result = sd.sd.mock_optimize()
        print(f"Optimized prompt: {result['optimized']}")
        print(f"Words saved: {result['saved_tokens']} ({result['saved_percentage']:.1f}%)")
        print()

def main():
    """Run all tests."""
    print_separator("SCALEDOWN TESTING")
    print("This script tests the basic functionality of the ScaleDown package\n")
    
    test_templates()
    test_styles()
    test_expert_mode()
    test_optimization()
    
    print_separator("TESTING COMPLETE")

if __name__ == "__main__":
    main()