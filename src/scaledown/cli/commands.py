import click
import json
from scaledown import sd

@click.group()
def cli():
    """ScaleDown CLI tool for optimizing AI prompts."""
    pass

@cli.command()
@click.argument('item_type', type=click.Choice(['templates', 'styles', 'models', 'expert_domains', 'expert_roles']))
def list(item_type):
    """List available templates, styles, or models."""
    items = sd.load(item_type)
    
    if not items:
        click.echo(f"No {item_type} found.")
        return
    
    click.echo(f"Available {item_type}:")
    for item in items:
        if item_type == 'templates':
            click.echo(f"[{item['id']}] {item['title']}")
            click.echo(f"  {item['description']}")
        else:
            click.echo(f"[{item['id']}] {item['name']}")
            click.echo(f"  {item['description']}")
        click.echo("")

@cli.command()
@click.argument('template_id')
@click.option('--style', '-s', help='Style ID to apply')
@click.option('--values', '-v', help='JSON string of placeholder values')
@click.option('--expert-domain', '-d', help='Expert domain for expert mode')
@click.option('--expert-role', '-r', help='Expert role for expert mode')
def render(template_id, style, values, expert_domain, expert_role):
    """Render a template with the given style and values."""
    try:
        # Select template
        sd.select_template(template_id)
        
        # Set values if provided
        values_dict = {}
        if values:
            try:
                values_dict = json.loads(values)
            except json.JSONDecodeError:
                click.echo("Invalid JSON format for values")
                return
        
        # Check for missing values
        missing = [p for p in sd.current_template.placeholders if p not in values_dict]
        if missing:
            click.echo(f"Missing values for placeholders: {', '.join(missing)}")
            for placeholder in missing:
                value = click.prompt(f"Enter value for [{placeholder}]", type=str)
                values_dict[placeholder] = value
        
        # Set values
        sd.set_values(values_dict)
        
        # Set style
        if expert_domain and expert_role:
            # Create and select expert style
            sd.create_expert_style(expert_domain, expert_role)
            click.echo(f"Created expert style: {expert_domain} {expert_role}")
        elif style:
            sd.select_style(style)
            click.echo(f"Selected style: {style}")
        
        # Generate prompt
        prompt = sd.get_prompt()
        click.echo("\nGenerated prompt:")
        click.echo(prompt)
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}")

@cli.command()
@click.argument('template_id')
@click.option('--style', '-s', help='Style ID to apply')
@click.option('--values', '-v', help='JSON string of placeholder values')
def mock_optimize(template_id, style, values):
    """Mock-optimize a prompt (for testing without models)."""
    try:
        # Select template
        sd.select_template(template_id)
        
        # Set values if provided
        values_dict = {}
        if values:
            try:
                values_dict = json.loads(values)
            except json.JSONDecodeError:
                click.echo("Invalid JSON format for values")
                return
        
        # Check for missing values
        missing = [p for p in sd.current_template.placeholders if p not in values_dict]
        if missing:
            click.echo(f"Missing values for placeholders: {', '.join(missing)}")
            for placeholder in missing:
                value = click.prompt(f"Enter value for [{placeholder}]", type=str)
                values_dict[placeholder] = value
        
        # Set values
        sd.set_values(values_dict)
        
        # Set style
        if style:
            sd.select_style(style)
            click.echo(f"Selected style: {style}")
        
        # Generate prompt
        prompt = sd.get_prompt()
        click.echo("\nOriginal prompt:")
        click.echo(prompt)
        
        # Mock optimize
        result = sd.mock_optimize()
        click.echo("\nMock-optimized prompt:")
        click.echo(result["optimized"])
        
        click.echo(f"\nOriginal word count: {result['original_tokens']}")
        click.echo(f"Optimized word count: {result['optimized_tokens']}")
        click.echo(f"Words saved: {result['saved_tokens']} ({result['saved_percentage']:.1f}%)")
        
    except ValueError as e:
        click.echo(f"Error: {str(e)}")