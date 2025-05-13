from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class CreatedUpdatedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def updated_recently(self):
        return self.updated_at > timezone.now() - timedelta(weeks=4)

    class Meta:
        abstract = True


class BaseModel(CreatedUpdatedMixin, models.Model):
    class Meta:
        abstract = True


class HydrogenaseSequence(BaseModel):
    OXYGEN_TOLERANCE = [
        ("Tolerant", "Tolerant"),
        ("Labile", "Labile"),
        ("Sensitive", "Sensitive"),
        ("Unknown", "Unknown"),
    ]

    ACTIVITIES = [
        ("Bidirectional", "Bidirectional"),
        ("Evolving", "Evolving"),
        ("Bifurcating", "Bifurcating"),
        ("Sensory", "Sensory"),
        ("Anaerobic Uptake", "Anaerobic Uptake"),
        ("Aerobic Uptake", "Aerobic Uptake"),
    ]

    ncbi_accession = models.CharField(
        "NCBI accession", max_length=256, primary_key=True
    )

    organism = models.CharField("Organism", max_length=256)

    hydrogenase_class = models.ForeignKey(
        "HydrogenaseClass",
        default=None,
        db_index=True,
        # on_delete=models.CASCADE,  # NOTE: added this to stop error, is needed for Django v2
    )

    protein_sequence = models.TextField(
        verbose_name="Protein Sequence",
        help_text=(
            "Protein sequence for the hydrogenase. This will be shown in the Browser."
        ),
    )

    dna_sequence = models.TextField(
        verbose_name="DNA Sequence",
        null=True,
        default="",
        blank=True,
        help_text="DNA sequence for the hydrogenase.",
    )

    sequence_for_classification = models.TextField(
        verbose_name="Sequence for Classification",
        blank=True,
        help_text=(
            "Protein sequence used for classification. This will not "
            "be shown in the Browser. If this sequence is not provided "
            "the 'Protein Sequence' will be used instead."
        ),
    )

    phylum = models.CharField("Phylum", max_length=256)

    order = models.CharField("Order", max_length=256)

    activity_predicted = models.CharField(
        "Activity (Predicted)", max_length=25, choices=ACTIVITIES
    )

    oxygen_tolerance_predicted = models.CharField(
        "Oxygen Tolerance (Predicted)", max_length=25, choices=OXYGEN_TOLERANCE
    )

    subunits_predicted = models.CharField("Subunits (Predicted)", max_length=256)

    metal_centres_predicted = models.CharField(
        "Metal Centres (Predicted)", max_length=256
    )

    accessory_subunits_predicted = models.CharField(
        "Accessory Subunits (Predicted)", max_length=256
    )

    @property
    def sequence(self):
        if self.sequence_for_classification:
            return self.sequence_for_classification
        return self.protein_sequence

    def __str__(self):
        return self.ncbi_accession

    class Meta:
        index_together = [["hydrogenase_class"]]


class NonHydrogenaseSequence(BaseModel):
    organism = models.CharField("Organism", max_length=256)

    accession = models.CharField("NCBI accession", max_length=256, primary_key=True)

    protein_sequence = models.TextField("Protein Sequence")

    phylum = models.CharField("Phylum", max_length=256)

    order = models.CharField("Order", max_length=256)

    domain = models.CharField("Domain", max_length=256)

    def __str__(self):
        return self.accession


class HydrogenaseClass(BaseModel):
    name = models.CharField(max_length=64, unique=True, primary_key=True)
    slug = models.SlugField(null=True)

    putative_class = models.BooleanField(default=False)

    # Properties
    group = models.CharField(max_length=512)
    subgroup = models.CharField(max_length=512)
    function = models.TextField()
    activity = models.CharField(max_length=512)
    oxygen_tolerance = models.CharField(max_length=512)
    localisation = models.CharField(max_length=512)

    # Distribution
    ecosystem_distribution = models.CharField(max_length=512)
    taxonomic_distribution = models.CharField(max_length=512)
    distribution_image = models.FileField(null=True, upload_to="distribution/")

    # Architecture
    subunits = models.CharField(max_length=128)
    subunit_description = models.TextField(default="", blank=True)
    catalytic_site = models.CharField(max_length=512)
    fes_clusters = models.TextField(max_length=512, blank=True, default="")

    # Important Notes
    notes = models.TextField(default="", blank=True)

    # Literature
    literature = models.TextField()

    objects = models.Manager()

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        super(HydrogenaseClass, self).save()

    class Meta:
        verbose_name_plural = "Hydrogenase classes"
        ordering = ["name"]


class GeneticOrganisation(BaseModel):
    hydrogenase_class = models.ForeignKey(
        HydrogenaseClass,
        # db_index=True,
        # on_delete=models.CASCADE,  # NOTE: added this to stop error, is needed for Django v2
    )

    # hydrogenase_class = models.ForeignKey(
    #     "HydrogenaseClass",
    #     default=None,
    #     db_index=True,
    #     # on_delete=models.CASCADE,  # NOTE: added this to stop error, is needed for Django v2
    # )

    description = models.CharField(max_length=512, null=True)
    image = models.FileField(null=True, upload_to="organisation/")

    def __str__(self):
        return self.description


class Structure(BaseModel):
    hydrogenase_class = models.ForeignKey(
        HydrogenaseClass,
        # on_delete=models.CASCADE,  # NOTE: added this to stop error, is needed for Django v2
    )
    pdb_id = models.CharField(max_length=25)
    description = models.CharField(max_length=256)

    def pdb_url(self):
        return "http://www.rcsb.org/pdb/explore/explore.do?pdbId={}".format(self.pdb_id)

    def __str__(self):
        return self.pdb_id
