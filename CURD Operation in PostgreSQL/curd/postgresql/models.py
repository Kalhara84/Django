from django.db import models


def yn():
    return models.CharField(max_length=1, blank=True, default="")


class Usdmast(models.Model):
    usdsno = models.AutoField(primary_key=True)                      
    usdusd = models.CharField(max_length=30)                         
    usdcomsno = models.IntegerField(default=0)
    usdnam = models.CharField(max_length=50, null=True, blank=True)   
    
    usdpwd = models.CharField(max_length=128, null=True, blank=True)
    usddesig = models.CharField(max_length=25, blank=True, default="")
    usddepsno = models.IntegerField(default=0)
    usdlocsno = models.IntegerField(default=0)
    usduno = models.CharField(max_length=4, blank=True, default="")
    usdemail = models.CharField(max_length=40, blank=True, default="")
    usdadmin = yn()
    usdactflg = yn()
    usdbockpodgrnyn = yn()
    usdbrcsalyn = yn()
    usdlacsalyn = yn()
    usdprnsalyn = yn()
    usdeggsalyn = yn()
    usdccnsalyn = yn()
    usdpgfsalyn = yn()
    usdcafsalyn = yn()
    usdmaisalyn = yn()
    usdhegsalyn = yn()
    usdhassalyn = yn()
    usdsalstkcatsnos = models.CharField(max_length=100, blank=True, default="")
    usdrepyn = yn()
    usdstkrolyn = yn()
    usdprintername = models.CharField(max_length=30, blank=True, default="")
    usdatfauthyn = yn()
    usdatfliamt = models.IntegerField(default=0)
    usdatfnosetday = models.IntegerField(default=0)

    usdpwdddt = models.DateField(null=True, blank=True)
    usdsohpvalyn = yn()
    usducdnew = models.CharField(max_length=10, blank=True, default="")      # created by
    usdentddt = models.DateField(null=True, blank=True)                      # created date
    usdenttime = models.CharField(max_length=12, blank=True, default="")     # created time
    usducdame = models.CharField(max_length=30, null=True, blank=True)       # LAST UPDATED BY
    usdameddt = models.DateField(null=True, blank=True)                      # last updated date
    usdametime = models.TimeField(null=True, blank=True)                     # last updated time

    class Meta:
        db_table = "usdmast"
        ordering = ["usdsno"]
        constraints = [
            models.UniqueConstraint(fields=["usdusd", "usdcomsno"], name="usdmast_usdusd_usdcomsno_uniq"),
        ]

    def __str__(self):
        return f"{self.usdusd} - {self.usdnam or ''}"

    @property
    def is_admin(self):
        return (self.usdadmin or "").upper() == "Y"

    @property
    def is_active_user(self):
        return (self.usdactflg or "").upper() != "N"


class Excmast(models.Model):
    """Item category"""
    excsno = models.AutoField(primary_key=True)
    excexc = models.CharField(max_length=40, default="")
    excnam = models.CharField(max_length=40, default="")
    excusdsno = models.IntegerField(null=True, blank=True)
    excucdnew = models.CharField(max_length=30, null=True, blank=True)
    excentddt = models.DateField(null=True, blank=True)
    excenttime = models.TimeField(null=True, blank=True)
    excucdame = models.CharField(max_length=30, null=True, blank=True)
    excameddt = models.DateField(null=True, blank=True)
    excametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "excmast"
        ordering = ["excexc"]
        constraints = [models.UniqueConstraint(fields=["excexc"], name="excmast_excexc_uniq")]

    def __str__(self):
        return f"{self.excexc} - {self.excnam}"


class Exlocmast(models.Model):
    """Location"""
    exlocsno = models.AutoField(primary_key=True)
    exlocloc = models.CharField(max_length=40, default="")
    exlocnam = models.CharField(max_length=40, default="")
    exlocucdnew = models.CharField(max_length=30, null=True, blank=True)
    exlocentddt = models.DateField(null=True, blank=True)
    exlocenttime = models.TimeField(null=True, blank=True)
    exlocucdame = models.CharField(max_length=30, null=True, blank=True)
    exlocameddt = models.DateField(null=True, blank=True)
    exlocametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exlocmast"
        ordering = ["exlocloc"]
        constraints = [models.UniqueConstraint(fields=["exlocloc"], name="exlocmast_exlocloc_uniq")]

    def __str__(self):
        return f"{self.exlocloc} - {self.exlocnam}"


class Exsmast(models.Model):
    """Service category"""
    exssno = models.AutoField(primary_key=True)
    exsexs = models.CharField(max_length=40, default="")
    exsnam = models.CharField(max_length=40, default="")
    exsucdnew = models.CharField(max_length=30, null=True, blank=True)
    exsentddt = models.DateField(null=True, blank=True)
    exsenttime = models.TimeField(null=True, blank=True)
    exsucdame = models.CharField(max_length=30, null=True, blank=True)
    exsameddt = models.DateField(null=True, blank=True)
    exsametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exsmast"
        ordering = ["exsexs"]
        constraints = [models.UniqueConstraint(fields=["exsexs"], name="exsmast_exsexs_uniq")]

    def __str__(self):
        return f"{self.exsexs} - {self.exsnam}"


class Expmast(models.Model):
    """Period"""
    expsno = models.AutoField(primary_key=True)
    expexp = models.CharField(max_length=40, default="")
    expdays = models.IntegerField(null=True, blank=True)
    expucdnew = models.CharField(max_length=30, null=True, blank=True)
    expentddt = models.DateField(null=True, blank=True)
    expenttime = models.TimeField(null=True, blank=True)
    expucdame = models.CharField(max_length=30, null=True, blank=True)
    expameddt = models.DateField(null=True, blank=True)
    expametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "expmast"
        ordering = ["expdays", "expexp"]
        constraints = [models.UniqueConstraint(fields=["expexp"], name="expmast_expexp_uniq")]

    def __str__(self):
        return f"{self.expexp} ({self.expdays} days)"


class GGenmast(models.Model):
    """General ledger / account master (Acc Code)"""
    gensno = models.AutoField(primary_key=True)
    genctl = models.CharField(max_length=8)
    gensub = models.CharField(max_length=4, default="", blank=True)
    genctlsub = models.CharField(max_length=8, default="", blank=True)
    gendebint = models.CharField(max_length=1, default="", blank=True)
    gencrdint = models.CharField(max_length=1, default="", blank=True)
    gendes = models.CharField(max_length=60, null=True, blank=True)
    gendes1 = models.CharField(max_length=30, default="", blank=True)
    genmapcode = models.CharField(max_length=15, null=True, blank=True)
    gencde = models.CharField(max_length=1, null=True, blank=True)
    gencomsno = models.IntegerField(default=0)
    genlocsno = models.IntegerField(default=0)
    gencatsno = models.IntegerField(null=True, blank=True)
    genaansno = models.IntegerField(null=True, blank=True)
    gencursno = models.IntegerField(default=0)
    genjobsno = models.IntegerField(default=0)
    genempsno = models.IntegerField(default=0)
    gengrpsno = models.IntegerField(default=0)
    genectsno = models.IntegerField(default=0)
    gensupyn = models.CharField(max_length=1, null=True, blank=True)
    genjobyn = models.CharField(max_length=1, null=True, blank=True)
    gendepyn = models.CharField(max_length=1, default="", blank=True)
    genempyn = models.CharField(max_length=1, default="", blank=True)
    gencusyn = models.CharField(max_length=1, default="", blank=True)
    genictyn = models.CharField(max_length=1, default="", blank=True)
    genadvyn = models.CharField(max_length=1, default="", blank=True)
    genappyn = models.CharField(max_length=1, default="", blank=True)
    gencamyn = models.CharField(max_length=1, default="", blank=True)
    genvehyn = models.CharField(max_length=1, default="", blank=True)
    genlocyn = models.CharField(max_length=1, default="", blank=True)
    genrate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    genbnkprefix = models.CharField(max_length=5, default="", blank=True)
    genoticrdacc = models.CharField(max_length=12, default="", blank=True)
    genucdnew = models.CharField(max_length=30, null=True, blank=True)
    genentddt = models.DateField(null=True, blank=True)
    genenttime = models.TimeField(null=True, blank=True)
    genucdame = models.CharField(max_length=30, null=True, blank=True)
    genameddt = models.DateField(null=True, blank=True)
    genametime = models.TimeField(null=True, blank=True)
    gentemp = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "g_genmast"
        ordering = ["genctl", "gensub"]
        constraints = [models.UniqueConstraint(fields=["genctl", "gensub"], name="g_genmast_genctl_gensub_uniq")]

    def __str__(self):
        return f"{self.genctl}-{self.gensub} {self.gendes or ''}"


class Exhmast(models.Model):
    """Expire entry HEADER"""
    exhsno = models.AutoField(primary_key=True)
    exhdno = models.CharField(max_length=30, unique=True)          # code
    exhexcsno = models.IntegerField()                              # -> excmast.excsno
    exhexlocsno = models.IntegerField()                            # -> exlocmast.exlocsno
    exhddt = models.DateField()                                    # date
    exhdes = models.CharField(max_length=50)                       # description
    exhucdnew = models.CharField(max_length=30, null=True, blank=True)
    exhentddt = models.DateField(null=True, blank=True)
    exhenttime = models.TimeField(null=True, blank=True)
    exhucdame = models.CharField(max_length=30, null=True, blank=True)
    exhameddt = models.DateField(null=True, blank=True)
    exhametime = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "exhmast"
        ordering = ["-exhsno"]

    def __str__(self):
        return self.exhdno


class Exlmast(models.Model):
    """Expire entry LINES  (exlexhsno = exhmast.exhsno, exllno = 1,2,3 ...)"""
    exlsno = models.AutoField(primary_key=True)
    exlexhsno = models.IntegerField(default=0)
    exllno = models.IntegerField(default=0)
    exlexssno = models.IntegerField()                              # -> exsmast.exssno
    exlexpsno = models.IntegerField()                              # -> expmast.expsno
    exlgensno = models.IntegerField()                              # -> g_genmast.gensno
    exlcomplddt = models.DateField(null=True, blank=True)
    exlcutoffddt = models.DateField(null=True, blank=True)
    exlucdnew = models.CharField(max_length=30, null=True, blank=True)
    exlentddt = models.DateField(null=True, blank=True)
    exlenttime = models.TimeField(null=True, blank=True)
    exlucdame = models.CharField(max_length=30, null=True, blank=True)
    exlameddt = models.DateField(null=True, blank=True)
    exlametime = models.TimeField(null=True, blank=True)
    exldelflg = models.CharField(max_length=1, default="", blank=True)

    class Meta:
        db_table = "exlmast"
        ordering = ["exlexhsno", "exllno"]
        constraints = [models.UniqueConstraint(fields=["exlexhsno", "exllno"], name="exlmast_exlexhsno_exllno_uniq")]
