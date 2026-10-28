# =============================================================================
# postgresql/migrations/0003_expire_tables.py  -  Database Migration: Expire Module Tables
# =============================================================================
# This migration creates all the tables required by the Expire module:
#
#   1. Exhmast   (exhmast)    - Header table (Master record: doc no, category, location, date, desc)
#   2. Excmast   (excmast)    - Expire Category lookup table (e.g. Medicine, Vaccines, Feed)
#   3. Exlmast   (exlmast)    - Detail Lines table (Child items linked by exlexhsno to Exhmast)
#   4. Exlocmast (exlocmast)  - Location lookup table (e.g. Main Store, Cold Room)
#   5. Expmast   (expmast)    - Period lookup table (e.g. 1 WEEK, 1 MONTH)
#   6. Exsmast   (exsmast)    - Service/Action lookup table (e.g. Inspection, Disposal)
#   7. GGenmast  (g_genmast)  - General Ledger Account lookup table (Control + Sub accounts)
#
# Related Files:
#   - postgresql/models.py       : Defines Python model classes for each of these tables.
#   - postgresql/expire_forms.py : Forms (HeaderForm, LineForm) mapped to these tables.
#   - postgresql/expire_views.py : Views (expire_list, expire_add, expire_edit, expire_delete).
# =============================================================================

from django.db import migrations, models


class Migration(migrations.Migration):

    # Depends on migration 0002 (which seeded the initial user accounts)
    dependencies = [
        ('postgresql', '0002_seed_users'),
    ]

    operations = [
        # ---------------------------------------------------------------------
        # 1. EXHMAST - Expire Header Master Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Exhmast',
            fields=[
                # Primary key ID for each expire header document
                ('exhsno', models.AutoField(primary_key=True, serialize=False)),
                
                # Document number (e.g. EXP-20261028-0001), must be unique
                ('exhdno', models.CharField(max_length=30, unique=True)),
                
                # Foreign key references to category and location lookup tables
                ('exhexcsno', models.IntegerField()),    # Category ID (references excmast.excsno)
                ('exhexlocsno', models.IntegerField()), # Location ID (references exlocmast.exlocsno)
                
                # Transaction date and description
                ('exhddt', models.DateField()),          # Expire document date
                ('exhdes', models.CharField(max_length=50)), # Brief description / remarks
                
                # Audit trail fields: Created by, date, and time
                ('exhucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('exhentddt', models.DateField(blank=True, null=True)),
                ('exhenttime', models.TimeField(blank=True, null=True)),
                
                # Audit trail fields: Last amended by, date, and time
                ('exhucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('exhameddt', models.DateField(blank=True, null=True)),
                ('exhametime', models.TimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'exhmast',          # PostgreSQL table name
                'ordering': ['-exhsno'],        # Latest documents appear first
            },
        ),

        # ---------------------------------------------------------------------
        # 2. EXCMAST - Expire Category Lookup Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Excmast',
            fields=[
                ('excsno', models.AutoField(primary_key=True, serialize=False)), # Primary key
                ('excexc', models.CharField(default='', max_length=40)),         # Category short code
                ('excnam', models.CharField(default='', max_length=40)),         # Category display name
                ('excusdsno', models.IntegerField(blank=True, null=True)),       # User assignment ID
                ('excucdnew', models.CharField(blank=True, max_length=30, null=True)), # Creator code
                ('excentddt', models.DateField(blank=True, null=True)),          # Creation date
                ('excenttime', models.TimeField(blank=True, null=True)),         # Creation time
                ('excucdame', models.CharField(blank=True, max_length=30, null=True)), # Amend user
                ('excameddt', models.DateField(blank=True, null=True)),          # Amend date
                ('excametime', models.TimeField(blank=True, null=True)),         # Amend time
            ],
            options={
                'db_table': 'excmast',
                'ordering': ['excexc'],
                'constraints': [
                    models.UniqueConstraint(fields=('excexc',), name='excmast_excexc_uniq')
                ],
            },
        ),

        # ---------------------------------------------------------------------
        # 3. EXLMAST - Expire Detail Lines Table (Child of Exhmast)
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Exlmast',
            fields=[
                # Primary key ID for each line item
                ('exlsno', models.AutoField(primary_key=True, serialize=False)),
                
                # Parent relationship: foreign key pointing to Exhmast.exhsno
                ('exlexhsno', models.IntegerField(default=0)),
                
                # Line sequence number within the header (1, 2, 3...)
                ('exllno', models.IntegerField(default=0)),
                
                # Foreign key references to lookup tables
                ('exlexssno', models.IntegerField()),   # Service Type (references exsmast.exssno)
                ('exlexpsno', models.IntegerField()),   # Period Type (references expmast.expsno)
                ('exlgensno', models.IntegerField()),   # General Account (references g_genmast.gensno)
                
                # Line target dates
                ('exlcomplddt', models.DateField(blank=True, null=True)),  # Target completion date
                ('exlcutoffddt', models.DateField(blank=True, null=True)), # Cutoff / expiry deadline
                
                # Audit trail tracking:
                ('exlucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('exlentddt', models.DateField(blank=True, null=True)),
                ('exlenttime', models.TimeField(blank=True, null=True)),
                ('exlucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('exlameddt', models.DateField(blank=True, null=True)),
                ('exlametime', models.TimeField(blank=True, null=True)),
                ('exldelflg', models.CharField(blank=True, default='', max_length=1)), # Soft-delete flag
            ],
            options={
                'db_table': 'exlmast',
                'ordering': ['exlexhsno', 'exllno'],
                'constraints': [
                    # Composite unique constraint: ensures unique line numbers per header document
                    models.UniqueConstraint(fields=('exlexhsno', 'exllno'), name='exlmast_exlexhsno_exllno_uniq')
                ],
            },
        ),

        # ---------------------------------------------------------------------
        # 4. EXLOCMAST - Expire Location Lookup Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Exlocmast',
            fields=[
                ('exlocsno', models.AutoField(primary_key=True, serialize=False)), # Primary key
                ('exlocloc', models.CharField(default='', max_length=40)),         # Location code
                ('exlocnam', models.CharField(default='', max_length=40)),         # Location display name
                ('exlocucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('exlocentddt', models.DateField(blank=True, null=True)),
                ('exlocenttime', models.TimeField(blank=True, null=True)),
                ('exlocucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('exlocameddt', models.DateField(blank=True, null=True)),
                ('exlocametime', models.TimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'exlocmast',
                'ordering': ['exlocloc'],
                'constraints': [
                    models.UniqueConstraint(fields=('exlocloc',), name='exlocmast_exlocloc_uniq')
                ],
            },
        ),

        # ---------------------------------------------------------------------
        # 5. EXPMAST - Expire Period Lookup Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Expmast',
            fields=[
                ('expsno', models.AutoField(primary_key=True, serialize=False)), # Primary key
                ('expexp', models.CharField(default='', max_length=40)),         # Period label (e.g. 1 MONTH)
                ('expdays', models.IntegerField(blank=True, null=True)),          # Number of calendar days
                ('expucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('expentddt', models.DateField(blank=True, null=True)),
                ('expenttime', models.TimeField(blank=True, null=True)),
                ('expucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('expameddt', models.DateField(blank=True, null=True)),
                ('expametime', models.TimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'expmast',
                'ordering': ['expdays', 'expexp'],
                'constraints': [
                    models.UniqueConstraint(fields=('expexp',), name='expmast_expexp_uniq')
                ],
            },
        ),

        # ---------------------------------------------------------------------
        # 6. EXSMAST - Expire Service / Action Lookup Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='Exsmast',
            fields=[
                ('exssno', models.AutoField(primary_key=True, serialize=False)), # Primary key
                ('exsexs', models.CharField(default='', max_length=40)),         # Service code (e.g. INSP)
                ('exsnam', models.CharField(default='', max_length=40)),         # Service name (e.g. Inspection)
                ('exsucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('exsentddt', models.DateField(blank=True, null=True)),
                ('exsenttime', models.TimeField(blank=True, null=True)),
                ('exsucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('exsameddt', models.DateField(blank=True, null=True)),
                ('exsametime', models.TimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'exsmast',
                'ordering': ['exsexs'],
                'constraints': [
                    models.UniqueConstraint(fields=('exsexs',), name='exsmast_exsexs_uniq')
                ],
            },
        ),

        # ---------------------------------------------------------------------
        # 7. GGENMAST - General Ledger Accounts Table
        # ---------------------------------------------------------------------
        migrations.CreateModel(
            name='GGenmast',
            fields=[
                ('gensno', models.AutoField(primary_key=True, serialize=False)), # Primary key
                ('genctl', models.CharField(max_length=8)),                      # Control account code
                ('gensub', models.CharField(blank=True, default='', max_length=4)),# Sub-account code
                ('genctlsub', models.CharField(blank=True, default='', max_length=8)), # Combined control + sub code
                ('gendebint', models.CharField(blank=True, default='', max_length=1)),
                ('gencrdint', models.CharField(blank=True, default='', max_length=1)),
                ('gendes', models.CharField(blank=True, max_length=60, null=True)),   # Account description
                ('gendes1', models.CharField(blank=True, default='', max_length=30)), # Short description
                ('genmapcode', models.CharField(blank=True, max_length=15, null=True)),
                ('gencde', models.CharField(blank=True, max_length=1, null=True)),
                ('gencomsno', models.IntegerField(default=0)),
                ('genlocsno', models.IntegerField(default=0)),
                ('gencatsno', models.IntegerField(blank=True, null=True)),
                ('genaansno', models.IntegerField(blank=True, null=True)),
                ('gencursno', models.IntegerField(default=0)),
                ('genjobsno', models.IntegerField(default=0)),
                ('genempsno', models.IntegerField(default=0)),
                ('gengrpsno', models.IntegerField(default=0)),
                ('genectsno', models.IntegerField(default=0)),
                ('gensupyn', models.CharField(blank=True, max_length=1, null=True)),
                ('genjobyn', models.CharField(blank=True, max_length=1, null=True)),
                ('gendepyn', models.CharField(blank=True, default='', max_length=1)),
                ('genempyn', models.CharField(blank=True, default='', max_length=1)),
                ('gencusyn', models.CharField(blank=True, default='', max_length=1)),
                ('genictyn', models.CharField(blank=True, default='', max_length=1)),
                ('genadvyn', models.CharField(blank=True, default='', max_length=1)),
                ('genappyn', models.CharField(blank=True, default='', max_length=1)),
                ('gencamyn', models.CharField(blank=True, default='', max_length=1)),
                ('genvehyn', models.CharField(blank=True, default='', max_length=1)),
                ('genlocyn', models.CharField(blank=True, default='', max_length=1)),
                ('genrate', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('genbnkprefix', models.CharField(blank=True, default='', max_length=5)),
                ('genoticrdacc', models.CharField(blank=True, default='', max_length=12)),
                ('genucdnew', models.CharField(blank=True, max_length=30, null=True)),
                ('genentddt', models.DateField(blank=True, null=True)),
                ('genenttime', models.TimeField(blank=True, null=True)),
                ('genucdame', models.CharField(blank=True, max_length=30, null=True)),
                ('genameddt', models.DateField(blank=True, null=True)),
                ('genametime', models.TimeField(blank=True, null=True)),
                ('gentemp', models.CharField(blank=True, default='', max_length=1)),
            ],
            options={
                'db_table': 'g_genmast',
                'ordering': ['genctl', 'gensub'],
                'constraints': [
                    models.UniqueConstraint(fields=('genctl', 'gensub'), name='g_genmast_genctl_gensub_uniq')
                ],
            },
        ),
    ]
