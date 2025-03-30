from django.db import migrations, models

def migrate_id_to_notes(apps, schema_editor):
    # Get the historical models
    Registration = apps.get_model('main', 'Registration')
    
    # Iterate through all registrations and copy id_number to notes
    for registration in Registration.objects.all():
        registration.notes = f"ID Number: {registration.id_number}"
        registration.save()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_registration_secretkey'),
    ]

    operations = [
        # First add the new notes field
        migrations.AddField(
            model_name='registration',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        
        # Then run the data migration
        migrations.RunPython(migrate_id_to_notes),
        
        # Finally remove the id_number field
        migrations.RemoveField(
            model_name='registration',
            name='id_number',
        ),
    ]