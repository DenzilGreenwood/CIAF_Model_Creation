"""
CIAF Vault CLI - Command-line tool for vault management.
"""

import click
import json
from tabulate import tabulate
from ciaf.vault.authentication import APIKeyManager
from ciaf.vault.core import VaultManager


@click.group()
def cli():
    """CIAF Vault Management CLI"""
    pass


# ============================================================================
# ORGANIZATION COMMANDS
# ============================================================================

@cli.group()
def org():
    """Manage organizations."""
    pass


@org.command()
@click.argument("org_id")
@click.argument("name")
def create(org_id: str, name: str):
    """Create new organization."""
    auth = APIKeyManager()
    org = auth.create_organization(org_id, name)
    click.secho(f"✓ Organization created: {org_id}", fg="green")
    click.echo(f"  Name: {org.name}")
    click.echo(f"  Created: {org.created_at}")


@org.command()
@click.argument("org_id")
def show(org_id: str):
    """Show organization details."""
    auth = APIKeyManager()
    org = auth.get_organization(org_id)

    if not org:
        click.secho(f"✗ Organization not found: {org_id}", fg="red")
        return

    click.echo(json.dumps({
        "org_id": org.org_id,
        "name": org.name,
        "created_at": org.created_at,
        "api_key_count": org.api_key_count,
        "last_activity": org.last_activity
    }, indent=2))


# ============================================================================
# API KEY COMMANDS
# ============================================================================

@cli.group()
def key():
    """Manage API keys."""
    pass


@key.command()
@click.argument("org_id")
@click.option("--expires-in", default=None, type=int, help="Expires in N days")
@click.option("--description", default="", help="Key description")
def create(org_id: str, expires_in: int, description: str):
    """Create new API key for organization."""
    auth = APIKeyManager()

    # Verify org exists
    if not auth.get_organization(org_id):
        click.secho(f"✗ Organization not found: {org_id}", fg="red")
        return

    raw_key, key_obj = auth.create_api_key(
        org_id,
        description=description,
        expires_in_days=expires_in
    )

    click.secho("✓ API key created", fg="green")
    click.secho("⚠️  SAVE THIS KEY - It will not be shown again:", fg="yellow")
    click.echo("")
    click.secho(raw_key, fg="cyan", bold=True)
    click.echo("")
    click.echo(f"  Key ID: {key_obj.key_id}")
    click.echo(f"  Prefix: {key_obj.key_prefix}...")
    click.echo(f"  Expires: {key_obj.expires_at or 'Never'}")


@key.command()
@click.argument("org_id")
def list(org_id: str):
    """List API keys for organization."""
    auth = APIKeyManager()
    keys = auth.list_api_keys(org_id)

    if not keys:
        click.echo("No API keys found")
        return

    table_data = [
        [
            k.key_prefix + "...",
            k.created_at[:10],
            "✓" if k.is_active else "✗",
            k.expires_at[:10] if k.expires_at else "Never",
            k.description
        ]
        for k in keys
    ]

    click.echo(tabulate(
        table_data,
        headers=["Key", "Created", "Active", "Expires", "Description"]
    ))


@key.command()
@click.argument("key_id")
def revoke(key_id: str):
    """Revoke API key."""
    auth = APIKeyManager()
    if auth.revoke_api_key(key_id):
        click.secho(f"✓ Key revoked: {key_id}", fg="green")
    else:
        click.secho(f"✗ Key not found: {key_id}", fg="red")


# ============================================================================
# VAULT COMMANDS
# ============================================================================

@cli.group()
def vault():
    """Manage vault."""
    pass


@vault.command()
def info():
    """Show vault information."""
    vault_mgr = VaultManager()
    stats = vault_mgr.get_vault_stats()

    click.echo("CIAF Vault Statistics")
    click.echo("=" * 50)
    click.echo(f"Total Proofs: {stats['total_proofs']}")
    click.echo(f"Total Organizations: {stats['total_organizations']}")
    click.echo(f"Active Organizations: {stats['active_organizations']}")
    click.echo(f"Total Reads: {stats['total_reads']}")
    click.echo(f"Avg Reads per Proof: {stats['avg_reads_per_proof']:.2f}")


if __name__ == "__main__":
    cli()
