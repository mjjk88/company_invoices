from company_invoices.logging_setup import setup_logger


_ERROR_LOGGER = setup_logger('DATA_ERROR', './data-errors.log')


# For now this method just log data processing errors.
# It is better to separate data processing errors/logs (detection of incorrect data record) from our own bugs in code.
# Error in processing single record should not break entire flow (I assume that).
# But our code bugs like "invalid token/password" should break the flow.
def handle_value_error(raw_data, e):
    _ERROR_LOGGER.error("%s for data record: %s ", e, raw_data)
