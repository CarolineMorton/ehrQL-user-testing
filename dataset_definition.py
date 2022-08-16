from databuilder.query_language import Dataset

from tests.acceptance.comparative_booster_study.schema import coded_events
from tests.acceptance.comparative_booster_study.schema import patients
from tests.acceptance.comparative_booster_study.schema import practice_registrations

from tests.acceptance.comparative_booster_study.codelists import codelist

from datetime import datetime, timedelta

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

asthma = codelist(['AAA'], system="snomedct")
has_asthma = coded_events.take(coded_events.snomedct_code.is_in(asthma)).exists_for_patient()

register_gp = practice_registrations.take(
        practice_registrations.start_date.is_on_or_before(start_of_follow_up)
        & (practice_registrations.end_date.is_after(study_date) | practice_registrations.end_date.is_null())
    ).exists_for_patient()

# set the population
dataset.set_population((age >= 18) & has_asthma & register_gp)

# variables - i.e. columns
dataset.age = age
dataset.sex = patients.sex
dataset.asthma_diag_date = coded_events.take(coded_events.snomedct_code.is_in(asthma)).sort_by(coded_events.date).first_for_patient().date

diabetes = codelist(['BBB'], system="snomedct")
dataset.has_diabetes = coded_events.take(coded_events.snomedct_code.is_in(diabetes)).exists_for_patient()

steroids = codelist(['CCC'], system="snomedct")
dataset.steroids_last_year = events_in_last_year.take(events_in_last_year.snomedct_code.is_in(steroids)).exists_for_patient()

dataset.steroids_count = events_in_last_year.take(events_in_last_year.snomedct_code.is_in(steroids)).count_for_patient()
