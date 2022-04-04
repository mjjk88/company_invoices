from sqlalchemy import Column, String, Integer, DateTime, Numeric, create_engine, ForeignKey
from sqlalchemy.orm import validates, sessionmaker, declarative_base

Base = declarative_base()


# I decided to go with SQLAlchemy as it:
# - simplifies schema creation
# - simplifies DB model validation
# - allows to save lot of coding time on writing inserts statements manually
# - auto documents DB model (it is more readable then plain sqlite statements)
# etc.
def create_db_session_class(db_url):
    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)

# I decided to create two tables:
# - invoices (with general information about each invoice)
# - invoices_items (with info about each item and on which invoice it is placed)


class Invoice(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    subscription_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    credits_applied = Column(Numeric, nullable=False)

    @validates('invoice_id', 'customer_id', 'subscription_id', 'status')
    def validate_not_empty_str(self, key, value):
        if not value:
            raise ValueError(f"Empty value for field {key}")
        return value

    # Just validate non-null for extra safety (defensive programming)
    # It will be validated by DDB constraint but at the moment of the commit
    # so one invalid row would break entire batch which we want to avoid.
    @validates('issue_date', 'due_date', 'credits_applied')
    def validate_not_none(self, key, value):
        if value is None:
            raise ValueError(f"None value for field {key}")
        return value


# Columns like customer_id, subscription_id are duplicated (are in both tables).
# Since storage is cheaper than CPU, to speed up potential analysis in the future (avoid joins),
# I decided to break the rule about not redundant columns/tables.

class InvoiceItem(Base):
    __tablename__ = 'invoices_items'

    item_id = Column(String, primary_key=True)
    invoice_id = Column(String, ForeignKey('invoices.invoice_id'), nullable=False)
    customer_id = Column(String, nullable=False)
    subscription_id = Column(String, nullable=False)
    object = Column(String, nullable=False)
    unit_amount = Column(Numeric, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Numeric, nullable=False)
    discount_amount = Column(Numeric, nullable=False)

    @validates('item_id', 'invoice_id', 'customer_id', 'subscription_id', 'object')
    def validate_not_empty_str(self, key, value):
        if not value:
            raise ValueError(f"Empty value for field {key}")
        return value

    @validates('unit_amount', 'quantity', 'amount')
    def validate_positive_integer(self, key, value):
        if type(value) != int or value <= 0:
            raise ValueError(f"None value for field {key}")
        return value

    @validates('discount_amount')
    def validate_not_none(self, key, value):
        if value is None:
            raise ValueError(f"None value for field {key}")
        return value
