# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class CardMembers(models.Model):
    대분류 = models.TextField(blank=True, null=True)
    카드_종류 = models.TextField(db_column='카드 종류', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    사용구분 = models.TextField(blank=True, null=True)
    회원_관련_정보 = models.TextField(db_column='회원 관련 정보', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    롯데카드 = models.FloatField(blank=True, null=True)
    비씨카드_자체_field = models.FloatField(db_column='비씨카드(자체)', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    삼성카드 = models.FloatField(blank=True, null=True)
    신한카드 = models.FloatField(blank=True, null=True)
    우리카드 = models.FloatField(blank=True, null=True)
    하나카드 = models.FloatField(blank=True, null=True)
    현대카드 = models.FloatField(blank=True, null=True)
    kb국민카드 = models.FloatField(db_column='KB국민카드', blank=True, null=True)  # Field name made lowercase.
    년월 = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card_members'


class CardSales(models.Model):
    대분류 = models.TextField(blank=True, null=True)
    카드_종류 = models.TextField(db_column='카드 종류', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    사용구분 = models.TextField(blank=True, null=True)
    결제_방법 = models.TextField(db_column='결제 방법', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    롯데카드 = models.FloatField(blank=True, null=True)
    비씨카드_자체_field = models.FloatField(db_column='비씨카드(자체)', blank=True, null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    삼성카드 = models.FloatField(blank=True, null=True)
    신한카드 = models.FloatField(blank=True, null=True)
    우리카드 = models.FloatField(blank=True, null=True)
    하나카드 = models.FloatField(blank=True, null=True)
    현대카드 = models.FloatField(blank=True, null=True)
    kb국민카드 = models.FloatField(db_column='KB국민카드', blank=True, null=True)  # Field name made lowercase.
    합계 = models.FloatField(blank=True, null=True)
    년월 = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'card_sales'


class ChatbotCardMembers(models.Model):
    id = models.BigAutoField(primary_key=True)
    대분류 = models.TextField()
    카드_종류 = models.TextField()
    사용구분 = models.TextField()
    결제_방법 = models.TextField()
    롯데카드 = models.FloatField()
    비씨카드 = models.FloatField()
    삼성카드 = models.FloatField()
    신한카드 = models.FloatField()
    우리카드 = models.FloatField()
    하나카드 = models.FloatField()
    현대카드 = models.FloatField()
    kb국민카드 = models.FloatField(db_column='KB국민카드')  # Field name made lowercase.
    date = models.DateField()

    class Meta:
        managed = False
        db_table = 'chatbot_card_members'


class ChatbotCardSales(models.Model):
    id = models.BigAutoField(primary_key=True)
    대분류 = models.TextField()
    카드_종류 = models.TextField()
    사용구분 = models.TextField()
    결제_방법 = models.TextField()
    롯데카드 = models.FloatField()
    비씨카드 = models.FloatField()
    삼성카드 = models.FloatField()
    신한카드 = models.FloatField()
    우리카드 = models.FloatField()
    하나카드 = models.FloatField()
    현대카드 = models.FloatField()
    kb국민카드 = models.FloatField(db_column='KB국민카드')  # Field name made lowercase.
    합계 = models.FloatField()
    date = models.DateField()

    class Meta:
        managed = False
        db_table = 'chatbot_card_sales'


class CpiCardData(models.Model):
    time = models.DateTimeField(db_column='TIME', blank=True, null=True)  # Field name made lowercase.
    합계_pce_pred = models.FloatField(db_column='합계_PCE_pred', blank=True, null=True)  # Field name made lowercase.
    합계_pce_lower = models.FloatField(db_column='합계_PCE_lower', blank=True, null=True)  # Field name made lowercase.
    합계_pce_upper = models.FloatField(db_column='합계_PCE_upper', blank=True, null=True)  # Field name made lowercase.
    합계_cpi_pred = models.FloatField(db_column='합계_CPI_pred', blank=True, null=True)  # Field name made lowercase.
    합계_cpi_lower = models.FloatField(db_column='합계_CPI_lower', blank=True, null=True)  # Field name made lowercase.
    합계_cpi_upper = models.FloatField(db_column='합계_CPI_upper', blank=True, null=True)  # Field name made lowercase.
    식료품_pce_pred = models.FloatField(db_column='식료품_PCE_pred', blank=True, null=True)  # Field name made lowercase.
    식료품_pce_lower = models.FloatField(db_column='식료품_PCE_lower', blank=True, null=True)  # Field name made lowercase.
    식료품_pce_upper = models.FloatField(db_column='식료품_PCE_upper', blank=True, null=True)  # Field name made lowercase.
    식료품_cpi_pred = models.FloatField(db_column='식료품_CPI_pred', blank=True, null=True)  # Field name made lowercase.
    식료품_cpi_lower = models.FloatField(db_column='식료품_CPI_lower', blank=True, null=True)  # Field name made lowercase.
    식료품_cpi_upper = models.FloatField(db_column='식료품_CPI_upper', blank=True, null=True)  # Field name made lowercase.
    의류_잡화_pce_pred = models.FloatField(db_column='의류/잡화_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의류_잡화_pce_lower = models.FloatField(db_column='의류/잡화_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의류_잡화_pce_upper = models.FloatField(db_column='의류/잡화_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의류_잡화_cpi_pred = models.FloatField(db_column='의류/잡화_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의류_잡화_cpi_lower = models.FloatField(db_column='의류/잡화_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의류_잡화_cpi_upper = models.FloatField(db_column='의류/잡화_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    연료_pce_pred = models.FloatField(db_column='연료_PCE_pred', blank=True, null=True)  # Field name made lowercase.
    연료_pce_lower = models.FloatField(db_column='연료_PCE_lower', blank=True, null=True)  # Field name made lowercase.
    연료_pce_upper = models.FloatField(db_column='연료_PCE_upper', blank=True, null=True)  # Field name made lowercase.
    연료_cpi_pred = models.FloatField(db_column='연료_CPI_pred', blank=True, null=True)  # Field name made lowercase.
    연료_cpi_lower = models.FloatField(db_column='연료_CPI_lower', blank=True, null=True)  # Field name made lowercase.
    연료_cpi_upper = models.FloatField(db_column='연료_CPI_upper', blank=True, null=True)  # Field name made lowercase.
    가구_가전_pce_pred = models.FloatField(db_column='가구/가전_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    가구_가전_pce_lower = models.FloatField(db_column='가구/가전_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    가구_가전_pce_upper = models.FloatField(db_column='가구/가전_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    가구_가전_cpi_pred = models.FloatField(db_column='가구/가전_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    가구_가전_cpi_lower = models.FloatField(db_column='가구/가전_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    가구_가전_cpi_upper = models.FloatField(db_column='가구/가전_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_pce_pred = models.FloatField(db_column='의료/보건_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_pce_lower = models.FloatField(db_column='의료/보건_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_pce_upper = models.FloatField(db_column='의료/보건_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_cpi_pred = models.FloatField(db_column='의료/보건_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_cpi_lower = models.FloatField(db_column='의료/보건_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    의료_보건_cpi_upper = models.FloatField(db_column='의료/보건_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_pce_pred = models.FloatField(db_column='여행/교통_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_pce_lower = models.FloatField(db_column='여행/교통_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_pce_upper = models.FloatField(db_column='여행/교통_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_cpi_pred = models.FloatField(db_column='여행/교통_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_cpi_lower = models.FloatField(db_column='여행/교통_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    여행_교통_cpi_upper = models.FloatField(db_column='여행/교통_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_pce_pred = models.FloatField(db_column='오락/문화_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_pce_lower = models.FloatField(db_column='오락/문화_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_pce_upper = models.FloatField(db_column='오락/문화_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_cpi_pred = models.FloatField(db_column='오락/문화_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_cpi_lower = models.FloatField(db_column='오락/문화_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    오락_문화_cpi_upper = models.FloatField(db_column='오락/문화_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    교육_pce_pred = models.FloatField(db_column='교육_PCE_pred', blank=True, null=True)  # Field name made lowercase.
    교육_pce_lower = models.FloatField(db_column='교육_PCE_lower', blank=True, null=True)  # Field name made lowercase.
    교육_pce_upper = models.FloatField(db_column='교육_PCE_upper', blank=True, null=True)  # Field name made lowercase.
    교육_cpi_pred = models.FloatField(db_column='교육_CPI_pred', blank=True, null=True)  # Field name made lowercase.
    교육_cpi_lower = models.FloatField(db_column='교육_CPI_lower', blank=True, null=True)  # Field name made lowercase.
    교육_cpi_upper = models.FloatField(db_column='교육_CPI_upper', blank=True, null=True)  # Field name made lowercase.
    숙박_음식_pce_pred = models.FloatField(db_column='숙박/음식_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    숙박_음식_pce_lower = models.FloatField(db_column='숙박/음식_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    숙박_음식_pce_upper = models.FloatField(db_column='숙박/음식_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    숙박_음식_cpi_pred = models.FloatField(db_column='숙박/음식_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    숙박_음식_cpi_lower = models.FloatField(db_column='숙박/음식_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    숙박_음식_cpi_upper = models.FloatField(db_column='숙박/음식_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_pce_pred = models.FloatField(db_column='공과금/개인 및 전문 서비스_PCE_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_pce_lower = models.FloatField(db_column='공과금/개인 및 전문 서비스_PCE_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_pce_upper = models.FloatField(db_column='공과금/개인 및 전문 서비스_PCE_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_cpi_pred = models.FloatField(db_column='공과금/개인 및 전문 서비스_CPI_pred', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_cpi_lower = models.FloatField(db_column='공과금/개인 및 전문 서비스_CPI_lower', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    공과금_개인_및_전문_서비스_cpi_upper = models.FloatField(db_column='공과금/개인 및 전문 서비스_CPI_upper', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'cpi_card_data'


class CurrencyRate(models.Model):
    cur_unit = models.TextField(blank=True, null=True)
    ttb = models.TextField(blank=True, null=True)
    tts = models.TextField(blank=True, null=True)
    deal_bas_r = models.TextField(blank=True, null=True)
    bkpr = models.TextField(blank=True, null=True)
    yy_efee_r = models.FloatField(blank=True, null=True)
    ten_dd_efee_r = models.FloatField(blank=True, null=True)
    kftc_bkpr = models.TextField(blank=True, null=True)
    kftc_deal_bas_r = models.TextField(blank=True, null=True)
    cur_nm = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'currency_rate'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField(blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)
    app = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    applied = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoPlotlyDashDashapp(models.Model):
    id = models.IntegerField(primary_key=True)
    instance_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.CharField(max_length=110, blank=True, null=True)
    base_state = models.TextField()
    creation = models.DateTimeField(blank=True, null=True)
    update = models.DateTimeField(blank=True, null=True)
    save_on_change = models.IntegerField(blank=True, null=True)
    stateless_app_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_plotly_dash_dashapp'


class DjangoPlotlyDashStatelessapp(models.Model):
    id = models.IntegerField(primary_key=True)
    app_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.CharField(max_length=110, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_plotly_dash_statelessapp'


class DjangoSession(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_session'


class EduDataFCleaned(models.Model):
    고객번호 = models.CharField(max_length=50, blank=True, null=True)
    연령대 = models.CharField(max_length=50, blank=True, null=True)
    성별 = models.CharField(max_length=50, blank=True, null=True)
    회원등급 = models.CharField(max_length=50, blank=True, null=True)
    거주지역_1 = models.CharField(max_length=50, blank=True, null=True)
    라이프스테이지 = models.CharField(max_length=50, blank=True, null=True)
    총이용금액 = models.IntegerField(blank=True, null=True)
    신용카드이용금액 = models.IntegerField(blank=True, null=True)
    체크카드이용금액 = models.IntegerField(blank=True, null=True)
    가전_가구_주방용품 = models.IntegerField(db_column='가전/가구/주방용품', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    보험_병원 = models.IntegerField(db_column='보험/병원', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    사무통신_서적_학원 = models.IntegerField(db_column='사무통신/서적/학원', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    여행_레져_문화 = models.IntegerField(db_column='여행/레져/문화', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    요식업 = models.IntegerField(blank=True, null=True)
    용역_수리_건축자재 = models.IntegerField(db_column='용역/수리/건축자재', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    유통 = models.IntegerField(blank=True, null=True)
    보건위생 = models.IntegerField(blank=True, null=True)
    의류_신변잡화 = models.IntegerField(db_column='의류/신변잡화', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    자동차_연료_정비 = models.IntegerField(db_column='자동차/연료/정비', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    가구 = models.IntegerField(blank=True, null=True)
    가전제품 = models.IntegerField(blank=True, null=True)
    건물및시설관리 = models.IntegerField(blank=True, null=True)
    건축_자재 = models.IntegerField(db_column='건축/자재', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    광학제품 = models.IntegerField(blank=True, null=True)
    농업 = models.IntegerField(blank=True, null=True)
    레져업소 = models.IntegerField(blank=True, null=True)
    레져용품 = models.IntegerField(blank=True, null=True)
    문화_취미 = models.IntegerField(db_column='문화/취미', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    보건_위생 = models.IntegerField(db_column='보건/위생', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    보험 = models.IntegerField(blank=True, null=True)
    사무_통신기기 = models.IntegerField(db_column='사무/통신기기', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    서적_문구 = models.IntegerField(db_column='서적/문구', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    수리서비스 = models.IntegerField(blank=True, null=True)
    숙박업 = models.IntegerField(blank=True, null=True)
    신변잡화 = models.IntegerField(blank=True, null=True)
    여행업 = models.IntegerField(blank=True, null=True)
    연료판매 = models.IntegerField(blank=True, null=True)
    용역서비스 = models.IntegerField(blank=True, null=True)
    유통업비영리 = models.IntegerField(blank=True, null=True)
    유통업영리 = models.IntegerField(blank=True, null=True)
    음식료품 = models.IntegerField(blank=True, null=True)
    의료기관 = models.IntegerField(blank=True, null=True)
    의류 = models.IntegerField(blank=True, null=True)
    일반_휴게음식 = models.IntegerField(db_column='일반/휴게음식', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    자동차정비_유지 = models.IntegerField(db_column='자동차정비/유지', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    자동차판매 = models.IntegerField(blank=True, null=True)
    주방용품 = models.IntegerField(blank=True, null=True)
    직물 = models.IntegerField(blank=True, null=True)
    학원 = models.IntegerField(blank=True, null=True)
    회원제형태업소 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edu_data_f_cleaned'


class FranchiseData(models.Model):
    yr = models.TextField(blank=True, null=True)
    indutylclasnm = models.TextField(db_column='indutyLclasNm', blank=True, null=True)  # Field name made lowercase.
    indutymlsfcnm = models.TextField(db_column='indutyMlsfcNm', blank=True, null=True)  # Field name made lowercase.
    corpnm = models.TextField(db_column='corpNm', blank=True, null=True)  # Field name made lowercase.
    brandnm = models.TextField(db_column='brandNm', blank=True, null=True)  # Field name made lowercase.
    frcscnt = models.BigIntegerField(db_column='frcsCnt', blank=True, null=True)  # Field name made lowercase.
    newfrcsrgscnt = models.BigIntegerField(db_column='newFrcsRgsCnt', blank=True, null=True)  # Field name made lowercase.
    ctrtendcnt = models.BigIntegerField(db_column='ctrtEndCnt', blank=True, null=True)  # Field name made lowercase.
    ctrtcncltncnt = models.BigIntegerField(db_column='ctrtCncltnCnt', blank=True, null=True)  # Field name made lowercase.
    nmchgcnt = models.BigIntegerField(db_column='nmChgCnt', blank=True, null=True)  # Field name made lowercase.
    avrgslsamt = models.FloatField(db_column='avrgSlsAmt', blank=True, null=True)  # Field name made lowercase.
    arunitavrgslsamt = models.FloatField(db_column='arUnitAvrgSlsAmt', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'franchise_data'


class FredData(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    fftr = models.FloatField(db_column='FFTR', blank=True, null=True)  # Field name made lowercase.
    gdp = models.FloatField(db_column='GDP', blank=True, null=True)  # Field name made lowercase.
    gdp_growth_rate = models.FloatField(db_column='GDP Growth Rate', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pce = models.FloatField(db_column='PCE', blank=True, null=True)  # Field name made lowercase.
    core_pce = models.FloatField(db_column='Core PCE', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    cpi = models.FloatField(db_column='CPI', blank=True, null=True)  # Field name made lowercase.
    core_cpi = models.FloatField(db_column='Core CPI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    personal_income = models.FloatField(db_column='Personal Income', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    unemployment_rate = models.FloatField(db_column='Unemployment Rate', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    ism_manufacturing = models.FloatField(db_column='ISM Manufacturing', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    durable_goods_orders = models.FloatField(db_column='Durable Goods Orders', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    building_permits = models.FloatField(db_column='Building Permits', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    retail_sales = models.FloatField(db_column='Retail Sales', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    consumer_sentiment = models.FloatField(db_column='Consumer Sentiment', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    nonfarm_payrolls = models.FloatField(db_column='Nonfarm Payrolls', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    jolts_hires = models.FloatField(db_column='JOLTS Hires', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'fred_data'


class KoreaBaseRate(models.Model):
    time = models.TextField(db_column='TIME', blank=True, null=True)  # Field name made lowercase.
    bor = models.TextField(db_column='BOR', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'korea_base_rate'


class KoreaIndex(models.Model):
    time = models.TextField(db_column='TIME', blank=True, null=True)  # Field name made lowercase.
    gdp = models.TextField(db_column='GDP', blank=True, null=True)  # Field name made lowercase.
    경제성장률 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'korea_index'


class TourIntrst(models.Model):
    respond_id = models.BigIntegerField(db_column='RESPOND_ID', blank=True, null=True)  # Field name made lowercase.
    examin_begin_de = models.DateTimeField(db_column='EXAMIN_BEGIN_DE', blank=True, null=True)  # Field name made lowercase.
    sexdstn_flag_cd = models.TextField(db_column='SEXDSTN_FLAG_CD', blank=True, null=True)  # Field name made lowercase.
    agrde_flag_nm = models.TextField(db_column='AGRDE_FLAG_NM', blank=True, null=True)  # Field name made lowercase.
    answrr_oc_area_nm = models.TextField(db_column='ANSWRR_OC_AREA_NM', blank=True, null=True)  # Field name made lowercase.
    hshld_income_dgree_nm = models.TextField(db_column='HSHLD_INCOME_DGREE_NM', blank=True, null=True)  # Field name made lowercase.
    china_tour_intrst_value = models.TextField(db_column='CHINA_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    jp_tour_intrst_value = models.TextField(db_column='JP_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    hongkong_macau_tour_intrst_value = models.TextField(db_column='HONGKONG_MACAU_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    seasia_tour_intrst_value = models.TextField(db_column='SEASIA_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    mdlest_swasia_tour_intrst_value = models.TextField(db_column='MDLEST_SWASIA_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    usa_canada_tour_intrst_value = models.TextField(db_column='USA_CANADA_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    samrc_lamrc_tour_intrst_value = models.TextField(db_column='SAMRC_LAMRC_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    weurp_neurp_tour_intrst_value = models.TextField(db_column='WEURP_NEURP_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    eeurp_tour_intrst_value = models.TextField(db_column='EEURP_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    seurp_tour_intrst_value = models.TextField(db_column='SEURP_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    spcpc_tour_intrst_value = models.TextField(db_column='SPCPC_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.
    africa_tour_intrst_value = models.TextField(db_column='AFRICA_TOUR_INTRST_VALUE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tour_intrst'


class TravelAdvices(models.Model):
    country = models.TextField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    travel_advice = models.TextField(db_column='Travel_Advice', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'travel_advices'


class TravelCaution(models.Model):
    country = models.TextField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    country_en = models.TextField(db_column='Country_EN', blank=True, null=True)  # Field name made lowercase.
    iso_alpha_3 = models.TextField(db_column='ISO_Alpha_3', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'travel_caution'


class TravelCautions(models.Model):
    country = models.TextField(db_column='Country', blank=True, null=True)  # Field name made lowercase.
    travel_caution = models.IntegerField(db_column='Travel_Caution', blank=True, null=True)  # Field name made lowercase.
    travel_restriction = models.IntegerField(db_column='Travel_Restriction', blank=True, null=True)  # Field name made lowercase.
    departure_advisory = models.IntegerField(db_column='Departure_Advisory', blank=True, null=True)  # Field name made lowercase.
    travel_ban = models.IntegerField(db_column='Travel_Ban', blank=True, null=True)  # Field name made lowercase.
    special_travel_advisory = models.IntegerField(db_column='Special_Travel_Advisory', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'travel_cautions'


class TravelNaverSearchAll(models.Model):
    group_name = models.TextField(blank=True, null=True)
    period = models.TextField(blank=True, null=True)
    ratio = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travel_naver_search_all'


class TravelTrend(models.Model):
    country = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    ratio = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travel_trend'


class TravelTrendCv(models.Model):
    country = models.TextField(blank=True, null=True)
    trend_growth = models.FloatField(blank=True, null=True)
    trend_var = models.FloatField(blank=True, null=True)
    trend_cv = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travel_trend_cv'

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    is_power_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['created_at']