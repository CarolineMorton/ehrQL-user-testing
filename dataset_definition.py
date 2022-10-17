from databuilder.query_language import Dataset
from databuilder.codes import codelist_from_csv

from tests.acceptance.comparative_booster_study.schema import coded_events
from tests.acceptance.comparative_booster_study.schema import patients
from tests.acceptance.comparative_booster_study.schema import practice_registrations

from tests.acceptance.comparative_booster_study.codelists import codelist

from datetime import datetime, timedelta


## define codelists
CODELIST_DIR = "codelists"

lung_cancer = codelist_from_csv(
    CODELIST_DIR
    / "lung-cancer-snomed.csv",
    system="snomedct",
    column="code",
)

diabetes = codelist_from_csv(
    CODELIST_DIR
    / "diabetes-codes.csv",
    system="snomedct",
    column="code",
)

systolic_bp = codelist_from_csv(
    CODELIST_DIR
    / "sbp.csv",
    system="snomedct",
    column="code",
)

# set up the dataset
dataset = Dataset()

# Convert datetime object to date object.
date_from_str = datetime.strptime("2022-08-14", "%Y-%m-%d")
study_date = date_from_str.date()
start_of_follow_up = study_date - timedelta(days=365)

# create list of events in the last year
events_in_last_year = coded_events.take((coded_events.date > start_of_follow_up) & (coded_events.date <= study_date))

# set up the population
# define variables for the population first
age = patients.date_of_birth.difference_in_years(study_date)

# lung cancer 
has_lung_cancer = coded_events.take(coded_events.snomedct_code.is_in(lung_cancer)).exists_for_patient()

# registered with GP
register_gp = practice_registrations.take(
        practice_registrations.start_date.is_on_or_before(start_of_follow_up)
        & (practice_registrations.end_date.is_after(study_date) | practice_registrations.end_date.is_null())
    ).exists_for_patient()

# set the population
dataset.set_population((age >= 18) & has_asthma & register_gp)

# variables - i.e. columns
dataset.age = age
dataset.sex = patients.sex
dataset.lung_cancer_diag_date = coded_events.take(coded_events.snomedct_code.is_in(lung_cancer)).sort_by(coded_events.date).first_for_patient().date

# diabetes
dataset.has_diabetes = coded_events.take(coded_events.snomedct_code.is_in(diabetes)).exists_for_patient()

# blood pressure
dataset.bp_last = events_in_last_year.take(events_in_last_year.snomedct_code.is_in(sbp)).value()
