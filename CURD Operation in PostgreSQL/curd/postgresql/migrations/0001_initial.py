# =============================================================================
# postgresql/migrations/0001_initial.py  -  Database Migration: Initial Setup
# =============================================================================
# This migration creates the initial 'usdmast' (User Master) table in PostgreSQL.
#
# Target Table:
#   - Table Name: usdmast
#   - Purpose: Stores system user credentials, permissions, audit timestamps,
#              and profile configurations.
#
# Related Files:
#   - postgresql/models.py: Defines the Python model class `Usdmast`.
#   - postgresql/auth.py: Authenticates user credentials stored in this table.
#   - postgresql/views.py: Provides CRUD operations for users in this table.
# =============================================================================

from django.db import migrations, models


class Migration(migrations.Migration):

    # Marks this migration as the first (root) migration for the 'postgresql' app
    initial = True

    # No prior migrations needed before running this migration
    dependencies = [
    ]

    # Database schema operations executed when running `python manage.py migrate`
    operations = [
        migrations.CreateModel(
            name='Usdmast',
            fields=[
                # Primary Key: Auto-incrementing unique user serial number
                ('usdsno', models.AutoField(primary_key=True, serialize=False)),
                
                # User identification and credentials:
                ('usdusd', models.CharField(max_length=30)),                # Username / User Code
                ('usdcomsno', models.IntegerField(default=0)),             # Company serial number (multi-tenant key)
                ('usdnam', models.CharField(blank=True, max_length=50, null=True)),  # Display name / Full name
                ('usdpwd', models.CharField(blank=True, max_length=128, null=True)), # PBKDF2 SHA-256 hashed password
                
                # Profile & Department:
                ('usddesig', models.CharField(blank=True, default='', max_length=25)), # Job designation / title
                ('usddepsno', models.IntegerField(default=0)),             # Department ID foreign reference
                ('usdlocsno', models.IntegerField(default=0)),             # Branch location ID reference
                ('usduno', models.CharField(blank=True, default='', max_length=4)),   # User short code / unit number
                ('usdemail', models.CharField(blank=True, default='', max_length=40)), # User email address
                
                # Flags & Role access:
                ('usdadmin', models.CharField(blank=True, default='', max_length=1)),  # 'Y' if user has administrator privileges
                ('usdactflg', models.CharField(blank=True, default='', max_length=1)), # 'Y' if account is active, 'N' if disabled
                
                # Module specific access flags ('Y' / ''):
                ('usdbockpodgrnyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdbrcsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdlacsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdprnsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdeggsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdccnsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdpgfsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdcafsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdmaisalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdhegsalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdhassalyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdsalstkcatsnos', models.CharField(blank=True, default='', max_length=100)),
                ('usdrepyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdstkrolyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdprintername', models.CharField(blank=True, default='', max_length=30)),
                ('usdatfauthyn', models.CharField(blank=True, default='', max_length=1)),
                ('usdatfliamt', models.IntegerField(default=0)),
                ('usdatfnosetday', models.IntegerField(default=0)),
                ('usdpwdddt', models.DateField(blank=True, null=True)),
                ('usdsohpvalyn', models.CharField(blank=True, default='', max_length=1)),
                
                # Audit trail (New record creation tracking):
                ('usducdnew', models.CharField(blank=True, default='', max_length=10)), # User who created the record
                ('usdentddt', models.DateField(blank=True, null=True)),                  # Date record was created
                ('usdenttime', models.CharField(blank=True, default='', max_length=12)), # Time record was created
                
                # Audit trail (Amendment/Update tracking):
                ('usducdame', models.CharField(blank=True, max_length=30, null=True)),  # User who last amended the record
                ('usdameddt', models.DateField(blank=True, null=True)),                  # Date of last amendment
                ('usdametime', models.TimeField(blank=True, null=True)),                 # Time of last amendment
            ],
            options={
                'db_table': 'usdmast',          # Maps to the physical PostgreSQL table name 'usdmast'
                'ordering': ['usdsno'],         # Default query ordering by serial number ascending
                'constraints': [
                    # Unique constraint ensuring username + company ID combination is unique
                    models.UniqueConstraint(fields=('usdusd', 'usdcomsno'), name='usdmast_usdusd_usdcomsno_uniq')
                ],
            },
        ),
    ]
