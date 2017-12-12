
class Tags:

    class Thematic:
        ACC_NOTE = "account:note"

        DELIMITER = "delimiter:thematic"

        FAM_SIBLINGS = "fam:siblings"
        FAM_CHILDREN = "fam:children"
        FAM_PARENTS = "fam:parents"
        FAM_SPOUSE = "fam:spouse"

        META_NO_REMARK = "meta:no-remarks"
        META_PARENTHETICAL = "meta:parenthetical"
        META_RECORD = "meta:record-reference"

        SUBJ_AGE = "subj:age"
        SUBJ_BIO = "subj:biographical-note"
        SUBJ_EMIGRATION = "subj:emigration-event"
        SUBJ_MARTIAL = "subj:marital-status"
        SUBJ_NAME = "subj:name"
        SUBJ_NATIVEOF = "subj:native-of"
        SUBJ_OCCUPATION = "subj:occupation"
        SUBJ_RESIDENCE = "subj:residence-info"

    class Token:
        END = "END"
        START = "START"
        DELIMITER = "delimiter:thematic"
        EMIGRATION_ARRIVED = "t:emigration:ARRIVED"
        EMIGRATION_VESSEL = "t:emigration:VESSEL"
        EMIGRATION_VESSEL_HAS_ORIGIN = "t:emigration:VESSEL_HAS_ORIGIN"
        EMIGRATION_VIA = "t:emigration:VIA"

        LOCATION_DISTANCE = "t:location:DISTANCE"
        LOCATION_DISTANCE_UNIT = "t:location:DISTANCE_UNIT"
        LOCATION_FROM = "t:location:FROM"
        LOCATION_NAME = "t:location:NAME"

        META_ACCOUNT_CLOSED = "t:meta:ACCOUNT_CLOSED"
        META_ACCOUNT_NUMBER = "t:meta:ACCOUNT_NUMBER"
        META_IS_SAME_AS = "t:meta:IS_SAME_AS"
        META_NO_REMARKS = "t:meta:NO_REMARKS"
        META_SEE = "t:meta:SEE"
        META_PARENTHETICAL = "meta:parenthetical"

        PERSON_AGE = "t:person:AGE"
        PERSON_AGE_YEAR = "t:person:AGE_YEAR"
        PERSON_BROTHERS = "t:person:BROTHERS"
        PERSON_CHILDREN = "t:person:CHILDREN"
        PERSON_FATHER = "t:person:FATHER"
        PERSON_HAS_NATIONALITY = "t:person:HAS_NATIONALITY"
        PERSON_IS_DEAD = "t:person:IS_DEAD"
        PERSON_IS_LIVING = "t:person:IS_LIVING"
        PERSON_IS_SINGLE = "t:person:IS_SINGLE"
        PERSON_IS_WIDOWED = "t:person:IS_WIDOWED"
        PERSON_LOCATED_IN = "t:person:LOCATED_IN"
        PERSON_MOTHER = "t:person:MOTHER"
        PERSON_NAME = "t:person:NAME"
        PERSON_NUMBER = "t:person:NUMBER"
        PERSON_PARENTS = "t:person:PARENTS"
        PERSON_SISTERS = "t:person:SISTERS"
        PERSON_SON = "t:person:SON"
        PERSON_HUSBAND = "t:person:HUSBAND"
        PERSON_WIFE = "t:person:WIFE"

        REL_HAS = "t:rel:HAS"
        REL_HAS_HUSBAND = "t:rel:HAS_HUSBAND"
        REL_HAS_WIFE = "t:rel:HAS_WIFE"
        REL_HAS_SPOUSE = "t:rel:HAS_SPOUSE"
        REL_IS_NATIVE_OF = "t:rel:IS_NATIVE_OF"
        REL_IS_WIDOW_OF = "t:rel:IS_WIDOW_OF"
        REL_IS_DAUGHTER_OF = "t:rel:IS_DAUGHTER_OF"

        RESIDENTIAL_RESIDENCE = "t:residential:RESIDENCE"
        RESIDENTIAL_CURRENTLY_LIVING_AT = "t:residential:CURRENTLY_LIVING_AT"
        RESIDENTIAL_FORMERLY_LOCATED_AT = "t:residential:FORMERLY_LOCATED_AT"
        RESIDENTIAL_LIVED_WITH = "t:residential:LIVED_WITH"
        RESIDENTIAL_LIVES_WITH = "t:residential:LIVES_WITH"

        SUBJ_IS_MAN = "t:subj:IS_MAN"
        SUBJ_IS_WOMAN = "t:subj:IS_WOMAN"

        TIME_DATE = "t:time:DATE"
        TIME_MONTH = "t:time:MONTH"
        TIME_YEAR = "t:time:YEAR"
        TIME_DURATION_VALUE = "t:time:DURATION_VALUE"
        TIME_DURATION_YEAR = "t:time:DURATION_YEAR"

        UNKNOWN = "t:UNKNOWN"

        WORK_EMPLOYER_NAME = "t:work:EMPLOYER_NAME"
        WORK_OCCUPATION = "t:work:OCCUPATION"
        WORK_WORKS_FOR = "t:work:WORKS_FOR"
