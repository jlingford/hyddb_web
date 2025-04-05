from django.db import models


class ClassificationTask(models.Model):
    task_id = models.CharField(max_length=256, primary_key=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    email_address = models.EmailField()
    no_sequences = models.PositiveIntegerField(default=0)
    downstream_protein_task_id = models.CharField(max_length=256)
