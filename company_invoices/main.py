import os
from datetime import datetime
from optparse import OptionParser

import chargebee

from company_invoices.db_model import create_db_session_class
from company_invoices.invoices_mapper import batch_map_chargebee_response_to_internal_model
from company_invoices.logging_setup import setup_logger


def parse_args():
    parser = OptionParser(version="0.1",
                          description="Script fetches all invoices from Chargebee and persists them to local SQL database.",
                          usage="main.py --domain CHARGEBEE_DOMAIN --db DB_URL")
    parser.add_option("--domain", dest="domain",
                      help="Chargebee domain to connect to e.g. 'test'")
    parser.add_option("--db", dest="db",
                      help="Database url e.g. 'sqlite:///company_invoices.db'")

    (options, args) = parser.parse_args()

    if not options.domain:
        parser.error("--domain is required")
    if not options.db:
        parser.error("--db is required")

    # I used environment variable for safety storing the token,
    # but we should ask the security team and do this in accordance with company policy.
    token = os.environ.get('CHARGEBEE_API_TOKEN')
    if not token:
        raise ValueError("CHARGEBEE_API_TOKEN env variable is required")

    options.token = token
    return options


if __name__ == '__main__':
    options = parse_args()
    logger_app = setup_logger('INVOICES', './company_invoices_etl.log')

    start = datetime.now()
    logger_app.info('INVOICES ETL script started')
    try:
        chargebee.configure(options.token, options.domain)
        logger_app.info('Chargebee connection configured')

        Session = create_db_session_class(options.db)
        session = Session()
        logger_app.info('DB session created')

        next_offset = None
        while True:
            logger_app.info("Processing next batch")
            # According to Chargebee documentation, max batch limit = 100
            invoices = chargebee.Invoice.list({"limit": 100, "offset": next_offset})

            logger_app.info("Received %d invoices from Chargebee", len(invoices.response))

            invoices_to_commit, invoices_items_to_commit = batch_map_chargebee_response_to_internal_model(invoices)
            logger_app.info("Mapped %d invoices and %d items to DB model", len(invoices_to_commit),
                            len(invoices_items_to_commit))

            session.add_all(invoices_to_commit)
            session.add_all(invoices_items_to_commit)

            session.commit()
            logger_app.info("DB batch committed")

            next_offset = invoices.next_offset
            if next_offset is None:
                break
    except:
        logger_app.exception("Error occurred")

    logger_app.info('Total time: %s', datetime.now() - start)
    # Maybe we should also log some stats like number of invoices saved, items saved and data errors
